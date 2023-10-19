.PHONY: test
test:
	@python3 devrun.py --help
	@pytest -vv --tb=long

.PHONY: coverage
coverage:
	@coverage run --source . -m pytest -vv --tb=long
	@coverage html
	@coverage report -m

.PHONY: type-checking
type-checking:
	@mypy ./hitchhiker --strict

.PHONY: install
install:
	@pip install -e .

.PHONY: distclean
distclean:
	@find . | grep -E "(/__pycache__$$)" | xargs rm -rf
	@rm -rf .pytest_cache/ build/ ./html_docs

.PHONY: setup-devcontainer
setup-devcontainer:
	@pip install coverage
	@python setup.py egg_info
	@pip install `grep -v '^\[' *.egg-info/requires.txt`

.PHONY: docs
docs:
	@pdoc ./hitchhiker -o ./html_docs