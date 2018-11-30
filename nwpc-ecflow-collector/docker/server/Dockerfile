FROM nwpcc/ecflow-collector:base

LABEL maintainer="perillaroc@gmail.com"

EXPOSE 50051

RUN set -ex \
    && cd /srv/nwpc-ecflow-collector \
    && pip install .[grpc]

WORKDIR /srv/nwpc-ecflow-collector/nwpc_ecflow_collector

ENTRYPOINT ["python3", "server/ecflow_collector_server.py"]

CMD ["--rpc-target=[::]:50051", "--workers-num=5"]