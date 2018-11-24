FROM nwpc/ecflow:python

LABEL maintainer="perillaroc@gmail.com"

COPY . /srv/nwpc-system-collector/

VOLUME /etc/nwpc-ecflow-collector

RUN set -ex \
    && cd /srv/nwpc-system-collector/vendor/nwpc-hpc-model \
    && pip install . \
    && cd /srv/nwpc-system-collector/vendor/nwpc-workflow-model \
    && pip install . \
    && cd /srv/nwpc-system-collector \
    && cp -r nwpc-ecflow-collector /srv \
    && cd /srv/nwpc-ecflow-collector \
    && pip install . \
    && rm -rf /srv/nwpc-system-collector

WORKDIR /srv/nwpc-ecflow-collector/nwpc_ecflow_collector

ENTRYPOINT ["python3"]