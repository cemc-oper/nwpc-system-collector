# nwpc-ecflow-collector

A collector for ecflow using in NWPC.

## Introduction

`nwpc-ecflow-collector` contains two collectors:

- status collector: collect all task status in ecflow server.
- node collector: collect node status with node path in ecflow server.

## Requirements

Building ecFlow by ECMWF with python support before installing.

## Installing

Download the latest release from github.

Install `nwpc-workflow-model` in `vendor` directory.

Then install `nwpc_ecflow_collector`:

```
pip install .
```

## Getting started

Run script `ecflow_node_collector.py` or `ecflow_status_collector.py`.

## RPC Server

Run script `nwpc_ecflow_collector/server/ecflow_collector_server.py`.

## Using Docker

### Requirements

`nwpc-ecflow-collector` docker uses `nwpc/ecflow:python` image 
which is build from [`ecflow-docker`](https://github.com/perillaroc/ecflow-docker).
Please make sure you have this image before building.

### Base

Build docker image from project's root directory.

```
docker build --tag nwpc/ecflow-collector:base -f nwpc-ecflow-collector/docker/base/Dockerfile --rm . 
```

Run script `ecflow_node_collector.py` or `ecflow_status_collector.py` using `docker run`.

For example, use the following command to collect server status from ecflow server.

```
sudo docker run -v /some/path/to/conf:/etc/nwpc-ecflow-collector \
    nwpc/ecflow-collector:base \
    ecflow_status_collector.py \
    collect --owner=some_owner --repo=some_repo \
    --host=some_host --port=some_port \
    --config=/etc/nwpc-ecflow-collector/ecflow_status_collector.config.yml \
    --disable-post --verbose
```

### Server

Build ecflow collector server.

```
docker build --tag nwpc/ecflow-collector:server -f nwpc-ecflow-collector/docker/server/Dockerfile --rm . 
```

Run ecflow collector server.

```
docker run --rm nwpc/ecflow-collector:server
```

Default status config file path is `/etc/nwpc-ecflow-collector/ecflow_status_collector.config.yml`.

Default RPC target is `[::]:50051` .
