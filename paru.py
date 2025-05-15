from pyinfra import host
from pyinfra.api import operation
from pyinfra.api.command import StringCommand
from pyinfra.facts.pacman import PacmanPackages
from pyinfra.facts.server import Home


@operation()
def setup():
    installed_packages = host.get_fact(PacmanPackages)
    if "paru-bin" in installed_packages:
        return

    yield StringCommand(
        "curl -L https://aur.archlinux.org/cgit/aur.git/snapshot/paru-bin.tar.gz -o paru-bin.tar.gz",
        _sudo=False,
    )
    yield StringCommand("tar -xvf paru-bin.tar.gz", _sudo=False)
    # makepkg must be run as non-root
    yield StringCommand("makepkg --noconfirm --dir paru-bin", _sudo=False)
    yield StringCommand("pacman -U paru-bin/*.pkg.tar.zst --noconfirm")
    yield StringCommand("rm -rf paru-bin.tar.gz paru-bin", _sudo=False)


@operation()
def packages(packages: list[str], present: bool = True):
    installed_packages = host.get_fact(PacmanPackages)

    to_change = []

    for package in packages:
        # Needs to be installed
        if present and not (package in installed_packages):
            to_change.append(package)

        # Needs to be removed
        if not present and package in installed_packages:
            to_change.append(package)

    # Nothing to do
    if len(to_change) == 0:
        return

    # Install packages
    if present:
        # Build packages and dependencies
        yield StringCommand(
            "paru --noconfirm --noinstall " + " ".join(to_change),
            _sudo=False,
        )
        # Get non-sudo user name
        non_root_user_home = host.get_fact(Home, _sudo=False)
        # Install previously built packages
        artifact_list = " ".join(
            [
                f"{non_root_user_home}/.cache/paru/clone/{package}/*.pkg.tar.zst"
                for package in to_change
            ]
        )
        yield StringCommand(
            f"pacman -U {artifact_list} --noconfirm",
        )
    # Remove packages
    else:
        yield StringCommand(
            "paru --noconfirm -R " + " ".join(to_change),
        )
