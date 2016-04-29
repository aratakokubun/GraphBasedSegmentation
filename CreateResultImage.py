# -*- coding:utf-8 -*-

from PIL import Image
import numpy as np
import MakeColor as mcolor

'''
Make monocolor segmented image
@param img  : source image
@param mcl  : merged component list
@param name : result image file name
'''
def create_monocolor_result(img, mcl, name):
  segmented_image = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
  mc_dict = mcl.get_mc_dict()
  mcl_len = len(mc_dict)
  # Apply a color to each component
  iter = 0
  for seg_id, mc in mc_dict.items():
    print("segment : {0}".format(iter))
    mono_value = iter * 255 / mcl_len
    for pixel in mc.get_pixel_list():
      elem = pixel.get_elem()
      segmented_image[elem[0], elem[1]] = mono_value
      print("{0}, {1}".format(elem[0], elem[1]))
    print("=============================")
    iter += 1

  img_raw = Image.fromarray(segmented_image, 'L')
  img_raw.save(name)

'''
Make rgb color segmented image with top n area segment.
@param img  : source image
@param mcl  : merged component list
@param n    : colorize top n are segment
@param name : result image file name
'''
def create_colorized_result(img, mcl, n, name):
  segmented_image = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
  mc_dict = mcl.get_mc_dict()
  # n can not be over size of mc_dict
  mcl_len = len(mc_dict)
  n = min(n, mcl_len)
  # Get top n of sorted dict 
  sorted_mc_dict = sorted(mc_dict.items(), key=lambda x:x[1].get_size(), reverse=True)[:n]
  # Create n colors
  colors = mcolor.create_random_colors(n)
  # Apply a color to each component
  for mc_item, color in zip(sorted_mc_dict, colors):
    seg_id = mc_item[0]
    mc = mc_item[1]
    print("Size : {0}, color : {1}",mc.get_size(), color) 
    for pixel in mc.get_pixel_list():
      elem = pixel.get_elem()
      segmented_image[elem[0], elem[1], 0] = color[0]
      segmented_image[elem[0], elem[1], 1] = color[1]
      segmented_image[elem[0], elem[1], 2] = color[2]

  img_raw = Image.fromarray(segmented_image)
  img_raw.save(name)
