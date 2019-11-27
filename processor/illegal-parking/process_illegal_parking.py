#########################################################
# @names process_illegal_parking.py
# @author Yen Chun Li, Chia Hsin Hsu
#
# @params input       Input Pulsar topic
# @params output      Output Pulsar topic
# @params url         Pulsar service url
# @params debug       debug mode when debug=1, default=0
#
#########################################################
from IllegalParkingDetector import IllegalParkingDetector
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
# 1.Connect to Pulsar
# 2.Create new reader and producer
############################################################
client = pulsar.Client(PULSAR_URL)
if(DEBUG):	print("[Info] Create Client to " + PULSAR_URL)

reader = client.create_reader(
                                topic=INPUT_TOPIC,  
                                start_message_id=MessageId.latest, 
                                receiver_queue_size=5000,
                                schema=AvroSchema(YOLOFrame)
                                )

producer = client.create_producer(
                topic=OUTPUT_TOPIC,
                schema=AvroSchema(YOLOFrame))


##################################
#  state   |    description
#    0     |  no car parking
#  1~11    |       buffer
#   12     |  illegal parking  
#################################
state = 0
now_time = time.time()
start_parking_time = time.time()

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
        time1 = time.time()
        if(DEBUG): print("[Time] read from pulsar {}".format(1/(time1-prev)))
        time2 = time.time()
        # convert string to array
        detections = ast.literal_eval(msg.value().detections)
        # decode img from bytes to numpy.ndarray
        frame = cv2.imdecode(np.frombuffer(msg.value().processed_img, np.uint8), -1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        time3 = time.time()
        if(DEBUG): print("[Time] {} imdecode from bytes to numpy.ndarray.".format(1/(time3-time2)))

        time2 = time.time()
        

        #############################################################
        # Do illegal-parking detecting
        # 1. Initialize the variables (isIllegalPark, coverRatio) that detector needs
        # 2. Transform the park poly cordinates to proper size and draw it(because we change the size of frames)
        # 3. Iterating the detections and do illegal-parking detecting
        # 4. If detects illegal parking, set isIllegalPark = True and set the coverRatio
        # 5. Put object name and its bounding box on the frame
        #############################################################
        isIllegalPark = False
        coverRatio = 0

        time2 = time.time()
        H = 864/416*1.8
        W = 1152/416*1.8
        
        park_poly = [[755.1129032258066, 544.5322580645161]/np.array([W,H]), [598.2096774193549, 680.7903225806451]/np.array([W,H]), [1436.4032258064517, 821.1774193548388]/np.array([W,H]), [1444.6612903225807, 656.016129032258]/np.array([W,H])]
        park_poly = np.array([park_poly], dtype = np.int32)
        cv2.polylines(frame, park_poly, True, (255,0,0),2)
        length_of_detections = len(detections)
        for detection in detections:
            object_name = detection[0].decode("utf-8") 
            if(DEBUG): print(object_name)
            if(object_name != 'car' and object_name !='truck' !='bus'):  continue
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
            cv2.putText(frame,
                        detection[0].decode() +
                        " [" + str(round(detection[1] * 100, 2)) + "]",
                        (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        [0, 0, 255], 2)

            obj_park = np.array([[[xmin,ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]], dtype = np.int32)
            illegal_park, frame, cover_ratio  = IllegalParkingDetector.detect(frame, park_poly, obj_park)
            if(illegal_park):
                isIllegalPark = True
                coverRatio = cover_ratio

        time3 = time.time()
        if(DEBUG): print("[Time] detect {} in {} FPS".format(length_of_detections,1/(time3-time2)))

        if(state == 0):
            if(isIllegalPark): 
                state = 1
                start_parking_time = time.time()
            else: state = 0
        elif(state <= 11):
            if(isIllegalPark): 
                state = state + 1
            else: state = state - 1
        else:
            if(isIllegalPark):
                now_time = time.time()
                state = 12
            else: state = 11

        # To display how long has the car been parking
        parking_minute = int(int(now_time-start_parking_time) /60)
        parking_second = int(now_time-start_parking_time) - parking_minute*60
        
        #text = "isParking: {} {:.2f} ".format(isIllegalPark, coverRatio)
        text = "Illegal Parking: {}".format(isIllegalPark)
        cv2.putText(frame, text, (10, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
        text2 = "Duration: {} s".format(int(now_time-start_parking_time))
        if(state == 12 and (parking_second>=20 or parking_minute>=1)):
            cv2.putText(frame, text2, (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)

        #########################################################################
        # Produce processed message to Pulsar
        # 1. Encode frame(numpy.ndarray) to jpg 
        # 2. Initialize message
        # 3. Produce it to Pular
        #########################################################################
        if(state != 0 and int(now_time-start_parking_time)>0):  d = str(int(now_time-start_parking_time))
        else:   d = "0"
        ret, jpeg = cv2.imencode('.jpg', frame)
        _t = msg.value().timestamp
        if(DEBUG): print(f'{d} {_t}')
        
        _Y = YOLOFrame(timestamp=_t,
                        processed_img=jpeg.tobytes(),
                        detections=d)
        producer.send(_Y)

        
        if(DEBUG): print("send data")
        if(DEBUG): print(isIllegalPark, coverRatio)
        time2 = time.time()
        if(DEBUG): print("[Time] {} send data to pulsar".format(1/(time2-time3)))
        cv2.waitKey(1)
        if(DEBUG): print(f'Fps {time.asctime( time.localtime(time.time()) )} {1/(time.time() - prev)}')
        print("state: ", state)
        if(state == 12): print("parking time: ", parking_minute, ":", parking_second)
    except Exception as e:
        print(e)
        pass
    