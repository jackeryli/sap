#! /usr/bin/env python3
import time
import sys
import pulsar
from pulsar import MessageId
from pulsar.schema import *
from gevent.pywsgi import WSGIServer
from gevent import monkey
from flask import Flask, Response, render_template, request, send_file, g, make_response, jsonify
from flask_cors import CORS, cross_origin
import io
import base64
from influxdb import InfluxDBClient
from datetime import datetime, timezone

import timeout_decorator

class Frame(Record):
    timestamp = String()
    img = Bytes()

class YOLOFrame(Record):
    timestamp = String()
    processed_img = Bytes()
    detections = String()

class TextFrame(Record):
    timestamp = String()
    people = String()

reader_dict = {}
client = pulsar.Client('pulsar://140.114.XX.XX:6650')
influx_client = InfluxDBClient('140.114.XX.XX', 8086, 'root', 'root', 'streaming')

client2 = pulsar.Client('pulsar://140.114.XX.XX:6650')

reader2 = None

measurement_dict = {
    'peopleCountPole1': 'amount_of_people',
    'webcamPole1': 'isParking',
    'objWithRectangle7': 'carDetection',
    'trafficFlowPole7': 'carFlowDetection',
    'motorDetectPole1': 'motorbike'
}
measurement_dict2 = {
    'illegal_parking': 'isParking',
    'people_counting': 'amountOfPeople',
    'traffic_flow': 'carFlowDetection'
}
                   
print("start Flask")
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def index():
    return

@app.route('/cursor', methods=['GET'])
@cross_origin()
def cursor_query():
    time = request.args['time']
    topic = request.args['topic']
    query_string = "SELECT cursor FROM {} WHERE time >= '{}' LIMIT 5".format(measurement_dict[topic], time)
    print(query_string)
    result = influx_client.query(query_string)
    
    print(result)
    result = list(result)
    print(result)
    if(len(result) == 0):
        return []
    else:
        return jsonify(result[0])

@app.route('/events', methods=['GET'])
@cross_origin()
def event_query():
    try:
        date = request.args['date']
        value = request.args['value']
        task_type = request.args['type']
        host = request.args['host']

        """
        
        timestamp in influxdb:   1571060750022000128
        timestamp in javascript: 1483326245000
        """
        
        query_string = "SELECT * FROM {} WHERE time >= {} and time <= {} + 1d and host = '{}'".format(measurement_dict2[task_type], date, date, host)
        
        if(task_type == 'illegal_parking'):
            query_string = query_string + ' and value = ' + value

        print(query_string)
        result = influx_client.query(query_string)
        
        #print(result)
        result = list(result)
        #print(result)
        if(len(result) == 0):
            return jsonify([])
        else:
            return jsonify(result[0])
    except TypeError:
        return jsonify([])
'''
@app.route('/chart', methods=['GET'])
@cross_origin()
def time_query():
    result = influx_client.query("SELECT * FROM amount_of_people WHERE time > now() - {} LIMIT 5 ".format(request.args['time']))
    print(result)
    result = list(result)
    print(result)
    if(len(result) == 0):
        return 
    else:
        return jsonify(result[0])
'''

@app.route('/fps', methods=['GET'])
@cross_origin()
def time_query():
    try:
        result = influx_client.query("SELECT time, value FROM collector_fps WHERE host = '{}' and time > now() - 1m ORDER BY time DESC LIMIT 20".format(request.args['pole']))
        print(result)
        result = list(result)
        print(result)
        if(len(result) == 0):
            return jsonify([])
        else:
            return jsonify(result[0])
    except:
        return jsonify([])

@app.route('/video', methods=['GET'])
@cross_origin()
def video_feed():
    #print(reader_dict)
    topic_path = "persistent://" + request.args['tenant'] + '/' + request.args['namespace'] + '/' + request.args['topic']
    #print(topic_path)
    if(request.args['namespace'] == 'raw-video'):    topic_frame = Frame
    elif(request.args['namespace'] == 'processed-video'): topic_frame = YOLOFrame
    elif(request.args['namespace'] == 'text'): topic_frame = TextFrame
    
    if(request.args['cursor'] == 'latest'):  topic_cursor = MessageId.latest
    elif(request.args['cursor'] == 'earliest'): topic_cursor = MessageId.earliest
    else:
        print(request.args['cursor'])
        #result = influx_client.query("SELECT * FROM amount_of_people WHERE time >= '{}' LIMIT 1".format(request.args['cursor']))
        #print(result)
        
        #result = list(result)[0][0]
        #print(result)
        #cursor_string = result['cursor']
        #print(result['time'])
        #print(cursor_string)
        #print(bytes.fromhex(cursor_string))
        #print(MessageId.deserialize(bytes.fromhex(cursor_string)))
        topic_cursor = MessageId.deserialize(bytes.fromhex(request.args['cursor']))
    #print(topic_cursor)

    reader = None
    username = request.args['username']
    if(username in reader_dict.keys() and reader_dict[username]['topic']==topic_path and reader_dict[username]['cursor_name']==request.args['cursor']):
        #print("reader {} {}".format(reader_dict[username]['cursor_name'],reader_dict[username]['topic']))
        reader = reader_dict[username]['reader']
    else:
        print("create reader {} {} {}".format(request.args['cursor'],request.args['namespace'],request.args['topic']))
        if(reader):
            reader.close()
            print("close reader")
            del reader_dict[username]
            time.sleep(10)
        reader_obj = {}
        reader_obj['topic'] = topic_path
        reader_obj['cursor_name'] = request.args['cursor']
        reader_obj['cursor'] = topic_cursor
        reader = client.create_reader(topic=topic_path,  
                                        start_message_id=topic_cursor, 
                                        receiver_queue_size=5000,
                                        schema=AvroSchema(topic_frame)
                                            )  
        reader_obj['reader'] = reader
        reader_dict[username] = reader_obj

    return get_video_stream(username,request.args['namespace'])
        
def get_video_stream(username, namespace):
    try:
        reader = reader_dict[username]['reader']
        prev_time = time.time()
        #time.sleep(1/20)
        #time.sleep(1/30)
        msg = reader.read_next()
        #print(msg.publish_timestamp())
        process_time = time.time()
        reader_dict[username]['reader'] = reader
        print(f'{reader.topic()} {1/(time.time()-prev_time)}')
        if(namespace == 'raw-video'):
            img_bytes = msg.value().img
            base64_bytes = base64.b64encode(img_bytes)
            base64_string = base64_bytes.decode('utf-8')
            return jsonify(img=base64_string,
                            timestamp=msg.value().timestamp)
        elif(namespace == 'processed-video'):
            img_bytes = msg.value().processed_img
            base64_bytes = base64.b64encode(img_bytes)
            base64_string = base64_bytes.decode('utf-8')
            return jsonify(img=base64_string,
                            detections=msg.value().detections,
                            timestamp=msg.value().timestamp)
        elif(namespace == 'text'):
            return jsonify( detections=msg.value().people,
                            timestamp=msg.value().timestamp)
    except Exception as e:
        print(e)

# Get bus
@app.route('/bus', methods=['GET'])
@cross_origin()
@timeout_decorator.timeout(1, use_signals=False)
def bus_dispatching():
    try:
        reader2 = client2.create_reader(
                                topic="persistent://campus-analytics/text/people_compare",  
                                start_message_id=MessageId.latest, 
                                receiver_queue_size=5000,
                                schema=AvroSchema(TextFrame)
                                )
        print("block")
        if not reader2.has_message_available():
            print("Don't have image")
            raise "Error"
        msg = reader2.read_next()
        print(msg)
        
        _string = msg.value().people
        _string = _string.split(" ")

        timestamp = msg.value().timestamp
        reader2.close()
        return jsonify(busStop=_string[0],
                    timestamp=timestamp,
                    p_1 =_string[1],
                    p_8 =_string[2])
    except:
        return ''


if __name__ == "__main__":
    http_server = WSGIServer(('0.0.0.0', 5001), app)
    http_server.serve_forever()



