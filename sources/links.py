# -*- coding: utf-8 -*-
"""
This is file `links.py'.

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
from .utils import Point, cw, ccw

class Vertex:
  """\
  Vertex base class for the link-based data structure of Blandford et al. (2005).

  Each vertex stores its link set as a list of lists of integers and its
  underlying point.

  Parameters
  ----------
    point : Point (optional)
            Any representation of a planar point (x,y).

  Examples
  --------
  >>> v = Vertex()
  >>> v.set_point(Point(0.0, 0.0))
  """
  def __init__(self, point=None):
    """Initializes the Vertex class."""
    self.__links = []
    self.__point = point

  # ACCESS methods

  @property
  def links(self):
    """Returns a reference to the vertex link."""
    return self.__links

  @property
  def point(self):
    """Returns a reference to underlying point."""
    return self.__point

  # UPDATE methods

  def set_point(self, point):
    """Set point coordinates."""
    self.__point = point

class LinkVertices:
  """\
  An uncompressed implementation of Blandford-Blelloch-Cardoze-Kadow data
  structure for planar triangulations.

  Each vertex link is implemented as a bare Python list of lists of indices,
  sorted in counter-clockwise order.
  The infinite vertex is always located at position 0 (zero).
  One can insert points, but not to remove vertices yet.

  Parameters
  ----------
    empty : empty

  Examples
  --------
  We can construct a triangulation with a single finite triangle as follows:

  >>> t = LinkVertices()
  >>> for i in range(3):
  >>>   t.create_vertex()
  >>> t.insert_face(0,2,1)
  >>> t.insert_face(0,3,2)
  >>> t.insert_face(0,1,3)
  >>> t.insert_face(1,2,3)
  >>> t.print()

  References
  ----------
    Blandford, D. K. et al., Compact representations of simplicial meshes in
      two and three dimensions. International Journal of Computational
      Geometry & Applications, v. 15, n. 1, p. 3-24, 2005.
  """
  def __init__(self):
    """Initializes the LinkVertices class."""
    self.__vertices = []
    self.create_vertex() # infinite vertex, index 0
    self.__vertices[0].set_point( Point(numpy.inf,numpy.inf) )

  # ACCESS methods

  def vertex(self, i):
    """Returns a reference to the i-th vertex."""
    return self.__vertices[i]

  @property
  def vertices(self):
    """Returns a reference to the container of vertices."""
    return self.__vertices
  
  @property
  def number_of_vertices(self): # number of vertices
    """Returns the total number of vertices, including the infinite one."""
    return len(self.__vertices)
  
  def neighbor(self, i, f):
    """Returns the neighbor face opposite to the i-th vertex of `f`."""
    return self.__find_up(f[cw(i)], f[ccw(i)])

  def __find_up(self, v0, v1=None):
    """\
    Returns an ordered simplex with the given ordered sub-simplex.

    If `v1 == None`, returns any face incident to vertex `v0`.
    Otherwise, returns the unique ordered simplex/face/triangle containing
    edge (v0, v1).

    Parameters
    ----------
      v0 : int
          The number of an existing vertex.
      v1 : int | None
          The number of an existing vertex, which forms an edge with `v0`.

    Returns
    -------
      (v0, v1, v2) : (int, int, int)
          A valid face (v0, v1, v2), if any. Otherwise, returns None.

    References
    ----------
      Blandford, D. K. et al., Compact representations of simplicial meshes in
        two and three dimensions. International Journal of Computational
        Geometry & Applications, v. 15, n. 1, p. 3-24, 2005.
    """
    if v0 is not None:
      if v1 is not None: # edge (v0,v1) defined, return oriented face (v0,v1,v2)
        i1 = p1 = None
        links = self.vertex(v0).links
        # get the path and index of v1
        for index, path in enumerate(links):
          if v1 in path:
            i1 = path.index(v1)
            p1 = index
            break

        link = self.vertex(v0).links[p1]
        last = len(link) - 1
         
         # If link[i1] == link[last], we must have i1 != last indicating a closed link,
         # because 'index()' always return first occurrence, so i1 < last.
         # Thus, if i1 == last, we have an open link.
         # So, there is no 'v2' such that (v0,v1,v2) is a face
        if i1 == last:
          return None

        v2 = link[i1+1]
        return v0, v1, v2
      else: # return any edge (v0,v1)
        link = self.vertex(v0).links[0]
        return v0, link[0]
    else: # error
      return None
    
  # PREDICATE methods
    
  def is_infinite(self, v0, v1 = None, v2 = None):
    """Returns True, if any vertex in {v0,v1,v2} is infinite."""
    if v2 is None:
      if v1 is None:
        return v0 == 0
      else:
        return  (v0 == 0) or (v1 == 0)
    else:
      return  (v0 == 0) or (v1 == 0) or (v2 == 0)

  # UPDATE methods

  def create_vertex(self):
    """Insert a new vertex at the end of the vertices container."""
    self.vertices.append(Vertex())

  def insert_face(self, v0, v1, v2):
    """\
    Insert in-place face `(v0, v1, v2)` into the triangulation.

    This method implements the `add` operation as described in the page 11,
    fourth paragraph, of Blandford et al. (2005). A triangle `t` can be added
    by finding its vertices and extending each of their link sets.
    The extension is carried out by the helper method `__insert_face`.

    Parameters
    ----------
      (v0, v1, v2) : (int, int, int)
          A valid face (v0, v1, v2), if any. Otherwise, returns None.

    References
    ----------
      Blandford, D. K. et al., Compact representations of simplicial meshes in
        two and three dimensions. International Journal of Computational
        Geometry & Applications, v. 15, n. 1, p. 3-24, 2005.
    """
    self.__insert_face(v0, v1, v2)
    self.__insert_face(v1, v2, v0)
    self.__insert_face(v2, v0, v1)

  def __insert_face(self, v0, v1, v2):
    """\
    Insert in-place face `(v0, v1, v2)` into the link of vertex `v0`.

    This function implements the `extension` operation as described in the
    page 11, fourth paragraph, of Blandford et al. (2005), as follows:
       (i) add a new path to the link set, if neither of the two
           vertices are in the set;
      (ii) extend an existing path, if one vertex is in the link set;
     (iii) join two existing paths, if the two vertices are in
           separate paths;
      (iv) join a path into a cycle, if the two vertices are the
           ends of the same path.

    Parameters
    ----------
      v0, v1, v2 : int, int, int
          The face vertices.
    """
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
    """\
    Remove in-place face `(v0, v1, v2)` from the triangulation.

    This method implements the `delete` operation as described in the page 11,
    fourth paragraph, of Blandford et al. (2005).
    A triange t can be deleted by finding its vertices and splitting a cycle
    or a path of each of their link sets.

    Parameters
    ----------
      (v0, v1, v2) : (int, int, int)
          A valid face (v0, v1, v2), if any. Otherwise, returns None.

    References
    ----------
      Blandford, D. K. et al., Compact representations of simplicial meshes in
        two and three dimensions. International Journal of Computational
        Geometry & Applications, v. 15, n. 1, p. 3-24, 2005.
    """
    self.__remove_face(v0, v1, v2)
    self.__remove_face(v1, v2, v0)
    self.__remove_face(v2, v0, v1)

  
  def __remove_face(self, v0, v1, v2):
    """\
    Remove in-place face `(v0, v1, v2)` from the link set of vertex `v0`.

    Different from Blandford et al. (2005), we do not remove vertices
    with empty link sets at the end.

    Parameters
    ----------
      v0, v1, v2 : int, int, int
          The vertices of the face to be removed.
    """
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
    """\
    Writes to the standard output stream the link sets of all vertices.

    The triangulation data structure is not supposed to have an undelying
    geometry. So, it outputs only the connectivity.

    Parameters
    ----------
      empty : empty
    """
    print('> links:')
    for i in range(self.number_of_vertices):
      print(self.vertex(i).links)
