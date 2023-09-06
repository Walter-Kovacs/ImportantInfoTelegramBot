COMMIT_TIME = $(shell git show -s --format=%ct | xargs -I {} date -d @{} +%Y-%m-%d_%H_%M)
COMMIT = $(shell git rev-parse --short HEAD)
BRANCH = $(shell git rev-parse --abbrev-ref HEAD)

VERSION ?= $(COMMIT_TIME)-${BRANCH}-${COMMIT}

IIBOT_INSTALL_WORKDIR ?= /usr/local/important_info_bot/

.PHONY: show_current_version
show_current_version:
	@echo ${VERSION}

.PHONY: install
install:
	@python3 scripts/install/install.py install --workdir="$(IIBOT_INSTALL_WORKDIR)" --version=$(VERSION) --source_code_dir=$(PWD)


.PHONY: install_venv
install_venv:
	cd ${IIBOT_INSTALL_WORKDIR}${VERSION} &&\
	. .venv/bin/activate &&\
	pip install -r requirements &&\
	deactivate

.PHONY: reload
reload:
	systemctl restart iibot


.PHONY: test_install_image
test_install_image:
	docker build -t iibot_install -f scripts/install/test.Dockerfile .


.PHONY: test_install
test_install: test_install_image
	docker run -v ${PWD}:/iibot --workdir /iibot iibot_install make install install_venv

.PHONY: enable
enable:
	@echo "Enabling version from VERSION env var: ${VERSION}; Just switching symlink, iibot service restart required after that"
	@python3 scripts/install/install.py enable --workdir="$(IIBOT_INSTALL_WORKDIR)" --version=$(VERSION)

.PHONY: show_installed
show_installed:
	@python3 scripts/install/install.py show_installed --workdir="${IIBOT_INSTALL_WORKDIR}"

.PHONY: deploy
deploy: install install_venv enable reload
	@systemctl status iibot
