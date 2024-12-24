from deployment_tool.ui import create_ui
from deployment_tool.aws_config import load_aws_credentials

if __name__ == "__main__":
    load_aws_credentials()
    create_ui()
