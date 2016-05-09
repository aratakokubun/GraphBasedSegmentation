# -*- coding:utf-8 -*-

from abc import ABCMeta, abstractmethod
from PIL import Image
import numpy as np

from UFGraphBasedSegment import *
from UFEdge import *
import UFCreateResultImage as cri

class UFSegmentationProcess:
  __metaclass__ = ABCMeta

  '''
  Initialize with empty lists.
  @param src_img : source image to process
  @param dst_img : path of an output image
  @param top_n   : color segmentations having top n area
  @param tau_k   : merging super parameter
  '''
  def __init__(self, src_img, dst_img, top_n, tau_k=4.5):
    self.img = src_img
    self.dst_img = dst_img
    self.top_n = top_n
    self.tau_k = tau_k
    self.edge_dict = dict()
    self.component_dict = dict()
    self.root_dict = dict()

  '''
  Get or create UF Component if not exist.
  And create UF Root node if not exist.
  @param target_id  : target id to be fetched
  @param target_row : pixel row on creating new component
  @param target_col : pixel col on creating new component
  @return UFComponent : component specified with the target_id
  '''
  def fetch_component(self, target_id, target_row, target_col):
    # Add component if not found
    if target_id in self.component_dict:
      return self.component_dict[target_id]
    else:
      target_component = UFComponent(row=target_row, col=target_col, img=self.img)
      self.component_dict[target_id] = target_component
      self.root_dict[target_id] = UFRoot(rank=1, min_dif=0, size=1)
      return target_component

  '''
  Abstract method to create graph.
  Implement concrete process at concrete class
  '''
  @abstractmethod
  def init_graph(self):
    pass

  '''
  Train graph based segmentation.
  '''
  def train(self):
    # Initialize segmentation
    self.init_graph()

    # Initialize uf graph based segment with the size of image
    size = self.img.shape[0]*self.img.shape[1]
    ufgbs = UFGraphBasedSegment(size=size, tau_k=self.tau_k, root_dict=self.root_dict)

    # Train segmentation
    sorted_edge = sorted(self.edge_dict.items(), key=lambda item:item[1].get_difference())
    print("edge len = {0}".format(len(sorted_edge)))

    for phase, edge_item in enumerate(sorted_edge):
      id_set = edge_item[0]
      edge = edge_item[1]
      edge_value = edge.get_difference()
      ufgbs.merge(id1=id_set.get_id1(), id2=id_set.get_id2(), edge_value=edge_value)
      # Debug
      if phase % 1000 == 0:
        print("phase = {0}".format(phase))
      # Debug

    # Create image
    cri.create_colorized_result(self.img, ufgbs.get_union_find(), self.top_n, self.dst_img)


'''
Implementation of Segmentation Process with Grid-Graph
'''
class GridGraphSegmentation(UFSegmentationProcess):

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
        pixel_id = create_pixel_id(self.img, row, col)

        pixel_component = self.fetch_component(target_id = pixel_id, target_row = row, target_col = col)

        # Search edges
        for dif in self.grid_graph_search:
          target_row = row + dif[0]
          target_col = col + dif[1]
          if not (0 <= target_row < img_row and 0 <= target_col < img_col):
            continue
          # Issue unique id for this element
          target_id = create_pixel_id(self.img, target_row, target_col)

          target_component = self.fetch_component(target_id = target_id, target_row = target_row, target_col = target_col)

          # Add edge
          uf_edge_id_set = EdgeIdSet(pixel_id, target_id)
          uf_edge = UFEdge(pixel_component, target_component)
          self.edge_dict[uf_edge_id_set] = uf_edge


'''
Implementation of Segmentation Process with Nearest-Neighbor-Graph
'''
class NearestNeightborGraphSegmentation(UFSegmentationProcess):

  '''
  Initialize with empty lists.
  @param src_img : source image to process
  @param dst_img : path of an output image
  @param top_n   : color segmentations having top n area
  @param nn      : nearest neighbor distance
  '''
  def __init__(self, src_img, dst_img, top_n, tau_k=4.5, nn=2):
    UFSegmentationProcess.__init__(self, src_img, dst_img, top_n, tau_k)
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
        pixel_id = create_pixel_id(self.img, row, col)

        pixel_component = self.fetch_component(target_id = pixel_id, target_row = row, target_col = col)

        # Search edges
        for dif in self.nn_graph_search:
          target_row = row + dif[0]
          target_col = col + dif[1]
          if not (0 <= target_row < img_row and 0 <= target_col < img_col):
            continue
          # Issue unique id for this element
          target_id = create_pixel_id(self.img, target_row, target_col)

          target_component = self.fetch_component(target_id = target_id, target_row = target_row, target_col = target_col)

          # Add edge
          uf_edge_id_set = EdgeIdSet(pixel_id, target_id)
          uf_edge = UFEdge(pixel_component, target_component)
          self.edge_dict[uf_edge_id_set] = uf_edge
