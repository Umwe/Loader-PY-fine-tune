import threading
from tkinter import Tk
from gui import FileLoaderApp
from file_processing import process_files

def main():
    root = Tk()
    app = FileLoaderApp(root)

    def start_processing():
        config = {
            "input_path": app.input_path_entry.get(),
            "output_path": app.output_path_entry.get(),
            "load_tmp_files": app.check_box_manager.get_checkbox_states()["load_tmp_files"],
            "delete_tmp_files": app.check_box_manager.get_checkbox_states()["delete_tmp_extension"],
            "delete_processed_files": app.check_box_manager.get_checkbox_states()["delete_processed_files"],
            "server": app.server_url_entry.get(),
            "database": app.database_name_entry.get(),
            "stored_procedure": app.stored_procedure_entry.get(),
            "auth_type": app.auth_type.get(),
            "username": app.username_entry.get(),
            "password": app.password_entry.get()
        }
        threading.Thread(target=process_files, args=(
            config["input_path"],
            config["output_path"],
            config["load_tmp_files"],
            config["delete_tmp_files"],
            config["delete_processed_files"],
            config["server"],
            config["database"],
            config["stored_procedure"],
            config["auth_type"],
            config["username"],
            config["password"],
            app.log,
            lambda: app.stop_requested,
            app.get_batch_size()
        ), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()
