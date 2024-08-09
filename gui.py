import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import threading
import time
from datetime import datetime
from CheckBoxManager import CheckBoxManager
from file_processing import process_files

class FileLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Loader Application")
        self.root.geometry("800x600")

        self.logging_active = False
        self.stop_requested = False
        self.batch_size = 1000  # Default batch size
        self.current_file_count = 0  # Track the current file count

        self.create_widgets()
        self.load_config()

        # Start the background thread to keep the file count updated
        self.file_count_thread = threading.Thread(target=self.monitor_file_count, daemon=True)
        self.file_count_thread.start()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg='lightgreen', height=100)
        header_frame.pack(fill='x')
        header_label = tk.Label(header_frame, text="GGSN LOADER7 (GGSN CDRS LOADER)", bg='lightgreen', font=("Arial", 20, "bold"))
        header_label.pack(expand=True)

        # Tab Control
        tab_control = ttk.Notebook(self.root)

        # Main Tab
        self.main_tab = ttk.Frame(tab_control)
        tab_control.add(self.main_tab, text='Main')

        # Status Tab
        self.status_tab = ttk.Frame(tab_control)
        tab_control.add(self.status_tab, text='Status')

        # Config (Paths) Tab
        self.config_paths_tab = ttk.Frame(tab_control)
        tab_control.add(self.config_paths_tab, text='Config (Paths)')

        # Config (DB) Tab
        self.config_db_tab = ttk.Frame(tab_control)
        tab_control.add(self.config_db_tab, text='Config (DB)')

        # Config (Others) Tab
        self.config_others_tab = ttk.Frame(tab_control)
        tab_control.add(self.config_others_tab, text='Config (Others)')

        tab_control.pack(expand=1, fill='both')

        # Main Tab Widgets
        self.create_main_tab_widgets()

        # Config Paths Tab Widgets
        self.create_config_paths_widgets()

        # Config DB Tab Widgets
        self.create_config_db_widgets()

        # Config Others Tab Widgets
        self.create_config_others_widgets()

        # Bottom Controls
        self.create_bottom_controls()

    def create_main_tab_widgets(self):
        # Sub Tabs in Main Tab
        sub_tab_control = ttk.Notebook(self.main_tab)

        main_sub_tab = ttk.Frame(sub_tab_control)
        sub_tab_control.add(main_sub_tab, text='Main')

        rejected_sub_tab = ttk.Frame(sub_tab_control)
        sub_tab_control.add(rejected_sub_tab, text='Rejected')

        sub_tab_control.pack(expand=1, fill='both')

        # Main Log Console with Scrollbars
        main_console_frame = tk.Frame(main_sub_tab)
        main_console_frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.log_console = tk.Text(main_console_frame, height=20, state='normal', wrap='none')
        self.log_console.pack(side='left', expand=True, fill='both')

        main_v_scrollbar = tk.Scrollbar(main_console_frame, command=self.log_console.yview)
        main_v_scrollbar.pack(side='right', fill='y')
        self.log_console.config(yscrollcommand=main_v_scrollbar.set)

        main_h_scrollbar = tk.Scrollbar(main_console_frame, command=self.log_console.xview, orient='horizontal')
        main_h_scrollbar.pack(side='bottom', fill='x')
        self.log_console.config(xscrollcommand=main_h_scrollbar.set)

        # Print Button for Main Console
        self.print_main_button = ttk.Button(main_console_frame, text="Print", command=self.print_main_console)
        self.print_main_button.pack(side='right', padx=10, pady=5)

        # Rejected Log Console with Scrollbars
        rejected_console_frame = tk.Frame(rejected_sub_tab)
        rejected_console_frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.rejected_log_console = tk.Text(rejected_console_frame, height=20, state='normal', wrap='none')
        self.rejected_log_console.pack(side='left', expand=True, fill='both')

        rejected_v_scrollbar = tk.Scrollbar(rejected_console_frame, command=self.rejected_log_console.yview)
        rejected_v_scrollbar.pack(side='right', fill='y')
        self.rejected_log_console.config(yscrollcommand=rejected_v_scrollbar.set)

        rejected_h_scrollbar = tk.Scrollbar(rejected_console_frame, command=self.rejected_log_console.xview, orient='horizontal')
        rejected_h_scrollbar.pack(side='bottom', fill='x')
        self.rejected_log_console.config(xscrollcommand=rejected_h_scrollbar.set)

        # Print Button for Rejected Console
        self.print_rejected_button = ttk.Button(rejected_console_frame, text="Print", command=self.print_rejected_console)
        self.print_rejected_button.pack(side='right', padx=10, pady=5)

        # Clear Log and Start Logging Buttons
        buttons_frame = tk.Frame(main_sub_tab)
        buttons_frame.pack(fill='x', padx=10, pady=5)

        self.clear_log_button = ttk.Button(buttons_frame, text="Clear Log", command=self.handle_clear_log)
        self.clear_log_button.pack(side='left', padx=5)

        self.start_logging_button = ttk.Button(buttons_frame, text="Start Logging", command=self.toggle_logging)
        self.start_logging_button.pack(side='left', padx=5)

        # Search and Navigation Controls placed just under "Clear Log" and "Start Logging" buttons
        search_frame = tk.Frame(main_sub_tab)
        search_frame.pack(fill='x', padx=10, pady=5)

        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side='left', padx=5)

        self.search_button = ttk.Button(search_frame, text="Search", command=self.search_main_console)
        self.search_button.pack(side='left', padx=5)

        self.search_count_label = ttk.Label(search_frame, text="Matches: 0")
        self.search_count_label.pack(side='left', padx=5)

        self.prev_button = ttk.Button(search_frame, text="Up", command=lambda: self.navigate_matches(self.log_console, direction="prev"))
        self.prev_button.pack(side='left', padx=5)

        self.next_button = ttk.Button(search_frame, text="Down", command=lambda: self.navigate_matches(self.log_console, direction="next"))
        self.next_button.pack(side='left', padx=5)

    def create_config_paths_widgets(self):
        ttk.Label(self.config_paths_tab, text="Input Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.input_path_entry = ttk.Entry(self.config_paths_tab, width=50)
        self.input_path_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.config_paths_tab, text="Browse", command=self.browse_input_path).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(self.config_paths_tab, text="Output Path:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.output_path_entry = ttk.Entry(self.config_paths_tab, width=50)
        self.output_path_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.config_paths_tab, text="Browse", command=self.browse_output_path).grid(row=1, column=2, padx=5, pady=5)

        ttk.Button(self.config_paths_tab, text="Save Paths", command=self.handle_save_paths).grid(row=2, column=1, padx=5, pady=5, sticky="e")

    def create_config_db_widgets(self):
        ttk.Label(self.config_db_tab, text="Server URL:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.server_url_entry = ttk.Entry(self.config_db_tab, width=50)
        self.server_url_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.config_db_tab, text="Database Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.database_name_entry = ttk.Entry(self.config_db_tab, width=50)
        self.database_name_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.config_db_tab, text="Stored Procedure:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.stored_procedure_entry = ttk.Entry(self.config_db_tab, width=50)
        self.stored_procedure_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.config_db_tab, text="Authentication Type:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.auth_type = tk.StringVar()
        self.auth_type.set("SQL Server Authentication")
        auth_type_menu = ttk.OptionMenu(self.config_db_tab, self.auth_type, "SQL Server Authentication", "SQL Server Authentication", "Windows Authentication", command=self.toggle_auth)
        auth_type_menu.grid(row=3, column=1, padx=5, pady=5)

        self.sql_auth_frame = tk.Frame(self.config_db_tab)
        self.sql_auth_frame.grid(row=4, column=0, columnspan=3, sticky='w')

        ttk.Label(self.sql_auth_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(self.sql_auth_frame, width=50)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.sql_auth_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(self.sql_auth_frame, width=50, show='*')
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.config_db_tab, text="Save DB Config", command=self.handle_save_db_config).grid(row=5, column=1, padx=5, pady=5, sticky="e")

    def create_config_others_widgets(self):
        ttk.Label(self.config_others_tab, text="Batch Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.batch_size_entry = ttk.Entry(self.config_others_tab, width=20)
        self.batch_size_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.config_others_tab, text="Set Default Batch Size", command=self.set_default_batch_size).grid(row=1, column=1, padx=5, pady=5, sticky="e")

        ttk.Button(self.config_others_tab, text="Save Batch Size", command=self.handle_save_batch_size).grid(row=2, column=1, padx=5, pady=5, sticky="e")

    def create_bottom_controls(self):
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill='x', padx=10, pady=5)

        self.check_box_manager = CheckBoxManager(bottom_frame, self.log, self.save_config)

        self.reload_config_button = ttk.Button(bottom_frame, text="Reload Config", command=self.handle_reload_config)
        self.reload_config_button.pack(side='left', padx=5)

        self.normal_operation_button = ttk.Button(bottom_frame, text="NORMAL Operation", command=self.handle_normal_operation)
        self.normal_operation_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(bottom_frame, text="Stop", command=self.handle_stop)
        self.stop_button.pack(side='left', padx=5)

        self.exit_button = ttk.Button(bottom_frame, text="Exit", command=self.handle_exit)
        self.exit_button.pack(side='left', padx=5)

        # Label to display the current number of files in the input directory
        self.file_count_label = tk.Label(bottom_frame, text="Total files: 0")
        self.file_count_label.pack(side='left', padx=5, pady=5)

        self.update_file_count()  # Initial count of the files

    def toggle_auth(self, value):
        if value == "Windows Authentication":
            self.sql_auth_frame.grid_remove()
        else:
            self.sql_auth_frame.grid()
        self.log(f"Authentication type changed to {value}.")

    def browse_input_path(self):
        input_path = filedialog.askdirectory()
        if input_path:
            self.input_path_entry.delete(0, tk.END)
            self.input_path_entry.insert(0, input_path)
            self.update_file_count()  # Update file count when a new input path is selected
            self.log(f"Input path set to {input_path}.")

    def browse_output_path(self):
        output_path = filedialog.askdirectory()
        if output_path:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, output_path)
            self.log(f"Output path set to {output_path}.")

    def handle_clear_log(self):
        self.log_console.configure(state='normal')
        self.log_console.delete(1.0, tk.END)
        self.log_console.configure(state='disabled')
        self.rejected_log_console.configure(state='normal')
        self.rejected_log_console.delete(1.0, tk.END)
        self.rejected_log_console.configure(state='disabled')
        self.log("Log cleared.")

    def toggle_logging(self):
        if self.start_logging_button.cget('text') == "Start Logging":
            self.start_logging_button.config(text="Stop Logging")
            self.log("Logging started.")
            self.logging_active = True
            self.stop_requested = False
            self.start_logging()
        else:
            self.log("Stop requested. Waiting for the current action to finish...")
            self.stop_requested = True

    def start_logging(self):
        config = {
            "input_path": self.input_path_entry.get(),
            "output_path": self.output_path_entry.get(),
            "load_tmp_files": self.check_box_manager.get_checkbox_states()["load_tmp_files"],
            "delete_tmp_files": self.check_box_manager.get_checkbox_states()["delete_tmp_extension"],
            "delete_processed_files": self.check_box_manager.get_checkbox_states()["delete_processed_files"],
            "server": self.server_url_entry.get(),
            "database": self.database_name_entry.get(),
            "stored_procedure": self.stored_procedure_entry.get(),
            "auth_type": self.auth_type.get(),
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
            "batch_size": self.get_batch_size()
        }
        threading.Thread(target=self.process_files_thread, args=(config,), daemon=True).start()

    def process_files_thread(self, config):
        process_files(
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
            self.log,
            lambda: self.stop_requested,
            config["batch_size"],
            self.log_rejected,
            self.update_file_count  # Pass the update_file_count method to refresh the file count
        )
        self.logging_active = False  # Mark the process as completed
        self.start_logging_button.config(text="Start Logging")  # Reset button text after stopping

    def handle_exit(self):
        if self.logging_active and not self.stop_requested:
            response = messagebox.askyesnocancel(
                "Warning",
                "The process is currently running. Exiting now might corrupt the current process. Do you want to stop the process first?"
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes, stop the process
                self.stop_requested = True
                self.logging_active = False
                self.start_logging_button.config(text="Start Logging")
                messagebox.showinfo("Process Stopped", "The process is being stopped. The application will close once the current process is finished.")
                # Start a thread to monitor the process and close the app when done
                threading.Thread(target=self.wait_for_process_to_end_and_exit, daemon=True).start()
            else:  # No, exit without stopping
                self.root.quit()
        else:
            self.root.quit()

    def wait_for_process_to_end_and_exit(self):
        while self.logging_active:  # Wait until the process is fully stopped
            time.sleep(1)  # Check every second
        self.root.quit()  # Close the application after stopping

    def update_file_count(self):
        """Update the Label with the current number of files in the input directory."""
        input_path = self.input_path_entry.get()
        if os.path.exists(input_path):
            file_count = len(os.listdir(input_path))
            self.file_count_label.config(text=f"Total files: {file_count}")
            self.current_file_count = file_count  # Update the current file count
        else:
            self.file_count_label.config(text="Total files: 0")
            self.current_file_count = 0

    def monitor_file_count(self):
        """Background thread to monitor and update the file count in real-time."""
        while True:
            input_path = self.input_path_entry.get()
            if os.path.exists(input_path):
                new_file_count = len(os.listdir(input_path))
                if new_file_count != self.current_file_count:
                    self.update_file_count()
            time.sleep(2)  # Check every 2 seconds

    def handle_save_paths(self):
        input_path = self.input_path_entry.get()
        output_path = self.output_path_entry.get()

        if not input_path or not output_path:
            messagebox.showwarning("Warning", "Both input and output paths must be set before saving.")
            return

        self.save_config()
        self.update_file_count()  # Update the file count when paths are saved
        self.log("Paths configuration saved successfully.")

    def handle_save_db_config(self):
        server_url = self.server_url_entry.get()
        database_name = self.database_name_entry.get()
        stored_procedure = self.stored_procedure_entry.get()
        auth_type = self.auth_type.get()

        if not server_url or not database_name or not stored_procedure:
            messagebox.showwarning("Warning", "Server URL, Database Name, and Stored Procedure must be set before saving.")
            return

        if auth_type == "SQL Server Authentication":
            username = self.username_entry.get()
            password = self.password_entry.get()
            if not username or password:
                messagebox.showwarning("Warning", "Username and Password must be set for SQL Server Authentication.")
                return

        self.save_config()
        self.log("Database configuration saved successfully.")

    def handle_save_batch_size(self):
        try:
            self.batch_size = int(self.batch_size_entry.get())
            self.save_config()
            self.log(f"Batch size set to {self.batch_size}.")
        except ValueError:
            messagebox.showwarning("Warning", "Batch size must be an integer.")

    def set_default_batch_size(self):
        self.batch_size = 1000
        self.batch_size_entry.delete(0, tk.END)
        self.batch_size_entry.insert(0, str(self.batch_size))
        self.save_config()
        self.log("Batch size set to default (1000).")

    def get_batch_size(self):
        return self.batch_size

    def handle_reload_config(self):
        self.log("Reload Config button clicked.")
        self.load_config()

    def handle_normal_operation(self):
        self.log("NORMAL Operation button clicked.")

    def handle_stop(self):
        self.log("Stop button clicked.")
        self.logging_active = False

    def log(self, message, color='black', overwrite=False):
        self.log_console.configure(state='normal')
        if overwrite:
            self.log_console.delete("end-2l", "end-1l")
        self.log_console.insert(tk.END, message + "\n", ('color',))
        self.log_console.tag_configure('color', foreground=color)
        self.log_console.configure(state='disabled')
        self.log_console.see(tk.END)

    def log_rejected(self, message, overwrite=False):
        self.rejected_log_console.configure(state='normal')
        if overwrite:
            self.rejected_log_console.delete("end-2l", "end-1l")
        self.rejected_log_console.insert(tk.END, message + "\n", ('color',))
        self.rejected_log_console.tag_configure('color', foreground='red')
        self.rejected_log_console.configure(state='disabled')
        self.rejected_log_console.see(tk.END)

    def save_config(self):
        config = {
            "input_path": self.input_path_entry.get(),
            "output_path": self.output_path_entry.get(),
            "server_url": self.server_url_entry.get(),
            "database_name": self.database_name_entry.get(),
            "stored_procedure": self.stored_procedure_entry.get(),
            "auth_type": self.auth_type.get(),
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
            "batch_size": self.batch_size,
            "check_box_states": self.check_box_manager.get_checkbox_states()
        }
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)

    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                self.input_path_entry.insert(0, config.get("input_path", ""))
                self.output_path_entry.insert(0, config.get("output_path", ""))
                self.server_url_entry.insert(0, config.get("server_url", ""))
                self.database_name_entry.insert(0, config.get("database_name", ""))
                self.stored_procedure_entry.insert(0, config.get("stored_procedure", ""))
                self.auth_type.set(config.get("auth_type", "SQL Server Authentication"))
                self.username_entry.insert(0, config.get("username", ""))
                self.password_entry.insert(0, config.get("password", ""))
                self.batch_size = config.get("batch_size", 1000)
                self.batch_size_entry.insert(0, str(self.batch_size))
                self.check_box_manager.set_checkbox_states(config.get("check_box_states", {}))
                self.toggle_auth(self.auth_type.get())
                self.update_file_count()  # Update file count on load
                self.log("Configuration loaded.")
        else:
            self.log("No configuration file found. Using default settings.")

    def print_main_console(self):
        """Save the contents of the main log console to a file and notify the user."""
        self.save_console_content(self.log_console, "Main Log")

    def print_rejected_console(self):
        """Save the contents of the rejected log console to a file and notify the user."""
        self.save_console_content(self.rejected_log_console, "Rejected Log")

    def save_console_content(self, console, log_type):
        """Save the content of a given console to a file using Save As dialog."""
        log_content = console.get(1.0, tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title=f"Save {log_type}",
            initialfile=f"{log_type}.txt"
        )
        if file_path:
            with open(file_path, 'w') as file:
                file.write(log_content)
            messagebox.showinfo("Print Log", f"{log_type} has been saved to {file_path}. You can print it manually.")

    def search_main_console(self):
        """Search for the keyword in the main console and highlight matches."""
        keyword = self.search_entry.get()
        self.highlight_text(self.log_console, keyword)
        count = self.count_matches(self.log_console, keyword)
        self.search_count_label.config(text=f"Matches: {count}")
        if count > 0:
            self.navigate_matches(self.log_console, direction="next")  # Navigate to the first match

    def search_rejected_console(self):
        """Search for the keyword in the rejected console and highlight matches."""
        keyword = self.search_entry.get()
        self.highlight_text(self.rejected_log_console, keyword)
        count = self.count_matches(self.rejected_log_console, keyword)
        self.search_count_label.config(text=f"Matches: {count}")
        if count > 0:
            self.navigate_matches(self.rejected_log_console, direction="next")  # Navigate to the first match

    def highlight_text(self, console, keyword):
        """Highlight all occurrences of the keyword in the specified console."""
        console.tag_remove('highlight', '1.0', tk.END)  # Remove previous highlights
        if keyword:
            start_pos = '1.0'
            while True:
                start_pos = console.search(keyword, start_pos, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(keyword)}c"
                console.tag_add('highlight', start_pos, end_pos)
                start_pos = end_pos
            console.tag_config('highlight', background='yellow', foreground='black')

    def count_matches(self, console, keyword):
        """Count the total number of matches for the keyword in the specified console."""
        count = 0
        if keyword:
            start_pos = '1.0'
            while True:
                start_pos = console.search(keyword, start_pos, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(keyword)}c"
                count += 1
                start_pos = end_pos
        return count

    def navigate_matches(self, console, direction="next"):
        """Navigate to the next or previous highlighted match."""
        if direction == "next":
            try:
                current = console.index(tk.INSERT)
                next_pos = console.tag_nextrange('highlight', current)
                if next_pos:
                    console.mark_set(tk.INSERT, next_pos[0])
                    console.see(tk.INSERT)
            except Exception as e:
                messagebox.showinfo("Navigation Error", str(e))
        elif direction == "prev":
            try:
                current = console.index(tk.INSERT)
                prev_pos = console.tag_prevrange('highlight', current)
                if prev_pos:
                    console.mark_set(tk.INSERT, prev_pos[0])
                    console.see(tk.INSERT)
            except Exception as e:
                messagebox.showinfo("Navigation Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = FileLoaderApp(root)
    root.mainloop()
    
