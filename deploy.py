from pyinfra import config
from pyinfra.operations import pacman, systemd

# Use sudo
config.SUDO = True


# Update package list and install Docker
pacman.packages(
    name="Install Docker",
    packages=["docker"],
    update=True,
)

# Enable and start Docker service
systemd.service(
    name="Enable Docker service",
    service="docker",
    running=True,
    enabled=True,
)
