import math
import numpy as np

origin_x = 160
origin_y = 120
fov_x = 59
fov_y = 46

#input_list[x, y , distance]
def user_alert(input_list):
    retval = np.array([])
    for data in input_list:
        theta, phi = get_angle(data[0], data[1])
        retval.append(to_cartesian(data[2], theta, phi))
    return retval

#[320, 240] ==> origin[160, 120]
def get_angle(x, y):
    theta = ((origin_x - x) / origin_x) * (fov_x /2)
    phi = math.pi - ((origin_y - y) / origin_y) * (for_y/2))
    return theta, phi

def to_cartesian(rou , theta, phi):
    x = rou * math.sin(theta) * math.cos(phi)
    y = rou * math.sin(theta) * math.sin(phi)
    z = rou * math.cos(theta)
    return (x, y, z)
