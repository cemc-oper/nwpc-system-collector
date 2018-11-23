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

`nwpc-ecflow-collector` docker uses `nwpc/ecflow:python` image 
which is build from [`ecflow-docker`](https://github.com/perillaroc/ecflow-docker).
Please make sure you have this image before building.

Build docker image from project's root directory.

```
docker build --tag nwpc/ecflow-collector -f nwpc-ecflow-collector/Dockerfile --rm . 
```

Run ecflow collector server.

```
docker run --rm nwpc/ecflow-collector
```

Default status config file path is `/etc/nwpc-ecflow-collector/ecflow_status_collector.config.yml`.

Default RPC target is `[::]:50051` .
