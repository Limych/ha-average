# Why?

While tests aren't required to publish a custom component for Home Assistant, they will generally make development easier because good tests will expose when changes you want to make to the component logic will break expected functionality. Home Assistant uses [`pytest`](https://docs.pytest.org/en/latest/) for its tests, and the tests that have been included are modeled after tests that are written for core Home Assistant integrations. These tests pass with 100% coverage (unless something has changed ;) ) and have comments to help you understand the purpose of different parts of the test.

# Getting Started

To begin, it is recommended to create a virtual environment and install all necessary dependencies:
```bash
./scripts/setup
```

# Useful commands

Command | Description
------- | -----------
`pytest` | This will run all tests and tell you how many passed/failed. It also show you a [code coverage](https://en.wikipedia.org/wiki/Code_coverage) summary of component, including % of code that was executed and the line numbers of missed executions.
`pytest tests/test_init.py -k test_setup_unload_and_reload_entry` | Runs the `test_setup_unload_and_reload_entry` test function located in `tests/test_init.py`
