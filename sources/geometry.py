# -*- coding: utf-8 -*-
"""\
This is file `geometry.py'.

Geometric primitives, predicates and constructors.

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

# Shewchuck geometric predicates
import geompreds as gp

# Comparison result
SMALLER = -1
EQUAL   = +0
LARGER  = +1

class Point:
  """\
  Representation class of a 2D cartesian point.

  This class provides methods to get and set point coordinates.

  Parameters
  ----------
    x : number type (convertible to float64)
        Point abscissa.
    y : number type (convertible to float64)
        Point ordinate.
          least the following methods:
  """
  def __init__(self, x, y):
    """Constructs a Point from its coordinates."""
    self.__x = numpy.float64(x)
    self.__y = numpy.float64(y)

  def __repr__(self):
    return f"Point({self.__x}, {self.__y})"

  @property
  def x(self):
    """Returns its abscissa."""
    return self.__x

  @property
  def y(self):
    """Returns its ordinate."""
    return self.__y

  @property
  def coords(self):
    """Returns the point coordinates."""
    return (self.__x, self.__y)
  
  def set_coords(self, x, y):
    """Set the point coordinates."""
    self.__x = x
    self.__y = y

  def set_x(self, x):
    """Set the point abscissa."""
    self.__x = x

  def set_y(self, y):
    """Set the point ordinate."""
    self.__y = y

class Circle:
  """\
  Representation class of a 2D circle.

  This class provides methods to get and set circle properties.

  Parameters
  ----------
    center : Point
        The center of the circle.
    radius : number type (convertible to float64)
        The circle radius.
  """
  def __init__(self, center: Point, radius):
    """Constructs a circle with the given center and radius."""
    self.__center = center
    self.__radius = radius

  @property
  def center(self):
    """Returns the circle center."""
    return self.__center
  
  @property
  def radius(self):
    """Returns the circle radius."""
    return self.__radius

class BoundingBox:
  """\
  Representation class of a 2D axis-aligned bounding box.

  This class provides methods to get and set bounding box properties.
  """
  def __init__(self, xmin=-numpy.inf, ymin=-numpy.inf,
                     xmax=numpy.inf, ymax=numpy.inf):
    """Constructs a bounding box, initially, unbounded."""
    self.__min = Point(xmin, ymin)
    self.__max = Point(xmax, ymax)

  def __repr__(self):
    return f"BoundingBox(min.x={self.min.x}, min.y={self.min.y}, " \
                        f"max.x={self.max.x}, max.y={self.max.y})"

  def fit(self, points):
    """Fit the bounding box to the given point set."""
    xmin = xmax = points[0].x
    ymin = ymax = points[0].y
    for p in points[1:]:
      xmin = min(p.x, xmin)
      ymin = min(p.y, ymin)

      xmax = max(p.x, xmax)
      ymax = max(p.y, ymax)

    self.__min = Point(xmin, ymin)
    self.__max = Point(xmax, ymax)

  def expand(self, points):
    """Expand the bounding box so as to contain the given point set."""
    xmin = self.__min.x
    ymin = self.__min.y
    xmax = self.__max.x
    ymax = self.__max.y
    for p in points:
      xmin = min(p.x, xmin)
      ymin = min(p.y, ymin)

      xmax = max(p.x, xmax)
      ymax = max(p.y, ymax)

    self.__min = Point(xmin, ymin)
    self.__max = Point(xmax, ymax)

  def scale(self, scale):
    """Apply a given scale to the bounding box."""
    xmin = self.__min.x
    ymin = self.__min.y
    xmax = self.__max.x
    ymax = self.__max.y

    dx = xmax - xmin
    dy = ymax - ymin

    cx = xmin + dx/2
    cy = ymin + dy/2

    xmin = scale*(xmin - cx) + cx
    ymin = scale*(ymin - cy) + cy
    xmax = scale*(xmax - cx) + cx
    ymax = scale*(ymax - cy) + cy

    self.__min = Point(xmin, ymin)
    self.__max = Point(xmax, ymax)

  @property
  def min(self):
    """Returns the bounding box lower-left corner."""
    return self.__min
  
  @property
  def max(self):
    """Returns the bounding box upper-right corner."""
    return self.__max
  
  def set_min(self, x, y):
    """Sets the bounding box lower-left corner."""
    self.__min = Point(x,y)
  
  def set_max(self, x, y):
    """Sets the bounding box upper-right corner."""
    self.__max = Point(x,y)
      
def __det2(a00, a01, a10, a11):
  """Returns the determinant of a 2x2 matrix."""
  return a00*a11 - a10*a01

def __circumcircle(p, q, r):
  """Computes the circumradius and circumcenter of a non-degenerate \
    triangle (p,q,r)."""
  x_rp = p.x - r.x
  y_rp = p.y - r.y
  x_rq = q.x - r.x
  y_rq = q.y - r.y
  x_pq = q.x - p.x
  y_pq = q.y - p.y

  d_rp = x_rp*x_rp + y_rp*y_rp
  d_rq = x_rq*x_rq + y_rq*y_rq
  d_pq = x_pq*x_pq + y_pq*y_pq

  numx = __det2(d_rp, y_rp, d_rq, y_rq)
  numy = __det2(x_rp, d_rp, x_rq, d_rq)

  den = 0.5 / __det2(x_rp, y_rp, x_rq, y_rq)

  c_x = r.x + numx * den
  c_y = r.y + numy * den

  numr = numpy.sqrt( d_rp * d_rq * d_pq )
  r = numr * den

  return Point(c_x, c_y), r

def circumcircle(p, q, r):
  """\
  Constructs the circumcircle of the triangle (p,q,r).

  This is an implementation of Schewchuk's formulas for the
  computation of the circumcenter and circumradius of a triangle.

  Parameters
  ----------
    p, q, r : Point, Point, Point
        Triangle vertices.

  Returns
  -------
    center : Point
      The circumcenter of the triangle (p,q,r).
    radius : double
      The circumradius of the triangle (p,q,r).

  References
  ----------
  Shewchuk, J. R., Lecture Notes on Robust Geometric Predicates,
    URL: https://people.eecs.berkeley.edu/~jrs/meshpapers/robnotes.pdf
  """
  orient = orientation(p, q, r)
  assert orient != 0 # not COLLINEAR?
  return __circumcircle(p, q, r)

def orientation(p0: Point, p1: Point, p2: Point, p3 = None):
  """A wrapper over Schewchuk's predicates."""
  if p3 is None:
    return numpy.sign(gp.orient2d(p0.coords, p1.coords, p2.coords))
  else:
    return numpy.sign(gp.incircle(p0.coords, p1.coords, p2.coords, p3.coords))
  
def __compare(a, b):
  """Compares two numbers."""
  if (a < b):
    return SMALLER
  if (a > b):
    return LARGER
  return EQUAL

def in_between(p, q, r):
  """\
     """
  """\
  Check if point `r` is strictly between `p` and `q`.

  This function was adapted from its CGAL's counterpart (compare_{x,y}).
  Points are supposed to be collinear.

  Parameters
  ----------
    p, q, r : Point, Point, Point
        Collinear points.

  Returns
  -------
    True if point `r` is strictly between `p` and `q`.
    False, otherwise.
  """
  c_pq = __compare(p.x, q.x)
  c_pr = None
  c_rq = None
  if (c_pq == EQUAL):
    c_pr = __compare(p.y, r.y)
    c_rq = __compare(r.y, q.y)
  else:
    c_pr = __compare(p.x, r.x)
    c_rq = __compare(r.x, q.x)

  return ( (c_pr == SMALLER) and (c_rq == SMALLER) ) or ( (c_pr == LARGER)  and (c_rq == LARGER) )