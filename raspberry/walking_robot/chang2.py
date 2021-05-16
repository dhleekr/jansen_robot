# https://www.mixedcontentexamples.com
host = 'MSI:8000'

from http.client import HTTPConnection
import numpy as np
import cv2
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import matplotlib.pyplot as plt 
from sys import argv
import json

PORT = 8000


"""

왜곡 보정

"""
map1 = np.load('map1.npy')
map2 = np.load('map2.npy')

camera = PiCamera()
camera.resolution = (320, 240)
camera.vflip = True
camera.hflip = True
camera.framerate = 30

rawCapture = PiRGBArray(camera, size= (320, 240))
time.sleep(.1)
t = time.time()

def undistort(image):
    h,w = image.shape[:2]
    undistorted_img = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img


"""  

통신

"""
def Upload(body, headers={}):
    conn = HTTPConnection(host)
    conn.request('POST', '/', body=body, headers=headers)
    res = conn.getresponse()
    print('Uploaded to', host, 'with status', res.status)

    chunk = res.readline()
    chunk = chunk[:-1].decode()
    data = json.loads(chunk)
    action = data['action']

    # return action
    return action


def UploadNumpy(mask_image):

    result, img = cv2.imencode('.jpg', mask_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if not result:
        raise Exception('Image encode error')

    # action = Upload(img.tobytes())
    action = Upload(img.tobytes())

    # return action
    return action


if __name__ == '__main__':

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        key = cv2.waitKey(1) & 0xFF
        image = frame.array
        cal_image = undistort(image)
        # mask_image = select_white(cal_image, 120)
        # edge_image = edge_detection(cal_image, thres=thres)
        rawCapture.truncate(0)
        # action = UploadNumpy(cal_image)
        action = UploadNumpy(cal_image)
        print(action)
        
        if key == ord('q'):
            GPIO.cleanup()
            break

        

