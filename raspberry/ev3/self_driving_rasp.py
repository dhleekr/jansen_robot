import socket
from _thread import *
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import numpy as np
import time
import marker

HOST = '192.168.137.33'
PORT = 12345



def undistort(image):
    h,w = image.shape[:2]
    undistorted_img = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img

def threaded(client_socket, addr):
    print('Connected by :', addr[0], ':', addr[1])
    global Loop_state
    global stop_time
    u_list = []
    

    for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port=True):
        try:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                client_socket.close()
                break
            image = frame.array
            raw_image = undistort(image)
            rawCapture.truncate(0)
            black_image, gray_image = make_black(raw_image)

            if time.time()-stop_time > 15: #한번 스탑을 읽으면 15초 이후에 다시 읽을 수 있음
                cas_sign = signal(image, './cascade.xml')

                if cas_sign == 'stop':
                    print('cascade')
                    decision = 'cascade_stop'
                    client_socket.sendall(decision.encode())
                    time.sleep(5)
                    stop_time=time.time()
                    continue

            markers = marker.marker_detect(black_image)
            is_marker =False

            if markers == 114:
                decision = 'l_marker'
                client_socket.sendall(decision.encode())
                is_marker =True

            elif markers == 922:
                decision = 'r_marker'
                client_socket.sendall(decision.encode())
                is_marker =True

            elif markers == 2537:
                decision = 's_marker'
                client_socket.sendall(decision.encode())
                is_marker =True

            if is_marker:
                print(decision)
                continue

            else:
                decision, m, forward_val = set_path3(black_image, 0.25)
                # y1, x1 = black_image.shape
                # x1 = int(x1/2)
                # x2 = int(-forward_val * m + x1)
                # y2 = y1-forward_val
                # cv2.line(black_image,(x1,y1),(x2,y2),(100),2)
                # cv2.imshow('Masked image', black_image)
                # decision = path_decision(black_image)
                print(decision)
                client_socket.sendall(decision.encode())

        except:
            print('except')
            client_socket.close()
            break
    Loop_state=2

def make_black(image, threshold = 90):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    black_image=cv2.inRange(gray_image, threshold, 255)
    return black_image, gray_image

def signal(image, path): #cascade
    signal_cascade = cv2.CascadeClassifier(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = signal_cascade.detectMultiScale(gray, 1.3,5, minSize=(20,20))

    if faces is ():
        return 'no_sign'
    else:
        return 'stop'


def first_nonzero(arr, axis, invalid_val=-1):
    arr = np.flipud(arr)   
    mask = arr != 0
    return np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)

def set_path3(image, forward_criteria):
    height, width = image.shape
    height = height-1
    width = width-1
    center=int(width/2)
    left=0
    right=width
    
    center = int((left+right)/2)        
    try:
        if image[height-40][:center].min(axis=0) == 255:
            left_u = 0
        else:
            left_u = image[height-40][:center].argmin(axis=0)    
        if image[height-40][center:].max(axis=0) == 0:
            right_u = width
        else:    
            right_u = center+image[height-40][center:].argmax(axis=0)


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

        print(left_u, forward, right_u)

        if left_u > 2 and right_u < 317 and forward < 100:
            action = 'u'
        elif forward < 92 and m > 0:
            action = 'l'
        elif forward < 92 and m < 0:
            action = 'r'
        elif forward < 70 and abs(m) < 0.2:
            action = 'b'
        else:
            action = 'f'
            straight_factor = 30
            if left_u > straight_factor:
                action = 'f_r'
            elif right_u < 320 - straight_factor:
                action = 'f_l'

    except:
        action = 'b'
        m = 0
    
    return action, round(m,4), forward

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

print('server start')

map1 = np.load('map1.npy')
map2 = np.load('map2.npy')
camera = PiCamera()
camera.resolution = (320,240)
camera.vflip = True
camera.hflip = True
camera.framerate = 40
rawCapture = PiRGBArray(camera, size =(320,240))
decision = None
Loop_state=1
time.sleep(.1)
stop_time = 0

print('wait')

client_socket, addr = server_socket.accept()
start_new_thread(threaded, (client_socket, addr))

while True:
    if Loop_state==2:
        break
    pass

server_socket.close()