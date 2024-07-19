# -*- coding: utf-8 -*-
"""
This is file `stars.py'.

An uncompressed implementation of the Blandford-Blelloch-Cardoze-Kadow data
structure for planar triangulations.

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

# Import from local packages
from .utils import Point

class Vertex: # here
  def __init__(self, point=None):
    self.__links = []
    self.__point = point

  # ACCESS methods

  @property
  def links(self):
    return self.__links

  @property
  def point(self):
    return self.__point

  # UPDATE methods

  def set_point(self, point):
    self.__point = point


class StarVertices:
  """
  This is an object oriented implementation of Blandford's simplicial
  complex data structure.
  """
  def __init__(self):
    self.__vertices = []
    self.create_vertex() # infinite vertex, index 0
    self.__vertices[0].set_point( Point(numpy.inf,numpy.inf) )

  # ACCESS methods

  def vertex(self, i):
    return self.__vertices[i]

  @property
  def vertices(self):
    return self.__vertices
  
  @property
  def number_of_vertices(self): # number of vertices
    return len(self.__vertices)
  
  # find_up sempre retorna o triângulo que contém
  # o simplexo dado.
  def find_up(self, v0, v1=None):
    if v0 is not None:
      if v1 is not None: # return oriented face (v0,v1,v2)
        i1 = p1 = None
        links = self.vertex(v0).links
        # get the path and index of v1
        for index, path in enumerate(links):
          if v1 in path:
            i1 = path.index(v1)
            p1 = index

        link = self.vertex(v0).links[p1]
        last = len(link) - 1
        if i1 == last: # open link, because 'index()' always return first occurrence
          return None  # so, there is no 'v2' such that (v0,v1,v2) is a face

        v2 = link[i1+1]
        return v0, v1, v2
      else: # return any edge (v0,v1)
        pass
    else: # error
      return None
    
  # PREDICATE methods
    
  def is_infinite(self, v0, v1 = None, v2 = None):
    if v2 is None:
      if v1 is None:
        return v0 == 0
      else:
        return  (v0 == 0) or (v1 == 0)
    else:
      return  (v0 == 0) or (v1 == 0) or (v2 == 0)

  # UPDATE methods

  def create_vertex(self):
    self.vertices.append(Vertex())

  def insert_face(self, v0, v1, v2):
    self.__insert_face(v0, v1, v2)
    self.__insert_face(v1, v2, v0)
    self.__insert_face(v2, v0, v1)

  # A triangle t can be added by finding the representative
  # vertices of t and extending each of their link sets.
  # This extension might:
  #     (i) add a new path to the set, if neither of the two
  #         vertices are in the set;
  #    (ii) extend an existing path, if one vertex is in the set;
  #   (iii) join two existing paths, if the two vertices are in
  #         separate paths;
  #    (iv) join a path into a cycle, if the two vertices are the
  #         ends of the same path.
  def __insert_face(self, v0, v1, v2):
    i1 = i2 = p1 = p2 = None
    links = self.vertex(v0).links
    print("      | adding face to vertex %d" % v0)
    print("      |                link before: ", links)
    # get the path of each neighbor, and its respective index
    for index, path in enumerate(links):
      if v1 in path:
        i1 = path.index(v1)
        p1 = index
      if v2 in path:
        i2 = path.index(v2)
        p2 = index

    if p1 is None and p2 is None: # case (i)
      links.append([v1,v2])
    elif p1 is not None and p2 is None: # case (ii-a)
      links[p1].insert(i1+1,v2)
    elif p1 is None and p2 is not None: # case (ii-b)
      links[p2].insert(i2,v1)
    else: # join paths
      if p1 != p2: # case (iii)
        pmin = pmax = pos = None
        if p1 < p2:
          pmin, pmax = p1, p2
          pos = i1 + 1
        else:
          pmin, pmax = p2, p1
          pos = i2
        links[pmin][pos:pos] = links[pmax]
        del links[pmax]
      else: # case (iv)
        # we can only join extreme neighbors
        assert i2 == 0 and (i1+1) == len(links[p1])
        links[p1].append(v2)
    print("      |                link after: ", links)

  def remove_face(self, v0, v1, v2):
    self.__remove_face(v0, v1, v2)
    self.__remove_face(v1, v2, v0)
    self.__remove_face(v2, v0, v1)

  # A triange t can be deleted by finding the representative
  # vertices of t and splitting a cycle or a path of each of
  # their links.
  def __remove_face(self, v0, v1, v2):
    i1 = i2 = p1 = p2 = None
    links = self.vertex(v0).links
    for index, path in enumerate(links):
      if v1 in path:
        i1 = path.index(v1)
        p1 = index
      if v2 in path:
        i2 = path.index(v2)
        p2 = index

    # face must exist
    assert (i1 is not None) and (i2 is not None), "Face does not exist"

    # both neighbors must be in the same path
    assert p1 == p2, "Face does not exist"

    begin  = links[p1][0]
    end    = links[p1][-1]

    first  = links[p1][:i2]
    latest = links[p1][i2:]

    del links[p1]

    assert (len(first) + len(latest)) > 1

    if begin == end: # closed links remain connected
      links.append(latest[:-1] + first)
    else: # open paths are just split
      if len(first) > 1:
        links.insert(p1,first)
      if len(latest) > 1:
        links.insert(p1+1,latest)


  # OUTPUT methods

  def print(self):
    print('> links:')
    for i in range(self.number_of_vertices):
      print(self.vertex(i).links)
