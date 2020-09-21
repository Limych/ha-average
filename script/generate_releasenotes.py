#!/usr/bin/env python3
"""Helper script to generate release notes."""
import argparse
import logging
import os

# http://docs.python.org/2/howto/logging.html#library-config
# Avoids spurious error messages if no logger is configured by the user
logging.getLogger(__name__).addHandler(logging.NullHandler())

_LOGGER = logging.getLogger(__name__)

VERSION = "0.1.0"

ROOT = os.path.dirname(os.path.abspath(f"{__file__}/.."))


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
    # pylint: disable=fixme
    # todo
    arguments = parser.parse_args()

    if arguments.verbose:
        _LOGGER.setLevel(logging.DEBUG)

    if arguments.dry_run:
        print("!!! Dry Run !!!")


if __name__ == "__main__":
    main()
