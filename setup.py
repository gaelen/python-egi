# -*- coding: utf-8 -*-

# standard
from __future__ import absolute_import
from setuptools import setup
import os

# local
from egi import __version__


def main():
    #cwd = os.path.dirname(os.path.abspath(__file__))
    #path = os.path.join(cwd, 'README.txt')
    #readme = open(path, 'rb').read()

    setup(
        name='egi',
        description='',
        #long_description=readme,
        version=__version__,
        #license='Apache 2.0',
        author='Gaelen Hadlett',
        author_email='gaelenh@gmail.com',
        url='https://github.com/gaelenh/python-egi',
        packages=['egi'],
        keywords=['egi', 'netstation', 'pynetstation'],
        classifiers=[
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Unix'
        ]
    )

if __name__ == '__main__':
    main()
