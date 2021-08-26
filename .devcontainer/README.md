There are two ways to use devcontainer: the original one with Visual Studio created by ludeeus, and the alternative one without any editor I created.

## Developing with Visual Studio Code + devcontainer

The easiest way to get started with custom integration development is to use Visual Studio Code with devcontainers. This approach will create a preconfigured development environment with all the tools you need.

In the container you will have a dedicated Home Assistant core instance running with your custom component code. You can configure this instance by updating the `./devcontainer/configuration.yaml` file.

**Prerequisites**

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- Docker
  -  For Linux, macOS, or Windows 10 Pro/Enterprise/Education use the [current release version of Docker](https://docs.docker.com/install/)
  -   Windows 10 Home requires [WSL 2](https://docs.microsoft.com/windows/wsl/wsl2-install) and the current Edge version of Docker Desktop (see instructions [here](https://docs.docker.com/docker-for-windows/wsl-tech-preview/)). This can also be used for Windows Pro/Enterprise/Education.
- [Visual Studio code](https://code.visualstudio.com/)
- [Remote - Containers (VSC Extension)][extension-link]

[More info about requirements and devcontainer in general](https://code.visualstudio.com/docs/remote/containers#_getting-started)

[extension-link]: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers

**Getting started:**

1. Fork the repository.
2. Clone the repository to your computer.
3. Open the repository using Visual Studio code.

When you open this repository with Visual Studio code you are asked to "Reopen in Container", this will start the build of the container.

_If you don't see this notification, open the command palette and select `Remote-Containers: Reopen Folder in Container`._

### Tasks

The devcontainer comes with some useful tasks to help you with development, you can start these tasks by opening the command palette and select `Tasks: Run Task` then select the task you want to run.

When a task is currently running (like `Run Home Assistant on port 9123` for the docs), it can be restarted by opening the command palette and selecting `Tasks: Restart Running Task`, then select the task you want to restart.

The available tasks are:

Task | Description
-- | --
Run Home Assistant on port 9123 | Launch Home Assistant with your custom component code and the configuration defined in `.devcontainer/configuration.yaml`.
Run Home Assistant configuration against /config | Check the configuration.
Upgrade Home Assistant to latest dev | Upgrade the Home Assistant core version in the container to the latest version of the `dev` branch.
Install a specific version of Home Assistant | Install a specific version of Home Assistant core in the container.

### Step by Step debugging

With the development container,
you can test your custom component in Home Assistant with step by step debugging.

You need to modify the `configuration.yaml` file in `.devcontainer` folder
by uncommenting the line:

```yaml
# debugpy:
```

Then launch the task `Run Home Assistant on port 9123`, and launch the debugger
with the existing debugging configuration `Python: Attach Local`.

For more information, look at [the Remote Python Debugger integration documentation](https://www.home-assistant.io/integrations/debugpy/).

## Developing with any editors + devcontainer

This repository inherits the integration_blueprint repository. Since I do not use Visual Studio, I left all its settings, but made my own mechanism for quick and convenient code testing, which works with absolutely any editor (I use PyCharm). And it can even be run on a remote machine. The only limitation of this method is that it needs Linux to work. Perhaps, it might work on other systems as well, but I haven't tested it, sorry.

Similar first way in the container you will have a dedicated Home Assistant core instance running with your custom component code. You can configure this instance by updating the `./devcontainer/configuration.yaml` file.

**Prerequisites**

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- Docker
  - For Linux, macOS, or Windows 10 Pro/Enterprise/Education use the [current release version of Docker](https://docs.docker.com/install/)
  - Windows 10 Home requires [WSL 2](https://docs.microsoft.com/windows/wsl/wsl2-install) and the current Edge version of Docker Desktop (see instructions [here](https://docs.docker.com/docker-for-windows/wsl-tech-preview/)). This can also be used for Windows Pro/Enterprise/Education.
- Bash environment

**Getting started:**

1. Fork the repository.
2. Clone the repository to your computer.
3. Run devcontainer from command line: \
    `./bin/devcontainer start`

Note: By default, the container is created in local access only mode.
If you want to have access from the outside (for example, when starting on a remote machine), add parameter `--public` at the first start (after creating the container, this setting is remembered by the system): \
`./bin/devcontainer --public start`

While container is run Home Assistant will be available at http://localhost:9123/

Note: The container can be stopped by pressing the good old Ctrl-C keys.

### Useful devcontainer commands

- Start container: `./bin/devcontainer start`
- Destroy container: `./bin/devcontainer down`
- Upgrade Home Assistant to latest dev: `./bin/devcontainer upgrade`
- Install a specific version of Home Assistant: `./bin/devcontainer set-version`
- Run command line into container: `./bin/devcontainer bash`

### Bootstrap script

Sometimes you need to perform additional steps at the stage of container initialization. To do this, you can use script `.devcontainer/bootstrap.sh`. By default, it is configured to automatically install the libraries required for your component from private repositories. But you are free to change it however you like.
The main thing to remember is that the script will be executed INSIDE the container.

The script is automatically executed immediately after initializing the container and immediately after upgrading the HA version. It can also be executed at any time with command `./bin/devcontainer bootstrap`.

When the script is run, it receives only one parameter — the current container command: `install`, `upgrade` or `bootstrap`.
The current directory when running the script is the root directory of the repository inside the container. Home Assistant settings are located in directory `/config`.

To automatically install libraries from private repositories, you need to register each such library in the `requirements.txt` file as a link of the form
```requirements.txt
git+https://{GITHUB_TOKEN}@github.com/<USER>/<REPOSITORY>.git@<BRANCH>#egg=<LIBRARY>
```
Note: `{GITHUB_TOKEN}` is text as is, NOT actual token!

After that, in the root of the repository, create a file `secrets.yaml` and write the contents to it:
```yaml
github_token: <YOUR_TOKEN>
```

When you run the bootstrap script, it will automatically extract the required lines from requirements.txt, replace line `{GITHUB_TOKEN}` in them with the real token, and install the libraries. At the same time, file `secrets.yaml` is prohibited via `.gitignore` from being sent to the repository. Therefore, you can not be afraid that the token will be compromised.
