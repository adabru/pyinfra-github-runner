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
python -m venv venv
# linux
source venv/bin/activate
# windows
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```sh
pip install pyinfra
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

Replace `your.server.ip.address` with the IP address of your server and `your-username` with your SSH username. This will also allow to connect to the server with the command `ssh ghrunner`.

If you run the script the first time, you need to use the root password to add your user to the server:

```sh
python add_user.py
```

Then you can run the deployment with following command:

```sh
pyinfra ghrunner deploy.py
```

## Contributing

Feel free to open issues or pull requests :)
