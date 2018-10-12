# coding: utf-8
from datetime import datetime
import json

import click

from nwpc_workload_collector.base.connection import get_ssh_client
from nwpc_workload_collector.base.encoder import CollectorJSONEncoder
from nwpc_workload_collector.loadleveler.common.config import get_config
from nwpc_workload_collector.loadleveler.common.llq import get_llq_query_model


@click.command('jobs', short_help='query jobs in slurm')
@click.option('--config-file', help="config file path")
@click.option('--host', help='remote host')
@click.option('--port', help='remote port', type=int, default=22)
@click.option('--user', help='remote user')
@click.option('--password', help='remote password')
@click.option('--show', 'output_style', flag_value='show', default=True)
@click.option('--post', 'output_style', flag_value='post')
def command(config_file, host, port, user, password, output_style):
    config = get_config(config_file)

    auth = {
        'host': host,
        'port': port,
        'user': user,
        'password': password
    }

    client = get_ssh_client(auth)

    query_model = get_llq_query_model(client, config)

    current_time = datetime.utcnow().replace(microsecond=0)

    result = {
        'app': 'nwpc_workload_collector.loadleveler.collector',
        'type': 'command',
        'time': current_time.isoformat(),
        'data': {
            'workload_system': 'loadleveler',
            'collected_time': current_time.isoformat(),
            'type': 'JobListContent',
            'request': {
                'command': 'loadleveler_collector',
                'sub_command': 'jobs',
                'arguments': []
            },
            'response': {
                'items': query_model.to_dict()['items']
            }
        }
    }

    if output_style == 'show':
        print(json.dumps(result, indent=2, cls=CollectorJSONEncoder))
