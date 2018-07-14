"""Setup.py."""
from setuptools import find_packages
from setuptools import setup

setup(
    name='5yncr-Backend',
    version='0.0.1',
    packages=find_packages(),
    license='AGPLv3',
    author="Matthew Bentley, Brett Johnson, David Lance, "
        "Jack LaRue, Alexander Tryjankowski",
    author_email="syncr@mtb.wtf",
    description="5yncr is a peer to peer file sync app",
    url="https://github.com/5yncr/",
    project_urls={
        "Bug Tracker": "https://github.com/5yncr/main/issues",
        "Documentation": "https://syncr.readthedocs.io",
        "Source Code": "https://github.com/5yncr",
    },
    entry_points={
        'console_scripts': [
            'check_drop = syncr_backend.bin.check_drop:main',
            'drop_init = syncr_backend.bin.drop_init:main',
            'sync_drop = syncr_backend.bin.sync_drop:main',
            'make_dht_configs = syncr_backend.bin.make_dht_configs:main',
            'make_tracker_configs = syncr_backend.bin.make_tracker_configs:main',  # noqa
            'node_init = syncr_backend.bin.node_init:main',
            'run_backend = syncr_backend.bin.run_backend:run_backend',
            'run_dht_server = syncr_backend.bin.run_dht_server:main',
            'new_version = syncr_backend.bin.new_version:main',
            'update_drop = syncr_backend.bin.update_drop:main',
            'check_for_updates = syncr_backend.bin.check_for_updates:main',
        ],
    },
    scripts=[
        'syncr_backend/contrib/bq',
    ],
    install_requires=[
        "aiofiles>=0.3.2",
        "bencode.py>=2.0.0",
        "cachetools>=2.1.0",
        "cryptography>=2.2.2",
        "kademlia>=1.0",
    ],
)
