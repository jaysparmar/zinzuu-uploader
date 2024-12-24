import boto3
import os
import json
from tkinter import messagebox

import tkinter as tk

CONFIG_FILE = os.path.expanduser("~/.aws/zinzuu_credentials.json")

def check_aws_configuration():
    """Check if AWS is configured and return IAM username."""
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if not credentials:
            return None
        sts_client = session.client("sts")
        identity = sts_client.get_caller_identity()
        iam_username = identity.get("Arn").split("/")[-1]
        return iam_username
    except Exception:
        return None

def configure_aws():
    """Prompt the user to configure AWS credentials."""
    try:
        # Input AWS credentials
        access_key = input("Enter AWS Access Key: ")
        secret_key = input("Enter AWS Secret Key: ")
        region = input("Enter AWS Region (default: us-west-2): ") or "us-west-2"

        # Save credentials to a file
        credentials = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "region": region,
        }

        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as file:
            json.dump(credentials, file)

        # Set environment variables for boto3
        os.environ["AWS_ACCESS_KEY_ID"] = access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
        os.environ["AWS_DEFAULT_REGION"] = region

        messagebox.showinfo("AWS Configuration", "AWS credentials configured successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to configure AWS credentials: {e}")

def load_aws_credentials():
    """Load AWS credentials from the file if available."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                credentials = json.load(file)
                os.environ["AWS_ACCESS_KEY_ID"] = credentials["aws_access_key_id"]
                os.environ["AWS_SECRET_ACCESS_KEY"] = credentials["aws_secret_access_key"]
                os.environ["AWS_DEFAULT_REGION"] = credentials["region"]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load AWS credentials: {e}")

def fetch_aws_secrets_and_upload(secret_name, region_name, client, remote_path, log_text):
    """Fetch AWS secrets and upload .env file to the server."""
    try:
        log_text.insert(tk.END, "Fetching secrets from AWS Secrets Manager...\n")
        secrets_client = boto3.client("secretsmanager", region_name=region_name)
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response["SecretString"])
        env_content = "\n".join([f"{key}={value}" for key, value in secret_data.items()])

        # Upload the .env file via SFTP
        sftp = client.open_sftp()
        remote_env_path = os.path.join(remote_path, ".env")
        with sftp.file(remote_env_path, "w") as remote_env_file:
            remote_env_file.write(env_content)
        sftp.close()
        log_text.insert(tk.END, f"Uploaded .env file to {remote_env_path}\n")
    except Exception as e:
        log_text.insert(tk.END, f"Error uploading secrets: {e}\n")
        raise
