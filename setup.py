from distutils.core import setup

setup(
    name='5yncr Backend',
    version='0.0.1',
    packages=[
        'syncr_backend',
        'syncr_backend.bin',
        'syncr_backend.util',
        'syncr_backend.metadata',
        'syncr_backend.init',
        'syncr_backend.external_interface',
    ],
    license='AGPLv3',
    entry_points={
        'console_scripts': [
            'check_drop = syncr_backend.bin.check_drop:main',
            'drop_init = syncr_backend.bin.drop_init:main',
            'sync_drop = syncr_backend.bin.sync_drop:main',
            'make_tracker_configs = syncr_backend.bin.make_tracker_configs:main',  # noqa
            'node_init = syncr_backend.bin.node_init:main',
            'run_backend = syncr_backend.bin.run_backend:run_backend',
        ],
    },
    scripts=[
        'syncr_backend/contrib/bq',
    ],
    install_requires=[
        "asn1crypto==0.24.0",
        "aspy.yaml==1.0.0",
        "attrs==17.4.0",
        "bencode.py==2.0.0",
        "cached-property==1.3.1",
        "cffi==1.11.4",
        "coverage==4.5.1",
        "cryptography==2.1.4",
        "flake8==3.5.0",
        "identify==1.0.7",
        "idna==2.6",
        "kademlia==1.0",
        "mccabe==0.6.1",
        "mypy==0.560",
        "nodeenv==1.2.0",
        "pluggy==0.6.0",
        "pre-commit==1.6.0",
        "psutil==5.4.3",
        "py==1.5.2",
        "pycodestyle==2.3.1",
        "pycparser==2.18",
        "pyflakes==1.6.0",
        "pytest==3.4.1",
        "PyYAML==3.12",
        "rpcudp==3.0.0",
        "six==1.11.0",
        "tox==2.9.1",
        "typed-ast==1.1.0",
        "u-msgpack-python==2.5.0",
        "virtualenv==15.1.0",
    ],
)
