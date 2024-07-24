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
import sys
from enum import Enum

# Local imports
from .log import *

# Sorting methods
class SortingMethod(Enum):
  NONE    = 0
  RANDOM  = 1
  HILBERT = 2
  KDTREE  = 3

# Temporarily, we have only implemented NONE and RANDOM.
class Brio:
  """\
  Constructs a Biased Randomized Insertion Order (BRIO).

  Currently available BRIOS: None and random shuffle.

  Parameters
  ----------
    points : random access container (list or numpy.array)
        Container of 2D points.

  Returns
  --------
    P : numpy.array
        Container of sorted points.

  References
  ----------
    Amenta, N., Choi, S., and Rote, G., Incremental constructions con BRIO.
      Proceedings of the 19th Annual Symposium on Computational geometry,
      p. 211-219, 2003.
  """
  def __init__(self, method = SortingMethod.RANDOM):
    self.__method = method

  def __call__(self, points):
    P = None
    if isinstance(points, numpy.ndarray):
      P = copy.deepcopy(points)
    elif isinstance(points, list):
      P = numpy.array(points)
    else:
      error("Input container not supported.")
      sys.exit(1)

    if self.__method == SortingMethod.NONE:
      return P
    if self.__method == SortingMethod.RANDOM:
      numpy.random.shuffle(P)
      return P
    
    return None