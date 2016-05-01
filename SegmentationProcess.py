# -*- coding:utf-8 -*-

from abc import ABCMeta, abstractmethod
from PIL import Image
import numpy as np

from Component import *
from Edge import *
import GraphBasedSegment as gbs
import CreateResultImage as cri

class SegmentationProcess:
  __metaclass__ = ABCMeta

  '''
  Initialize with empty lists.
  @param src_img : source image to process
  @param dst_img : path of an output image
  @param top_n   : color segmentations having top n area
  '''
  def __init__(self, src_img, dst_img, top_n):
    self.img = src_img
    self.dst_img = dst_img
    self.top_n = top_n
    self.mcl = MergedComponentList()
    self.mel = MergedEdgeList()
    self.converted_id_list = ConvertedIdList()
    self.cd = dict()

  '''
  Get or create component if not exist.
  @param target_id  : target id to be fetched
  @param target_row : pixel row on creating new component
  @param target_col : pixel col on creating new component
  @return Component : component specified with the target_id
  '''
  def fetch_component(self, target_id, target_row, target_col):
    # Add component if not found
    if target_id in self.cd:
      return self.cd[target_id]
    else:
      target_component = Component(id=target_id, row=target_row, col=target_col, img=self.img)
      self.cd[target_id] = target_component
      return target_component

  '''
  Abstract method to create graph.
  Implement concrete process at concrete class
  '''
  @abstractmethod
  def init_graph(self):
    pass

  '''
  Construct new segmentation from previous segmentation.
  @param id_set : id set to check segmentation
  '''
  def construct_segmentation(self, id_set):
    # Convert ids which is merged
    id1 = id_set.get_id1()
    id2 = id_set.get_id2()
    converted_id1 = self.converted_id_list.get(id1)
    converted_id2 = self.converted_id_list.get(id2)

    if converted_id1 == converted_id2:
      return

    id_set = EdgeIdSet(converted_id1, converted_id2)

    if gbs.gbs_is_merge(id_set=id_set, mcl=self.mcl, mel=self.mel):
      # merge id2 to id1
      self.mcl.merge(id_set.get_id2(), id_set.get_id1())
      self.mel.merge(id_set.get_id2(), id_set.get_id1())
      self.converted_id_list.add(id_set.get_id2(), id_set.get_id1())

  '''
  Train graph based segmentation.
  '''
  def train(self):
    # Initialize segmentation
    self.init_graph()
    # Release dict memory
    self.cd.clear()

    # Train segmentation
    sorted_mc = self.mel.create_sorted_mc()
    print("edge_len = {0}".format(len(sorted_mc)))

    for phase, mc in enumerate(sorted_mc):
      self.construct_segmentation(id_set=mc[0])
      if phase % 1000 == 0:
        print("phase = {0}".format(phase))

    # Create image
    cri.create_colorized_result(self.img, self.mcl, self.top_n, self.dst_img)


'''
Implementation of Segmentation Process with Grid-Graph
'''
class GridGraphSegmentation(SegmentationProcess):

  '''
  Search for 4 direction (drow, dcol)
  '''
  grid_graph_search = [(1, -1), (1, 0), (1, 1), (0, 1)]

  '''
  Create grid-graph based initailized components.
  '''
  def init_graph(self):
    img_row = self.img.shape[0]
    img_col = self.img.shape[1]

    # y loop
    for row in range(img_row):
      # x loop
      for col in range(img_col):
        # Issue unique id for this element
        pixel_id = img_col * row + col

        pixel_component = self.fetch_component(target_id = pixel_id, target_row = row, target_col = col)
        # Add to merged component list
        self.mcl.add(pixel_id, pixel_component.get_pixel())

        # Search edges
        for dif in self.grid_graph_search:
          target_row = row + dif[0]
          target_col = col + dif[1]
          if not (0 <= target_row < img_row and 0 <= target_col < img_col):
            continue
          target_id = img_col * target_row + target_col

          target_component = self.fetch_component(target_id = target_id, target_row = target_row, target_col = target_col)

          # Add edge
          self.mel.add_edge(pixel_component, target_component)


'''
Implementation of Segmentation Process with Nearest-Neighbor-Graph
'''
class NearestNeightborGraphSegmentation(SegmentationProcess):

  '''
  Initialize with empty lists.
  @param src_img : source image to process
  @param dst_img : path of an output image
  @param top_n   : color segmentations having top n area
  @param nn      : nearest neighbor distance
  '''
  def __init__(self, src_img, dst_img, top_n, nn=2):
    SegmentationProcess.__init__(self, src_img, dst_img, top_n)
    # Limit maximum nn to size/4
    img_row = self.img.shape[0]
    img_col = self.img.shape[1]
    self.nn = min(nn, min(img_row/4, img_col/4))
    self.nn_graph_search = list()

    self.init_nn()

  '''
  Define nearest neighbor.
  '''
  def init_nn(self):
    for row in range(0, self.nn+1):
      for col in range(self.nn, -self.nn, -1):
        # Check if the cell is in the range nn
        if sqrt(row**2+col**2) > self.nn:
          continue
        # Check if not base point
        if row == 0 and col == 0:
          continue
        self.nn_graph_search.append((row, col))
        print((row, col))

  '''
  Create grid-graph based initailized components.
  '''
  def init_graph(self):
    img_row = self.img.shape[0]
    img_col = self.img.shape[1]

    # y loop
    for row in range(img_row):
      # x loop
      for col in range(img_col):
        # Issue unique id for this element
        pixel_id = img_col * row + col

        pixel_component = self.fetch_component(target_id = pixel_id, target_row = row, target_col = col)
        # Add to merged component list
        self.mcl.add(pixel_id, pixel_component.get_pixel())

        # Search edges
        for dif in self.nn_graph_search:
          target_row = row + dif[0]
          target_col = col + dif[1]
          if not (0 <= target_row < img_row and 0 <= target_col < img_col):
            continue
          target_id = img_col * target_row + target_col

          target_component = self.fetch_component(target_id = target_id, target_row = target_row, target_col = target_col)

          # Add edge
          self.mel.add_edge(pixel_component, target_component)


'''
Preserve converted id (from, to)
'''
class ConvertedIdList:

  '''
  Initialize with empty dict(from: to)
  '''
  def __init__(self):
    self.converted_id = dict()

  '''
  Add new convert list
  '''
  def add(self, from_id, to_id):
    # If to in dict matches with from_id, convert it to to_id.
    changed_cand = list()
    for dict_from, dict_to in self.converted_id.items():
      if dict_to == from_id:
        changed_cand.append(dict_from)

    # Convert id
    for dict_from in changed_cand:
      self.converted_id[dict_from] = to_id

    # Append new id
    self.converted_id[from_id] = to_id

  '''
  Get converted id if exist.
  @param from_id : id to search
  @return int : id to be converted from from_id
  '''
  def get(self, from_id):
    return self.converted_id.get(from_id, from_id)
