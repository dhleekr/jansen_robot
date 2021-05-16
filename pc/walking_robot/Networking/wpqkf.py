PORT = 8000

from http.server import BaseHTTPRequestHandler
import socketserver
import json
from readchar import readkey
from sys import argv
from os import environ
import numpy as np
import cv2
from Time import Time

httpd = None
DISPLAY = 'DISPLAY' in environ

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
            if w > 50:
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
            if w > 50:
                cv2.rectangle(image, (x,y),(x+w,y+h),(255,0,0),2)
                return 'left'
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

def edge_detection(image, thres=(100,200), blur=True):
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if blur:
        image = cv2.GaussianBlur(image, (5,5),0)
    return cv2.Canny(image, thres[0], thres[1])


"""  
방향 결정
"""
def first_nonzero(arr, axis, invalid_val=-1):
    arr = np.flipud(arr)   
    mask = arr != 0
    return np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)

def sum_of_zeromask(arr, height, forward):
    mask = arr == 0
    zeromask = np.where(mask, 1, 0)
    left_sum = np.sum(zeromask[height-forward:height, :160])
    right_sum = np.sum(zeromask[height-forward:height, 160:])


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


    if forward_sum < 400:
        result = 'back'
    elif forward_sum > 2200:
        result = 'forward'
    elif forward_sum < 1500 and left_sum < 13000 and right_sum < 13000 and abs(left_sum - right_sum) < 1000:
        result = 'uturn'
    elif left_sum > right_sum + 150:
        result = 'left'
    elif right_sum > left_sum + 150:
        result = 'right'
    else:
        result = 'back'
    return result, forward_sum, left_sum, right_sum


""" 
통신 
"""
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()

        print("Write to stdin")
        # while True:
        data = {"action": self.result[0]}
        print(Time(), 'Sending', data)
        self.wfile.write(
            bytes(json.dumps(data), encoding='utf8'))
        self.wfile.write(b'\n')

        self.finish()
        httpd.shutdown()



    def do_POST(self):
        self.send_response(200)
        # self.send_header("")
        self.end_headers()

        # 이미지 받음
        data = self.rfile.read(int(self.headers['Content-Length']))
        data = np.asarray(bytearray(data), dtype="uint8")
        img = cv2.imdecode(data, cv2.IMREAD_ANYCOLOR)
        masked_img = select_white(img, 120)
        
        """  
        순서 : 거리 -> ar marker -> cascade -> 방향결정
        """
        marker_res = ar_left(img)
        
        c = signal(img, './cascade.xml')

        result, forward_sum, left_sum, right_sum = set_path2(masked_img, 120)

        if DISPLAY:
            cv2.imshow('Masked image', masked_img)
            # cv2.imshow('Raw image', img)
            cv2.waitKey(1)
            pass


        data = {"action": result, "markers" : marker_res, "cascade" : c}
        # data = {"action": result[0]}
        # print(Time(), 'Sending', data)
        print('forward_sum : {}\nleft_sum : {}\nright_sum : {}'.format(forward_sum, left_sum, right_sum))
        self.wfile.write(bytes(json.dumps(data), encoding='utf8'))
        self.wfile.write(b'\n')




if __name__ == '__main__':
    with socketserver.TCPServer(("0.0.0.0", PORT),
                                Handler,
                                bind_and_activate=False) as httpd:
        httpd.server = httpd
        httpd.allow_reuse_address = True
        httpd.server_bind()
        httpd.server_activate()
        print("HTTPServer Serving at port", PORT)
        httpd.serve_forever()