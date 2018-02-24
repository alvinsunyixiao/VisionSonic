import numpy as np
import scipy.ndimage.filters as filters
from scipy import ndimage
import cv2
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
	plt.imshow(f_n)
	plt.show()
	return f

def read_from_file(path):
	file = np.load(path)
	print(file)
	#file = file * 255 / file.max() 
	#file[file > file.max() / 6] = 0
	# file[file > 1000] = 0
	plt.imshow(file)
	plt.show()
	return file

def filter_img_gaussian(f, std):
	f = filters.gaussian_filter(f, std)
	#f[f > f.max() / 2] = 0
	#f = f * 255 / 0x100000
	#f = f.astype('uint8')
	#print(f) 
	plt.imshow(f)
	plt.show()
	return f

def find_obstacle(im):
	#f = f * 255 / f.max()
	# f = f.astype('uint8')
	#f_b = cv2.adaptiveThreshold(f, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13, 2)
	#ret,f_b = cv2.threshold(f, 127, 255, cv2.THRESH_BINARY)
	# plt.imshow(f)
	# plt.show()
	#kernel = np.ones((5,5))
	#f = cv2.morphologyEx(f, cv2.MORPH_OPEN, kernel) # cv2.erode(f_b, kernel, iterations=1)
	#print(f_b)
	#plt.pcolormesh(f_b)
	#plt.show()
	return f_b

def filter_img(im, std):
	im[im > 1000] = 0

	img = filter_img_gaussian(im, std)

	mask = (img > im.mean()).astype(np.float)

	img = mask + 0.2 * np.random.randn(*mask.shape)

	binary_img = img > 0.5
	
	#plt.imshow(binary_img)
	#plt.show()

	# Remove small white regions
	open_img = ndimage.binary_opening(binary_img)
	# Remove small black hole
	close_img = ndimage.binary_closing(open_img)
	
	im[close_img == 0] = 0



	return im

#f = read_from_file('debug.npy')
#f = create_test_img(f.shape)
#ff = filter_img(f, 5)
#fb = find_obstacle(ff)
#fff = filter_img(f, 5)
#plt.imshow(fff)
#plt.show()
