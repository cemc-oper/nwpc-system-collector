FROM nwpc/ecflow:python

LABEL maintainer="perillaroc@gmail.com"

RUN apt-get update \
    && apt-get -y install sudo \
    && rm -rf /var/lib/apt/lists/*

COPY vendor /tmp/vendor
COPY nwpc-ecflow-collector /srv/nwpc-ecflow-collector

RUN set -ex \
    && cd /tmp/vendor/nwpc-hpc-model \
    && pip install . \
    && cd /tmp/vendor/nwpc-workflow-model \
    && pip install . \
    && rm -rf /tmp/* \
    && cd /srv/nwpc-ecflow-collector \
    && pip install . \
    && chmod -R go+rx /srv/nwpc-ecflow-collector

WORKDIR /srv/nwpc-ecflow-collector/nwpc_ecflow_collector

ENTRYPOINT ["python3"]