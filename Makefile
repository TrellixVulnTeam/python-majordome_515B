all: test dist

test:
	pytest -s -v --ignore=sandbox/

dist: dist-clean
	python setup.py sdist
	python setup.py bdist_wheel

dist-clean: clean
	rm -rf build/ dist/ *.egg-info
	
clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

upload: dist-clean
	twine upload dist/*

install: dist-clean
	python setup.py install
