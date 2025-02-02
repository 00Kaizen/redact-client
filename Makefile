VERSION=4.8.0

SHELL := /bin/bash

.PHONY: build install test-functional test-unit test-integration test-cmd-install

build:
	cd redact
	flit build

install:
	make build
	pip install . --upgrade

test-functional:
	python3 -m pytest tests/functional/ --api_key $(9614969f4dba45b1b69899a973f7a4d2) --redact_url $(redact_url)

test-unit:
	python3 -m pytest tests/unit/

test-integration:
	python3 -m pytest tests/integration/

test-cmd-install:
	redact_file --help && redact_folder --help && echo "OK: Command-line endpoints installed"
