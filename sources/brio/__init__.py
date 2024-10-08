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
from random import sample
from enum import Enum

# Local imports
from .kdtree import *
from ..geometry import BoundingBox, Point
from ..canvas import Canvas
from ..log import *

# Sorting methods
BRIO_NONE    = 0
BRIO_RANDOM  = 1
BRIO_KDTREE  = 2

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
    self.__canvas = None

  def rounds(self):
    return self.__rounds

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
      if r[1]-r[0] > 1:
        block = tree.sort(self.__points[r[0]:r[1]])
        self.__points[r[0]:r[1]] = block[:]

    return self.__points
  
  def draw(self):
    """Draw circumcircles over the current active canvas."""
    if self.__canvas is None:
      bbox = BoundingBox()
      bbox.fit(self.__points)
      bbox.scale(1.25)
      self.__canvas = Canvas(bbox)
      
    # SORTING CURVE
    import matplotlib.colors as pltc
    all_colors = [k for k,v in pltc.cnames.items()]
    colors = sample(all_colors, len(self.__rounds))

    for i, r in enumerate(self.__rounds):
      self.__canvas.begin()
      for j in range(r[0], r[1]-1):
        p = self.__points[j]
        q = self.__points[j+1]      
        self.__canvas.draw_segment(p, q, colors[i])
      for p in self.__points:
        self.__canvas.draw_point(p)
      self.__canvas.end()
