#!/bin/bash
set -ex -o pipefail

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then

    brew update
    brew upgrade python
    brew install tox || true
    brew link --overwrite tox
    python --version

else

    sudo apt-get update
    sudo apt-get install python
    sudo pip install tox flake8

fi
