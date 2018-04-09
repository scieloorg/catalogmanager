#!/usr/bin/env python
from setuptools import setup, find_packages

requires = [
    'CouchDB>=1.2',
    'Mako>=1.0.7',
    'pyramid>=1.9.1',
    'pyramid-mako>=1.0.2',
    'pyramid_debugtoolbar>=4.4',
    'waitress',
    'lxml',
]

test_requires = ['webtest', 'pytest', 'pytest-cov']
setup_requires = ['pytest-runner']

setup(
    name="catalogmanager",
    version='1.0.0',
    description="",
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    license="BSD 2-clause",
    url="https://github.com/scieloorg/catalogmanager",
    keywords='scielo catalogmanager',
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Operating System :: POSIX :: Linux",
        "Topic :: System",
        "Topic :: Utilities",
    ],
    zip_safe=False,
    extras_require={
        'testing': test_requires,
    },
    setup_requires=setup_requires,
    tests_require=test_requires,
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = catalog_persistence:main',
        ],
    },
)
