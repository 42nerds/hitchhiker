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
	@rm -rf .pytest_cache/ build/
