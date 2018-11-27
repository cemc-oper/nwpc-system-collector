# coding: utf-8
from concurrent import futures
import time
import json
import logging

import click
import grpc

from nwpc_workload_collector.loadleveler.commands.jobs import collect_jobs
from nwpc_workload_collector.loadleveler.commands.queues import collect_queues
from nwpc_workload_collector.loadleveler.server.proto import (
    loadleveler_collector_pb2, loadleveler_collector_pb2_grpc)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='[%Y-%m-%d %H:%M:%S]',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class LoadLevelerCollectorService(loadleveler_collector_pb2_grpc.LoadLevelerCollectorServicer):
    def __init__(self, config):
        self.config = config

    def CollectJobs(self, request, context):
        owner = request.owner
        repo = request.repo
        host = request.host
        port = request.port
        user = request.user
        password = request.password
        output_style = request.output_style
        post_url = request.post_url
        content_encoding = request.content_encoding
        verbose = request.verbose

        post_url = post_url.format(owner=owner, repo=repo)

        logger.info('CollectJobs: {owner}/{repo}...'.format(owner=owner, repo=repo))

        result = collect_jobs(
            self.config,
            owner, repo,
            host, port, user, password,
            output_style, post_url, content_encoding,
            verbose
        )
        logger.info('CollectStatus: {owner}/{repo}...done'.format(owner=owner, repo=repo))

        response = loadleveler_collector_pb2.Response(
            status="ok"
        )
        if result is not None:
            response.result = json.dumps(result)

        return response

    def CollectQueues(self, request, context):
        owner = request.owner
        repo = request.repo
        host = request.host
        port = str(request.port)
        user = request.user
        password = request.password
        output_style = request.output_style
        post_url = request.post_url
        content_encoding = request.content_encoding
        verbose = request.verbose

        post_url = post_url.format(owner=owner, repo=repo)

        logger.info('CollectJobs: {owner}/{repo}...'.format(owner=owner, repo=repo))

        result = collect_queues(
            self.config,
            owner, repo,
            host, port, user, password,
            output_style, post_url, content_encoding,
            verbose
        )
        logger.info('CollectQueues: {owner}/{repo}...done'.format(owner=owner, repo=repo))

        response = loadleveler_collector_pb2.Response(
            status="ok"
        )
        if result is not None:
            response.result = json.dumps(result)

        return response


@click.command()
@click.option('-t', '--rpc-target', help='rpc-target', default="[::]:50051")
@click.option('-n', '--workers-num', help='max workers number', default=5, type=int)
@click.option('--config', 'config_file_path',
              help="collector's config file path", required=True)
def serve(rpc_target, workers_num, config_file_path):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers_num))

    from nwpc_workload_collector.loadleveler.common.config import get_config
    config = get_config(config_file_path)

    loadleveler_collector_pb2_grpc.add_LoadLevelerCollectorServicer_to_server(
        LoadLevelerCollectorService(config), server)
    server.add_insecure_port('{rpc_target}'.format(rpc_target=rpc_target))
    logger.info('listening on {rpc_target}'.format(rpc_target=rpc_target))
    logger.info('starting loadleveler collector server...')
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
