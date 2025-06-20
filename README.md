# pyinfra github runner

## Overview

This project uses [pyinfra](https://pyinfra.com/) to setup a self-hosted github runner on an arch server with ssh access.

## Installation

Prerequisites:

- Python 3.x
- git / Git for Windows

Clone the repository

```sh
git clone https://github.com/adabru/pyinfra-github-runner.git
cd pyinfra-github-runner
```

Create and activate a virtual environment:

```sh
python -m venv .venv
# linux
source .venv/bin/activate
# windows
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```sh
pip install pyinfra passlib
```

If you don't have an ssh key yet, create one:

```
ssh-keygen -t ecdsa -b 521
```

Just keep pressing enter to finish the key generation with default values.

Add an entry to your `~/.ssh/config` file:

```
Host ghrunner
   HostName your.server.ip.address
   User your-username
   IdentityFile ~/.ssh/id_ecdsa
```

Replace `your.server.ip.address` with the IP address of your server.
Replace `your-username` with your SSH username.
Optionally replace `ghrunner` with an alias of your choice.

Add your user to the server. You will need your server's root password.

```sh
python add_user.py ghrunner
```

Then you can run the deployment with following command:

```sh
pyinfra ghrunner deploy.py
```

Your server will be listed as self-hosted runner on GitHub now.

## Contributing

Feel free to open issues or pull requests :)
