# -*- coding:utf-8 -*-

from PIL import Image
import numpy as np
from Component import *

'''
Judge if merging two components.
@param id_set : id set to check merge
@param mcl : Merged Component List
@param mec : Merged Edge Components
@return bool : TRUE if merging two components, else FALSE
'''
def gbs_is_merge(id_set, mcl, mec):
  return gbs_dif(id_set.get_id1(), id_set.get_id2(), mec) < gbs_mint(id_set.get_id1(), id_set.get_id2(), mcl)

'''
Calculate the mimum internal difference between two components.
@param id1 : One of two components to calculate minimum internal difference of boundary
@param id2 : One of two components to calculate minimum internal difference of boundary
@param mcl : Merged Component List
@return float : minimum internal difference between two components
'''
def gbs_mint(id1, id2, mcl):
  mc1 = mcl.get_merged_component(id1)
  mc2 = mcl.get_merged_component(id2)
  return min(gbs_int(mc1)+gbs_tau(mc1), gbs_int(mc2)+gbs_tau(mc2))

'''
Difference method
'''
LUMINANCE = 0
RGB_DIFF = 1

method = LUMINANCE

'''
Calculate the minimum difference of boundary between two components.
THIS PROGRAM ADAPT LUMINANCE AS A DIFFERENCE
@param id1 : One of two components to calculate minimum difference of boundary
@param id2 : One of two components to calculate minimum difference of boundary
@param mec : Merged Edge Components
@return int : minimum difference of boundary
'''
def gbs_dif(id1, id2, mec):
  me = mec.get_merged_edge(id1, id2)
  return me.get_min_edge().get_difference()

'''
Calculate the maximum difference in the componet.
THIS PROGRAM ADAPT LUMINANCE AS A DIFFERENCE
@param mc : merged component to calculate maximum difference in the component
@return int : maximum difference in the component
'''
def gbs_int(mc):
  return mc.get_internal_diff()

'''
Coefficient parameter to calculate threashold
'''
tau_k = 10
'''
Calculate threashold based on the size of the component.
@param mc : merged component to calculate the threashold
@return float : threashold based on the size of the component
'''
def gbs_tau(mc):
  return float(tau_k / mc.get_size())

'''
Calculate luminance
@param rgb : list pf rgb value of the pixel
@return float : luminance
'''
def calc_luminance(rgb):
  if type(rgb): # rgb or rgba
    return 0.298912*rgb[0] + 0.586611*rgb[1] + 0.114478*rgb[2]
  else:
    return rgb # monocolor

'''
Preserve pixel, rgba and value
THIS PROGRAM USES LUMINANCE AS VALUE
'''
class Pixel:

  '''
  Constructer for the pixel object
  @param row : row coordinate of the pixel
  @param col : col coordinate of the pixel
  @param img : numpy array of image
  '''
  def __init__(self, row, col, img):
    self.elem = (row, col)
    self.rgba = img[row][col]
    self.value = calc_luminance(self.rgba)

  def get_elem(self):
    return self.elem

  def get_rgba(self):
    return self.rgba

  def get_value(self):
    return self.value
