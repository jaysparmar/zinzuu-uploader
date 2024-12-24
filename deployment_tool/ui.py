import tkinter as tk
from tkinter import ttk, messagebox
from deployment_tool.ssh_manager import execute_git_command
from deployment_tool.aws_config import check_aws_configuration, configure_aws
from deployment_tool.configurations import CONFIGURATIONS  # Import configurations

def create_ui():
    """Create the Tkinter UI."""
    root = tk.Tk()
    root.title("Deployment Tool")

    tk.Label(root, text="Select a site:").pack(pady=5)
    site_var = tk.StringVar()
    ttk.Combobox(root, textvariable=site_var, values=list(CONFIGURATIONS.keys()), state="readonly").pack(pady=5)

    sudo_var = tk.BooleanVar()
    ttk.Checkbutton(root, text="Run as sudo", variable=sudo_var).pack(pady=5)

    progress_var = tk.IntVar()
    ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", variable=progress_var).pack(pady=10)

    log_text = tk.Text(root, wrap=tk.WORD, height=15)
    log_text.pack(pady=10, fill=tk.BOTH, expand=True)

    def on_execute():
        site = site_var.get()
        if not site:
            tk.messagebox.showwarning("Warning", "Please select a site.")
            return
        log_text.delete("1.0", tk.END)
        execute_git_command(site, progress_var, log_text, sudo_var.get())

    ttk.Button(root, text="Execute Git Command", command=on_execute).pack(pady=5)

    root.mainloop()
