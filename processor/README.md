# Processor

There are different kinds of processor, including
1. illegal-motor
2. illegal-parking
3. object-detect
4. people-counting
5. traffic-flow

They are all wrapping with docker.


## object-detect

We set up an environments which can run YOLO.

### CPU / object-detect


```
docker build -t yolo_processor_cpu .
docker run -it yolo_processor_cpu python3 process_object_detection.py \
-i {PULSAR_TOPIC} \
-o {PULSAR_TOPIC} \
-u {PULSAR_URL}
```

### GPU / object-detect

* Notice: You need to install nvidia-docker if you need gpu support in docker
* Command: -m 0 means that using tiny-yolo
           -m 1 means that using yolov3

```
docker build -t yolo_processor_gpu .
docker run --gpus=all -itd yolo_processor_gpu \
python3 process_object_detection.py \
-i {PULSAR_TOPIC} \
-o {PULSAR_TOPIC} \
-u {PULSAR_URL} \
-m 1
```

## Illegal-parking

This processor is designed to do illegal parking detection.
It will consume data from pulsar topic which is produced by **object-detect**.

```
docker build -t processor-ip .
docker run -it processor-ip python3 process_illegal_parking.py \
-i {PULSAR_TOPIC} \
-o {PULSAR_TOPIC} \
-u {PULSAR_URL}
```

## Traffic-flow 

This processor is designed to do traffic flow detection from a parking lot entrance.
It will consume data from pulsar topic which is produced by **object-detect**.

```
docker build -t processor-tf .
docker run -it processor-tf python3 process_traffic_flow.py \
-i {PULSAR_TOPIC} \
-o {PULSAR_TOPIC} \
-u {PULSAR_URL}
```

## People Counting

This processor is designed to do people counting from a certain area.
The x-axis and y-axis are defined in an *.ini file.
It will consume data from pulsar topic which is produced by **object-detect**.

* Command:
Establish an *.ini first, edit dockerfile to copy it into docker.

```
docker build -t processor-pc .
docker run -it processor-pc python3 process_people_counting.py \
-c camera1
```

## Illegal-motor

This processor is designed to do illegal motor detection from a certain area. 
The x-axis and y-axis are defined in an *.ini file.
It will consume data from pulsar topic which is produced by **object-detect**.

* Command:
Establish an *.ini first, edit dockerfile to copy it into docker.

```
docker build -t processor-im .
docker run -it processor-im python3 process_illegal_motor.py \
-c camera1
```







