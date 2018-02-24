import logging
logging.basicConfig(level=logging.INFO)

import time
import numpy as np
import cv2
import pyrealsense as pyrs
from pyrealsense.constants import rs_option
from IPython import embed
from filter import filter_img
import stereosound

DEPTH_FPS = 60
WIDTH = 320
HEIGHT = 240
SI_X = np.deg2rad(59)
SI_Y = np.deg2rad(46)
K_X = np.tan(SI_X/2)
K_Y = np.tan(SI_Y/2)

depth_stream = pyrs.stream.DepthStream(fps=DEPTH_FPS, width=WIDTH, height=HEIGHT)

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
    x_obj = 1.0*d*(x-WIDTH/2)/WIDTH*K_X
    z_obj = 1.0*d*(y-HEIGHT/2)/HEIGHT*K_Y
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
    with serv.Device(streams=(depth_stream,)) as dev:

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
        stereo = stereosound.stereosound()

        while True:
            cnt += 1
            if (cnt % 30) == 0:
                now = time.time()
                dt = now - last
                fps = 30/dt
                fps_smooth = (fps_smooth * smoothing) + (fps * (1.0-smoothing))
                last = now

            dev.wait_for_frames()
            frame = dev.depth
            print frame[frame.shape[0] / 2, frame.shape[1] / 2]
            #d = convert_z16_to_bgr(frame)
            #cv2.putText(d, str(fps_smooth)[:4], (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255))

            #cv2.imshow('', d)
            f_img = filter_img(frame.copy(),1)
            temp_img = f_img.copy()
            temp_img = temp_img.astype('float32') / 0x1000
            temp_img *= 255
            temp_img = temp_img.astype('uint8')
            contours = bound_contours_with_size_filter(temp_img)
            m = [cv2.moments(i) for i in contours]
            m = [(int(i['m10'] / i['m00']), int(i['m01'] / i['m00'])) for i in m]
            #print contours
            temp_img = cv2.cvtColor(temp_img, cv2.COLOR_GRAY2RGB)
            #cv2.drawContours(temp_img, contours, -1, (0, 0, 255), 3)
            for x, y in m:
                cv2.circle(temp_img, (x, y), 6, (0, 0, 255), thickness = 4)
                cart_tuple = transform(x,y, frame[y, x])
                avg_value = naive_avg_distance(frame, x ,y)
                stereo.play(cart_tuple, avg_value)
            #cv2.imshow('1', f_img.astype('float32') / 0x1000)
            #cv2.imshow('2', frame.astype('float32') / 0x1000)
            cv2.imshow('3', temp_img)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            elif key & 0xFF == ord('s'):
                np.save('debug', f_img)
            elif key & 0xFF == ord('p'):
                while cv2.waitKey(0) & 0xFF != ord('c'):
                    pass
