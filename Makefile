.PHONY: test

clean:
	rm -rf *.egg-info

clear-poetry-cache:  # clear poetry/pypi cache. for user to do explicitly, never automatic
	poetry cache clear pypi --all

configure:  # does any pre-requisite installs
	pip install poetry==1.4.2

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
	# New Python based publish script in dcicutils (2023-04-25).
	poetry run publish-to-pypi

publish-for-ga:
	# New Python based publish script in dcicutils (2023-04-25).
	poetry run publish-to-pypi --noconfirm

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
