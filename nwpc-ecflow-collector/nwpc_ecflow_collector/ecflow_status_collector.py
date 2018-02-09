# coding=utf-8
import json

import click
import ecflow

from nwpc_workflow_model.ecflow import Bunch, NodeStatus


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


if __name__ == "__main__":
    cli()
