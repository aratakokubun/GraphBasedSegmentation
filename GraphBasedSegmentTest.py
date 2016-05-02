# -*- coding:utf-8 -*-

'''
Sample program of graph based segmentation algorithm
'''

# Import required packages
from PIL import Image
import numpy as np

from SegmentationProcess import *
import GraphBasedSegment as gbs

# Load image via PIL.
src_file = 'images/sample5.jpg'
img = np.array(Image.open(src_file))
# Specify destination output file.
dst = 'result/gbs_ret.png'
# Specify coloring segmentations each of which has top n area. 
top_n = 40
# Specify tau_k parameter optinally.
gbs.tau_k = 1.4

# Print image information
print("file : {0}, shape:{1}".format(src_file, img.shape))

'''
# Initialize SegmentationProcess.
ggs = GridGraphSegmentation(img, dst, top_n)
# Traing the image and output a image file.
ggs.train()
'''

# Initialize SegmentationProcess.
nn = 3
nngs = NearestNeightborGraphSegmentation(img, dst, top_n, nn)
# Traing the image and output a image file.
nngs.train()