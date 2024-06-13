test:
	@python3 -m unittest discover
	@python3 -m unittest discover tests/autoarchaologist

default: test
