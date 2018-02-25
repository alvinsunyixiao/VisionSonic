# Stupid python path shit.
# Instead just add darknet.py to somewhere in your python path
# OK actually that might not be a great idea, idk, work in progress
# Use at your own risk. or don't, i don't care

from scipy.misc import imread
import cv2
import time
import numpy as np

def array_to_image(arr):
    arr = arr.transpose(2,0,1)
    c = arr.shape[0]
    h = arr.shape[1]
    w = arr.shape[2]
    arr = (arr/255.0).flatten()
    data = dn.c_array(dn.c_float, arr)
    im = dn.IMAGE(w,h,c,data)
    return im

def detect2(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
    boxes = dn.make_boxes(net)
    probs = dn.make_probs(net)
    num =   dn.num_boxes(net)
    dn.network_detect(net, image, thresh, hier_thresh, nms, boxes, probs)
    res = []
    for j in range(num):
        for i in range(meta.classes):
            if probs[j][i] > 0:
                res.append((meta.names[i], probs[j][i], (boxes[j].x, boxes[j].y, boxes[j].w, boxes[j].h)))
    res = sorted(res, key=lambda x: -x[1])
    dn.free_ptrs(dn.cast(probs, dn.POINTER(dn.c_void_p)), num)
    return res

import sys, os
sys.path.append(os.path.join(os.getcwd(),'python/'))

import darknet as dn

# Darknet
net = dn.load_net("config/tiny-yolo-voc.cfg", "model/tiny-yolo-voc.weights", 0)
meta = dn.load_meta("config/voc.data")
r = dn.detect(net, meta, "data/dog.jpg")
print r

# OpenCV
arr = cv2.imread('debug.jpg')
h, w = arr.shape[0], arr.shape[1]
arr = arr[:, w/2-h/2:w/2+h/2,:]
arr = cv2.resize(arr, (416, 416))
im = array_to_image(arr)
dn.rgbgr_image(im)
st = time.clock()
for i in range(10):
    r = detect2(net, meta, im)
t = time.clock() - st
print 'time consumed per frame:', t / 10
print r
for label, confidence, bbox in r:
    bbox = np.array(bbox,dtype='int')
    #bbox = cv2.boundingBox(bbox)
    cv2.rectangle(arr, (bbox[0]-bbox[2]/2, bbox[1]-bbox[3]/2), (bbox[0]+bbox[2]/2,bbox[1]+bbox[3]/2), (255,0,0), 2)
cv2.imshow('', arr)
cv2.waitKey(0)

