import datetime

import click

from nwpc_workload_collector.base.connection import get_ssh_client
from nwpc_workload_collector.slurm.common.config import get_config
from nwpc_workload_collector.slurm.common.squeue import get_squeue_query_model


@click.command('jobs', short_help='query jobs in slurm')
@click.option('--config-file', help="config file path")
@click.option('--host', help='remote host')
@click.option('--port', help='remote port', type=int, default=22)
@click.option('--user', help='remote user')
@click.option('--password', help='remote password')
def command(config_file, host, port, user, password):
    config = get_config(config_file)

    auth = {
        'host': host,
        'port': port,
        'user': user,
        'password': password
    }

    client = get_ssh_client(auth)

    query_model = get_squeue_query_model(client, config)

    result = {
        'app': 'nwpc_workload_collector.slurm.collector',
        'type': 'command',
        'time': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        'data': {
            'request': {
                'sub_command': 'jobs',
            },
            'response': {
                'jobs': query_model.to_dict()['items']
            }
        }
    }
    print(result)
