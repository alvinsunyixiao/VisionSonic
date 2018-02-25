import logging
logging.basicConfig(level=logging.INFO)

import time
import numpy as np
import cv2
import pyrealsense as pyrs
from pyrealsense.constants import rs_option
from IPython import embed
from filter import filter_img
import audio_module
import darknet as dn

visited_dict = {"dog": {"left": False, "front": False, "right": False},
                    "person": {"left": False, "front": False, "right": False},
                    "beep": {"left_low": False, "left_high": False, "right_low": False, "right_high": False}}

beep_all = set(["left_low", "left_high", "right_low", "right_high"])
person_all = set(["left", "front", "right"])

COLOR_FPS = 60
COLOR_WIDTH = 640
COLOR_HEIGHT = 480

HIGH_BEEP_THRESHOLD = 700

DEPTH_FPS = 60
DEPTH_WIDTH = 320
DEPTH_HEIGHT = 240
SI_X = np.deg2rad(59)
SI_Y = np.deg2rad(46)
K_X = np.tan(SI_X/2)
K_Y = np.tan(SI_Y/2)

depth_stream = pyrs.stream.DepthStream(fps=DEPTH_FPS, width=DEPTH_WIDTH, height=DEPTH_HEIGHT)

color_stream = pyrs.stream.ColorStream(fps=COLOR_FPS, width=COLOR_WIDTH,
height=COLOR_HEIGHT)

net = dn.load_net("../Detection/config/tiny-yolo-voc.cfg",
                  "../Detection/model/tiny-yolo-voc.weights",
                  0)
meta = dn.load_meta("../Detection/config/voc.data")

def array_to_image(arr):
    arr = arr.transpose(2,0,1)
    c = arr.shape[0]
    h = arr.shape[1]
    w = arr.shape[2]
    arr = (arr/255.0).flatten()
    data = dn.c_array(dn.c_float, arr)
    im = dn.IMAGE(w,h,c,data)
    return im

def direction_generator(x, y):
    if x < 416.0 / 3:
        return "left"
    elif x < 416.0 / 3 * 2:
        return "front"
    return "right"

def beep_direction_generator(x, y):
    if x < 416.0 / 2:
        return "left"
    return "right"

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


def naive_avg_distance(frame, x_coo, y_coo):
    return np.mean(frame[y_coo-3:y_coo+3, x_coo-3:x_coo+3])

def convert_z16_to_bgr(frame):
    '''Performs depth histogram normalization

    This raw Python implementation is slow. See here for a fast implementation using Cython:
    https://github.com/pupil-labs/pupil/blob/master/pupil_src/shared_modules/cython_methods/methods.pyx
    '''
    hist = np.histogram(frame, bins=0x10000)[0]
    hist = np.cumsum(hist)
    hist -= hist[0]
    rgb_frame = np.empty(frame.shape[:2] + (3,), dtype=np.uint8)

    zeros = frame == 0
    non_zeros = frame != 0

    f = hist[frame[non_zeros]] * 255 / hist[0xFFFF]
    rgb_frame[non_zeros, 0] = 255 - f
    rgb_frame[non_zeros, 1] = 0
    rgb_frame[non_zeros, 2] = f
    rgb_frame[zeros, 0] = 20
    rgb_frame[zeros, 1] = 5
    rgb_frame[zeros, 2] = 0
    return rgb_frame

def transform(x, y, d):
    y_obj = d
    x_obj = 1.0*d*(x-DEPTH_WIDTH/2)/DEPTH_WIDTH*K_X
    z_obj = 1.0*d*(y-DEPTH_HEIGHT/2)/DEPTH_HEIGHT*K_Y
    return x_obj, y_obj, z_obj

def bound_contours_with_size_filter(filtered_img):
	_, contours, hierarchy = cv2.findContours(filtered_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	#contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 400]
	areas = []
	for i in range(len(contours)):
		areas.append(cv2.contourArea(contours[i]))
	contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 1000]
	if len(contours) <= 2:
	    return contours
	#too many point!
	return contours

with pyrs.Service() as serv:
    with serv.Device(streams=(depth_stream,color_stream)) as dev:

        dev.apply_ivcam_preset(0)

        try:  # set custom gain/exposure values to obtain good depth image
            custom_options = [(rs_option.RS_OPTION_R200_LR_AUTO_EXPOSURE_ENABLED, 1),
                              (rs_option.RS_OPTION_R200_LR_GAIN, 100)]
            dev.set_device_options(*zip(*custom_options))
        except pyrs.RealsenseError:
            pass  # options are not available on all devices

        cnt = 0
        last = time.time()
        smoothing = 0.9
        fps_smooth = DEPTH_FPS
        am = audio_module.audio_module()


        while True:
            cnt += 1
            if (cnt % 30) == 0:
                now = time.time()
                dt = now - last
                fps = 30/dt
                fps_smooth = (fps_smooth * smoothing) + (fps * (1.0-smoothing))
                last = now

            dev.wait_for_frames()
            color_raw = cv2.cvtColor(dev.color, cv2.COLOR_BGR2RGB)
            square = cv2.resize(color_raw, (416, 416))
            im = array_to_image(square)
            dn.rgbgr_image(im)
            r = detect2(net, meta,im)
            #temp_dire_visited_list = []
            #person_to_be_close = []
            for label, confidence, bbox in r:
                #embed()
                if label == "person":
                    print "person cases!"
                    #hardcoded case
                    dire = direction_generator(bbox[0], bbox[1])
                    #temp_dire_visited_list.append(dire)
                    am.play("person", dire)
                        #person_to_be_close.append(dire)
                bbox = np.array(bbox, dtype='int')
                cv2.rectangle(square, (bbox[0]-bbox[2]/2, bbox[1]-bbox[3]/2), (bbox[0]+bbox[2]/2, bbox[1]+bbox[3]/2), (255,0,0), 2)
                cv2.putText(square,
                            label,
                            (bbox[0]-bbox[2]/2, bbox[1]-bbox[3]/2-20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0,0,255),
                            2, cv2.LINE_AA)

            #temp_dire_visited_list = set(temp_dire_visited_list)
            #person_to_be_close = person_all - temp_dire_visited_list
            '''
            for i in person_to_be_close:
                if am.is_active("person", i):
                    #is active and not in current frame
                    am.stop("person", i)
                    visited_dict["person"][i] = False
            '''
            depth_raw = dev.depth
            f_img = filter_img(depth_raw.copy(),1)
            temp_img = f_img.copy()
            temp_img = temp_img.astype('float32') / 0x1000
            temp_img *= 255
            temp_img = temp_img.astype('uint8')
            contours = bound_contours_with_size_filter(temp_img)
            m = [cv2.moments(i) for i in contours]
            m = [(int(i['m10'] / i['m00']), int(i['m01'] / i['m00'])) for i in m]
            temp_img = cv2.cvtColor(temp_img, cv2.COLOR_GRAY2RGB)
            beep_cur_iter_visited_list = []
            for x, y in m:
                cv2.circle(temp_img, (x, y), 6, (0, 0, 255), thickness = 4)
                dire = beep_direction_generator(x, y)
                dire += "_"
                vg_value = naive_avg_distance(depth_raw, x ,y)
                if vg_value < HIGH_BEEP_THRESHOLD:
                    dire += "high"
                else:
                    dire += "low"
                beep_cur_iter_visited_list.append(dire)
                if visited_dict["beep"][dire] == False:
                    am.play("beep", dire)
                    visited_dict["beep"][dire] = True
                else:
                    #already ringing!
                    continue
                #cart_tuple = transform(x,y, depth_raw[y, x])
            beep_cur_iter_visited_list = set(beep_cur_iter_visited_list)
            beep_to_be_closed = beep_all - beep_cur_iter_visited_list
            for dire in beep_to_be_closed:
                if am.is_active("beep", dire):
                    #is active and is not present in current frame
                    am.stop("beep", dire)
                    visited_dict["beep"][dire] = False
            cv2.imshow('gray', temp_img)
            cv2.imshow('color', square)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
                for thread in am.thread_pool:
                    if thread.is_alive():
                        thread.stop()
            elif key & 0xFF == ord('s'):
                np.save('debug', f_img)
            elif key & 0xFF == ord('p'):
                while cv2.waitKey(0) & 0xFF != ord('c'):
                    pass
