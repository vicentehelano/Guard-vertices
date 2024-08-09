# -*- coding: utf-8 -*-
"""\
This is file `kdtree.py'.

Implementation of a BRIO using kD-trees.

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
import copy
import numpy
from numpy import random
from queue import Queue

# Local imports
from ..geometry import BoundingBox, Point
from ..canvas import Canvas
from ..log import *

X_AXIS = 0
Y_AXIS = 1

class Node:
  """\
  Kd-tree node class.
  """
  def __init__(self):
    self.__axis  = None
    self.__point = None
    self.__child = [None, None]
    self.__bbox  = BoundingBox()
  
  @property
  def axis(self):
    return self.__axis
  
  @property
  def point(self):
    return self.__point
  
  def child(self, i):
    assert 0 <= i <= 1
    return self.__child[i]
  
  @property
  def bbox(self):
    return self.__bbox

  def set_point(self, point):
    self.__point = copy.copy(point)

  def set_axis(self, axis):
    self.__axis = axis
    
  def set_child(self, i, node):
    self.__child[i] = node

  def set_bbox(self, xmin, ymin, xmax, ymax):
    self.__bbox.set_min(xmin, ymin)
    self.__bbox.set_max(xmax, ymax)

class KdTree:
  """\
  A 2D kD-tree class.

  This class implements a 2D kD-tree following the design of Liu et al. (2013),
  where points area stored in both internal and external nodes.

  References
  ----------
    LIU, Jian-Fei; YAN, Jin-Hui; LO, S. H. A new insertion sequence for
      incremental Delaunay triangulation. Acta Mechanica Sinica, v. 29,
      n. 1, p. 99-109, 2013.
  """
  def __init__(self):
    self.__nodes  = []
    self.__points = None
    self.__bbox = BoundingBox()
    self.__canvas = None

  @property
  def root(self):
    assert len(self.__nodes) > 0
    return self.__nodes[0]
  
  @property
  def node(self, i):
    return self.__nodes[i]
    
  @property
  def nodes(self):
    return self.__nodes

  @property
  def point(self, i):
    return self.__points[i]
    
  @property
  def points(self):
    return self.__points
  
  @property
  def bbox(self):
    return self.__bbox
  
  @property
  def number_of_nodes(self):
    return len(self.__nodes)

  @property
  def number_of_points(self):
    return len(self.__points)
  
  def create_node(self):
    self.__nodes.append(Node())
    return self.nodes[-1]

  def insert(self, points):
    # Get bounding box for the whole tree
    self.__points = points
    self.bbox.fit(points)

    # set point ids
    for i, p in enumerate(self.__points):
      p.set_id(i)

    self.__insert(0, len(points),
      self.bbox.min.x, self.bbox.min.y, self.bbox.max.x, self.bbox.max.y)

  def __insert(self, begin, end, xmin, ymin, xmax, ymax):
    n = end - begin
    node = None
    if n == 1: # end of recursion, create leaf node
      node = self.create_node()
      node.set_point(self.points[begin])
      node.set_bbox(xmin, ymin, xmax, ymax)
      return node

    axis = self.__longest_axis(xmin, ymin, xmax, ymax)
    k = (n + n%2)/2
    median = self.__select_median_along_axis(k, axis, begin, end-1)
    print("Mediana: ", median)

    # Split bounding box
    left_xmin  = xmin
    left_ymin  = ymin
    left_xmax  = xmax
    left_ymax  = ymax
    right_xmin = xmin
    right_ymin = ymin
    right_xmax = xmax
    right_ymax = ymax

    if axis == X_AXIS:
      left_xmax = right_xmin = self.points[median].x
    else:
      left_ymax = right_ymin = self.points[median].y

    node = self.create_node()
    node.set_point(self.points[median])
    node.set_bbox(xmin, ymin, xmax, ymax)
    node.set_axis(axis)
    assert node.axis is not None

    # Constrói de forma recursiva a subárvore esquerda
    left  = None
    if begin < median: # check for non-emptyness
      left  = self.__insert(begin, median, left_xmin, left_ymin, left_xmax, left_ymax)

    right = None
    if median+1 < end: # check for non-emptyness
      right = self.__insert(median+1, end, right_xmin, right_ymin, right_xmax, right_ymax)

    node.set_child(0, left)
    node.set_child(1, right)
  
    return node
    
  def __longest_axis(self, xmin, ymin, xmax, ymax):
    if (xmax - xmin) > (ymax - ymin):
      return X_AXIS
    else:
      return Y_AXIS
  
  def __select_median_along_axis(self, i, axis, left, right):

    if left == right:
      assert i == 1
      info("  | >> mediana TRIVIAL em %d" % left)
      return left

    info("Iniciando seleção do %dº:" % i)
    info("  | axis: %d" % axis)
    info("  | [left, right]: [%d, %d]" % (left, right))

    pivot = self.__partition(axis, left, right)

    info("  | pivô definitivo: %d" % pivot)

    k = pivot - left # size of left side
    if i < k+1:
      info("  | >> buscando o %dº" % i)
      info("  | >> no intervalo: [%d,%d]" % (left, pivot-1))
      return self.__select_median_along_axis(i, axis, left, pivot-1)
    elif i > k+1:
      info("  | >> buscando o %dº" % (i-k-1))
      info("  | >> no intervalo: [%d,%d]" % (pivot+1, right))
      return self.__select_median_along_axis(i-k-1, axis, pivot+1, right)
    else: # i == k+1:
      info("  | >> mediana encontrada em %d" % pivot)
      return pivot
  
  def __partition(self, axis, left, right):
    """Lomuto partition."""
    info("  | Particionando...")
    # Seleciona um pivô aleatório e mova-o para o final, temporariamente
    index = random.randint(left, right+1)
    info("  | pivô aleatório inicial: %d" % index)
    pivot = self.points[index]
    self.points[index], self.points[right] = self.points[right], self.points[index]

    # Particiona os pontos em torno do pivô
    i = left - 1
    for j in range(left, right):
      if (self.points[j].coords[axis] <= pivot.coords[axis]):
        i = i + 1
        self.points[i], self.points[j] = self.points[j], self.points[i]

    # Move o pivô de volta para a posição correta
    self.points[i+1], self.points[right] = self.points[right], self.points[i+1]

    return i + 1
  
  def __sort_inorder_left_first(self, node, buffer):
    if node is None:
      return

    self.__sort_inorder_left_first(node.child(0), buffer)
    buffer.append(node.point)
    self.__sort_inorder_left_first(node.child(1), buffer)

  def __sort_inorder_right_first(self, node, buffer):
    if node is None:
      return

    self.__sort_inorder_right_first(node.child(1), buffer)
    buffer.append(node.point)
    self.__sort_inorder_right_first(node.child(0), buffer)

  def __sort_inorder_alternating(self, node, buffer):
    if node is None:
      return

    if node.axis == X_AXIS:
      self.__sort_inorder_left_first(node.child(0), buffer)
      buffer.append(node.point)
      aux = []
      self.__sort_inorder_right_first(node.child(1), aux)
      buffer.extend(reversed(aux))
    else:
      self.__sort_inorder_right_first(node.child(0), buffer)
      buffer.append(node.point)
      self.__sort_inorder_left_first(node.child(1), buffer)

  def __sort_inorder_alternating2(self, node, buffer, swap = 0):
    if node is None:
      return
    
    if swap == 0:
      self.__sort_inorder_alternating2(node.child(0), buffer, swap)
      buffer.append(node.point)
      aux = []
      self.__sort_inorder_alternating2(node.child(1), aux, swap)
      buffer.extend(reversed(aux))
    else:
      self.__sort_inorder_alternating2(node.child(1), aux, swap)
      buffer.append(node.point)
      aux = []
      self.__sort_inorder_alternating2(node.child(0), aux, swap)
      buffer.extend(reversed(aux))

  def __sort_inorder(self, node, buffer):
    if node is None:
      return

    self.__sort_inorder(node.child(0), buffer)
    buffer.append(node.point)
    self.__sort_inorder(node.child(1), buffer)

  def __sort_breadth_first(self, root, buffer):
    Q = Queue(maxsize = 0) # do we need an infinite size queue?
    Q.put(root)

    i = 0
    while not Q.empty():
      node = Q.get()

      if node.child(0) != None:
        Q.put(node.child(0))

      if node.child(1) != None:
        Q.put(node.child(1))

      buffer.append(node.point)
      i = i + 1

  def sort(self, points):
    # Build the kD-tree
    self.insert(points)

    # Calling sort algorithm
    buffer = []
    #self.__sort_breadth_first(self.root, buffer)
    #self.__sort_inorder(self.root, buffer)
    #self.__sort_inorder_alternating(self.root, buffer)
    self.__sort_inorder_alternating2(self.root, buffer)
    self.__points = numpy.array(buffer)

    return self.__points
  
  def is_leaf(self, node):
    if node.child(0) is None:
      if node.child(1) is None:
        return True
    else:
      return False
  
  def draw(self):
    """Draw circumcircles over the current active canvas."""
    if self.__canvas is None:
      bbox = copy.deepcopy(self.__bbox)
      bbox.scale(1.25)
      self.__canvas = Canvas(bbox)

    rectangles = []
    for node in self.nodes:
      rectangles.append(node.bbox)

    self.__canvas.begin()
    self.__canvas.draw_rectangle(rectangles)
    for p in self.points:
      self.__canvas.draw_point(p)
      
    # SORTING CURVE
    for i in range(len(self.points)-1):
      p = self.points[i]
      q = self.points[i+1]      
      self.__canvas.draw_segment(p, q)
    self.__canvas.end()

  def statistics(self):
    # squared walk length
    sqlen = 0.0
    for i in range(len(self.points)-1):
      p = self.points[i]
      q = self.points[i+1]
      sqlen = sqlen + (q.x - p.x)**2 + (q.y - p.y)**2

    print("Squared walk length:", sqlen)




