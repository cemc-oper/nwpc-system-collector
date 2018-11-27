# coding: utf-8
import grpc
import click

from nwpc_workload_collector.loadleveler.server.proto import (
    loadleveler_collector_pb2_grpc, loadleveler_collector_pb2)


@click.group()
def cli():
    pass


@cli.command()
@click.option('--rpc-target', '-t', help='rpc target')
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
def jobs(rpc_target, owner, repo,
         host, port, user, password,
         output_style, post_url, content_encoding, verbose):

    jobs_request = loadleveler_collector_pb2.JobsRequest(
        owner=owner,
        repo=repo,
        host=host,
        port=port,
        user=user,
        password=password,
        output_style=output_style,
        post_url=post_url,
        content_encoding=content_encoding,
        verbose=verbose
    )

    with grpc.insecure_channel(rpc_target) as channel:
        stub = loadleveler_collector_pb2_grpc.LoadLevelerCollectorStub(channel)
        response = stub.CollectJobs(jobs_request)
        print(response.status)

    return


@cli.command()
@click.option('--rpc-target', '-t', help='rpc target')
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
def queues(rpc_target, owner, repo,
           host, port, user, password,
           output_style, post_url, content_encoding, verbose):
    queues_request = loadleveler_collector_pb2.QueuesRequest(
        owner=owner,
        repo=repo,
        host=host,
        port=port,
        user=user,
        password=password,
        output_style=output_style,
        post_url=post_url,
        content_encoding=content_encoding,
        verbose=verbose
    )

    with grpc.insecure_channel(rpc_target) as channel:
        stub = loadleveler_collector_pb2_grpc.LoadLevelerCollectorStub(channel)
        response = stub.CollectQueues(queues_request)
        print(response.status)

    return


if __name__ == "__main__":
    cli()
