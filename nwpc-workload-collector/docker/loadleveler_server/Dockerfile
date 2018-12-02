FROM nwpcc/workload-collect

LABEL maintainer="perillaroc@gmail.com"

WORKDIR /srv/nwpc-workload-collector/nwpc_workload_collector

EXPOSE 50051

ENTRYPOINT ["python3", "loadleveler/server/loadleveler_collector_server.py"]

CMD ["--rpc-target=[::]:50051", \
    "--workers-num=5", \
    "--config=/etc/nwpc-workload-collector/loadleveler.config.yml"]