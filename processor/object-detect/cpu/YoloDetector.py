from darknet import darknet
import os
import numpy as np
import cv2

class YoloDetector:
    def __init__(self, yolo_dir, mode=0):
    
        #darknet.set_gpu(gpu_num)
        self.metaMain = None
        self.netMain = None
        altNames = None
        configPath = None
        weightPath = None
        # Use tiny yolov3
        if(mode == 0):
            configPath = os.path.join(yolo_dir, "cfg/tiny-yolo.cfg")
            weightPath = os.path.join(yolo_dir, "yolov3-tiny.weights")
        # Use yolov3
        elif(mode == 1):
            configPath = os.path.join(yolo_dir, "cfg/yolov3.cfg")
            weightPath = os.path.join(yolo_dir, "yolov3.weights")
        
        metaPath = os.path.join(yolo_dir, "cfg/coco.data")
        if not os.path.exists(configPath):
            raise ValueError("Invalid config path `" +
                                os.path.abspath(configPath)+"`")
        if not os.path.exists(weightPath):
            raise ValueError("Invalid weight path `" +
                                os.path.abspath(weightPath)+"`")
        if not os.path.exists(metaPath):
            raise ValueError("Invalid data file path `" +
                                os.path.abspath(metaPath)+"`")
        if self.netMain is None:
            self.netMain = darknet.load_net_custom(configPath.encode(
                "ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
        if self.metaMain is None:
            self.metaMain = darknet.load_meta(metaPath.encode("ascii"))
        if altNames is None:
            try:
                with open(metaPath) as metaFH:
                    metaContents = metaFH.read()
                    import re
                    match = re.search("names *= *(.*)$", metaContents,
                                        re.IGNORECASE | re.MULTILINE)
                    if match:
                        result = match.group(1)
                    else:
                        result = None
                    try:
                        if os.path.exists(result):
                            with open(result) as namesFH:
                                namesList = namesFH.read().strip().split("\n")
                                altNames = [x.strip() for x in namesList]
                    except TypeError as e:
                        print(e)
                        pass
            except Exception as e:
                print(e)
                pass
        
        self.darknet_image = darknet.make_image(darknet.network_width(self.netMain),
                                        darknet.network_height(self.netMain),3)


    def convertBack(self,x, y, w, h):
        xmin = int(round(x - (w / 2)))
        xmax = int(round(x + (w / 2)))
        ymin = int(round(y - (h / 2)))
        ymax = int(round(y + (h / 2)))
        return xmin, ymin, xmax, ymax


    def cvDrawBoxes(self,detections, img):
        for detection in detections:
            x, y, w, h = detection[2][0],\
                detection[2][1],\
                detection[2][2],\
                detection[2][3]
            xmin, ymin, xmax, ymax = convertBack(
                float(x), float(y), float(w), float(h))
            pt1 = (xmin, ymin)
            pt2 = (xmax, ymax)
            cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
            cv2.putText(img,
                        detection[0].decode() +
                        " [" + str(round(detection[1] * 100, 2)) + "]",
                        (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        [0, 255, 0], 2)
        return img


    ##
    # @params frame bytes or numpy.ndarray
    # @return detections
    def processImgByYolo(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb,
                                (darknet.network_width(self.netMain),
                                darknet.network_height(self.netMain)),
                                interpolation=cv2.INTER_LINEAR)
        self.frame_resized = frame_resized

        darknet.copy_image_from_bytes(self.darknet_image,frame_resized.tobytes())

        detections = darknet.detect_image(self.netMain, self.metaMain, self.darknet_image, thresh=0.25)

        
        return detections

    
