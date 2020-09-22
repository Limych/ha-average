#!/usr/bin/env python3
"""Helper script to update requirements."""
import json
import os

import requests

ROOT = os.path.dirname(os.path.abspath(f"{__file__}/.."))

PKG_PATH = PACKAGE = None
for current_path, dirs, _ in os.walk(f"{ROOT}/custom_components"):
    if current_path.find("__pycache__") != -1:
        continue
    for dname in dirs:
        if dname != "__pycache__":
            PACKAGE = dname
PKG_PATH = f"{ROOT}/custom_components/{PACKAGE}"


def get_package(requre: str) -> str:
    """Extract package name from requirement."""
    return requre.split(">")[0].split("<")[0].split("!")[0].split("=")[0].split("~")[0]


harequire = []
request = requests.get(
    "https://raw.githubusercontent.com/home-assistant/home-assistant/dev/setup.py"
)
request = request.text.split("REQUIRES = [")[1].split("]")[0].split("\n")
for req in request:
    if "=" in req:
        harequire.append(get_package(req.split('"')[1]))

print(harequire)

with open(f"{PKG_PATH}/manifest.json") as manifest:
    manifest = json.load(manifest)
    requirements = []
    for req in manifest["requirements"]:
        requirements.append(get_package(req))
    manifest["requirements"] = requirements
with open(f"{ROOT}/requirements.txt") as requirements:
    tmp = requirements.readlines()
    requirements = []
    for req in tmp:
        requirements.append(req.replace("\n", ""))
for req in requirements:
    pkg = get_package(req)
    if pkg in manifest["requirements"]:
        manifest["requirements"].remove(pkg)
        manifest["requirements"].append(req)

for req in manifest["requirements"]:
    pkg = get_package(req)
    if pkg in harequire:
        print(f"{pkg} in HA requirements, no need here.")
print(json.dumps(manifest["requirements"], indent=4, sort_keys=True))
with open(f"{PKG_PATH}/manifest.json", "w") as manifestfile:
    manifestfile.write(json.dumps(manifest, indent=4, sort_keys=True))
