#!/usr/bin/env bash
# shellcheck source=/dev/null

source /opt/container/helpers/common/paths.sh
mkdir -p /config

if test -f "$(workspacePath)config/configuration.yaml"; then
  echo "Copy configuration.yaml"
  ln -sf "$(workspacePath)config/configuration.yaml" /config/configuration.yaml || echo "config/configuration.yaml are missing"
fi

if test -f "$(workspacePath)config/ui-lovelace.yaml"; then
  echo "Copy ui-lovelace.yaml"
  ln -sf "$(workspacePath)config/ui-lovelace.yaml" /config/ui-lovelace.yaml || echo ""
fi

if test -f "$(workspacePath)config/secrets.yaml"; then
  echo "Copy secrets.yaml"
  ln -sf "$(workspacePath)config/secrets.yaml" /config/secrets.yaml || echo ""
fi

if test -d "$(workspacePath)custom_components"; then
  echo "Symlink the custom component directory"

  if test -d "$(workspacePath)custom_components"; then
    rm -R /config/custom_components
  fi

  ln -sf "$(workspacePath)custom_components/" /config/custom_components || echo "Could not copy the custom_component" exit 1
elif  test -f "__init__.py"; then
  echo "Having the component in the root is currently not supported"
fi

echo "Start Home Assistant"
if ! [ -x "$(command -v hass)" ]; then
  echo "Home Assistant is not installed, running installation."
  python3 -m pip --disable-pip-version-check install --upgrade git+https://github.com/home-assistant/home-assistant.git@dev
fi
hass --script ensure_config -c /config
hass -c /config
