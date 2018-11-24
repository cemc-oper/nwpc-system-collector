# coding=utf-8
import json
import sys
from datetime import datetime, timedelta
import gzip

import click
import yaml
import requests
import ecflow

from nwpc_workflow_model.ecflow import Bunch, NodeStatus

from nwpc_ecflow_collector.ecflow_util import server_util


def get_config(config_file_path):
    with open(config_file_path) as config_file:
        config = yaml.load(config_file)
        return config


def collect_status(owner, repo, host, port, config_file_path, disable_post, post_url, content_encoding, verbose):
    """
    collect ecflow server's status and post it to nmp-broker.

    POST data
    message: json string
        {
            'app': 'ecflow_status_collector',
            'type': 'ecflow_status',
            'timestamp': current_time,
            'data': {
                'owner': owner,
                'repo': repo,
                'server_name': repo,
                'ecflow_host': port,
                'ecflow_port': port,
                'time': current_time,
                'status': bunch_dict
            }
        }
    """
    start_time = datetime.utcnow()
    if config_file_path:
        config = get_config(config_file_path)
    else:
        config = None

    host, port = server_util.get_server_address(host, port)

    client = ecflow.Client(host, port)
    client.sync_local()
    defs = client.get_defs()

    if defs is None:
        print("The server has no definition", file=sys.stderr)
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
            'server_name': repo,
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
            print("Posting ecflow status for {owner}/{repo}...".format(owner=owner, repo=repo))

        if post_url:
            url = post_url.format(owner=owner, repo=repo)
        elif config:
            host = config['post']['host']
            port = config['post']['port']
            url = config['post']['url'].format(
                host=host,
                port=port,
                owner=owner,
                repo=repo
            )
        else:
            raise Exception("post url is not set.")

        if content_encoding is None:
            if config:
                if 'content-encoding' in config['post']['headers']:
                    content_encoding = config['post']['headers']['content-encoding']

        if content_encoding == 'gzip':
            gzipped_data = gzip.compress(bytes(json.dumps(post_data), 'utf-8'))

            requests.post(url, data=gzipped_data, headers={
                'content-encoding': 'gzip'
            })
        else:
            requests.post(url, data=post_data)

        if verbose:
            print("Posting ecflow status for {owner}/{repo}...done".format(owner=owner, repo=repo))

    end_time = datetime.utcnow()
    if verbose:
        print("Collect ecflow status for {owner}/{repo}...used {time}".format(
            owner=owner, repo=repo, time=end_time - start_time))


@click.group()
def cli():
    pass


@cli.command()
@click.option('--owner', '-o', help='owner name')
@click.option('--repo', '-r', help='repo name')
@click.option('--host', help='ecflow host, if not set, use environment variable ECF_HOST')
@click.option('--port', help='ecflow port, ECF_PORT')
@click.option('--config', '-c', 'config_file_path', help='config file path')
def show(owner, repo, host, port, config_file_path):
    host, port = server_util.get_server_address(host, port)

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
@click.option('--owner', '-o', help='owner name', required=True)
@click.option('--repo', '-r', help='repo name', required=True)
@click.option('--host', help='ecflow host, ECF_HOST')
@click.option('--port', help='ecflow port, ECF_PORT')
@click.option('--config', '-c', 'config_file_path', help='config file path')
@click.option('--disable-post', is_flag=True, help='disable post to agent', default=False)
@click.option('--post-url', help='post URL')
@click.option('--gzip', 'content_encoding', flag_value='gzip', help='use gzip to post data.')
@click.option('--verbose', is_flag=True, help='show more outputs', default=False)
def collect(owner, repo, host, port, config_file_path, disable_post, post_url, content_encoding, verbose):
    collect_status(
        owner, repo, host, port, config_file_path,
        disable_post, post_url, content_encoding, verbose
    )


if __name__ == "__main__":
    cli()
