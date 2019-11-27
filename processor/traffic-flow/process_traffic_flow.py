#########################################################
# @names process_illegal_parking.py
# @author Chia Hsin Hsu
#
# @params input       Input Pulsar topic
# @params output      Output Pulsar topic
# @params url         Pulsar service url
# @params debug       debug mode when debug=1, default=0
#
#########################################################
import argparse
import cv2
import numpy as np
import pulsar
from pulsar import MessageId
from pulsar.schema import *
import time
import mxnet as mx
import ast
import configparser

class Frame(Record):
    timestamp = String()
    img = Bytes()

class YOLOFrame(Record):
    timestamp = String()
    processed_img = Bytes()
    detections = String()

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
    help="pulsar topic to input streaming video")
ap.add_argument("-o", "--output", required=True,
    help="pulsar topic to output streaming video")
ap.add_argument("-u", "--url", required=True,
    help="url for pulsar broker")
ap.add_argument("--debug", default=0)

args = vars(ap.parse_args())

INPUT_TOPIC = args['input']
OUTPUT_TOPIC = args['output']
PULSAR_URL = args['url']
DEBUG = args['debug']

############################################################
# 1. Connect to Pulsar and create 
# 2. Initial YoloDetector to use Yolov3
############################################################
debug = DEBUG
client = pulsar.Client(PULSAR_URL)
if(debug):	print("[Info] Create Client to " + PULSAR_URL)

reader = client.create_reader(
                                topic=INPUT_TOPIC,  
                                start_message_id=MessageId.latest, 
                                receiver_queue_size=5000,
                                schema=AvroSchema(YOLOFrame)
                                )

producer = client.create_producer(
                topic=OUTPUT_TOPIC,
                schema=AvroSchema(YOLOFrame))


state = 0
now_time = time.time()
start_parking_time = time.time()
hasChecked = False
carIn = 0
carOut = 0
totalCarIn = 0
totalCarOut = 0
Up = 0
Down = 0
x_left = (499-442)/392*416
x_right = (814-442)/392*416
y_up = (459-232)/392*416
y_middle = (489-232)/392*416
y_down = (519-232)/392*416
day = -1

print("[Info] start sending data")

while True:
    try:
        #############################################################
        # Get Input Streaming data
        # 1. Read data from Pulsar
        # 2. Decode img from bytes to numpy.ndarray
        #############################################################
        prev = time.time()
        msg = reader.read_next()
        #print(msg.publish_timestamp())
        time1 = time.time()

        #Make carIn and carOut be zero when the day is changing
        _l = time.localtime()
        print(day, _l[7], _l)
        if(day != _l[7]+1 and _l[3]==16):
            print("Another day!")
            day = _l[7]+1
            carIn = 0
            carOut = 0

        if(debug): print("[Time] read from pulsar {}".format(1/(time1-prev)))
        time2 = time.time()
        
        detections = ast.literal_eval(msg.value().detections)
        img_ndarray = mx.image.imdecode(msg.value().processed_img)
        frame = img_ndarray.asnumpy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        time3 = time.time()
        if(debug): print("[Time] imdecode from bytes to numpy.ndarray{}".format(1/(time3-time2)))

        time2 = time.time()
        hasCar = 0
        
        #cv2.line(frame, (int(x_left), int(y_middle)), (int(x_right), int(y_middle)), (0,0,255), 2)
        length_of_detections = len(detections)
        for detection in detections:
            object_name = detection[0].decode("utf-8") 
            if(debug): print(object_name)
            if(object_name != 'car' and object_name !='truck' and object_name!='bus'):  continue
            x = detection[2]
            y = detection[3]
            w = detection[4]
            h = detection[5]
            xmin = int(round(x - (w / 2)))
            xmax = int(round(x + (w / 2)))
            ymin = int(round(y - (h / 2)))
            ymax = int(round(y + (h / 2)))
            pt1 = (xmin, ymin)
            pt2 = (xmax, ymax)
            cv2.rectangle(frame, pt1, pt2, (0, 0, 255), 4)
            _x = (xmin + xmax)/2
            _y = (ymax + ymin)/2
            if(_x>x_left and _x<x_right and _y < y_down and _y >= y_middle): 
                Down = Down + 1
                hasCar = hasCar + 1
            elif(_x>x_left and _x<x_right and _y < y_middle and _y > y_up): 
                Up = Up + 1
                hasCar = hasCar + 1

        if(hasChecked == False and hasCar != 0 and Down != 0 and Up != 0 and Down != Up):
            if(Down > Up):
                hasChecked = True
                carIn = carIn + 1
                totalCarIn = totalCarIn + 1
            else:
                hasChecked = True
                carOut = carOut + 1
                totalCarOut = totalCarOut + 1

        if(hasCar == 0):
            hasChecked = False
            Down = 0
            Up = 0

        time3 = time.time()
        if(debug): print("[Time] detect {} in {} FPS".format(length_of_detections,1/(time3-time2)))
        
        numberOfCars = 0
        if(carIn - carOut > 0): numberOfCars = carIn - carOut
        
        
        text = "# of Cars: {}".format(numberOfCars)
        cv2.putText(frame, text, (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)

        #########################################################################
        # Produce processed message to Pulsar
        # 1. Encode frame(numpy.ndarray) to jpg 
        # 2. Initialize message
        # 3. Produce it to Pular
        #########################################################################
        d = str(carIn) + " " + str(carOut) + " " + str(totalCarIn) + " " + str(totalCarOut)
        ret, jpeg = cv2.imencode('.jpg', frame)
        _t = msg.value().timestamp
        print(_t, ": ", text)
        
        _Y = YOLOFrame(timestamp=_t,
                        processed_img=jpeg.tobytes(),
                        detections=d)
        producer.send(_Y)

        
        if(debug): print("send data")
        time2 = time.time()
        if(debug): print("[Time] send data to pulsar {}".format(1/(time2-time3)))
        cv2.waitKey(1)
        print(f'Fps {time.asctime( time.localtime(time.time()) )} {1/(time.time() - prev)}')
    except Exception as e:
        print(e)
        pass
    