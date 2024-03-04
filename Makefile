.PHONY: test
test:
	@python3 devrun.py --help
	@pytest -vv --tb=long
	@echo "pytest OK"

.PHONY: coverage
coverage:
	@coverage run --source . -m pytest -vv --tb=long
	@coverage html
	@coverage report -m
	@echo "coverage OK"

.PHONY: type-checking
type-checking:
	@mypy ./hitchhiker --strict --no-warn-unused-ignores
	@echo "mypy OK"

.PHONY: install
install:
	@pip install -e .

.PHONY: distclean
distclean:
	@find . | grep -E "(/__pycache__$$)" | xargs rm -rf
	@rm -rf .mypy_cache/ hitchhiker.egg-info/ hitchhiker/hitchhiker.egg-info/ .pytest_cache/ build/ ./html_docs ./htmlcov .coverage

.PHONY: setup-devcontainer
setup-devcontainer:
	@pip install coverage
	@pip install -e .[release,odoo,test,docs,copier]

.PHONY: docs
docs:
	@pdoc ./hitchhiker -o ./html_docs

.PHONY: lint
lint:
	@flake8 --ignore=E501,W503
	@echo "flake8 OK"
	@pylint --disable=fixme,missing-function-docstring,missing-class-docstring ./hitchhiker # TODO: write more docs so this can be disabled
	@echo "pylint hitchhiker OK"
	@#pylint --disable=missing-function-docstring,missing-class-docstring ./tests # FIXME: please linter in tests/
	@#echo "pylint tests OK"

.PHONY: precommit
precommit: coverage type-checking lint
	@echo "precommit OK"
