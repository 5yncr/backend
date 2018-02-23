all:
	sh -c "tox -e py36,coverage,mypy;\
	flake8 tests syncr_backend;\
	pycodestyle tests syncr_backend"

setup:
	sh -c "virtualenv -p python3 venv;
	source venv/bin/activate;
	pip install -r requirements.txt;
	pre-commit install --install-hooks;"

clean:
