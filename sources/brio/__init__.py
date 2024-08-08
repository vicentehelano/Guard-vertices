# -*- coding: utf-8 -*-
"""\
This is file `__init__.py'.

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
from .kdtree import *
from ..log import *

# Sorting methods
BRIO_NONE    = 0
BRIO_RANDOM  = 1
BRIO_HILBERT = 2
BRIO_KDTREE  = 3

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
  def __init__(self, method = BRIO_RANDOM):
    self.__method = method
    self.__points = None
    self.__rounds = None

  def __call__(self, points):
    # copy input point set
    self.__points = None
    if isinstance(points, numpy.ndarray):
      self.__points = copy.deepcopy(points)
    elif isinstance(points, list):
      self.__points = numpy.array(points)
    else:
      error("Input container not supported.")
      sys.exit(1)

    # set the chosen brio order
    if self.__method == BRIO_RANDOM:
      self.__brio_random()
    elif self.__method == BRIO_KDTREE:
      self.__brio_kdtree()
    else:
      assert self.__method == BRIO_NONE
    
    return self.__points
  
  def __create_rounds(self):
    """Computes round intervals."""
    n = len(self.__points) # number of points
    r = int(numpy.floor(numpy.log2(n))) # number of rounds
    sizes = numpy.zeros((r,), dtype=int) # size of each round
    for i in range(r-1, 0, -1):
      k = sum(random.binomial(1, 0.5, n))
      sizes[i] = k
      n = n - k
    sizes[0] = n

    # compute round ranges
    self.__rounds = numpy.zeros((r,), dtype=tuple)
    left = 0
    for i, size in enumerate(sizes):
      right = left + size
      self.__rounds[i] = (left,right)
      left = right

  def __brio_random(self):
    random.shuffle(self.__points)
  
  def __brio_kdtree(self):
    # create rounds
    self.__create_rounds()

    for r in self.__rounds:
      tree = KdTree()
      #tree.sort(self.__points)