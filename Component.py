# -*- coding:utf-8 -*-

from PIL import Image
import numpy as np
from GraphBasedSegment import *

'''
Preserve pixel, ids of the component.
'''
class Component:

  '''
  Initialize with one pixel (row, col).
  @param id  : component id
  @param row : row coordinate of the pixel
  @param col : col coordinate of the pixel
  @param img : numpy array of image
  '''
  def __init__(self, id, row, col, img):
    self.id = id
    self.pixel = Pixel(row, col, img)

  '''
  Get pixel of the component.
  @return list(row, col) : pixel list
  '''
  def get_pixel(self):
    return self.pixel

  '''
  Get if this component contains the pixel.
  @return boolean : TRUE if contains the pixel, else FALSE
  '''
  def contain(self, row, col):
    return self.pixel.get_elem()[0] == row and \
     self.pixel.get_elem()[1] == col

  '''
  Get the id of this component.
  @return int : id
  '''
  def get_id(self):
    return self.id

  '''
  Convert id of this component.
  @param id   : id will be changed to this id
  '''
  def set_id(self, to_id):
    self.id = to_id

  '''
  Print content of component
  '''
  def print_component(self):
    print("component :) {0} : {1}".format(self.id, self.pixel))


'''
Preserve merged pixels and max/min of them.
'''
class MergedComponent:

  '''
  Initialize with a pixel.
  @param pixel : pixel of the new merged component
  '''
  def __init__(self, pixel):
    self.pixel_list = list()
    self.pixel_list.append(pixel)
    self.pixel_max = pixel.get_value()
    self.pixel_min = pixel.get_value()

  '''
  Add pixel to the merged pixel list.
  @param added_pixel : a pixel to add to the component
  '''
  def add(self, added_pixel):
    self.pixel_list.append(added_pixel)
    # Update max value pixel
    if self.pixel_max < added_pixel.get_value():
      self.pixel_max = added_pixel.get_value()
    # Update min value pixel
    if self.pixel_min > added_pixel.get_value():
      self.pixel_min = added_pixel.get_value()

  '''
  Merge another merged component to this.
  @param mc : another merged component
  '''
  def merge(self, mc):
    move_pixel_list = mc.get_pixel_list()
    # update list
    self.pixel_list += move_pixel_list
    # update max
    if self.pixel_max < mc.get_max():
      self.pixel_max = mc.get_max()
    # update min
    if self.pixel_min > mc.get_min():
      self.pixel_min = mc.get_min()

  '''
  Get internal difference of the merged component.
  Internal difference is defined as 
  Max Value - Min Value
  @return int : Internal difference
  '''
  def get_internal_diff(self):
    return self.pixel_max - self.pixel_min

  '''
  Get max value pixel.
  @return int : max value pixel
  '''
  def get_max(self):
    return self.pixel_max

  '''
  Get min value pixel.
  @return int : min value pixel
  '''
  def get_min(self):
    return self.pixel_min

  '''
  Get pixel list
  @return list(Pixel) : pixel list
  '''
  def get_pixel_list(self):
    return self.pixel_list

  '''
  Get pixel number size.
  @return int : size
  '''
  def get_size(self):
    return len(self.pixel_list)


'''
Relationship between current components and components merged in them
The format of the dict is (id: pixel_list)
'''
class MergedComponentList:

  '''
  Initialize with empty list.
  '''
  def __init__(self):
    self.mc_dict = dict()

  '''
  Add pixel to specific id.
  @param id : specified component id
  @param pixel : added pixel
  '''
  def add(self, id, pixel):
    if id in self.mc_dict.keys():
      self.mc_dict[id].append(pixel)
    else:
      self.mc_dict[id] = MergedComponent(pixel)

  '''
  Get all merged components.
  @return dict(int, MergedComponent) : all merged component dict
  '''
  def get_mc_dict(self):
    return self.mc_dict

  '''
  Merge pixels of from_id to pixels of to_id
  @param from_id : Edge of this id will be changed to to_id
  @param to_id   : Edge of from_id will be changed to this id
  '''
  def merge(self, from_id, to_id):
    move_mc = self.mc_dict.pop(from_id)
    self.mc_dict[to_id].merge(move_mc)

  '''
  Get the specified merged component
  @param search_id : id of the component to search
  @return MergedComponent : specified merged component
          None if id of the component does not exist
  '''
  def get_merged_component(self, search_id):
    if search_id in self.mc_dict:
      return self.mc_dict[search_id]
    else:
      return None

  '''
  Print list of components
  '''
  def print_list(self):
    print("--- list of components ---")
    for k, v in self.mc_dict.items():
      print("{0} : {1}".format(k, v))
    print("--- list of components ---")
