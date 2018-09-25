# coding: utf-8
import os


def get_server_address(host, port):
    if host is None:
        if 'ECF_HOST' not in os.environ:
            raise ValueError('Can\'t find environment variable ECF_HOST.')
        host = os.environ['ECF_HOST']

    if port is None:
        if 'ECF_PORT' not in os.environ:
            raise ValueError('Can\'t find environment variable ECF_PORT.')
        port = os.environ['ECF_PORT']

    return host, port
