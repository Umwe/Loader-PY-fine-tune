import tkinter as tk

class CheckBoxManager:
    def __init__(self, parent, log_callback, save_config_callback):
        self.log = log_callback
        self.save_config = save_config_callback

        self.load_tmp_files_var = tk.BooleanVar(value=False)
        self.delete_tmp_extension_var = tk.BooleanVar(value=False)
        self.delete_processed_files_var = tk.BooleanVar(value=False)

        self.load_tmp_files_cb = tk.Checkbutton(parent, text="Load .tmp Files", variable=self.load_tmp_files_var, command=self.save_and_log_load_tmp_files)
        self.load_tmp_files_cb.pack(side='left', padx=5)

        self.delete_tmp_extension_cb = tk.Checkbutton(parent, text="Delete .tmp Files", variable=self.delete_tmp_extension_var, command=self.save_and_log_delete_tmp_files)
        self.delete_tmp_extension_cb.pack(side='left', padx=5)

        self.delete_processed_files_cb = tk.Checkbutton(parent, text="Delete Processed Files", variable=self.delete_processed_files_var, command=self.save_and_log_delete_processed_files)
        self.delete_processed_files_cb.pack(side='left', padx=5)

    def save_and_log_load_tmp_files(self):
        if self.load_tmp_files_var.get() and self.delete_tmp_extension_var.get():
            self.delete_tmp_extension_var.set(False)
            self.log("You cannot select both 'Load .tmp Files' and 'Delete .tmp Files'. Please deselect one.")
        else:
            self.save_config()
            if self.load_tmp_files_var.get():
                self.log("Load .tmp files selected.")
            else:
                self.log("Load .tmp files deselected.")

    def save_and_log_delete_tmp_files(self):
        if self.delete_tmp_extension_var.get() and self.load_tmp_files_var.get():
            self.load_tmp_files_var.set(False)
            self.log("You cannot select both 'Load .tmp Files' and 'Delete .tmp Files'. Please deselect one.")
        else:
            self.save_config()
            if self.delete_tmp_extension_var.get():
                self.log("Delete .tmp files selected.")
            else:
                self.log("Delete .tmp files deselected.")

    def save_and_log_delete_processed_files(self):
        self.save_config()
        if self.delete_processed_files_var.get():
            self.log("Delete processed files selected.")
        else:
            self.log("Delete processed files deselected.")

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
