#!/bin/bash

echo "Pushing to PyPi..."
python setup.py sdist
twine upload dist/*
echo "Done..."
