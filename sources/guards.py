# -*- coding: utf-8 -*-
"""\
This is file `guards.py'.

An implementation of a compact data structure for planar triangulations
based on vertex-guards.

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
from numpy import random

# Import from local packages
from .geometry import Point
from .utils import cw, ccw
from .log import *

# Vertex status
ORDINARY_VERTEX = 0
GUARD_VERTEX    = 1

# Face status
UNGUARDED_FACE = 0
GUARDED_FACE   = 1

# Guarding policy
RANDOM_POLICY = 0
GREEDY_POLICY = 1

class Vertex:
  """\
  Vertex base class for the guard-based data structure of Batista (2010).

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
  def __init__(self, point=None, status=ORDINARY_VERTEX):
    """Initializes the Vertex class."""
    self.__links = []
    self.__guards = set()
    self.__point = point
    self.__status = status

  # ACCESS methods

  @property
  def links(self):
    """Returns a reference to the link set."""
    return self.__links
  
  @property
  def guards(self):
    """Returns a reference to the guard set."""
    return self.__guards

  @property
  def point(self):
    """Returns a reference to underlying point."""
    return self.__point
  
  @property
  def status(self):
    """Returns the type of the vertex."""
    return self.__status

  # UPDATE methods

  def set_point(self, point):
    """Set point coordinates."""
    self.__point = point

  def set_status(self, status):
    """Set vertex status."""
    self.__status = status

class GuardVertices:
  """\
  An implementation of the compact data structure for planar triangulations
  based on vertex-guards due to Batista (2010).

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

  >>> t = GuardVertices()
  >>> for i in range(3):
  >>>   t.create_vertex()
  >>> t.insert_face(0,2,1)
  >>> t.insert_face(0,3,2)
  >>> t.insert_face(0,1,3)
  >>> t.insert_face(1,2,3)
  >>> t.print()

  References
  ----------
    Batista, V. H. F., Transversais de triângulos e suas aplicações em
      triangulações. PhD thesis, Universidade Federal do Rio de Janeiro, COPPE,
      Civil Engineering Program, 2010.
  """
  def __init__(self):
    """Initializes the GuardVertices class."""
    self.__vertices = []
    self.create_vertex() # infinite vertex, index 0
    self.__vertices[0].set_point( Point(numpy.inf,numpy.inf) )
    self.__vertices[0].set_status(GUARD_VERTEX)

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
  
  @property
  def number_of_guards(self): # number of guards
    """Returns the total number of guard-vertices, including the infinite one."""
    return sum(1 for v in self.vertices if v.status == GUARD_VERTEX)
  
  @property
  def number_of_ordinaries(self): # number of ordinaries
    """Returns the total number of ordinary vertices."""
    return sum(1 for v in self.vertices if v.status == ORDINARY_VERTEX)
  
  @property
  def number_of_references(self): # number of references
    """Returns the total number of references."""
    references  = sum(len(sum(v.links, [])) for v in self.vertices if v.status == GUARD_VERTEX)
    references += sum(len(v.guards) for v in self.vertices if v.status == ORDINARY_VERTEX)
    return references
    
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
      [1] Batista, V. H. F., Transversais de triângulos e suas aplicações em
        triangulações. PhD thesis, Universidade Federal do Rio de Janeiro, COPPE,
        Civil Engineering Program, 2010.

      [2] Blandford, D. K. et al., Compact representations of simplicial meshes in
        two and three dimensions. International Journal of Computational
        Geometry & Applications, v. 15, n. 1, p. 3-24, 2005.
    """
    if v0 is not None:
      v = self.vertex(v0)
      if v1 is not None: # edge (v0,v1) defined, return oriented face (v0,v1,v2), if any
        if v.status == GUARD_VERTEX:
          return self.__find_up_guard(v0,v1)
        else: # ORDINARY_VERTEX
          return self.__find_up_ordinary(v0,v1)
      else: # return any edge (v0,v1)
        if v.status == GUARD_VERTEX:
          link = v.links[0]
          return v0, link[0]
        else: # ORDINARY_VERTEX
          guard = v.guards[0]
          return v0, guard[0]
    else: # error
      warning("Cannot find up undefined vertex.")
      return None

  # guards are bare link-vertices, proceed as for LinkVertices.
  def __find_up_guard(self, v0, v1):
    assert self.vertex(v0).status == GUARD_VERTEX

    i1 = p1 = None
    links = self.vertex(v0).links
    # get the path and index of v1
    for index, path in enumerate(links):
      if v1 in path:
        i1 = path.index(v1)
        p1 = index
        break

    link = links[p1]
    last = len(link) - 1
      
    # If link[i1] == link[last], we must have i1 != last indicating a closed link,
    # because 'index()' always return first occurrence, so i1 < last.
    # Thus, if i1 == last, we have an open link.
    # So, there is no 'v2' such that (v0,v1,v2) is a face
    if i1 == last:
      return None

    v2 = link[i1+1]
    return v0, v1, v2

  def __find_up_ordinary(self, v0, v1):
    assert self.vertex(v0).status == ORDINARY_VERTEX

    v2 = None
    guards = self.vertex(v0).guards
    for vg in guards:
      i0 = p0 = None
      links = self.vertex(vg).links
      # get the path and index of v0
      for index, path in enumerate(links):
        if v0 in path:
          i0 = path.index(v0)
          p0 = index
          break

      link = self.vertex(vg).links[p0]

      if vg == v1:
        # closed paths always have previous vertex
        if link[0] == link[-1]:
          if i0 == 0:
            v2 = link[i0 - 2]
          else:
            v2 = link[i0 - 1]
        else: # open path
          if i0 > 0: # there is a previous vertex
            v2 = link[i0 - 1]
          else:
            warning("There is NO previous vertex.")
      else:
        if (i0 + 1) < len(link): # there is a next vertex in this path
          if link[i0+1] == v1:
            v2 = vg
        else:
          warning("There is NO next vertex.")

    if v2 is None:
      warning("Cannot find neighbor face.")
      return None

    return (v0, v1, v2)

  def incident_faces(self, a):
    """Return all incident faces to vertex `a`."""
    v = self.vertex(a)
    if v.status == GUARD_VERTEX:
      return self.__incident_faces_to_guard(a)
    else: # ORDINARY_VERTEX
      return self.__incident_faces_to_ordinary(a)
    
  def __incident_faces_to_guard(self, a):
    """Return all incident faces to guard vertex `a`."""
    assert self.vertex(a).status == GUARD_VERTEX

    faces = []
    for path in self.vertex(a).links:
      for i in range(len(path)-1):
        b = path[i]
        c = path[i+1]
        faces.append( (a, b, c) )
    
    return faces

  # we sort face vertices so as the first vertex of each incident
  # face is always vertex `a` itself.
  def __incident_faces_to_ordinary(self, a):
    """Return all incident faces to ordinary vertex `a`."""
    assert self.vertex(a).status == ORDINARY_VERTEX
    all_around = [] # all faces incident to neighbor guards
    for g in self.vertex(a).guards:
      faces = self.__incident_faces_to_guard(g)
      all_around.extend(faces)

    # Filter `all_around` that have `a` as a vertex
    incidents = set()
    for face in all_around:
      if a in face:
        i = face.index(a)
        incidents.add((face[i], face[ccw(i)], face[cw(i)]))

    return incidents

  # QUERY methods
    
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
    debug("Inserting face (%d, %d, %d)" % (v0,v1,v2))
    # Check if face is guarded.
    # Otherwise, set any of its vertices as guard.
    status = self.vertex(v0).status | \
             self.vertex(v1).status | \
             self.vertex(v2).status
    
    if status == UNGUARDED_FACE:
      self.__guard_face(v0, v1, v2)
    else:
      debug("Face already GUARDED, so no additional guard is needed.")

    self.__insert_face(v0, v1, v2)
    self.__insert_face(v1, v2, v0)
    self.__insert_face(v2, v0, v1)
  
  def __guard_face(self, v0, v1, v2):
    # first, choose a guard
    g  = self.__select_guard(v0, v1, v2)
    vg = self.vertex(g)

    # collect faces incident to vertex `g`
    faces = self.incident_faces(g)

    # we can only set its status at this moment,
    # after collecting its incident faces.
    vg.set_status(GUARD_VERTEX)
    vg.guards.clear() # vertex `g` is now a guard, clear its old guard set

    # insert incident faces to `g` link set
    for f in faces:
      self.__insert_face_into_guard(f[0], f[1], f[2])

    # Now, broadcast the new guard to its ordinary neighbors
    neighbors = set(sum(vg.links, []))
    for n in neighbors:
      vn = self.vertex(n)
      if vn.status == ORDINARY_VERTEX:
        vn.guards.add(g)

  def degree(self, v0):
    k = 0
    for path in self.vertex(v0).links:
      k = k + len(path) - 1

    return k

  def __select_guard(self, v0, v1, v2, policy = GREEDY_POLICY):
    # choose the NEW guard at random
    # TODO: soon, test greedy and other criteria.
    if policy == GREEDY_POLICY:
      d0 = self.degree(v0)
      d1 = self.degree(v1)
      d2 = self.degree(v2)
      i = numpy.argmax([d0, d1, d2])
      v = [v0, v1, v2]
      return v[i]

    return random.choice([v0,v1,v2])


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
    if self.vertex(v0).status == ORDINARY_VERTEX:
      self.__insert_face_into_ordinary(v0,v1,v2)
    else: # GUARD_VERTEX
      self.__insert_face_into_guard(v0,v1,v2)

  # Here, `v0` MUST be a guard
  def __insert_face_into_guard(self, v0, v1, v2):
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
    else:
      if p1 != p2: # case (iii), join paths
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
        # We can only join extreme neighbors. Otherwise, skip.
        if i2 == 0 and (i1+1) == len(links[p1]):
          links[p1].append(v2)
        else:
          warning("Trying to insert face (%d, %d, %d) multiple times." % (v0, v1, v2))
          warning("Nothing done.")

  # Here, `v0` MUST be ordinary
  def __insert_face_into_ordinary(self, v0, v1, v2):
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
    guards = self.vertex(v0).guards

    if self.vertex(v1).status == GUARD_VERTEX:
      guards.add(v1)

    if self.vertex(v2).status == GUARD_VERTEX:
      guards.add(v2)

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
    # First, remove face from guards
    ordinaries = []
    f = [v0, v1, v2]
    for i in range(3):
      if self.vertex(f[i]).status == GUARD_VERTEX:
        self.__remove_face_from_guard(f[i], f[ccw(i)], f[cw(i)])
      else: 
        ordinaries.append(i)

    # Second, update all ordinary guard sets
    for i in ordinaries:
      self.__update_guard_set(f[i])

  def __remove_face_from_guard(self, v0, v1, v2):
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
    assert (i1 is not None) and (i2 is not None), "Cannot remove missing face."

    # both neighbors must be in the same path
    assert p1 == p2, "Cannot remove missing face."

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

    # If link set is empty, make it ordinary (except, for the infinite vertex)
    if len(links) == 0:
      if not self.is_infinite(v0):
        self.vertex(v0).set_status(ORDINARY_VERTEX)
        self.vertex(v0).links.clear()

  # v0 MUST be ordinary
  def __update_guard_set(self, v0):
    inactive = [] # we must remove any inactive guard
    for g in self.vertex(v0).guards:
      # this guard might be inactive, check it out
      if self.vertex(g).status == GUARD_VERTEX:
        guarding = False
        for path in self.vertex(g).links:
          if v0 in path:
            guarding = True
            break
        
        if not guarding:
          inactive.append(g)
      else:
        inactive.append(g)

    # remove all inactive guards
    self.vertex(v0).guards.difference_update(set(inactive))

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
    print('Triangulation:')
    for i in range(self.number_of_vertices):
      if self.vertex(i).status == GUARD_VERTEX:
        print(self.vertex(i).links)
      else:
        print(list(self.vertex(i).guards))

  def statistics(self):
    """\
    Writes to the standard output stream the link sets of all vertices.

    The triangulation data structure is not supposed to have an undelying
    geometry. So, it outputs only the connectivity.

    Parameters
    ----------
      empty : empty
    """
    print('Statistics:')
    print("  > Number of vertices: ", self.number_of_vertices)
    print("  > Number of guards: ", self.number_of_guards)
    print("  > Number of ordinaries: ", self.number_of_ordinaries)
    print("  > Number of references: ", self.number_of_references)
