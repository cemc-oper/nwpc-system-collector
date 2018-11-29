# coding: utf-8
from concurrent import futures
import time
import logging

import click
import grpc

from nwpc_ecflow_collector.ecflow_status_collector import collect_status
from nwpc_ecflow_collector.server.proto import ecflow_collector_pb2_grpc, ecflow_collector_pb2

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='[%Y-%m-%d %H:%M:%S]',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class EcflowCollectorService(ecflow_collector_pb2_grpc.EcflowCollectorServicer):
    def __init__(self):
        pass

    def CollectStatus(self, request, context):
        owner = request.owner
        repo = request.repo
        host = request.host
        port = request.port

        config_file_path = request.config
        if len(config_file_path) == 0:
            config_file_path = None

        post_url = request.post_url
        content_encoding = request.content_encoding
        disable_post = request.disable_post
        verbose = request.verbose

        logger.info('CollectStatus: {owner}/{repo}...'.format(owner=owner, repo=repo))
        collect_status(
            owner, repo, host, port, config_file_path,
            disable_post, post_url, content_encoding,
            verbose
        )
        logger.info('CollectStatus: {owner}/{repo}...Done'.format(owner=owner, repo=repo))

        return ecflow_collector_pb2.Response(
            status="ok"
        )


@click.command()
@click.option('-t', '--rpc-target', help='rpc-target', default="[::]:50051")
@click.option('-n', '--workers-num', help='max workers number', default=5, type=int)
def serve(rpc_target, workers_num):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers_num))
    ecflow_collector_pb2_grpc.add_EcflowCollectorServicer_to_server(
        EcflowCollectorService(), server)
    server.add_insecure_port('{rpc_target}'.format(rpc_target=rpc_target))
    logger.info('listening on {rpc_target}'.format(rpc_target=rpc_target))
    logger.info('starting server...')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logger.info('warm stop...')
        server.stop(0)
        logger.info('warm stop...done')


if __name__ == "__main__":
    serve()
