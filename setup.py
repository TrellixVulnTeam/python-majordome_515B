# -*- coding: utf-8 -*-
""" Setup support. """
from setuptools import setup
from setuptools import find_packages

version = {}
with open('majordome/version.py') as fp:
    exec(fp.read(), version)

setup(
    name=version['name'],
    packages=find_packages(),
    author=version['author'],
    author_email=version['author_email'],
    description=version['description'],
    keywords=version['keywords'],
    version=version['version'],
    install_requires=version['install_requires'],
    package_data=version['package_data'],
    license='MIT',
    url='https://gogs.sprtmonitor.com/walter/majordome',
    download_url='https://gogs.sprtmonitor.com/walter/majordome/archive/0.1.0.tar.gz',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ]
)
