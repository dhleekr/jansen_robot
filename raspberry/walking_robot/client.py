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

모터 제어

"""
r_motor_back = 24
r_motor_forward = 22
l_motor_forward = 16
l_motor_back = 18

GPIO_TRIGGER = 10
GPIO_ECHO = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(r_motor_back, GPIO.OUT)
GPIO.setup(r_motor_forward, GPIO.OUT)
GPIO.setup(l_motor_forward, GPIO.OUT)
GPIO.setup(l_motor_back, GPIO.OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
rb_pwm = GPIO.PWM(r_motor_back, 1000)
rf_pwm = GPIO.PWM(r_motor_forward, 1000)
lf_pwm = GPIO.PWM(l_motor_forward, 1000)
lb_pwm = GPIO.PWM(l_motor_back, 1000)
rb_pwm.start(0)
rf_pwm.start(0)
lf_pwm.start(0)
lb_pwm.start(0)

def forward():
    rf_pwm.ChangeDutyCycle(100)
    rb_pwm.ChangeDutyCycle(0)
    lf_pwm.ChangeDutyCycle(100)
    lb_pwm.ChangeDutyCycle(0)

def back():
    rf_pwm.ChangeDutyCycle(0)
    rb_pwm.ChangeDutyCycle(100)
    lf_pwm.ChangeDutyCycle(0)
    lb_pwm.ChangeDutyCycle(100)

def right():
    rf_pwm.ChangeDutyCycle(0)
    rb_pwm.ChangeDutyCycle(100)
    lf_pwm.ChangeDutyCycle(100)
    lb_pwm.ChangeDutyCycle(0)

def left():
    rf_pwm.ChangeDutyCycle(100)
    rb_pwm.ChangeDutyCycle(0)
    lf_pwm.ChangeDutyCycle(0)
    lb_pwm.ChangeDutyCycle(100)

def rf():
    rf_pwm.ChangeDutyCycle(80)
    rb_pwm.ChangeDutyCycle(0)
    lf_pwm.ChangeDutyCycle(100)
    lb_pwm.ChangeDutyCycle(0)

def lf():
    rf_pwm.ChangeDutyCycle(100)
    rb_pwm.ChangeDutyCycle(0)
    lf_pwm.ChangeDutyCycle(80)
    lb_pwm.ChangeDutyCycle(0)

def stop():
    rf_pwm.ChangeDutyCycle(0)
    rb_pwm.ChangeDutyCycle(0)
    lf_pwm.ChangeDutyCycle(0)
    lb_pwm.ChangeDutyCycle(0) 


"""  

초음파 거리

"""
def measure():
   GPIO.output(GPIO_TRIGGER, True)
   time.sleep(0.00001)
   GPIO.output(GPIO_TRIGGER, False)
   start = time.time()
   while GPIO.input(GPIO_ECHO)==0:
      start = time.time()
   while GPIO.input(GPIO_ECHO)==1:
      stop = time.time()
   elapsed = stop-start
   distance = (elapsed * 34300)/2
   return distance


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
    left_res = data['ar_left']
    stop_res = data['ar_stop']
    c = data['cascade']

    # return action
    return action, left_res, stop_res, c


def UploadNumpy(mask_image):

    result, img = cv2.imencode('.jpg', mask_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if not result:
        raise Exception('Image encode error')

    # action = Upload(img.tobytes())
    action, left_res, stop_res, c = Upload(img.tobytes())

    # return action
    return action, left_res, stop_res, c


if __name__ == '__main__':

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        key = cv2.waitKey(1) & 0xFF
        image = frame.array
        cal_image = undistort(image)
        # mask_image = select_white(cal_image, 120)
        # edge_image = edge_detection(cal_image, thres=thres)
        rawCapture.truncate(0)
        # action = UploadNumpy(cal_image)
        action, left_res, stop_res, c = UploadNumpy(cal_image)
    
        distance = measure()

        if distance < 15:
            print("obstacle detected")
            stop()

        elif left_res == 'left':
            print("ar_left")
            forward()
            time.sleep(0.8)
            left()
            time.sleep(0.4)
            back()
            time.sleep(0.15)
            forward()
            time.sleep(0.2)
            left()
            time.sleep(0.4)
            back()
            time.sleep(0.15)
            forward()
            time.sleep(0.2)
            left()
            time.sleep(0.4)
            back()
            time.sleep(0.15)
            forward()
            time.sleep(0.15)
        # elif right_res == 'right':
        #     print("ar_right")
        #     forward()
        #     right()
        #     time.sleep(0.4)
        #     back()
        #     time.sleep(0.15)
        #     forward()
        #     time.sleep(0.15)
        #     right()
        #     time.sleep(0.4)
        #     back()
        #     time.sleep(0.15)
        #     forward()
        #     time.sleep(0.15)
        #     right()
        #     time.sleep(0.4)
        #     back()
        #     time.sleep(0.15)
        #     forward()
        #     time.sleep(0.15)
        #     right()
        #     time.sleep(0.3)
        #     back()
        #     time.sleep(0.1)
        #     forward()
        #     time.sleep(0.1)
        elif stop_res == 'stop':
            print("ar_stop")
            stop()
            time.sleep(5)
            forward()
            time.sleep(1)

        else:
            if c == 'good':
                stime = time.time()
                print("cascade_stop")
                stop()
                time.sleep(5)
                forward()
                time.sleep(0.5)
        
            else: 
                if action == 'forward':
                    print('forward')
                    forward()
                elif action == 'left':
                    print('left')
                    left()
                    time.sleep(0.4)
                    back()
                    time.sleep(0.18)
                    forward()
                elif action == 'right':
                    print('right')
                    right()
                    time.sleep(0.4)
                    back()
                    time.sleep(0.18)
                    forward()
                elif action == 'back':
                    print('back')
                    back()
                elif action == 'uturn':
                    print('uturn')
                    left()
                    time.sleep(0.4)
                    back()
                    time.sleep(0.1)
                    forward()
                    time.sleep(0.1)
                    left()
                    time.sleep(0.4)
                    back()
                    time.sleep(0.1)
                    forward()
                    time.sleep(0.1)
                    left()
                    time.sleep(0.4)
                    back()
                    time.sleep(0.1)
                    forward()
                    time.sleep(0.1)
                    left()
                    time.sleep(0.4)
                    back()
                    time.sleep(0.1)
                    forward()
                    time.sleep(0.1)
                    left()
                    time.sleep(0.4)
                    back()
                    time.sleep(0.1)
                    forward()
                    time.sleep(0.1)
                    left()
                    time.sleep(0.4)
                    back()
                    time.sleep(0.1)
                    forward()
                    time.sleep(0.1)
                    
        
        if key == ord('q'):
            GPIO.cleanup()
            break

        

