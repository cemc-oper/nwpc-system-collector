from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nwpc-workload-collector',

    version='0.2.0',

    description='Collectors for workload systems at NWPC.',
    long_description=long_description,

    url='https://github.com/perillaroc/nwpc-system-collector',

    author='perillaroc',
    author_email='perillaroc@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],

    keywords='nwpc collector loadleveler slurm',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[
        'click',
        'PyYAML',
        'paramiko',
        'requests',
        'nwpc_hpc_model'
    ],

    package_data={
        'nwpc_workload_collector': ['conf/*.yml']
    },

    extras_require={
        'test': ['pytest'],
        'server': [
            'grpcio',
            'googleapis-common-protos'
        ]
    },

    entry_points={
        'console_scripts': [
            'loadleveler_collector=nwpc_workload_collector.loadleveler.collector:cli',
            'slurm_collector=nwpc_workload_collector.slurm.collector:cli',
        ]}
)
