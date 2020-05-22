#!/bin/bash

version=$1

sudo pip3 uninstall megaoptim
rm -rf dist/megaoptim-$version.tar.gz
python3 setup.py sdist
sudo pip3 install dist/megaoptim-$version.tar.gz
