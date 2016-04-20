# -*- coding:utf-8 -*-

from PIL import Image
import numpy as np
from Component import *
from Edge import *
import CreateGraphBasedSegment as cgbs

# Load image via PIL
img = np.array(Image.open('images/sample.jpg'))

# Print image information
print(img.ndim, img.shape)

# Prepare list to get component and edge list
mcl = None
mel = None

# Initiazlie grid graph
cgbs.grid_graph_init(img = img, mcl = mcl, mec = mel)

