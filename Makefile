COMMIT_TIME = $(shell git show -s --format=%ct | xargs -I {} date -d @{} +%Y-%m-%d_%H_%m)
COMMIT = $(shell git rev-parse --short HEAD)

VERSION=$(COMMIT_TIME)-${COMMIT}

IIBOT_INSTALL_WORKDIR ?= /usr/local/important_info_bot/

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
	sudo docker build -t iibot_install -f scripts/install/test.Dockerfile .


.PHONY: test_install
test_install: test_install_image
	sudo docker run -v ${PWD}:/iibot --workdir /iibot iibot_install make install install_venv

.PHONY: enable_current
enable_current:
	@python3 scripts/install/install.py enable --workdir="$(IIBOT_INSTALL_WORKDIR)" --version=$(VERSION)


.PHONY: deploy
deploy:
	install
	install_venv
	enable_current
	reload
