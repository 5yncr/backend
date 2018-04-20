#!/bin/bash
set -ex -o pipefail

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then

    brew update
    brew upgrade python
    brew install tox || true
    brew link --overwrite tox
    python --version

fi
