#!/usr/bin/env python3
from distutils.core import setup

setup(
        name = 'libarsc',
        packages = ['arsc', 'arsc.type', 'arsc.external'],
        version = '0.2.0',
        description = 'Python library to manipulate resources.arsc files',
        url = 'https://github.com/v3l0c1r4pt0r/libarsc',
        author = 'v3l0c1r4pt0r',
        author_email = 'v3l0c1r4pt0r@gmail.com',
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: Apache Software License',
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        )
