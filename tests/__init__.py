"""Tests for integration."""
import pathlib
import traceback


def get_fixture_path(filename: str) -> pathlib.Path:
    """Get path of fixture."""
    start_path = traceback.extract_stack()[-1].filename
    return pathlib.Path(start_path).parent.joinpath("fixtures", filename)
