#!/usr/bin/env python
"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = []

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest>=3',
]

setup(
    author="Vsevolod O. Shegolev",
    author_email='v.sheg@icloud.com',
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="traju makes manipulation with MD trajectories using AmberTools a little bit easier",
    entry_points={
        'console_scripts': [
            'traju=traju.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='traju',
    name='traju',
    packages=find_packages(include=['traju', 'traju.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/vsheg/traju',
    version='0.1.0',
    zip_safe=False,
)
