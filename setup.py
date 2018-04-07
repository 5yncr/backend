from distutils.core import setup

setup(
    name='5yncr Backend',
    version='0.0.1',
    packages=[
        'syncr_backend',
        'syncr_backend.util',
        'syncr_backend.metadata',
        'syncr_backend.init',
        'syncr_backend.external_interface',
    ],
    license='AGPLv3',
    scripts=[
        'bin/make_tracker_configs',
        'bin/run_backend',
        'bin/node_init',
        'bin/drop_init',
        'bin/make_tracker_configs',
        'bin/sync_drop',
        'syncr_backend/contrib/bq',
    ],
    install_requires=[
        "aiofiles==0.3.2",
        "alabaster==0.7.10",
        "asn1crypto==0.24.0",
        "aspy.yaml==1.0.0",
        "attrs==17.4.0",
        "Babel==2.5.3",
        "bencode.py==2.0.0",
        "cached-property==1.3.1",
        "cachetools==2.0.1",
        "certifi==2018.1.18",
        "cffi==1.11.4",
        "chardet==3.0.4",
        "coverage==4.5.1",
        "cryptography==2.1.4",
        "docutils==0.14",
        "flake8==3.5.0",
        "identify==1.0.7",
        "idna==2.6",
        "imagesize==1.0.0",
        "Jinja2==2.10",
        "Mako==1.0.7",
        "Markdown==2.4.1",
        "MarkupSafe==1.0",
        "mccabe==0.6.1",
        "mypy==0.560",
        "mypy-extensions==0.3.0",
        "nodeenv==1.2.0",
        "packaging==17.1",
        "pluggy==0.6.0",
        "pre-commit==1.6.0",
        "psutil==5.4.3",
        "py==1.5.2",
        "pycodestyle==2.3.1",
        "pycparser==2.18",
        "pyflakes==1.6.0",
        "Pygments==2.2.0",
        "pyparsing==2.2.0",
        "pytest==3.4.1",
        "pytz==2018.3",
        "PyYAML==3.12",
        "requests==2.18.4",
        "six==1.11.0",
        "snowballstemmer==1.2.1",
        "Sphinx==1.7.2",
        "sphinxcontrib-websupport==1.0.1",
        "tox==2.9.1",
        "typed-ast==1.1.0",
        "urllib3==1.22",
        "virtualenv==15.1.0",
    ],
)
