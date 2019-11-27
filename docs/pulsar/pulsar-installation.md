# Pulsar Installation Guide

## Run the docker

```sh
PULSAR_DATA=/data/pulsar
docker run -itd -p 6650:6650 --restart always -p 8080:8080 \
-v $PULSAR_DATA/data:/pulsar/data apachepulsar/pulsar:2.4.1 \
bin/pulsar standalone
```

## Create Pulsar components (Tenant, Namespace)

**Important**: Get into the docker first by using `docker exec`

```sh
bin/pulsar-admin tenants create video-streaming
bin/pulsar-admin namespaces create video-streaming/raw-video
bin/pulsar-admin namespaces create video-streaming/processed-video
bin/pulsar-admin namespaces create video-streaming/text
bin/pulsar-admin namespaces create video-streaming/fps
```

## Limit the usage of each Pulsar topic

**Important**: Get into the docker first by using `docker exec`

```sh
bin/pulsar-admin namespaces set-backlog-quota video-streaming/raw-video --limit 50G --policy consumer_backlog_eviction
bin/pulsar-admin namespaces set-backlog-quota video-streaming/processed-video --limit 50G --policy consumer_backlog_eviction
bin/pulsar-admin namespaces set-backlog-quota video-streaming/text --limit 10G --policy consumer_backlog_eviction
bin/pulsar-admin namespaces set-backlog-quota video-streaming/fps --limit 10G --policy consumer_backlog_eviction
```
