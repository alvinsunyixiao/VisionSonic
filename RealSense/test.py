import numpy as np
import scipy.ndimage.filters as filters
#import cv2
import matplotlib.pyplot as plt 

def create_test_img(shape):
	width = shape[0]
	height = shape[1]
	x = np.arange(width)
	x = np.repeat(x[None], height, axis=0)
	y = x.T
	f = np.exp(x / x.max() + y / y.max()) # * (np.sin(x / 2) * np.cos(y / 2) + 1)
	print(f)
	for i in range(50):
		wrand = np.random.randint(0, width)
		hrand = np.random.randint(0, height)
		f[wrand,hrand] = np.random.randint(20,30)
	f_n = f / f.max() * 255
	#f_n = f_n.astype('uint8')
	print(f_n)
	plt.pcolormesh(f_n)
	plt.show()
	return f

def read_from_file(path):
	file = np.load(path)
	print(file)
	file = file / file.max() * 255
	plt.pcolormesh(file)
	plt.show()
	return file

def filter_img(f, std):
	f = filters.gaussian_filter(f, std)
	f = f / f.max() * 255
	#f = f.astype('uint8')
	print(f) 
	plt.pcolormesh(f)
	plt.show()
	return f

def find_obstacle(f, threshold):
	f = (f >= threshold)
	print(f)
	plt.pcolormesh(f)
	plt.show()
	return (f)

f = read_from_file('debug.npy')
#f = create_test_img(f.shape)
f = filter_img(f, 3)
find_obstacle(f, f.max() / 5 * 4)