# coding: utf-8
from datetime import datetime
import json
import gzip

import click
import requests

from nwpc_workload_collector.base.connection import get_ssh_client
from nwpc_workload_collector.slurm.common.config import get_config
from nwpc_workload_collector.base.encoder import CollectorJSONEncoder
from nwpc_workload_collector.slurm.common.sinfo import get_sinfo_query_model


def collect_queues(config, owner, repo, host, port, user, password,
                   output_style, post_url, content_encoding, verbose):
    auth = {
        'host': host,
        'port': port,
        'user': user,
        'password': password
    }

    client = get_ssh_client(auth)

    query_model = get_sinfo_query_model(client, config)

    current_time = datetime.utcnow().replace(microsecond=0)

    result = {
        'app': 'nwpc_workload_collector.slurm.collector',
        'type': 'command',
        'time': current_time.isoformat(),
        'data': {
            'owner': owner,
            'repo': repo,
            'workload_system': 'slurm',
            'collected_time': current_time.isoformat(),
            'request': {
                'command': 'slurm_collector',
                'sub_command': 'queues',
                'arguments': []
            },
            'response': {
                'items': query_model.to_dict()['items']
            }
        }
    }

    if output_style == 'show':
        show_string = json.dumps(result, indent=2, cls=CollectorJSONEncoder)
        print(show_string)
        return show_string
    elif output_style == 'post':
        if verbose:
            print("Posting slurm jobs for {owner}/{repo}...".format(owner=owner, repo=repo))

        if not post_url:
            raise Exception("post url is not set.")

        post_data = {
            'message': json.dumps(result, cls=CollectorJSONEncoder)
        }

        post_url = post_url.format(owner=owner, repo=repo)

        if content_encoding == 'gzip':
            gzipped_data = gzip.compress(bytes(json.dumps(post_data), 'utf-8'))

            requests.post(post_url, data=gzipped_data, headers={
                'content-encoding': 'gzip'
            })
        else:
            requests.post(post_url, data=post_data)

        if verbose:
            print("Posting slurm jobs for {owner}/{repo}...done".format(owner=owner, repo=repo))

        return None


@click.command('queues', short_help='show queues information in slurm')
@click.option('--config-file', help="config file path")
@click.option('--owner', help='owner name', required=True)
@click.option('--repo', help='repo name', required=True)
@click.option('--host', help='remote host')
@click.option('--port', help='remote port', type=int, default=22)
@click.option('--user', help='remote user')
@click.option('--password', help='remote password')
@click.option('--show', 'output_style', flag_value='show', default=True)
@click.option('--post', 'output_style', flag_value='post')
@click.option('--post-url', help='post url')
@click.option('--gzip', 'content_encoding', flag_value='gzip', help='use gzip to post data.')
@click.option('--verbose', is_flag=True, help='show more outputs', default=False)
def command(config_file, owner, repo, host, port, user, password,
            output_style, post_url, content_encoding, verbose):
    config = get_config(config_file)
    return collect_queues(config, owner, repo, host, port, user, password,
                          output_style, post_url, content_encoding, verbose)
