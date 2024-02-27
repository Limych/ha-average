MAKEFLAGS += --no-print-directory
SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
.DEFAULT_GOAL := help

include /opt/container/makefiles/*.mk

help: ## Show help
	@printf "  \033[1m%s\033[0m\n    %s\033[32m\033[0m\n    %s\033[32m\033[0m \n\n" "container" "Custom CLI used in this container" "https://github.com/ludeeus/container";
	@printf "  \033[1m%s\033[0m\n    %s\033[32m\033[0m \n\n" "usage:" "container [command]";
	@printf "  \033[1m%s\033[0m\n" "where [command] is one of:";
	@awk 'BEGIN {FS = ":.*##";} /^[a-zA-Z_-]+:.*?##/ { printf "   \033[36m container %-25s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST);
	@echo
