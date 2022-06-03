*Please :star: this repo if you find it useful*

# Notice

The component and platforms in this repository are not meant to be used by a
user, but as a "blueprint" that custom component developers can build
upon, to make more awesome stuff.

HAVE FUN! 😎

## Why?

This is simple, by having custom_components look (README + structure) the same
it is easier for developers to help each other and for users to start using them.

If you are a developer and you want to add things to this "blueprint" that you think more
developers will have use for, please open a PR to add it :)

## What?

This repository is an extension and addition to the [integration_blueprint](https://github.com/custom-components/integration_blueprint) repository. It is regularly updated with all the edits from parent repository and makes it easy to apply new edits to your project. This way you can easily keep it up to date.

This repository contains multiple files, here is a overview:

File | Purpose
-- | --
`.devcontainer/*` | Used for development/testing with VSCODE, more info in the readme file in that dir.
`.github/ISSUE_TEMPLATE/feature_request.md` | Template for Feature Requests
`.github/ISSUE_TEMPLATE/issue.md` | Template for issues
`.vscode/tasks.json` | Tasks for the devcontainer.
`custom_components/integration_blueprint/translations/*` | [Translation files.](https://developers.home-assistant.io/docs/internationalization/custom_integration)
`custom_components/integration_blueprint/__init__.py` | The component file for the integration.
`custom_components/integration_blueprint/api.py` | This is a sample API client.
`custom_components/integration_blueprint/binary_sensor.py` | Binary sensor platform for the integration.
`custom_components/integration_blueprint/config_flow.py` | Config flow file, this adds the UI configuration possibilities.
`custom_components/integration_blueprint/const.py` | A file to hold shared variables/constants for the entire integration.
`custom_components/integration_blueprint/manifest.json` | A [manifest file](https://developers.home-assistant.io/docs/en/creating_integration_manifest.html) for Home Assistant.
`custom_components/integration_blueprint/sensor.py` | Sensor platform for the integration.
`custom_components/integration_blueprint/switch.py` | Switch sensor platform for the integration.
`tests/__init__.py` | Makes the `tests` folder a module.
`tests/conftest.py` | Global [fixtures](https://docs.pytest.org/en/stable/fixture.html) used in tests to [patch](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch) functions.
`tests/test_api.py` | Tests for `custom_components/integration_blueprint/api.py`.
`tests/test_config_flow.py` | Tests for `custom_components/integration_blueprint/config_flow.py`.
`tests/test_init.py` | Tests for `custom_components/integration_blueprint/__init__.py`.
`tests/test_switch.py` | Tests for `custom_components/integration_blueprint/switch.py`.
`CONTRIBUTING.md` | Guidelines on how to contribute.
`example.png` | Screenshot that demonstrate how it might look in the UI.
`info.md` | An example on a info file (used by [hacs][hacs]).
`LICENSE.md` | The license file for the project.
`README.md` | The file you are reading now, should contain info about the integration, installation and configuration instructions.
`requirements.txt` | Python packages used by this integration.
`requirements-dev.txt` | Python packages used to provide [IntelliSense](https://code.visualstudio.com/docs/editor/intellisense)/code hints during development of this integration, typically includes packages in `requirements.txt` but may include additional packages
`requirements-text.txt` | Python packages required to run the tests for this integration, typically includes packages in `requirements-dev.txt` but may include additional packages

## How?

* …or [use this template](https://github.com/Limych/ha-blueprint/generate) to create your new repository.
  Then download a copy of the new repository to your IDE and run the final environment setup commands:
    ```bash
    # Configure future updates from blueprint repository
    git remote add blueprint https://github.com/Limych/ha-blueprint.git
    git fetch blueprint dev
    git merge blueprint/dev --allow-unrelated-histories

    # Push changes to origin repository
    git push -u origin dev

    # Initialize the development environment
    ./bin/setup
    ```

* …or create a new repository on the command line:
    ```bash
    # Initialize your new origin repository
    git init
    git remote add origin https://github.com/YOUR_NEW_REPOSITORY

    # Apply blueprint repository
    git remote add blueprint https://github.com/Limych/ha-blueprint.git
    git fetch blueprint dev
    git reset --hard blueprint/dev
    git branch -M dev

    # Push changes to origin repository
    git push -u origin dev

    # Initialize the development environment
    ./bin/setup
    ```

* …or apply blueprint to an existing repository from the command line:
    ```bash
    # Apply blueprint repository
    git remote add blueprint https://github.com/Limych/ha-blueprint.git
    git fetch blueprint dev
    git merge blueprint/dev --allow-unrelated-histories

    # Push changes to origin repository
    git push -u origin dev

    # Initialize the development environment
    ./bin/setup
    ```

After these steps, your repository will developing on a own branch. But in parallel there will be this blueprint repository, new changes in which you can always apply with a couple of simple commands:
```bash
./bin/update
git merge blueprint/dev
```

If you want to use all the potential and features of this blueprint template you
should use devcontainer. See [.devcontainer/README.md](./.devcontainer/README.md) for more information.

If you need to work on the python library in parallel of this integration
(`sampleclient` in this example) there are different options. The following one seems
easy to implement:

- Create a dedicated branch for your python library on a public git repository (example: branch
`dev` on `https://github.com/ludeeus/sampleclient`)
- Update in the `manifest.json` file the `requirements` key to point on your development branch
( example: `"requirements": ["git+https://github.com/ludeeus/sampleclient.git@dev#devp==0.0.1beta1"]`)
- Each time you need to make a modification to your python library, push it to your
development branch and increase the number of the python library version in `manifest.json` file
to ensure Home Assistant update the code of the python library. (example `"requirements": ["git+https://...==0.0.1beta2"]`).


***
README content if this was a published component:
***

*Please :star: this repo if you find it useful*

# integration_blueprint

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![Support me on Patreon][patreon-shield]][patreon]

[![Community Forum][forum-shield]][forum]

_Component to integrate with [integration_blueprint][component]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show something `True` or `False`.
`sensor` | Show info from blueprint API.
`switch` | Switch something `True` or `False`.

![example][exampleimg]

## Known Limitations and Issues

- Some example limitation.

## Installation

### Install from HACS (recommended)

1. Have [HACS][hacs] installed, this will allow you to easily manage and track updates.
1. Search for "Blueprint".
1. Click Install below the found integration.
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI go to "Configuration" > "Integrations" click "+" and search for "Integration blueprint".
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions below, then restart Home Assistant.

### Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `integration_blueprint`.
1. Download file `integration_blueprint.zip` from the [latest release section][releases-latest] in this repository.
1. Extract _all_ files from this archive you downloaded in the directory (folder) you created.
1. Restart Home Assistant
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI go to "Configuration" > "Integrations" click "+" and search for "Blueprint".
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions below, then restart Home Assistant.

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

## Configuration is done in the UI

<!---->

## Track updates

You can automatically track new versions of this component and update it by [HACS][hacs].

## Troubleshooting

To enable debug logs use this configuration:
```yaml
# Example configuration.yaml entry
logger:
  default: info
  logs:
    custom_components.integration_blueprint: debug
```
... then restart HA.

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this component is by [Andrey "Limych" Khrolenok](https://github.com/Limych).

For a full list of all authors and contributors,
check [the contributor's page][contributors].

This Home Assistant custom component was created and is updated using the [HA-Blueprint template](https://github.com/Limych/ha-blueprint). You can use this template to maintain your own Home Assistant custom components.

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

***

[component]: https://github.com/Limych/ha-blueprint
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-blueprint.svg?style=popout
[commits]: https://github.com/Limych/ha-blueprint/commits/master
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=popout
[hacs]: https://hacs.xyz
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/
[license]: https://github.com/Limych/ha-blueprint/blob/main/LICENSE.md
[license-shield]: https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout
[maintenance-shield]: https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout
[releases-shield]: https://img.shields.io/github/release/Limych/ha-blueprint.svg?style=popout
[releases]: https://github.com/Limych/ha-blueprint/releases
[releases-latest]: https://github.com/Limych/ha-blueprint/releases/latest
[user_profile]: https://github.com/Limych
[report_bug]: https://github.com/Limych/ha-blueprint/issues/new?template=bug_report.md
[suggest_idea]: https://github.com/Limych/ha-blueprint/issues/new?template=feature_request.md
[contributors]: https://github.com/Limych/ha-blueprint/graphs/contributors
[patreon-shield]: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3DLimych%26type%3Dpatrons&style=popout
[patreon]: https://www.patreon.com/join/limych
