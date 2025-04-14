default: example

example:
	python3 -m autoarchaeologist --excavator examples.excavations.showcase examples/30001393.bin

test:
	@./venv/bin/python3 -m unittest
