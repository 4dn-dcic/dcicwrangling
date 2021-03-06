.PHONY: test

configure:  # does any pre-requisite installs
	pip install poetry

lint:
	flake8 dcicwrangling

build:  # builds
	make configure
	poetry install

test:
	pytest -vv

update:  # updates dependencies
	poetry update

publish:
	commands/publish

help:
	@make info

info:
	@: $(info Here are some 'make' options:)
	   $(info - Use 'make configure' to install poetry, though 'make build' will do it automatically.)
	   $(info - Use 'make lint' to check style with flake8.)
	   $(info - Use 'make build' to install dependencies using poetry.)
	   $(info - Use 'make publish' to publish this library, but only if auto-publishing has failed.)
	   $(info - Use 'make test' to run tests with the normal options we use on travis)
	   $(info - Use 'make update' to update dependencies (and the lock file))
