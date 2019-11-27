#! /usr/bin/env python3
import time
import argparse
import threading
import cv2

import pulsar
from pulsar.schema import *

# Schema for the topic 
class Frame(Record):
    timestamp = String()
    img = Bytes()
class FpsFrame(Record):
    timestamp = String()
    fps = Integer()
  
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
                                 help="url of streaming video")
ap.add_argument("-o", "--output", required=True,
    help="pulsar topic to output streaming video")
ap.add_argument("-u", "--url", required=True,
    help="url for pulsar broker")
ap.add_argument("--debug", default=0,
    help="debug mode")
ap.add_argument("-f", "--fps_topic", default="",
    help="fps-topic")

args = vars(ap.parse_args())

print("[Start]")
print("input {}".format(args['input']))
print("output {}".format(args['output']))
print("url {}".format(args['url']))
print("fps topic {}".format(args['fps_topic']))
    
ERROR_MAXCOUNT = 5

INPUT_URL = args['input']
OUTPUT_TOPIC = args['output']
PULSAR_URL = args['url']
DEBUG = args['debug']
FPS_TOPIC = args['fps_topic']

print(FPS_TOPIC)
print(len(FPS_TOPIC))
print(len(FPS_TOPIC)==0)

def create_pulsar_client(pulsar_url, topic_frame, topic_fps, debug):
    """Create Client to Pulsar


    Args:
        pulsar_url: Url of pulsar broker
        frame_topic: A pulsar topic to record raw frame
        fps_topic: A pulsar topic to record fps frame

    Returns:
        frame_producer: pulsar producer object
        fps_producer: pulsar producer object

    Raises:
        IOError: An error occurred accessing the bigtable.Table object.
    """
    return 

CLIENT = pulsar.Client(PULSAR_URL)
if(DEBUG): print("create client")

producer = CLIENT.create_producer(topic=OUTPUT_TOPIC,
                                  schema=AvroSchema(Frame))
if(DEBUG): print("create producer")

if(len(FPS_TOPIC)!=0):
    fps_producer = CLIENT.create_producer(topic=FPS_TOPIC, schema=AvroSchema(FpsFrame))
if(DEBUG): print("create producer for FPS")


class IpcamCapture:
    """
    """
    def __init__(self, URL):
        self.Frame = []
        self.status = False
        self.isstop = False
        self.capture = cv2.VideoCapture(URL)

    def start(self):
        print('ipcam started!')
        threading.Thread(target=self.queryframe, daemon=True, args=()).start()

    def stop(self):
        self.isstop = True
        print('ipcam stopped!')
   
    def getframe(self):
        return self.Frame
        
    def queryframe(self):
        while (not self.isstop):
            self.status, self.Frame = self.capture.read()
        
        self.capture.release()

ipcam = IpcamCapture(INPUT_URL)

ipcam.start()

time.sleep(1)

ERROR_COUNTER = 0

if(DEBUG):  print("Get frame from {}".format(INPUT_URL))
while True:
    try:
        prev_time = time.time()
        image = ipcam.getframe()
        # resize image to 720p
        image = cv2.resize(image,(1280, 720))
        _t = str(round(time.time()*1000))
        # decode image from numpy.array to bytes
        ret, jpeg = cv2.imencode('.jpg', image)
        # send to pulsar
        producer.send(Frame(timestamp=_t, img=jpeg.tobytes()))
        if(DEBUG): print("Produce to {}".format(OUTPUT_TOPIC))
        # Reduce speed to 20 fps
        time.sleep(0.05)
        fps = 1/(time.time()-prev_time)
        if(len(FPS_TOPIC)!=0):
            fps_producer.send(FpsFrame(timestamp=_t, fps=int(fps)))
        if(DEBUG): print("Produce to {}".format(FPS_TOPIC))
        
        print("FPS: {4:.2f}".format(fps))
    except Exception as e:
        print(e)
        ERROR_COUNTER = ERROR_COUNTER + 1
        time.sleep(2)
        if(ERROR_COUNTER >= ERROR_MAXCOUNT):
            break
