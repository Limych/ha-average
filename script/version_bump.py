#!/usr/bin/env python3
"""Helper script to bump the current version."""
import argparse
import logging
import os
import sys
from datetime import datetime
import re
import subprocess

from packaging.version import Version

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
logging.getLogger(__name__).addHandler(logging.NullHandler())

# logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)

ROOT = os.path.dirname(os.path.abspath(f"{__file__}/.."))

sys.path.append(ROOT)


def fallback_version(localpath):
    """Return version from regex match."""
    return_value = ""
    if os.path.isfile(localpath):
        with open(localpath) as local:
            ret = re.compile(r"^\b(VERSION|__version__)\s*=\s*['\"](.*)['\"]")
            for line in local.readlines():
                matcher = ret.match(line)
                if matcher:
                    return_value = str(matcher.group(2))
    return return_value


def get_component_version(localpath, package):
    """Return the local version if any."""
    if "." in package:
        package = "{}.{}".format(package.split(".")[1], package.split(".")[0])
    package = f"custom_components.{package}"
    _LOGGER.debug("Started for %s (%s)", localpath, package)
    return_value = ""
    if os.path.isfile(localpath):
        try:
            name = "__version__"
            return_value = getattr(__import__(package, fromlist=[name]), name)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.debug(str(err))
        if return_value == "":
            try:
                name = "VERSION"
                return_value = getattr(__import__(package, fromlist=[name]), name)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.debug(str(err))
    if return_value == "":
        return_value = fallback_version(localpath)
    _LOGGER.debug(str(return_value))
    return return_value


def _bump_release(release, bump_type):
    """Bump a release tuple consisting of 3 numbers."""
    major, minor, patch = release

    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0

    return major, minor, patch


def bump_version(version, bump_type):
    """Return a new version given a current version and action."""
    to_change = {}

    if bump_type == "minor":
        # Convert 0.67.3 to 0.68.0
        # Convert 0.67.3.b5 to 0.68.0
        # Convert 0.67.3.dev0 to 0.68.0
        # Convert 0.67.0.b5 to 0.67.0
        # Convert 0.67.0.dev0 to 0.67.0
        to_change["dev"] = None
        to_change["pre"] = None

        if not version.is_prerelease or version.release[2] != 0:
            to_change["release"] = _bump_release(version.release, "minor")

    elif bump_type == "patch":
        # Convert 0.67.3 to 0.67.4
        # Convert 0.67.3.b5 to 0.67.3
        # Convert 0.67.3.dev0 to 0.67.3
        to_change["dev"] = None
        to_change["pre"] = None

        if not version.is_prerelease:
            to_change["release"] = _bump_release(version.release, "patch")

    elif bump_type == "dev":
        # Convert 0.67.3 to 0.67.4.dev0
        # Convert 0.67.3.b5 to 0.67.4.dev0
        # Convert 0.67.3.dev0 to 0.67.3.dev1
        if version.is_devrelease:
            to_change["dev"] = ("dev", version.dev + 1)
        else:
            to_change["pre"] = ("dev", 0)
            to_change["release"] = _bump_release(version.release, "minor")

    elif bump_type == "beta":
        # Convert 0.67.5 to 0.67.6b0
        # Convert 0.67.0.dev0 to 0.67.0b0
        # Convert 0.67.5.b4 to 0.67.5b5

        if version.is_devrelease:
            to_change["dev"] = None
            to_change["pre"] = ("b", 0)

        elif version.is_prerelease:
            if version.pre[0] == "a":
                to_change["pre"] = ("b", 0)
            if version.pre[0] == "b":
                to_change["pre"] = ("b", version.pre[1] + 1)
            else:
                to_change["pre"] = ("b", 0)
                to_change["release"] = _bump_release(version.release, "patch")

        else:
            to_change["release"] = _bump_release(version.release, "patch")
            to_change["pre"] = ("b", 0)

    elif bump_type == "nightly":
        # Convert 0.70.0d0 to 0.70.0d20190424, fails when run on non dev release
        if not version.is_devrelease:
            raise ValueError("Can only be run on dev release")

        to_change["dev"] = (
            "dev",
            datetime.utcnow().date().isoformat().replace("-", ""),
        )

    else:
        assert False, f"Unsupported type: {bump_type}"

    temp = Version("0")
    temp._version = version._version._replace(  # pylint: disable=protected-access
        **to_change
    )
    return Version(str(temp))


def write_version(component_path, version):
    """Update custom component constant file with new version."""
    component_path += "/const.py"
    with open(component_path) as fil:
        content = fil.read()

    content = re.sub("VERSION = .*\n", f"VERSION = '{version}'\n", content)
    content = re.sub("__version__ = .*\n", f"__version__ = '{version}'\n", content)

    with open(component_path, "wt") as fil:
        fil.write(content)


def main():
    """Execute script."""
    parser = argparse.ArgumentParser(
        description="Bump version of Home Assistant custom component"
    )
    parser.add_argument(
        "type",
        help="The type of the bump the version to.",
        choices=["beta", "dev", "patch", "minor", "nightly"],
    )
    parser.add_argument(
        "--commit", action="store_true", help="Create a version bump commit."
    )
    arguments = parser.parse_args()

    # pylint: disable=subprocess-run-check
    if arguments.commit and subprocess.run(["git", "diff", "--quiet"]).returncode == 1:
        print("Cannot use --commit because git is dirty.")
        return

    component = None
    for current_path, dirs, _ in os.walk(f"{ROOT}/custom_components"):
        if current_path.find("__pycache__") != -1:
            continue
        for dname in dirs:
            if dname != "__pycache__":
                component = dname

    assert component, "Component not found!"
    component_path = f"{ROOT}/custom_components/{component}"

    current = Version(get_component_version(f"{component_path}/__init__.py", component))
    bumped = bump_version(current, arguments.type)
    assert bumped > current, "BUG! New version is not newer than old version"

    write_version(component_path, bumped)

    if not arguments.commit:
        return

    subprocess.run(["git", "commit", "-nam", f"Bumped version to {bumped}"])


# pylint: disable=import-outside-toplevel
def test_bump_version():
    """Make sure it all works."""
    import pytest

    assert bump_version(Version("0.56.0"), "beta") == Version("0.56.1b0")
    assert bump_version(Version("0.56.0b3"), "beta") == Version("0.56.0b4")
    assert bump_version(Version("0.56.0.dev0"), "beta") == Version("0.56.0b0")

    assert bump_version(Version("0.56.3"), "dev") == Version("0.57.0.dev0")
    assert bump_version(Version("0.56.0b3"), "dev") == Version("0.57.0.dev0")
    assert bump_version(Version("0.56.0.dev0"), "dev") == Version("0.56.0.dev1")

    assert bump_version(Version("0.56.3"), "patch") == Version("0.56.4")
    assert bump_version(Version("0.56.3.b3"), "patch") == Version("0.56.3")
    assert bump_version(Version("0.56.0.dev0"), "patch") == Version("0.56.0")

    assert bump_version(Version("0.56.0"), "minor") == Version("0.57.0")
    assert bump_version(Version("0.56.3"), "minor") == Version("0.57.0")
    assert bump_version(Version("0.56.0.b3"), "minor") == Version("0.56.0")
    assert bump_version(Version("0.56.3.b3"), "minor") == Version("0.57.0")
    assert bump_version(Version("0.56.0.dev0"), "minor") == Version("0.56.0")
    assert bump_version(Version("0.56.2.dev0"), "minor") == Version("0.57.0")

    today = datetime.utcnow().date().isoformat().replace("-", "")
    assert bump_version(Version("0.56.0.dev0"), "nightly") == Version(
        f"0.56.0.dev{today}"
    )
    with pytest.raises(ValueError):
        assert bump_version(Version("0.56.0"), "nightly")


if __name__ == "__main__":
    main()
