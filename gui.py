import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import threading
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

        self.create_widgets()
        self.load_config()

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

        # Main Log Console with Scrollbar
        main_console_frame = tk.Frame(main_sub_tab)
        main_console_frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.log_console = tk.Text(main_console_frame, height=20, state='disabled', wrap='none')
        self.log_console.pack(side='left', expand=True, fill='both')

        main_scrollbar = tk.Scrollbar(main_console_frame, command=self.log_console.yview)
        main_scrollbar.pack(side='right', fill='y')
        self.log_console.config(yscrollcommand=main_scrollbar.set)

        # Rejected Log Console with Scrollbar
        rejected_console_frame = tk.Frame(rejected_sub_tab)
        rejected_console_frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.rejected_log_console = tk.Text(rejected_console_frame, height=20, state='disabled', wrap='none')
        self.rejected_log_console.pack(side='left', expand=True, fill='both')

        rejected_scrollbar = tk.Scrollbar(rejected_console_frame, command=self.rejected_log_console.yview)
        rejected_scrollbar.pack(side='right', fill='y')
        self.rejected_log_console.config(yscrollcommand=rejected_scrollbar.set)

        # Clear Log and Start Logging Buttons
        buttons_frame = tk.Frame(main_sub_tab)
        buttons_frame.pack(fill='x', padx=10, pady=5)

        self.clear_log_button = ttk.Button(buttons_frame, text="Clear Log", command=self.handle_clear_log)
        self.clear_log_button.pack(side='left', padx=5)

        self.start_logging_button = ttk.Button(buttons_frame, text="Start Logging", command=self.toggle_logging)
        self.start_logging_button.pack(side='left', padx=5)

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

        ttk.Label(self.config_db_tab, text="Stored Procedure Name:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.stored_procedure_entry = ttk.Entry(self.config_db_tab, width=50)
        self.stored_procedure_entry.grid(row=2, column=1, padx=5, pady=5)

        self.auth_type = tk.StringVar(value="SQL Server Authentication")
        ttk.Label(self.config_db_tab, text="Authentication Type:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.OptionMenu(self.config_db_tab, self.auth_type, "SQL Server Authentication", "SQL Server Authentication", "Windows Authentication", command=self.toggle_auth).grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.sql_auth_frame = ttk.Frame(self.config_db_tab)
        self.sql_auth_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        ttk.Label(self.sql_auth_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(self.sql_auth_frame, width=50)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.sql_auth_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(self.sql_auth_frame, width=50, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.config_db_tab, text="Save DB Config", command=self.handle_save_db_config).grid(row=5, column=1, padx=5, pady=5, sticky="e")

    def create_config_others_widgets(self):
        ttk.Label(self.config_others_tab, text="Batch Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.batch_size_entry = ttk.Entry(self.config_others_tab, width=20)
        self.batch_size_entry.grid(row=0, column=1, padx=5, pady=5)
        self.batch_size_entry.insert(0, str(self.batch_size))

        ttk.Button(self.config_others_tab, text="Set as Default", command=self.set_default_batch_size).grid(row=1, column=1, padx=5, pady=5, sticky="e")

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
            self.log(f"Input path set to {input_path}.")
            print(f"Input path set to {input_path}.")

    def browse_output_path(self):
        output_path = filedialog.askdirectory()
        if output_path:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, output_path)
            self.log(f"Output path set to {output_path}.")
            print(f"Output path set to {output_path}.")

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
            self.log("Stop requested. Waiting for the current batch to finish...")
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
            "password": self.password_entry.get()
        }
        threading.Thread(target=self.process_files_thread, args=(config,)).start()

    def process_files_thread(self, config):
        batch_size = self.get_batch_size()
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
            batch_size,
            self.log_rejected
        )

    def handle_save_paths(self):
        input_path = self.input_path_entry.get()
        output_path = self.output_path_entry.get()

        if not input_path or not output_path:
            messagebox.showwarning("Warning", "Both input and output paths must be set before saving.")
            return

        self.save_config()
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

    def handle_exit(self):
        self.log("Exit button clicked.")
        self.root.quit()

    def log(self, message, overwrite=False):
        self.log_console.configure(state='normal')
        if overwrite:
            self.log_console.delete("end-2l", "end-1l")
        self.log_console.insert(tk.END, message + "\n")
        self.log_console.configure(state='disabled')
        self.log_console.see(tk.END)

    def log_rejected(self, message):
        self.rejected_log_console.configure(state='normal')
        self.rejected_log_console.insert(tk.END, message + "\n")
        self.rejected_log_console.configure(state='disabled')
        self.rejected_log_console.see(tk.END)

    def load_config(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as file:
                config = json.load(file)
                self.input_path_entry.insert(0, config.get("input_path", ""))
                self.output_path_entry.insert(0, config.get("output_path", ""))
                self.server_url_entry.insert(0, config.get("server_url", ""))
                self.database_name_entry.insert(0, config.get("database_name", ""))
                self.stored_procedure_entry.insert(0, config.get("stored_procedure", ""))
                self.auth_type.set(config.get("auth_type", "SQL Server Authentication"))
                self.username_entry.insert(0, config.get("username", ""))
                self.password_entry.insert(0, config.get("password", ""))
                self.check_box_manager.set_checkbox_states({
                    "load_tmp_files": config.get("load_tmp_files", False),
                    "delete_tmp_extension": config.get("delete_tmp_files", False),
                    "delete_processed_files": config.get("delete_processed_files", False)
                })
                self.batch_size = config.get("batch_size", 1000)
                self.batch_size_entry.delete(0, tk.END)
                self.batch_size_entry.insert(0, str(self.batch_size))
                self.toggle_auth(self.auth_type.get())
                self.log("Configuration loaded.")

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
            "load_tmp_files": self.check_box_manager.get_checkbox_states()["load_tmp_files"],
            "delete_tmp_files": self.check_box_manager.get_checkbox_states()["delete_tmp_extension"],
            "delete_processed_files": self.check_box_manager.get_checkbox_states()["delete_processed_files"],
            "batch_size": self.batch_size
        }
        with open("config.json", "w") as file:
            json.dump(config, file)
        self.log("Configuration saved.")

    def on_closing(self):
        self.save_config()
        self.root.destroy()
        self.log("Application closed.")
