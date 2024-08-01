import tkinter as tk
from tkinter import ttk

class CheckBoxManager:
    def __init__(self, parent, log, save_config):
        self.log = log
        self.save_config = save_config

        self.load_tmp_files_var = tk.BooleanVar()
        self.delete_tmp_extension_var = tk.BooleanVar()
        self.delete_processed_files_var = tk.BooleanVar()

        self.create_checkboxes(parent)

    def create_checkboxes(self, parent):
        self.load_tmp_files_check = ttk.Checkbutton(
            parent,
            text="Load .tmp files",
            variable=self.load_tmp_files_var,
            command=self.save_config_and_log
        )
        self.load_tmp_files_check.pack(side='left', padx=5)

        self.delete_tmp_extension_check = ttk.Checkbutton(
            parent,
            text="Delete .tmp files",
            variable=self.delete_tmp_extension_var,
            command=self.save_config_and_log
        )
        self.delete_tmp_extension_check.pack(side='left', padx=5)

        self.delete_processed_files_check = ttk.Checkbutton(
            parent,
            text="Delete processed files",
            variable=self.delete_processed_files_var,
            command=self.save_config_and_log
        )
        self.delete_processed_files_check.pack(side='left', padx=5)

    def save_config_and_log(self):
        self.log(f"Checkbox status updated: {self.get_checkbox_states()}")
        self.save_config()

    def get_checkbox_states(self):
        return {
            "load_tmp_files": self.load_tmp_files_var.get(),
            "delete_tmp_extension": self.delete_tmp_extension_var.get(),
            "delete_processed_files": self.delete_processed_files_var.get()
        }

    def set_checkbox_states(self, states):
        self.load_tmp_files_var.set(states.get("load_tmp_files", False))
        self.delete_tmp_extension_var.set(states.get("delete_tmp_extension", False))
        self.delete_processed_files_var.set(states.get("delete_processed_files", False))
