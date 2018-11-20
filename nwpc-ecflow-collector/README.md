# nwpc-ecflow-collector

A collector for ecflow using in NWPC.

## Introduction

`nwpc-ecflow-collector` contains two collectors:

- status collector: collect all task status in ecflow server.
- node collector: collect node status with node path in ecflow server.

## Requirements

Building ecFlow by ECMWF with python support before installing.

## Installing

Download the latest release and install:

```
python setup.py install
```

## Getting started

Run script `ecflow_node_collector.py` or `ecflow_status_collector.py`.

## Docker

Build docker image from project's root directory.

```
docker build --tag nwpc/ecflow-collector -f nwpc-ecflow-collector/Dockerfile --rm . 
```

Run script `ecflow_node_collector.py` or `ecflow_status_collector.py`. Such as

```
docker run --rm nwpc/ecflow-collector ecflow_node_collector.py --help
```
