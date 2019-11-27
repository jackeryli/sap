import subprocess as sp
import cv2
import numpy as np
import pulsar
from pulsar import MessageId
from pulsar.schema import *
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-r", "--rtmp", required=True,
                                 help="rtmp url")
ap.add_argument("-p", "--pulsar", required=True,
                                 help="pulsar url")
ap.add_argument("-t", "--topic", required=True,
                                 help="pulsar topic")


args = vars(ap.parse_args())

rtmpUrl = args['rtmp']
pulsarUrl = args['pulsar']
topic = args['topic']

class Frame(Record):
    timestamp = String()
    img = Bytes()
class YOLOFrame(Record):
    timestamp = String()
    processed_img = Bytes()
    detections = String()


client = pulsar.Client(pulsarUrl)

reader = client.create_reader(
                                topic=topic,  
                                start_message_id=MessageId.latest, 
                                receiver_queue_size=5000,
                                schema=AvroSchema(YOLOFrame)
                                )

# Get video information
fps = 10
width = 416
height = 416
# ffmpeg command
command = ['ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', "{}x{}".format(width, height),
        '-r', str(fps),
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-f', 'flv', 
        rtmpUrl]


p = sp.Popen(command, stdin=sp.PIPE)
        
# read webcamera
while True:
    msg = reader.read_next()
    #print(msg.value().processed_img)
            
    # process frame
    # your code
    # process frame
   
    # write to pipe
    #print(type(msg.value().processed_img))
    
    #img_ndarray = cv2.imdecode(msg.value().processed_img)

    frame = cv2.imdecode(np.frombuffer(msg.value().processed_img, np.uint8), -1)

    #print(frame)
    #cv2.imshow('Demo', frame)
    cv2.waitKey(3)

    
    p.stdin.write(frame.tostring())
