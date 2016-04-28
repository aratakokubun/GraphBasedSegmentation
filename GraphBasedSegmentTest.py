# -*- coding:utf-8 -*-

from PIL import Image
import numpy as np
from Component import *
from Edge import *
import CreateGraphBasedSegment as cgbs

# Load image via PIL
img = np.array(Image.open('images/sample5.jpg'))
# img = np.array(Image.open('images/texture.png'))

# Print image information
print(img.ndim, img.shape)

cgbs.train(img)