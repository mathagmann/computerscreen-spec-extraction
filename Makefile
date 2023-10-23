.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	@echo "Running using $(ENV_PREFIX)"
	@$(ENV_PREFIX)python -V
	@$(ENV_PREFIX)python -m site

.PHONY: install
install:          ## Install the project in dev mode.
	@echo "Don't forget to run 'make virtualenv' if you got errors."
	$(ENV_PREFIX)pip install -e .[dev]
	$(ENV_PREFIX)pre-commit install
	$(ENV_PREFIX)python -m playwright install chromium

.PHONY: fmt
fmt:              ## Format code using ruff & black.
	$(ENV_PREFIX)black specification_extraction/
	$(ENV_PREFIX)black tests/
	$(ENV_PREFIX)ruff --fix specification_extraction
	$(ENV_PREFIX)ruff --fix tests

.PHONY: lint
lint:             ## Run black, ruff linters.
	$(ENV_PREFIX)black --check specification_extraction/
	$(ENV_PREFIX)black --check tests/
	$(ENV_PREFIX)ruff specification_extraction/
	$(ENV_PREFIX)ruff tests/

.PHONY: test
test:	          ## Run tests and generate coverage report.
	$(ENV_PREFIX)pytest --cov
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage html

.PHONY: clean
clean:            ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build

.PHONY: virtualenv
virtualenv:       ## Create a virtual environment.
	@echo "creating virtualenv ..."
	@rm -rf .venv
	@python3 -m venv .venv
	@./.venv/bin/pip install -U pip
	@./.venv/bin/pip install -e .[dev]
	@echo
	@echo "!!! Please run 'source .venv/bin/activate' to enable the environment !!!"

.PHONY: release
release:          ## Create a new tag for release.
	@echo "WARNING: This operation will create a version tag and push to github"
	@read -p "Version? (provide the next x.y.z semver): " TAG
	@echo "$${TAG}" > specification_extraction/VERSION
	@$(ENV_PREFIX)gitchangelog > HISTORY.md
	@git add specification_extraction/VERSION HISTORY.md
	@git commit -m "release: version $${TAG}"
	@echo "creating git tag: $${TAG}"
	@git tag $${TAG}
	@git push -u origin HEAD --tags
	@echo "Github Actions will detect the new tag and release the new version."

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@$(ENV_PREFIX)mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL || open $$URL
