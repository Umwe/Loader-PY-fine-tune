import os
from datetime import datetime
from database import connect_to_db, call_stored_procedure

def process_files(input_path, output_path, load_tmp_files, delete_tmp_files, delete_processed_files, server, database, stored_procedure, auth_type, username, password, log, stop_requested, batch_size, log_rejected):
    connection = connect_to_db(server, database, auth_type, username, password)
    
    files = os.listdir(input_path)
    files_processed = 0
    total_files = len(files)
    
    log(f"Read {total_files} files.")
    
    for file_name in files:
        if stop_requested():
            log("Stop requested. Waiting for the current batch to finish...")
            break

        file_path = os.path.join(input_path, file_name)
        start_time = datetime.now()
        
        status, message = call_stored_procedure(connection, stored_procedure, file_name, file_path)
        end_time = datetime.now()
        processing_time = end_time - start_time
        
        if status == 0:
            log(f"{datetime.now()} FILE: {file_name} STATUS: LOADED SUCCESSFULLY in {processing_time}. TABLE: {message.split()[-1]}", 'green')
        elif status == 1:
            log(f"{datetime.now()} FILE: {file_name} STATUS: ALREADY EXISTS ({message.split()[-1]})", 'yellow')
        else:
            log(f"{datetime.now()} FILE: {file_name} PROCESSING FAILED: {message}", 'red')
            log_rejected(f"{datetime.now()} FILE: {file_name} PROCESSING FAILED: {message}")
            log_rejected("-------------------------------------------------------------")
        
        log("-------------------------------------------------------------")
        files_processed += 1
        log(f"Processed files: {files_processed} out of {total_files}", overwrite=True)
