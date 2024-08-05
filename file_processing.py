import os
import shutil
import time
from database import connect_to_db, call_stored_procedure

def process_files(input_path, output_path, load_tmp_files, delete_tmp_files, delete_processed_files, server, database, stored_procedure, auth_type, username, password, log, stop_requested, batch_size=1000, log_rejected=None):
    while not stop_requested():
        try:
            connection = connect_to_db(server, database, auth_type, username, password)
            log("Connected to the database successfully.")
        except Exception as e:
            log(f"Failed to connect to the database: {e}")
            return

        files = os.listdir(input_path)
        if not load_tmp_files:
            files_to_process = [f for f in files if not f.endswith('.tmp')]
        else:
            files_to_process = files

        if delete_tmp_files:
            tmp_files = [f for f in files if f.endswith('.tmp')]
            for tmp_file in tmp_files:
                os.remove(os.path.join(input_path, tmp_file))
                log(f"Deleted .tmp file: {tmp_file}")

        if len(files_to_process) > batch_size:
            files_to_process = files_to_process[:batch_size]

        if files_to_process:
            log(f"Read {len(files_to_process)} files.")
            time.sleep(3)  # Simulate countdown

            for file_name in files_to_process:
                file_path = os.path.join(input_path, file_name)
                status, message = call_stored_procedure(connection, stored_procedure, file_name, file_path)
                color = "green" if status == 0 else "yellow" if status == 1 else "red"
                log(f"{time.strftime('%Y-%m-%d %H:%M:%S')} FILE: {file_path} STATUS: {status} MESSAGE: {message}", color=color)

                if status == 0 or status == 1:
                    if delete_processed_files:
                        os.remove(file_path)
                        log(f"Deleted processed file: {file_name}", status=str(status))
                    else:
                        shutil.move(file_path, output_path)
                        log(f"Moved file: {file_name}", status=str(status))
                else:
                    log_rejected(f"{time.strftime('%Y-%m-%d %H:%M:%S')} FILE: {file_path} STATUS: {status} MESSAGE: {message}", color="red")
                log("---------------------------------------------------------")
        else:
            log("No files to process.")
        
        time.sleep(30)  # Wait before next batch

        if stop_requested():
            break
