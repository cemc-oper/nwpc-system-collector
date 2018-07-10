# coding=utf-8
import json
from datetime import datetime, timedelta
import gzip

import click
import yaml
import requests
import ecflow

from nwpc_workflow_model.ecflow import Bunch, NodeStatus


def get_config(config_file_path):
    with open(config_file_path) as config_file:
        config = yaml.load(config_file)
        return config


@click.group()
def cli():
    pass


@cli.command()
@click.option('--owner', '-o', help='owner name')
@click.option('--repo', '-r', help='repo name')
@click.option('--host', help='ecflow host, ECF_HOST')
@click.option('--port', help='ecflow port, ECF_PORT')
@click.option('--config', '-c', 'config_file_path', help='config file path')
def show(owner, repo, host, port, config_file_path):
    client = ecflow.Client(host, port)
    client.sync_local()
    defs = client.get_defs()

    if defs is None:
        print("The server has no definition")
        return

    nodes = defs.get_all_nodes()

    bunch = Bunch()

    for node in nodes:
        node_path = node.get_abs_node_path()
        node_name = node.name()
        node_status = NodeStatus(str(node.get_dstate()))
        node = {
            'path': node_path,
            'status': node_status,
            'name': node_name
        }
        bunch.add_node_status(node)

    bunch.status = NodeStatus(str(defs.get_state()))

    print(json.dumps(bunch.to_dict(), indent=2))


@cli.command()
@click.option('--owner', '-o', help='owner name')
@click.option('--repo', '-r', help='repo name')
@click.option('--host', help='ecflow host, ECF_HOST')
@click.option('--port', help='ecflow port, ECF_PORT')
@click.option('--config', '-c', 'config_file_path', help='config file path', required=True)
@click.option('--disable-post', is_flag=True, help='disable post to agent', default=False)
@click.option('--verbose', is_flag=True, help='show more outputs', default=False)
def collect(owner, repo, host, port, config_file_path, disable_post, verbose):

    config = get_config(config_file_path)

    client = ecflow.Client(host, port)
    client.sync_local()
    defs = client.get_defs()

    if defs is None:
        print("The server has no definition")
        return

    nodes = defs.get_all_nodes()

    bunch = Bunch()

    for node in nodes:
        node_path = node.get_abs_node_path()
        node_name = node.name()
        node_status = NodeStatus(str(node.get_dstate()))
        node = {
            'path': node_path,
            'status': node_status,
            'name': node_name
        }
        bunch.add_node_status(node)

    bunch.status = NodeStatus(str(defs.get_state()))
    bunch_dict = bunch.to_dict()

    current_time = (datetime.utcnow() + timedelta(hours=8)).isoformat()  # 北京时间
    result = {
        'app': 'ecflow_status_collector',
        'type': 'ecflow_status',
        'timestamp': current_time,
        'data': {
            'owner': owner,
            'repo': repo,
            'ecflow_host': host,
            'ecflow_port': port,
            'time': current_time,
            'status': bunch_dict
        }
    }

    post_data = {
        'message': json.dumps(result)
    }

    if not disable_post:
        if verbose:
            print("Posting sms status...")
        host = config['post']['host']
        port = config['post']['port']
        url = config['post']['url'].format(host=host, port=port)

        if 'content-encoding' in config['post']['headers']:
            content_encoding = config['post']['headers']['content-encoding']
        else:
            content_encoding = ''

        if content_encoding == 'gzip':
            gzipped_data = gzip.compress(bytes(json.dumps(post_data), 'utf-8'))

            requests.post(url, data=gzipped_data, headers={
                'content-encoding': 'gzip'
            })
        else:
            requests.post(url, data=post_data)

        if verbose:
            print("Posting sms status...done")


if __name__ == "__main__":
    cli()
