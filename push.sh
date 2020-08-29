#!/bin/bash

echo "Pushing to PyPi..."
python3 setup.py sdist
twine upload dist/*
echo "Done..."
