import os
import shutil
import time
from database import connect_to_db, call_stored_procedure
from datetime import datetime

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
            for i in range(3, 0, -1):
                log(f"Calling stored procedure in {i} seconds...")
                time.sleep(1)  # Simulate countdown

            success_count = 0
            exist_count = 0
            fail_count = 0

            for index, file_name in enumerate(files_to_process, start=1):
                file_path = os.path.join(input_path, file_name)
                status, message = call_stored_procedure(connection, stored_procedure, file_path)

                if status == 0:
                    success_count += 1
                    if delete_processed_files:
                        os.remove(file_path)
                    else:
                        shutil.move(file_path, output_path)
                elif status == 1:
                    exist_count += 1
                    if delete_processed_files:
                        os.remove(file_path)
                    else:
                        shutil.move(file_path, output_path)
                else:
                    fail_count += 1
                    if log_rejected:
                        log_rejected(f"File {file_name}: {message}")

                # Update progress
                log(f"Processed {index} out of {len(files_to_process)} files.", overwrite=True)

            batch_summary = (
                f"Batch Summary:\n"
                f"Total files processed: {len(files_to_process)}\n"
                f"Success: {success_count}\n"
                f"Already exist: {exist_count}\n"
                f"Failed: {fail_count}\n"
                f"Processed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                "----------------------------------------"
            )
            log(batch_summary)
            
            rejected_summary = (
                f"Rejected Batch Summary:\n"
                f"Processed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                "----------------------------------------"
            )
            if log_rejected:
                log_rejected(rejected_summary)
        else:
            log("No files to process.")

        time.sleep(30)  # Wait before next batch

        if stop_requested():
            break
