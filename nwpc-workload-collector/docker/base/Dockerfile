FROM python:3

LABEL maintainer="perillaroc@gmail.com"

COPY vendor/ /srv/vendor/
COPY nwpc-workload-collector/ /srv/nwpc-workload-collector/

RUN set -ex \
    && cd /srv/vendor/nwpc-hpc-model \
    && pip install . \
    && cd /srv/nwpc-workload-collector \
    && mkdir -p /etc/nwpc-workload-collector \
    && cp nwpc_workload_collector/conf/*.yml /etc/nwpc-workload-collector/ \
    && cd /srv/nwpc-workload-collector \
    && pip install . \
    && pip install .[server] \
    && rm -rf /srv/vendor

WORKDIR /srv/nwpc-workload-collector/nwpc_workload_collector

ENTRYPOINT ["python3"]