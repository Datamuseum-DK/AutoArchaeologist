default: example

example:
	./venv/bin/python3 run_example.py -d .

test:
	@./venv/bin/python3 -m unittest
