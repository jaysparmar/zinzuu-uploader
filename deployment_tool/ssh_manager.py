import paramiko
import os
import threading
from deployment_tool.configurations import CONFIGURATIONS
from deployment_tool.aws_config import fetch_aws_secrets_and_upload

def execute_git_command(site, progress_var, log_text, use_sudo):
    """Execute Git commands via SSH."""
    config = CONFIGURATIONS.get(site)
    if not config:
        log_text.insert("1.0", "Invalid site selected.\n")
        return

    sudo_prefix = "sudo " if use_sudo else ""

    def run_command():
        try:
            progress_var.set(10)
            log_text.insert("1.0", "Connecting to server...\n")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            private_key_path = config["pem_file"]
            private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

            client.connect(
                hostname=config["host"],
                port=config["port"],
                username=config["username"],
                pkey=private_key
            )

            remote_path = config["remote_path"]
            command_check = f"{sudo_prefix}if [ -d {remote_path} ] && [ -d {remote_path}/.git ]; then echo 'git_repo_exists'; else echo 'no_git_repo'; fi"
            stdin, stdout, stderr = client.exec_command(command_check)
            repo_status = stdout.read().decode("utf-8").strip()

            if repo_status == "no_git_repo":
                log_text.insert("1.0", "Cloning repository...\n")
                client.exec_command(f"{sudo_prefix}mkdir -p {remote_path}")
                git_command = f"cd {remote_path} && {sudo_prefix}git clone {config['git_repo']} ."
            else:
                log_text.insert("1.0", "Pulling latest changes...\n")
                git_command = f"cd {remote_path} && {sudo_prefix}git pull origin {config['git_branch']}"

            stdin, stdout, stderr = client.exec_command(git_command)
            log_text.insert("1.0", stdout.read().decode("utf-8"))

            fetch_aws_secrets_and_upload(config["aws_secret_name"], config["aws_region"], client, remote_path, log_text)

        except Exception as e:
            log_text.insert("1.0", f"Error: {e}\n")
        finally:
            client.close()

    threading.Thread(target=run_command).start()
