start:  ## Start Home Assistant with the integration loaded
	@bash /opt/container/helpers/common/homeassistant/start.sh

set-version: ## Set Home Assistant version
	@bash /opt/container/helpers/common/homeassistant/set-version.sh

install:  ## Install Home Assistant dev in the container
	@python3 -m pip --disable-pip-version-check install --upgrade git+https://github.com/home-assistant/home-assistant.git@dev

upgrade:  ## Upgrade Home Assistant to latest dev in the container
	install

run:
	start

check-config: ## Check Home Assistant config
	@hass -c /config --script check_config

init: ## Initialize the dev env
	@bash /opt/container/helpers/integration/init.sh