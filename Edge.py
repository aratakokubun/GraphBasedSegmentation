# -*- coding:utf-8 -*-

from PIL import Image
import numpy as np
from math import *
import sys

'''
Preserve pair of edge pixels between two components
'''
class Edge:

  '''
  Initialize with components.
  @note ids of comp1 and comp2 are different.
  @param comp1 : One of the interested components
  @param comp2 : One of the interested components
  '''
  def __init__(self, comp1, comp2):
    self.comp1 = comp1
    self.comp2 = comp2
    self.diff = abs(self.comp1.get_pixel().get_value() - self.comp2.get_pixel().get_value())

  '''
  Get ids of the intereseted components.
  @return tupple : (id1, id2)
  '''
  def get_ids(self):
    return (self.comp1.get_id(), self.comp2.get_id())

  '''
  Get edge pixels between interested components.
  @return tupple : (pixel1, pixel2)
  '''
  def get_edge_pixels(self):
    return (self.comp1.get_pixel(), self.comp2.get_pixel())

  '''
  Get difference value between the componennts
  @return int : difference between the components
  '''
  def get_difference(self):
    return self.diff

  '''
  Print content of edge
  '''
  def print_edge(self):
    print("edge :) {0} with {1}"
      .format(self.comp1.get_pixel().get_elem(), self.comp2.get_pixel().get_elem()))


'''
Preserve edges and min of them between two components 
'''
class MergedEdge:

  '''
  Initialize with a edge.
  @param edge : initial edge of this merged edge list
  '''
  def __init__(self, edge):
    self.edge_list = [edge]
    self.min_edge = edge

  '''
  Add edge to the list
  @param edge : edge to be added
  '''
  def add(self, edge):
    self.edge_list.append(edge)
    # update min edge
    if self.min_edge.get_difference() > edge.get_difference():
      self.min_edge = edge

  '''
  Get merged edge list.
  @return list(Edge) : merged edge list
  '''
  def get_merged_edge_list(self):
    return self.edge_list

  '''
  Get minimum difference edge.
  @return Edge : min edeg
  '''
  def get_min_edge(self):
    return self.min_edge

  '''
  Get list of edges.
  @return list(Edge) : list of edges
  '''
  def get_edge_list(self):
    return self.edge_list

  '''
  Merge another merged edge to this.
  @param me : merged edge to be merged
  '''
  def merge(self, me):
    self.edge_list += me.get_edge_list()
    # update min edge
    if self.min_edge.get_difference() > me.get_min_edge().get_difference():
      self.min_edge = me.get_min_edge()

  '''
  Print edges in the edge list.
  '''
  def print_edges(self):
    for e in self.edge_list:
      e.print_edge()

'''
Preserve two ids of edge components.
This class is used to edge key of dictionary.
DO NOT CHANGE IDS IN THIS OBJECT.
'''
class EdgeIdSet(object):

  '''
  Intialize with two ids.
  @param id1 : id of one component (id1 < id2)
  @param id2 : id of one component (id1 < id2)
  '''
  def __init__(self, id1, id2):
    if id1 > id2:
      self.id1 = id2
      self.id2 = id1
    else:
      self.id1 = id1
      self.id2 = id2

  def __eq__(self, other):
    return isinstance(other, self.__class__) \
            and self.id1 == other.get_id1() \
            and self.id2 == other.get_id2()

  def  __ne__(self, other):
    return not self.__eq__(other)

  def __hash__(self):
    # Use large prime number
    return self.id1 + 14365291*self.id2

  '''
  Get an id of smaller value.
  @return int : id
  '''
  def get_id1(self):
    return self.id1

  '''
  Get an id of larger value.
  @return int : id
  '''
  def get_id2(self):
    return self.id2

  '''
  Get if this id set contains the specified key id
  @param key_id : id to be searched
  @return bool : True if contains the id, else False
  '''
  def contains_id(self, key_id):
    return self.id1 == key_id or self.id2 == key_id


'''
Manage all edges and components in them.
'''
class MergedEdgeComponent:

  '''
  Initialize with empty dicts
  '''
  def __init__(self):
    self.edge_dict = dict()
    self.component_dict = dict()

  '''
  Add edge to the list
  @param comp1 : A component to compose a edge
  @param comp2 : A component to compose a edge
  '''
  def add_edge(self, comp1, comp2):
    id_set = EdgeIdSet(comp1.get_id(), comp2.get_id())
    edge = Edge(comp1, comp2)
    if id_set in self.edge_dict:
      self.edge_dict[id_set].add(edge)
    else:
      self.edge_dict[id_set] = MergedEdge(edge)

  '''
  Get edege which has id1 and id2.
  @param id_set : edge id set
  @return MergedEdge : specified merged edge
  '''
  def get_merged_edge(self, id_set):
    return self.edge_dict[id_set]

  '''
  Get merged edge dict.
  @return dict(EdgeIdSet, MergedEdge) : All merged edge dict
  '''
  def get_edge_dict(self):
    return self.edge_dict

  '''
  Add component to the list
  '''
  def add_component(self, cid, component):
    self.component_dict[cid] = component

  '''
  Search component with id
  @param search_id : id to search 
  @return bool : TRUE if the id is found, else FALSE
  '''
  def search_component(self, search_id):
    return search_id in self.component_dict

  '''
  Get specified component
  @param search_id : id to search 
  @return Component : target component
  '''
  def get_component(self, search_id):
    if search_id in self.component_dict:
      return self.component_dict[search_id]
    else:
      return None

  '''
  Merge edges with changing ids of all components.
  Since all components are preseved in component_dict, change id in it.
  @param from_id : Edge of this id will be changed to to_id
  @param to_id   : Edge of from_id will be changed to this id
  '''
  def merge(self, from_id, to_id):
    # Id sets to be changed
    changed_id_sets = list()
    deleted_id_sets = list()
    # Change ids in id sets in edge_dict
    for id_set in self.edge_dict.keys():
      if id_set.contains_id(from_id):
        if id_set.contains_id(to_id):
          deleted_id_sets.append(id_set)
        else:
          changed_id_sets.append(id_set)

    # Delete edge_dict
    for id_set in deleted_id_sets:
      del self.edge_dict[id_set]

    # Merge edge_dict
    for id_set in changed_id_sets:
      id1 = id_set.get_id1()
      id2 = id_set.get_id2()

      id_pair_of_to = id2 if id1==from_id else id1
      # id set after change
      changed_id_set = EdgeIdSet(id_pair_of_to, to_id)
      # Merge
      move_me = self.edge_dict.pop(id_set)

      if changed_id_set in self.edge_dict:
        self.edge_dict[changed_id_set].merge(move_me)
      else:
        self.edge_dict[changed_id_set] = move_me

  '''
  Print list of components
  '''
  def print_list(self):
    print("--- list of components in merged edges---")
    for c in self.component_dict.values():
      c.print_component()
    print("--- list of components in merged edges ---")

    print("--- list of edges in merged edges---")
    for id_set, me in self.edge_dict.items():
      print("======(id1:{0}, id2:{1})======".format(id_set.get_id1(), id_set.get_id2()))
      me.print_edges()
      print("==================================")
    print("--- list of edges in merged edges ---")

  '''
  Get minimum difference edge between the specified two components.
  '''
  def calc_min_diff(self, id1, id2):
    id_set = EdgeIdSet(id1, id2)
    if id_set in self.edge_dict:
      return self.edge_dict[id_set].get_min_edge().get_difference()
    else:
      # Edge is infinite
      return sys.maxint
