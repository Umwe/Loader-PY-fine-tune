import os
import time
from datetime import datetime
from database import connect_to_db, call_stored_procedure

def process_files(input_path, output_path, load_tmp_files, delete_tmp_files, delete_processed_files, server, database, stored_procedure, auth_type, username, password, log, stop_requested, batch_size, log_rejected, update_file_count):
    connection = connect_to_db(server, database, auth_type, username, password)
    
    log(f"System started at {datetime.now()}")

    while True:
        files = os.listdir(input_path)
        total_files = len(files)

        if stop_requested():
            log("Stop requested. Ending processing after current action...")
            break  # Exit the loop after the current action finishes
        
        if total_files == 0:
            log("No files to process. Waiting for the next batch...", 'blue')
            countdown_timer(30, log, "Next batch in")
            if stop_requested():
                break  # Exit if stop is requested during the wait
            continue
        
        # Determine the batch size to process
        current_batch_size = min(batch_size, total_files)
        log(f"Batch size to be processed: {current_batch_size} out of {total_files} files.", 'blue')

        files_processed = 0
        
        for file_name in files[:current_batch_size]:
            if stop_requested():
                break  # Exit the inner loop if stop is requested during file processing

            file_path = os.path.join(input_path, file_name)
            start_time = datetime.now()
            
            status, message = call_stored_procedure(connection, stored_procedure, file_name, file_path)
            end_time = datetime.now()
            processing_time = end_time - start_time

            if status == 0:
                table_name = message[message.index('('):]
                status_message = message[:message.index('(')].strip()
                log(f"{datetime.now()} FILE: {file_name} STATUS: LOADED SUCCESSFULLY in {processing_time}. TABLE: {table_name}. STATUS: {status_message}", 'green')
            elif status == 1:
                log(f"{datetime.now()} FILE: {file_name} STATUS: ALREADY EXISTS ({message})", 'yellow')
            else:
                log(f"{datetime.now()} FILE: {file_name} PROCESSING FAILED: {message}", 'red')
                log_rejected(f"{datetime.now()} FILE: {file_name} PROCESSING FAILED: {message}")
                log_rejected("-------------------------------------------------------------")
            
            log("-------------------------------------------------------------")
            files_processed += 1
            
            if files_processed < current_batch_size:  # Only delay if there are more files to process in the current batch
                log("Waiting 5 seconds before processing the next file in the batch...", 'blue')
                countdown_timer(5, log, "Next file in")
                if stop_requested():
                    break  # Exit if stop is requested during the wait
        
        log(f"Processed batch of {files_processed} files. Remaining files: {total_files - files_processed}")
        
        # Update the file count in the GUI
        update_file_count()
        
        if stop_requested():
            break  # Exit after finishing the current batch
        
        countdown_timer(30, log, "Next batch in")  # Wait 30 seconds before the next batch
        if stop_requested():
            break  # Exit if stop is requested during the wait

def countdown_timer(seconds, log, message):
    """Countdown function to log the remaining time before the next file or batch."""
    while seconds:
        log(f"{message} {seconds} seconds...", overwrite=True)
        time.sleep(1)
        seconds -= 1
