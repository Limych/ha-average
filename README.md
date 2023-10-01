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

File | Purpose | Documentation
-- | -- | --
`.devcontainer.json` | Used for development/testing with Visual Studio Code. | [Documentation](https://code.visualstudio.com/docs/remote/containers)
`.github/ISSUE_TEMPLATE/*.yml` | Templates for the issue tracker | [Documentation](https://help.github.com/en/github/building-a-strong-community/configuring-issue-templates-for-your-repository)
`.vscode/tasks.json` | Tasks for the devcontainer. | [Documentation](https://code.visualstudio.com/docs/editor/tasks)
`custom_components/integration_blueprint/*` | Integration files, this is where everything happens. | [Documentation](https://developers.home-assistant.io/docs/creating_component_index)
`tests/*` | Integration unit tests. |
`CONTRIBUTING.md` | Guidelines on how to contribute. | [Documentation](https://help.github.com/en/github/building-a-strong-community/setting-guidelines-for-repository-contributors)
`LICENSE` | The license file for the project. | [Documentation](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/licensing-a-repository)
`README.md` | The file you are reading now, should contain info about the integration, installation and configuration instructions. | [Documentation](https://help.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax)
`requirements.txt` | Python packages used for development/lint/testing this integration. | [Documentation](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

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
    ./scripts/setup
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
    ./scripts/setup
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
    ./scripts/setup
    ```

After these steps, your repository will developing on a own branch. But in parallel there will be this blueprint repository, new changes in which you can always apply with a couple of simple commands:
```bash
./scripts/update
git merge blueprint/dev
```

Then:
1. Rename all instances of the `integration_blueprint` to `custom_components/<your_integration_domain>` (e.g. `custom_components/awesome_integration`).
1. Rename all instances of the `Integration Blueprint` to `<Your Integration Name>` (e.g. `Awesome Integration`).

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

## Next steps

These are some next steps you may want to look into:
- Add tests to your integration, [`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component) can help you get started.
- Add brand images (logo/icon) to https://github.com/home-assistant/brands.
- Create your first release.
- Share your integration on the [Home Assistant Forum](https://community.home-assistant.io/).
- Submit your integration to the [HACS](https://hacs.xyz/docs/publish/start).
