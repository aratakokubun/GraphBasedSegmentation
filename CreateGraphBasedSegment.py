# -*- coding:utf-8 -*-

from PIL import Image
import numpy as np
from Component import *
from Edge import *
import GraphBasedSegment as gbs
import CreateResultImage as cri

'''
Get or create component if not exist
'''
def fetch_component(target_id, target_row, target_col, mec, img):
  # Add component if not found
  target_component = mec.get_component(target_id)
  if target_component == None:
    target_component = Component(id=target_id, row=target_row, col=target_col, img=img)
    mec.add_component(target_id, target_component)
  return target_component

'''
Search for 4 direction (drow, dcol)
'''
grid_graph_search = [(1, -1), (1, 0), (1, 1), (0, 1)]

'''
Create grid-graph based initailized components.
@param img : np array image
@param mcl : reference object to get the initial merged component list
@param mec : reference object to get the initial merged edge component
'''
def grid_graph_init(img, mcl, mec):
  # y loop
  for row in range(img.shape[0]):
    # x loop
    for col in range(img.shape[1]):
      # Issue unique id for this element
      pixel_id = img.shape[1] * row + col

      pixel_component = fetch_component(pixel_id, row, col, mec, img)
      # Add to merged component list
      mcl.add(pixel_id, pixel_component.get_pixel())

      # Search edges
      for dif in grid_graph_search:
        target_row = row + dif[0]
        target_col = col + dif[1]
        if not (0 <= target_row < img.shape[0] and 0 <= target_col < img.shape[1]):
          continue
        target_id = img.shape[1] * target_row + target_col

        target_component = fetch_component(target_id, target_row, target_col, mec, img)

        # Add edge
        mec.add_edge(pixel_component, target_component)

'''
Create sorted edge by no-decreasing edge weight.
@param mec : meged edge component to create sorted edge with
@return dict(EdgeIdSet, MergedEdge) : Sorted merged edge
'''
def create_sorted_mc(mec):
  org_edge_dict = mec.get_edge_dict()
  return sorted(org_edge_dict.items(), key=lambda x:x[1].get_min_edge().get_difference())

'''
Construct new segmentation from previous segmentation.
'''
def construct_segmentation(mcl, mec, id_set, converted_id_list):
  # Convert ids which is merged
  id1 = id_set.get_id1()
  id2 = id_set.get_id2()
  converted_id1 = converted_id_list.get(id1)
  converted_id2 = converted_id_list.get(id2)

  if converted_id1 == converted_id2:
    return

  id_set = EdgeIdSet(converted_id1, converted_id2)

  if gbs.gbs_is_merge(id_set=id_set, mcl=mcl, mec=mec):
    # merge id2 to id1
    mcl.merge(id_set.get_id2(), id_set.get_id1())
    mec.merge(id_set.get_id2(), id_set.get_id1())
    converted_id_list.add(id_set.get_id2(), id_set.get_id1())

'''
Train graph based segmentation.
'''
def train(img):
  # Initialize segmentation
  mcl = MergedComponentList()
  mec = MergedEdgeComponent()
  grid_graph_init(img = img, mcl = mcl, mec = mec)

  # Train segmentation
  sorted_mc = create_sorted_mc(mec)
  converted_id_list = ConvertedIdList()
  print("edge_len = {0}".format(len(sorted_mc)))
  for phase, mc in enumerate(sorted_mc):
    # mec.get_merged_edge(1241, 1304).print_edges()
    construct_segmentation(mcl=mcl, mec=mec, id_set=mc[0], converted_id_list=converted_id_list)
    if phase % 1000 == 0:
      print("phase = {0}".format(phase))

  # Create image
  # cri.create_monocolor_result(img, mcl, "result.png")
  cri.create_colorized_result(img, mcl, 30, "result.png")


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

'''
Create nn-graph based initailized components.
Create ndim sets of component list and eged list
@param img : np array image
@param mergedComponentLists : reference of empty list to get the result of component list
@param mergedEdgeComponents : reference of empty list to get the result of edge list
'''
def nn_graph_init(img, mergedComponentLists, mergedEdgeComponents):
  # FXIME
  # Write NN-graph code

  # Merged Component List 
  mergedComponentLists = list()
  mergedEdgeComponents = list()

  for n in range(img.ndim):
    mcl = MergedComponentList()
    mec = MergedEdgeComponent()
    # y loop
    for row in range(img.shape[0]):
      # x loop
      for col in range(img.shape[1]):
        # Issue unique id for this element
        pixel_id = img.shape[1] * row + col
        # Add to merged component list
        mcl.add(pixel_id, (row, col))

        pixel_component = fetch_component(pixel_id, row, col, mec, img)

        # Search edges
        for dif in grid_graph_search:
          target_row = row + dif[0]
          target_col = col + dif[1]
          target_id = img.shape[1] * target_row + target_col

          target_component = fetch_component(target_id, target_row, target_col, mec, img)

          # Add edge
          edge = Edge(pixel_component, target_component)
          mec.add_edge(edge)

    mergedComponentLists.append(mcl)
    mergedEdgeComponents.append(mec)
