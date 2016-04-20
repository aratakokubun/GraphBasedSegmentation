# -*- coding:utf-8 -*-

class InvalidParameterException(Exception):

  '''
  Print error content.
  '''
  def print_err(self):
    print("Invalid parameters are passed to the function")
