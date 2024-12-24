PEM_FILE = "resources/private_key.pem"

CONFIGURATIONS = {
    "testdeployment.zinzuu.com": {
        "host": "35.82.84.21",
        "port": 22,
        "username": "ubuntu",
        "pem_file": PEM_FILE,
        "protocol": "sftp",
        "remote_path": "/home/zinzuu-testdeployment/htdocs/testdeployment.zinzuu.com",
        "aws_secret_name": "zinzuu-dev-env",
        "aws_region": "us-west-2",
        "git_repo": "git@github.com:zinzuu-dev/zinzuu-web.git",
        "git_branch": "main",
    },
    # Add other configurations as needed...
}
