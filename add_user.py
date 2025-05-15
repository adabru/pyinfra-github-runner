"""
This script automates the creation of a new admin user on a remote machine using pyinfra.
Reference for pyinfra api:  https://docs.pyinfra.com/en/2.x/api/index.html
"""

from pathlib import Path

from passlib.hash import sha512_crypt
from pyinfra.api import Config, Inventory, State  # noqa: E402
from pyinfra.api.connect import connect_all  # noqa: E402
from pyinfra.api.operation import add_op  # noqa: E402
from pyinfra.api.operations import run_ops  # noqa: E402
from pyinfra.operations import files, server  # noqa: E402

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
    print(
        "Missing 'ghrunner' entry in .ssh/config or missing 'User' or 'IdentityFile' field in 'ghrunner' entry"
    )
    exit(1)

with open(Path(user_ssh_keyfile + ".pub").expanduser()) as f:
    user_ssh_pubkey = f.read()

print(f"Creating user {user_name} with SSH key {user_ssh_keyfile}")
print("Please enter the new user's password:")
user_password = input()
print("Please repeat the new user's password:")
user_password_repeat = input()
if user_password != user_password_repeat:
    print("Passwords do not match")
    exit(1)

# Encrypt the password in a "crypt" compatible format
# see https://linux.die.net/man/8/useradd#:~:text=%2Dp
user_password_encrypted = sha512_crypt.hash(user_password)

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
# create sudo group
add_op(
    state,
    server.group,
    name="Create sudo group",
    group="sudo",
    present=True,
)
# allow sudo group to run any command
add_op(
    state,
    files.line,
    name="Allow sudo group to run any command",
    path="/etc/sudoers",
    line=f"# %sudo\tALL=(ALL:ALL) ALL",
    replace=f"%sudo\tALL=(ALL:ALL) ALL",
)
# create user
add_op(
    state,
    server.user,
    name=f"Create user {user_name}",
    user=user_name,
    groups=["sudo"],
    home=f"/home/{user_name}",
    public_keys=user_ssh_pubkey,
    password=user_password_encrypted,
    present=True,
)
run_ops(state)
