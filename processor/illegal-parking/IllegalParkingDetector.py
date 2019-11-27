import cv2
import numpy as np

class IllegalParkingDetector():
    def detect(frame, park_poly, obj_box):

        im = np.zeros(frame.shape[:2])
        im1 =np.zeros(frame.shape[:2])
        
        park_poly_mask = cv2.fillPoly(im, park_poly,255)
        obj_box_mask = cv2.fillPoly(im1,obj_box,255)
        
        #cv2.polylines(frame, obj_box, True, (0,255,0),2)
        masked_and = cv2.bitwise_and(park_poly_mask,obj_box_mask)
        #masked_or = cv2.bitwise_or(park_poly_mask,obj_box_mask)
        
        obj_area = np.sum(np.float32(np.greater(obj_box_mask,0)))
        #or_area = np.sum(np.float32(np.greater(masked_or,0)))
        and_area = np.sum(np.float32(np.greater(masked_and,0)))
        
        cover_ratio = and_area / obj_area
        #print("and_area / obj_area : ", IOU)
        if(cover_ratio>0.2):
            return True ,frame, cover_ratio
        else:
            return False ,frame, cover_ratio
