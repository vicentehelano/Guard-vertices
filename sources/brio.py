# -*- coding: utf-8 -*-
"""\
This is file `brio.py'.

Implementation of Biased Randomized Insertion Orders.

Copyright (C) 2024 any individual authors listed elsewhere in this file.

This code is marked with CC0 1.0 Universal. To view a copy of this license, visit
https://creativecommons.org/publicdomain/zero/1.0/ or the accompanying
LICENSE file.

It is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
CC0 1.0 Universal for more details.

Author(s): Vicente Sobrinho <vicente.sobrinho@ufca.edu.br>
"""
import numpy
import copy
from enum import Enum

# Sorting methods
class SortingMethod(Enum):
  NONE    = 0
  RANDOM  = 1
  HILBERT = 2
  KDTREE  = 3

# Temporarily, we have only implemented NONE and RANDOM.
class Brio:
  def __init__(self, method = SortingMethod.RANDOM):
    print("> creating BRIO functor")
    self.__method = method

  def __call__(self, points):
    assert isinstance(points, numpy.ndarray)
    P = copy.deepcopy(points)
    if self.__method == SortingMethod.NONE:
      return P
    if self.__method == SortingMethod.RANDOM:
      numpy.random.shuffle(P)
      print("  | random shuffle done.")
      return P
    
    return None