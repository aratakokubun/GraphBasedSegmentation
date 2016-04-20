# -*- coding:utf-8 -*-

from PIL import Image
import numpy as np
from Component import *
from Edge import *

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
  mcl = MergedComponentList()
  mec = MergedEdgeComponent()
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
