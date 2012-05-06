#coding: utf-8
from setuptools import setup, find_packages

requirements = open('pip-requirements.txt').read().split('\n')

desc = open('README.rst').read()

setup(
    name='fuedf',
    version='0.9.0',
    description='Small web app for following energy consumptions',
    long_description=desc,
    author='Brice Vissière',
    author_email='brahici@gmail.com',
    licence='BSD',
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'License :: OSI Approved :: BSD License',
    ],
    url='https://github.com/brahici/fuEDF',
    install_requires=requirements,
    tests_require=requirements,
    packages=find_packages(),
    include_package_data=True,
    scripts=['runfuedf.py',],
    test_suite='fuedf_tests',
)
