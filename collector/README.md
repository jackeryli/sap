# Stream collector

This docker is designed to collect video stream and produce it to pulsar topic.
If you want to use it, please follow the following steps.

1. Ensure Apache Pulsar is runnning
2. Run the script [here](#run-docker)

## Start Pulsar
```
docker run -itd --name pulsar \
-p 6650:6650 -p 8080:8080 \
-v /home/ycl01/Documents/streaming-analytics-platform/data/pulsar/data:/pulsar/data \
apachepulsar/pulsar:2.4.1 \
bin/pulsar standalone
```

## Run docker

```
docker run -it \
lemonyc/stream_collector \
-i {RTSP_URL} \
-o {PULSAR_TOPIC} \
-u {PULSAR_URL}
```

Args         | Description
-------------|------------------------
-i, --input  | url of streaming video
-o, --output | pulsar topic to output streaming video
-u, --url    | url for pulsar broker

# How to run opencv in python:3.7-slim

[links](https://blog.csdn.net/keineahnung2345/article/details/84299532)

# Unknown problems

We can't activate pulsar and collector in the same script, because Pulsar isn't activated yet when the scripts is about to execute collector.
