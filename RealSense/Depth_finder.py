import numpy as np
import matplotlib.pyplot as plt

from scipy import ndimage
im= np.load("debug.npy")
np.set_printoptions(threshold=np.nan)
#print(img)
im[im>600]=0
#print(img)


l = 25
img = ndimage.gaussian_filter(im, sigma=l)

mask = (img > im.mean()).astype(np.float)


img = mask + 0.2*np.random.randn(*mask.shape)

binary_img = img > 0.5

# Remove small white regions
open_img = ndimage.binary_opening(binary_img)
# Remove small black hole
close_img = ndimage.binary_closing(open_img)

im[close_img ==0] = 0
plt.imshow(im)
plt.show()

