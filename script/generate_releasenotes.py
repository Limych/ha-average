#!/usr/bin/env python3
"""Helper script to generate release notes."""
import argparse
import logging
import os
import re
import subprocess
from datetime import datetime
from typing import Dict

from github import Github, Repository

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
logging.getLogger(__name__).addHandler(logging.NullHandler())

logging.basicConfig(level=logging.CRITICAL)

_LOGGER = logging.getLogger(__name__)

VERSION = "0.1.0"

ROOT = os.path.dirname(os.path.abspath(f"{__file__}/.."))

BODY = """
[![Downloads for this release](https://img.shields.io/github/downloads/{repo}/{version}/total.svg)](https://github.com/{repo}/releases/{version})

{changes}

## Links

- [If you like what I (@limych) do please consider sponsoring me on Patreon](https://www.patreon.com/join/limych?)
"""

CHANGE = "- [{line}]({link}) @{author}\n"
NOCHANGE = "_No changes in this release._"


def new_commits(repo: Repository, sha: str):
    """Get new commits in repo."""
    dateformat = "%a, %d %b %Y %H:%M:%S GMT"
    release_commit = repo.get_commit(sha)
    since = datetime.strptime(release_commit.last_modified, dateformat)
    commits = repo.get_commits(since=since)
    if len(list(commits)) == 1:
        return []
    return reversed(list(commits)[:-1])


def last_release(github: Github, repo: Repository, skip=True) -> Dict[str, str]:
    """Return last release."""
    tag_sha = None
    data = {}
    tags = list(repo.get_tags())
    reg = "(v|^)?(\\d+\\.)?(\\d+\\.)?(\\*|\\d+)$"
    _LOGGER.debug("Found tags: %s", tags)
    if tags:
        for tag in tags:
            tag_name = tag.name
            if re.match(reg, tag_name):
                tag_sha = tag.commit.sha
                if skip:
                    skip = False
                    continue
                break
    data["tag_name"] = tag_name
    data["tag_sha"] = tag_sha
    return data


def get_commits(github: Github, repo: Repository) -> str:
    """Generate list of commits."""
    changes = ""
    commits = new_commits(repo, last_release(github, repo)["tag_sha"])

    for commit in commits:
        msg = repo.get_git_commit(commit.sha).message
        if "Bump version " in msg:
            continue
        if "Merge branch " in msg:
            continue
        if "Merge tag " in msg:
            continue
        if "Merge pull request " in msg:
            continue
        if "\n" in msg:
            msg = msg.split("\n")[0]
        changes += CHANGE.format(
            line=msg, link=commit.html_url, author=commit.author.login
        )

    if changes == "":
        changes = NOCHANGE

    return changes


def main():
    """Execute script."""
    parser = argparse.ArgumentParser(
        description=f"Release notes generator. Version {VERSION}"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debugging output.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview version bumping without running it.",
    )
    parser.add_argument(
        "--token",
        help="Github token to access to repository.",
        # required=True,
    )
    parser.add_argument(
        "--repo",
        help="Github repository (default: %(default)s).",
        default=subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            stdout=subprocess.PIPE,
            check=True,
        )
        .stdout.decode("UTF-8")
        .replace("https://github.com/", "")
        .replace(".git", "")
        .strip(),
    )
    parser.add_argument(
        "--update-release", help="Github release tag to update.", required=True,
    )
    arguments = parser.parse_args()

    if arguments.verbose:
        _LOGGER.setLevel(logging.DEBUG)

    if arguments.dry_run:
        print("!!! Dry Run !!!")

    github = Github(arguments.token)
    _LOGGER.debug("Repo: %s", arguments.repo)
    repo = github.get_repo(arguments.repo)
    version = arguments.update_release.replace("refs/tags/", "")
    _LOGGER.debug("Tag: %s", version)
    release = repo.get_release(version)
    release.update_release(
        name=version,
        prerelease=release.prerelease,
        draft=release.draft,
        message=BODY.format(
            repo=arguments.repo, version=version, changes=get_commits(github, repo),
        ),
    )


if __name__ == "__main__":
    main()
