# coding=utf-8

from megaoptim._version import __version__

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


setup(
    name='megaoptim',
    version=__version__,
    description='MegaOptim API Client',
    long_description='Python library for working with the powerful MegaOptim.com Image Optimization RESTful APIs',
    url='https://github.com/megaoptim/megaoptim-python',
    author='IDEOLOGIX Media',
    author_email='info@megaoptim.com',
    license='GPLv3',
    keywords='megaoptim megaoptim.com image optimizer lossless compression lossy gif jpeg',

    packages=find_packages(),

    entry_points={'console_scripts': ['megaoptim = megaoptim.cli.cli:do']},

    install_requires=[
        'requests'
    ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ]
)
