# coding: utf-8
import grpc
import click

from nwpc_ecflow_collector.server.proto import ecflow_collector_pb2_grpc, ecflow_collector_pb2


@click.group()
def cli():
    pass


@cli.command()
@click.option('--rpc-target', '-t', help='rpc target')
@click.option('--owner', '-o', help='owner name', required=True)
@click.option('--repo', '-r', help='repo name', required=True)
@click.option('--host', help='ecflow host, ECF_HOST')
@click.option('--port', help='ecflow port, ECF_PORT')
@click.option('--disable-post', is_flag=True, help='disable post to agent', default=False)
@click.option('--post-url', help='post URL')
@click.option('--gzip', 'content_encoding', flag_value='gzip', help='use gzip to post data.')
@click.option('--verbose', is_flag=True, help='show more outputs', default=False)
def collect(rpc_target, owner, repo, host, port, disable_post, post_url, content_encoding, verbose):
    status_request = ecflow_collector_pb2.StatusRequest(
        owner=owner,
        repo=repo,
        host=host,
        port=port,
        post_url=post_url,
        content_encoding=content_encoding,
        disable_post=disable_post,
        verbose=verbose
    )

    with grpc.insecure_channel(rpc_target) as channel:
        stub = ecflow_collector_pb2_grpc.EcflowCollectorStub(channel)
        response = stub.CollectStatus(status_request)
        print(response.status)

    return


if __name__ == "__main__":
    cli()
