import numpy as np
import cv2
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import matplotlib.pyplot as plt 
from ar_markers import detect_markers

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
stop sign
"""
def signal(image, path):
    signal_cascade = cv2.CascadeClassifier(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = signal_cascade.detectMultiScale(gray, 1.2, 5)
    if faces is ():
        return 'bad'
    else:
        for (x,y,w,h) in faces:
            if w > 40:
                cv2.rectangle(image, (x,y),(x+w,y+h),(255,0,0),2)
                return 'good'
            else:
                return 'bad'

def ar_left(image):
    cascade = cv2.CascadeClassifier('114_2.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.2, 5)
    if faces is ():
        return 'no'
    else:
        for (x,y,w,h) in faces:
            if w > 45:
                cv2.rectangle(image, (x,y),(x+w,y+h),(255,0,0),2)
                return 'left'
            else:
                return 'no'

def ar_stop(image):
    cascade = cv2.CascadeClassifier('2537_2.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.2, 5)
    if faces is ():
        return 'no'
    else:
        for (x,y,w,h) in faces:
            if w > 45:
                cv2.rectangle(image, (x,y),(x+w,y+h),(255,0,0),2)
                return 'stop'
            else:
                return 'no'


"""  
mask
"""
def select_white(image, white):
    lower = np.uint8([white,white,white])
    upper = np.uint8([255,255,255])
    white_mask = cv2.inRange(image, lower, upper)
    return white_mask


"""  
방향 결정
"""
def first_nonzero(arr, axis, invalid_val=-1):
    arr = np.flipud(arr)   
    mask = arr != 0
    return np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)

def set_path2(image, upper_limit, fixed_center = 'False'):
    height, width = image.shape
    image = image[height-upper_limit:,:]
    height = upper_limit-1
    width = width-1
    center=int(width/2)
    left=0
    right=width       
    
    if not fixed_center:
        center = int((left+right)/2)        
        if image[height][:center].min(axis=0) == 255:
            left = 0
        else:
            left = image[height][:center].argmin(axis=0)
        
        if image[height][center:].max(axis=0) == 0:
            right = width
        else:    
            right = center+image[height][center:].argmax(axis=0)        
        center = int((left+right)/2)  
    
    image = np.flipud(image) # in python3, np.flip(image, axis=0)
    mask = image!= 0
    integral = np.where(mask.any(axis=0), mask.argmax(axis=0), height) 
    
    left_sum = np.sum(integral[left:center])
    right_sum = np.sum(integral[center:right])
    forward_sum = np.sum(integral[center-10:center+10])   
    
    return forward_sum, left_sum, right_sum

def set_path3(image, forward_cri):
    height, width = image.shape
    height = height-1
    width = width-1
    center=int(width/2)
    left=0
    right=width
    
    center = int((left+right)/2)      

    try:
        if image[height][:center].min(axis=0) == 255:
            left = 0
        else:
            left = image[height][:center].argmin(axis=0)    
        if image[height][center:].max(axis=0) == 0:
            right = width
        else:    
            right = center+image[height][center:].argmax(axis=0)  
        center = int((left+right)/2)
        
        # print(int(first_nonzero(image[:,center],0,height)))

        forward = min(int(height),int(first_nonzero(image[:,center],0,height))-1)
        #print(height, first_nonzero(image[:,center],0,height))
        
        left_line = first_nonzero(image[height-forward:height,center:],1, width-center)
        right_line = first_nonzero(np.fliplr(image[height-forward:height,:center]),1, center)
        
        center_y = (np.ones(forward)*2*center-left_line+right_line)/2-center
        center_x = np.vstack((np.arange(forward), np.zeros(forward)))
        m, c = np.linalg.lstsq(center_x.T, center_y, rcond=-1)[0]

    except:
        m = 0
    
    return m, forward
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



if __name__ == '__main__':

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        key = cv2.waitKey(1) & 0xFF
        image = frame.array
        cal_image = undistort(image)
        mask_image = select_white(cal_image, 120)
        rawCapture.truncate(0)
        
        distance = measure()
        left_res = ar_left(cal_image)
        stop_res = ar_stop(cal_image)
        # markers = detect_markers(cal_image)
        # right_res = ''
        # if markers:
        #     for marker in markers:
        #         print("detected",marker.id)
        #         marker.highlite_marker(cal_image)
        #         cv2.imshow("Ar", marker.highlite_marker(cal_image))
        #         if marker.id == 922:
        #             right_res = 'right'
        c = signal(cal_image, './cascade.xml')

        forward_sum, left_sum, right_sum = set_path2(mask_image, 120)
        m, forward_val = set_path3(mask_image, 0.25)

        if forward_val < 25 or forward_sum < 1300 :
            action = 'back'
        elif abs(m)< 0.15 and forward_val > 100: # + forward sum 이용하기
            action = 'forward'
        elif forward_val < 80 and abs(m) < 0.2 and abs(left_sum - right_sum) < 1000 and left_sum < 13000 and right_sum < 13000:
            action = 'uturn'
        elif m > 0 or left_sum > right_sum + 70:
            action = 'left' 
        elif m < 0 or left_sum < right_sum - 70:
            action = 'right'
        
        else:
            action = 'back'

        y1, x1 = mask_image.shape
        x1 = int(x1/2)
        x2 = int(-forward_val * round(m,4) + x1)
        y2 = y1-forward_val
        # cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)  
        cv2.line(mask_image,(x1,y1),(x2,y2),(100),2)
        cv2.imshow('Masked image', mask_image)
        # cv2.imshow('Raw image', cal_image)

        if distance < 15:
            print("obstacle detected")
            stop()

        
        elif left_res == 'left':
            print("ar_left")
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
                    time.sleep(0.5)
                    back()
                    time.sleep(0.3)
                    forward()
                    time.sleep(0.25)
                elif action == 'right':
                    print('right')
                    right()
                    time.sleep(0.5)
                    back()
                    time.sleep(0.3)
                    forward()
                    time.sleep(0.25)
                elif action == 'back':
                    print('back')
                    back()
                    time.sleep(0.2)
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
