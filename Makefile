.PHONY: setup demo build check clean distclean

setup:
	./setup.sh --clean

build:
	./build_lab.sh

demo:
	./run_demo.sh

check:
	bash -n setup.sh env.sh build_lab.sh run_demo.sh
	python3 -m compileall -q scripts tests
	@if [ -x .venv/bin/python ]; then .venv/bin/python tests/check_environment.py; fi

clean:
	rm -rf output __pycache__ scripts/__pycache__ tests/__pycache__

distclean: clean
	rm -rf .venv .env
