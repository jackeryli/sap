# SAP (Streaming Analytics Platform)

## Introduction

* Increasingly more surveillance cameras are being deployed in smart spaces
* Hardware-defined camera analytics are not scalable
* Stream the surveillance videos to data centers for analysis faces bottleneck links between cameras and data center
* We deploy edge servers closer to the surveillance cameras and end-users 

## Implementation

* Pulsar realize our broker.
* Docker deploy and manage on the resources-limited
edge servers.
* Kubernetes deploy, monitor, and manage
containerized applications.
* OpenCV handle surveillance videos.
* YOLO serves as the basis of our video analytics.
* InfluxDB allows us to store and query analytics
results as time-series data.
* Flask is used for the user interface.
* Grafana monitor the status of our overall system

## System Overview

![Architecture](https://i.imgur.com/0AczNMn.png)

## How to Run our platform

Read the [Pulsar installation](docs/pulsar/pulsar-installation.md) guide to know how to make Pulsar running.

Read the [Collector](collector/README.md) guide to know how to collect video stream from rtmp to pulsar.

Read the [Processor](processor/README.md) guide to know how to run the existed analytics.

Read the [Kubernetes installation](docs/kubernetes/k8s-installation.md) guide to know how to run a k8s cluster on serveral computers.











