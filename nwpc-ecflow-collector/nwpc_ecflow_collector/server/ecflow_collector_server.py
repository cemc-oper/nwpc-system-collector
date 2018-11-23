# coding: utf-8
from concurrent import futures
import time
from nwpc_ecflow_collector.ecflow_status_collector import collect_status

import grpc

import ecflow_collector_pb2
import ecflow_collector_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class EcflowCollectorService(ecflow_collector_pb2_grpc.EcflowCollectorServicer):
    def __init__(self):
        pass

    def CollectStatus(self, request, context):
        owner = request.owner
        repo = request.repo
        host = request.host
        port = request.port
        config_file_path = request.config
        post_url = request.post_url
        content_encoding = request.content_encoding
        disable_post = request.disable_post
        verbose = request.verbose

        collect_status(
            owner, repo, host, port, config_file_path,
            disable_post, post_url, content_encoding,
            verbose
        )

        return ecflow_collector_pb2.Response(
            status="ok"
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ecflow_collector_pb2_grpc.add_EcflowCollectorServicer_to_server(
        EcflowCollectorService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
