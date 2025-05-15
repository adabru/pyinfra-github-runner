import sys

from pyinfra import config, host
from pyinfra.api import operation
from pyinfra.api.command import StringCommand
from pyinfra.facts.files import File
from pyinfra.operations import files, pacman, systemd

import paru

configure_line = ""
print(
    """
To configure the GitHub Actions runner, you need to enter the url and the token. When you add a new runner to your repository or your organisation from the GitHub website, you will be presented with a line like the following:

./config.sh --url https://github.com/adabru/pyinfra-github-runner --token ABOTOMRNCGLMUALMU6Vxxxxxxxxxx

Please copy the whole line and enter it here:"""
)
configure_line = sys.stdin.readline().strip()
if not configure_line:
    print("No runner configuration entered, exiting")
    sys.exit(1)


@operation()
def configure_runner(configure_line: str):
    # Don't do anything if the runner is already configured
    runner_config = host.get_fact(File, "/var/lib/github-actions/.runner")
    if runner_config != None:
        return

    # Configure runner
    yield StringCommand(
        f"{configure_line} --unattended",
        _sudo_user="github-actions",
        _chdir="/var/lib/github-actions",
    )


# Use sudo
config.SUDO = True

pacman.packages(
    name="Install paru dependencies",
    packages=["git", "base-devel"],
    update=True,
)

paru.setup()

# Patch githhub-actions-bin
# see https://aur.archlinux.org/packages/github-actions-bin#comment-1008295
# see https://github.com/Morganamilo/paru/blob/55efaabda3567908c3875cea0dcd3f47847896b3/man/paru.conf.5#L403-L409
files.block(
    name="Patch github-actions-bin",
    path="/etc/paru.conf",
    content=("[ADABRU]\nUrl = https://github.com/adabru/github-actions-bin"),
)

paru.packages(name="Install runner", packages=["github-actions-bin"])

# Configure runner on first run
configure_runner(configure_line)

systemd.service(
    name="Enable and start GitHub Actions service",
    service="github-actions.service",
    running=True,
    enabled=True,
)
