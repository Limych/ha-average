#!/usr/bin/env python3
"""Tracker updater for custom_updater."""

#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
import copy
import json
import logging
import os
import re

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
import sys

logging.getLogger(__name__).addHandler(logging.NullHandler())

# logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)

ROOT = os.path.dirname(os.path.abspath(f"{__file__}/.."))
TRACKER_FPATH = (
    f"{ROOT}/custom_components.json"
    if os.path.isfile(f"{ROOT}/custom_components.json")
    else f"{ROOT}/tracker.json"
)

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
        _LOGGER.debug(package)
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


def update_tracker(tracker_fpath):
    """Run tracker file update."""
    with open(tracker_fpath) as tracker_file:
        tracker = json.load(tracker_file)
    old_tr = copy.deepcopy(tracker)
    for package in tracker:
        _LOGGER.info("Updating version for %s", package)
        local_path = "{}/{}".format(
            ROOT, tracker[package]["local_location"].lstrip("/\\")
        )
        tracker[package]["version"] = get_component_version(local_path, package)
        base_path = os.path.split(local_path)[0]
        base_url = os.path.split(tracker[package]["remote_location"])[0]
        resources = []
        for current_path, _, files in os.walk(base_path):
            if current_path.find("__pycache__") != -1:
                continue
            for file in files:
                file = os.path.join(current_path, file).replace("\\", "/")
                if file != local_path:
                    resources.append(base_url + file[len(base_path) :])
        resources.sort()
        tracker[package]["resources"] = resources

    if tracker != old_tr:
        with open(tracker_fpath, "w") as tracker_file:
            json.dump(tracker, tracker_file, indent=4)


update_tracker(TRACKER_FPATH)
# subprocess.run(["git", "add", TRACKER_FPATH])
