FROM nwpcc/ecflow:python

LABEL maintainer="perillaroc@gmail.com"

COPY nwpc-ecflow-collector /srv/nwpc-ecflow-collector/
COPY vendor/ /srv/vendor/

RUN set -ex \
    && cd /srv/vendor/nwpc-hpc-model \
    && pip install . \
    && cd /srv/vendor/nwpc-workflow-model \
    && pip install . \
    && cd /srv/nwpc-ecflow-collector \
    && pip install . \
    && rm -rf /srv/vendor

WORKDIR /srv/nwpc-ecflow-collector/nwpc_ecflow_collector

ENTRYPOINT ["python3"]