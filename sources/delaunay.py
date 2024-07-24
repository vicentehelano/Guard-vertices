# -*- coding: utf-8 -*-
"""
This is file `delaunay.py'.

Just another implementation of the Bowyer-Watson algorithm for constructing the
Delaunay triangulation of a planar point set.

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
import random
from queue import Queue

# Local imports
from .utils import Point, Circle, BoundingBox
from .utils import orientation, in_between, circumcircle, cw, ccw
from .canvas import Canvas
from .brio import Brio
from .log import *

class DelaunayTriangulation:
  """\
  Constructs the Delaunay triangulation of a planar point set.

  This class contains an implementation of the Boywer-Watson algorithm
  con BRIO for triangulating planar point sets. It closely follows CGAL's
  Delaunay_triangulation_3 design.

  Parameters
  ----------
    tds : class
          An implementation of a triangulation data structure providing at
          least the following methods:
            - vertex(i: int): returns the i-th vertex of `tds`.
            - neighbor(i: int, f: list): returns the i-th neighbor of face `f`.
            - create_vertex(): create a new vertex in `tds`.
            - insert_face(v0: int, v1: int, v2: int):  insert face (v0,v1,v2) into `tds`.
            - remove_face(v0: int, v1: int, v2: int): remove face (v0,v1,v2) from `tds`.
            - is_infinite(v0: int, v1: int, v2: int): check if face (v0,v1,v2) is infinite.

  Examples
  --------
  >>> t = DelaunayTriangulation(LinkVertices)
  >>> t.insert(Point(0.0, 0.0))
  >>> t.insert(Point(1.0, 0.0))
  >>> t.insert(Point(0.0, 1.0))
  >>> t.insert(Point(1.0, 0.0))
  >>> t.draw()
  """
  def __init__(self, tds):
    self.__tds = tds()
    self.__bbox = BoundingBox()
    self.__canvas = None

  # ACCESS methods

  def vertex(self, i):
    return self.__tds.vertex(i)
  
  @property
  def number_of_vertices(self): # number of vertices, including the infinite one
    return self.__tds.number_of_vertices
  
  def neighbor(self, i, f):
    return self.__tds.neighbor(i, f)

  # PREDICATE methods

  def __is_infinite(self, v0, v1 = None, v2 = None):
    return self.__tds.is_infinite(v0, v1, v2)

  def __all_infinite(self, faces):
    n = 0
    for f in faces:
      if self.__is_infinite(f[0], f[1], f[2]):
        n = n + 1

    return n == len(faces)

  # UPDATE methods

  def __create_vertex(self):
    self.__tds.create_vertex()

  def __insert_face(self, v0, v1, v2):
    self.__tds.insert_face(v0, v1, v2)

  def __remove_face(self, v0, v1, v2):
    self.__tds.remove_face(v0, v1, v2)

  # Bowyer-Watson algoritm con BRIO
  def insert(self, points):
    assert len(points) >= 3

    info('Creating BRIO...')
    brio = Brio()
    points = brio(points)
    info('BRIO done.')

    info('Inserting first three points...')
    self.__insert_first_three(points)
    info('First three insertion done.')

    info('Inserting remaining points...')
    hint = [1, 2, 3] # first finite face
    for p in points[3:]:
      debug("+-- Inserting point: " + str(p.coords))

      debug("+-- Finding conflict set and cavity.")
      conflict, cavity = self.__find_conflict(p, hint)
      debug("    |-- conflict set: " + str(conflict))
      debug("    |-- cavity: " + str(cavity))

      debug("    |-- removing conflict set.")
      self.__remove_conflict(conflict)

      debug("    |-- filling cavity.")
      self.__fill_cavity(p, cavity)

      debug("    |-- updating walk hint face.")
      i = self.number_of_vertices - 1
      link = self.vertex(i).links[0]
      hint[0] = i
      hint[1] = link[0]
      hint[2] = link[1]

    info('Insertion done.')

    # reshaping bounding box
    debug("Updating bounding box.")
    self.__bbox.reshape(points)

  def visual_insert(self, points, with_labels=False):
    assert len(points) >= 3

    # reshaping bounding box
    info("Updating bounding box.")
    self.__bbox.reshape(points)

    if self.__canvas is None:
      info("Creating canvas...")
      bbox = copy.deepcopy(self.__bbox)
      bbox.scale(1.25)
      self.__canvas = Canvas(bbox)
      info("Canvas ready.")

    info('Creating BRIO...')
    brio = Brio()
    points = brio(points)
    info('BRIO done.')

    info('Inserting first three points...')
    self.__insert_first_three(points)
    info('First three insertion done.')

    info('Drawing initial triangulation...')
    self.__canvas.begin()
    self.__draw(with_labels)
    self.__canvas.end()

    info('Inserting remaining points...')
    hint = [1, 2, 3] # first hint face
    for p in points[3:]:
      info("+-- Inserting point: " + str(p.coords))
      self.__canvas.begin()
      self.__canvas.draw_point(p)
      self.__canvas.end()
      
      info("+-- Finding conflict set and cavity.")
      conflict, cavity = self.__find_conflict(p, hint)
      info("    |-- conflict set: " + str(conflict))
      info("    |-- cavity: " + str(cavity))

      info("+-- Drawing conflict set and cavity.")
      self.__canvas.begin()
      self.draw_conflict(conflict)
      self.draw_cavity(cavity)
      self.draw_circumcircles(conflict)
      self.__canvas.end()

      info("    |-- removing conflict set.")
      self.__remove_conflict(conflict)

      if not self.__all_infinite(conflict):
        self.__canvas.clear()
        self.__canvas.begin()
        self.__canvas.draw_point(p)
        self.draw_conflict(conflict)
        self.draw_cavity(cavity)
        self.__draw(with_labels)
        self.__canvas.end()

      info("    |-- filling cavity.")
      self.__fill_cavity(p, cavity)

      info('+-- Drawing updated triangulation...')
      self.__canvas.clear()
      self.__canvas.begin()
      self.__draw(with_labels)
      self.__canvas.end()

      info("+-- Updating walk hint face...")
      i = self.number_of_vertices - 1
      link = self.vertex(i).links[0]
      hint[0] = i
      hint[1] = link[0]
      hint[2] = link[1]

    info('Insertion done.')

  # BOWYER-WATSON internal methods
  
  def __insert_first_three(self, points):
    """Add first three non-collinear points.
    """
    self.__create_vertex()
    self.__create_vertex()
    self.__create_vertex()

    p0 = points[0]
    p1 = points[1]
    # find p3 such that (p1,p2,p3) has positive orientation
    i = 2
    found = False
    while i < points.size:
      p2 = points[i]
      if orientation(p0, p1, p2) > 0:
        found = True
        break
      i = i + 1

    if not found:
      p0 = points[1]
      p1 = points[0]
      # find p3 such that (p1,p2,p3) has positive orientation
      i = 2
      while i < points.size:
        p2 = points[i]
        if orientation(p0, p1, p2) > 0:
          found = True
          break
        i = i + 1

    assert found == True

    if i != 2: # the third point is not at the third position, so fix it
      points[2], points[i] = points[i], points[2]

    # add faces (finite and infinite)
    self.__insert_face(1,2,3)
    self.__insert_face(0,2,1)
    self.__insert_face(0,3,2)
    self.__insert_face(0,1,3)

    # set points
    self.vertex(1).set_point(p0)
    self.vertex(2).set_point(p1)
    self.vertex(3).set_point(p2)

  def __find_conflict(self, p, hint):
    first  = self.__find_first_conflict(p, hint)
    conflict, cavity = self.__find_other_conflicts(p, first)
    return conflict, cavity

  def __in_conflict(self, p: Point, v0: int, v1: int, v2: int):
    if self.__is_infinite(v0, v1, v2):
      # sort vertices to get (v0, v1, v2 = 0), i.e., infinite at last
      face = [v0,v1,v2]
      i  = face.index(0)
      v0 = face[(i+1)%3]
      v1 = face[(i+2)%3]

      v0 = self.vertex(v0)
      v1 = self.vertex(v1)

      p0 = v0.point
      p1 = v1.point
      
      orient = orientation(p0, p1, p)

      if orient > 0: # p is outside convex hull
        return True

      if orient == 0:  # in this case, only inside edge implies conflict
        return in_between(p0, p1, p)

    else: # in case of finite face, proceed as always
      # compute incircle test
      v0 = self.vertex(v0)
      v1 = self.vertex(v1)
      v2 = self.vertex(v2)
      
      p0 = v0.point
      p1 = v1.point
      p2 = v2.point

      orient = orientation(p0, p1, p2, p)

      if orient >= 0:
        return True
      else:
        return False

  def __find_first_conflict(self, p, hint):
    if 0 in hint: # infinite face, find oposite face, which must be finite
      i = hint.index(0)
      hint = self.neighbor(i, hint)

    found = False
    while not found:
      v0 = self.vertex(hint[0])
      v1 = self.vertex(hint[1])
      v2 = self.vertex(hint[2])
      
      p0 = v0.point
      p1 = v1.point
      p2 = v2.point

      e0 = orientation(p0, p1, p) + 1
      e1 = orientation(p1, p2, p) + 1
      e2 = orientation(p2, p0, p) + 1

      mask = int(e2*9 + e1*3 + e0)
      
      if mask in [11, 20, 19]: # walk to v0 opposite vertex
        hint = self.neighbor(0, hint)
      elif mask in [5, 7, 8]: # walk to v1 opposite vertex
        hint = self.neighbor(1, hint)
      elif mask in [15, 21, 24]: # walk to v2 opposite vertex
        hint = self.neighbor(2, hint)
      elif mask == 2: # walk to v0 or v1 opposite vertex
        i = random.choice([0,1])
        hint = self.neighbor(i, hint)
      elif mask == 6: # walk to v1 or v2 opposite vertex
        i = random.choice([1,2])
        hint = self.neighbor(i, hint)
      elif mask == 18: # walk to v2 or v0 opposite vertex
        i = random.choice([0,2])
        hint = self.neighbor(i, hint)
      elif mask == 16: # found at vertex v0
        found = True
      elif mask == 22: # found at vertex v1
        hint = [hint[1],hint[2],hint[0]]
        found = True
      elif mask == 14: # found at vertex v2
        hint = [hint[2],hint[0],hint[1]]
        found = True
      elif mask == 25: # found at edge (v0,v1)
        found = True
      elif mask == 23: # found at edge (v1,v2)
        hint = [hint[1],hint[2],hint[0]]
        found = True
      elif mask == 17: # found at edge (v2,v0)
        hint = [hint[2],hint[0],hint[1]]
        found = True
      elif mask == 26: # found inside face (v0,v1,v2)
        found = True
      else: # 0 | 1 | 3 | 4 | 9 | 10 | 12 | 13: # undefined
        return None

      if hint[2] == 0: # p is outside the convex hull
        break
      else: # could not be an infinite face
        assert 0 not in hint

    return hint

  def __find_other_conflicts(self, p, first):
    conflict = [first]
    cavity = []
    Q = Queue(maxsize = 0) # do we need an infinite size queue?
    Q.put(first)
    visited = numpy.full(self.number_of_vertices, False)

    while not Q.empty():
      face = Q.get()
      # check each neighbor face for conflict
      for i in range(3):
        N = self.neighbor(i, face)

        # if visited, skip
        if visited[N[0]] and visited[N[1]] and visited[N[2]]:
          continue

        in_conflict = self.__in_conflict(p, N[0], N[1], N[2])

        if in_conflict:
          conflict.append(N)
          Q.put(N)
        else: # we've reached the boundary of the cavity
          cavity.append([face[ccw(i)], face[cw(i)]])

      # mark vertices as visited
      visited[numpy.array(face)] = True
    
    return conflict, cavity
  
  def __remove_conflict(self, conflict):
    # remove faces from cavity
    for face in conflict:
      v0 = face[0]
      v1 = face[1]
      v2 = face[2]
      self.__remove_face(v0, v1, v2)

  def __fill_cavity(self, p, cavity):
    self.__create_vertex()
    v0 = self.number_of_vertices - 1
    for edge in cavity:
      v1 = edge[0]
      v2 = edge[1]
      self.__insert_face(v0, v1, v2)
    
    self.vertex(v0).set_point(p)

  # OUTPUT methods
  def print(self):
    self.__tds.print()

  def draw_labels(self):
    for i in range(self.number_of_vertices):
      p = self.vertex(i).point
      label = r"$v_{0}$".format(i)
      self.__canvas.draw_label(label, p)

  def draw_conflict(self, cavity):
    for face in cavity:
      iv0 = face[0]
      iv1 = face[1]
      iv2 = face[2]
      if not self.__is_infinite(iv0, iv1, iv2):
        v0 = self.vertex(iv0)
        v1 = self.vertex(iv1)
        v2 = self.vertex(iv2)
        self.__canvas.draw_triangle(v0.point, v1.point, v2.point, filled=True)

  def draw_circumcircles(self, faces):
    circles = []
    for face in faces:
      iv0 = face[0]
      iv1 = face[1]
      iv2 = face[2]
      if not self.__is_infinite(iv0, iv1, iv2):
        v0 = self.vertex(iv0)
        v1 = self.vertex(iv1)
        v2 = self.vertex(iv2)

        c,r = circumcircle(v0.point, v1.point, v2.point)
        circles.append(Circle(c, r))

    self.__canvas.draw_circle(circles)

  def draw_cavity(self, cavity):
    for edge in cavity:
      iv0 = edge[0]
      iv1 = edge[1]
      if not self.__is_infinite(iv0, iv1):
        v0 = self.vertex(iv0)
        v1 = self.vertex(iv1)
        self.__canvas.draw_segment(v0.point, v1.point)

  def draw(self, with_labels = False):
    if self.__canvas is None:
      bbox = copy.deepcopy(self.__bbox)
      bbox.scale(1.25)
      self.__canvas = Canvas(bbox)

    self.__canvas.begin()
    self.__draw(with_labels)
    self.__canvas.end()

  def __draw(self, with_labels):
    for iv0 in range(1, self.number_of_vertices): # skip infinite vertex
      v0 = self.vertex(iv0)
      for path in v0.links:
        for j in range(len(path)-1):
          iv1 = path[j]
          iv2 = path[j+1]
          if not self.__is_infinite(iv0, iv1, iv2):
            v1 = self.vertex(iv1)
            v2 = self.vertex(iv2)
            self.__canvas.draw_triangle(v0.point, v1.point, v2.point, filled=False)
    if with_labels:
      self.draw_labels()