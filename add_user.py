"""
This script automates the creation and deletion of an admin user on a remote machine using pyinfra.
Reference for pyinfra api:  https://docs.pyinfra.com/en/2.x/api/index.html
"""

from pathlib import Path
from pyinfra.api import Config, Inventory, State  # noqa: E402
from pyinfra.api.connect import connect_all  # noqa: E402
from pyinfra.api.operation import add_op  # noqa: E402
from pyinfra.api.operations import run_ops  # noqa: E402
from pyinfra.operations import files, server  # noqa: E402
from pyinfra.api.exceptions import OperationFailed  # noqa: E402

# Read username and SSH key from "ghrunner" entry in .ssh/config
try:
    user_name = None
    user_ssh_keyfile = None
    with open(Path("~/.ssh/config").expanduser()) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.strip() == "Host ghrunner":
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith("User "):
                        user_name = lines[j].strip().split()[1]
                    if lines[j].strip().startswith("IdentityFile "):
                        user_ssh_keyfile = lines[j].strip().split()[1]
                    if user_name is not None and user_ssh_keyfile is not None:
                        break
            if user_name is not None and user_ssh_keyfile is not None:
                break
except FileNotFoundError:
    print("No .ssh/config file found")
    exit(1)

if user_name is None or user_ssh_keyfile is None:
    print("Missing 'ghrunner' entry in .ssh/config or missing 'User' or 'IdentityFile' field in 'ghrunner' entry")
    exit(1)

with open(Path(user_ssh_keyfile + ".pub").expanduser()) as f:
    user_ssh_pubkey = f.read()

# Connect to the target host
print("Please enter the password for the root user on the target machine")
root_password = input()

hosts = [
    (
        "ghrunner",
        {
            "ssh_user": "root",
            "ssh_password": root_password,
        },
    )
]
inventory = Inventory((hosts, {}))
config = Config()
state = State(inventory, config)

connect_all(state)

# Ask user if they want to create or delete a user
action = input("Would you like to create (C) or delete (D) a user? ").strip().upper()

if action == 'C':
    print(f"Creating user {user_name} with SSH key {user_ssh_keyfile}")
    print("Please enter the new user's password:")
    user_password = input()
    print("Please repeat the new user's password:")
    user_password_repeat = input()
    if user_password != user_password_repeat:
        print("Passwords do not match")
        exit(1)

    # Check if the user already exists
    try:
        # Check for the existence of the user
        add_op(
            state,
            server.user,
            name=f"Check if user {user_name} exists",
            user=user_name,
            present=False  # Check existence
        )
        
        # If we reach this point, it means the user exists
        print(f"User {user_name} is not available.")  # User exists
    except OperationFailed as e:
        # If the user does not exist, we create the user
        if "not found" in str(e).lower():
            print(f"User {user_name} does not exist. Proceeding to create the user.")

            # Create sudo group if not exists
            add_op(
                state,
                server.group,
                name="Create sudo group",
                group="sudo",
                present=True,
            )

            # Allow sudo group to run any command if not already set
            add_op(
                state,
                files.line,
                name="Allow sudo group to run any command",
                path="/etc/sudoers",
                line="# %sudo\tALL=(ALL:ALL) ALL",
                replace="%sudo\tALL=(ALL:ALL) ALL",
            )

            # Create user
            add_op(
                state,
                server.user,
                name=f"Create user {user_name}",
                user=user_name,
                groups=["sudo"],
                home=f"/home/{user_name}",
                public_keys=user_ssh_pubkey,
                password=user_password,  # Ensure this is plain text
                present=True,
            )

            print(f"User {user_name} created successfully.")

elif action == 'D':
    # Deleting a user
    user_to_delete = input("Please enter the username you wish to delete: ")

    # Check if the user exists
    try:
        add_op(
            state,
            server.user,
            name=f"Check if user {user_to_delete} exists",
            user=user_to_delete,
            present=False  # Check existence
        )
        
        # If we reach this point, it means the user exists
        print(f"User {user_to_delete} exists. Proceeding to delete the user.")

        # Remove the user's home directory
        add_op(
            state,
            files.directory,
            name=f"Remove home directory of {user_to_delete}",
            path=f"/home/{user_to_delete}",
            present=False,
        )
        print(f"User {user_to_delete} deleted successfully.")

    except OperationFailed as e:
        # If the user does not exist, handle the case
        if "not found" in str(e).lower():
            print(f"User {user_to_delete} does not exist.")
        else:
            print(f"An unexpected error occurred: {e}")
try:
    run_ops(state)
except Exception as e:
    print(f"An error occurred while running operations: {e}")
