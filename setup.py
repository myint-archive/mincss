#!/usr/bin/env python

import ast

import setuptools


def version():
    """Return version string."""
    with open('mincss/__init__.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with open('README.rst') as readme:
    setuptools.setup(
        name='mincss3k',
        version=version(),
        description='Clears the junk out of your CSS.',
        long_description=readme.read(),
        license='BSD',
        packages=setuptools.find_packages(),
        include_package_data=True,
        zip_safe=False,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
        ],
        install_requires=['lxml', 'cssselect'],
        entry_points={'console_scripts': ['mincss=mincss.main:main']},
        tests_require=['nose'],
        test_suite='tests.test_mincss',
        url='https://github.com/myint/mincss'
    )
