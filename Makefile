.PHONY: test
test:
	@pytest -vv

.PHONY: install
install:
	@pip install -e .
