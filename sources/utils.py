# -*- coding: utf-8 -*-
"""\
This is file `utils.py'.

Utility constants, classes and functions.

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

def cw(i):
  return (i-1)%3

def ccw(i):
  return (i+1)%3

class Point: # here
  def __init__(self, x, y):
    self.__x = x
    self.__y = y

  @property
  def x(self):
    return self.__x

  @property
  def y(self):
    return self.__y

  @property
  def coords(self):
    return (self.__x, self.__y)
  
  def set_coords(self, x, y):
    self.__x = x
    self.__y = y

  def set_x(self, x):
    self.__x = x

  def set_y(self, y):
    self.__y = y

class Circle:
  def __init__(self, center: Point, radius):
    self.__center = center
    self.__radius = radius

  @property
  def center(self):
    return self.__center
  
  @property
  def radius(self):
    return self.__radius

class BoundingBox:
  def __init__(self):
    self.__min = Point( numpy.inf,  numpy.inf)
    self.__max = Point(-numpy.inf, -numpy.inf)

  def reshape(self, points):
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

    print("    > Bounding box corners: ")
    print("      | x_min: ", xmin)
    print("      | y_min: ", ymin)
    print("      | x_max: ", xmax)
    print("      | y_max: ", ymax)

  def scale(self, scale):
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
    return self.__min
  
  @property
  def max(self):
    return self.__max
      

def determinant(a00, a01, a10, a11):
  return a00*a11 - a10*a01

def __circumcircle(p, q, r):
  print("    >> circumcircle for points:")
  print("       | p: (%f, %f)" % (p.x, p.y))
  print("       | q: (%f, %f)" % (q.x, q.y))
  print("       | r: (%f, %f)" % (r.x, r.y))
  # compute circumcenter
  x_rp = p.x - r.x
  y_rp = p.y - r.y
  x_rq = q.x - r.x
  y_rq = q.y - r.y
  x_pq = q.x - p.x
  y_pq = q.y - p.y

  d_rp = x_rp*x_rp + y_rp*y_rp
  d_rq = x_rq*x_rq + y_rq*y_rq
  d_pq = x_pq*x_pq + y_pq*y_pq

  numx = determinant(d_rp, y_rp, d_rq, y_rq)
  numy = determinant(x_rp, d_rp, x_rq, d_rq)

  den = 0.5 / determinant(x_rp, y_rp, x_rq, y_rq)

  c_x = r.x + numx * den
  c_y = r.y + numy * den

  numr = numpy.sqrt( d_rp * d_rq * d_pq )
  r = numr * den

  return Point(c_x, c_y), r

# Source: Shewchuk notes on Robust Geometric Predicates
# https://people.eecs.berkeley.edu/~jrs/meshpapers/robnotes.pdf
def circumcircle(p, q, r):
  orient = orientation(p, q, r)
  assert orient != 0 # COLLINEAR
  print("    >> computing circumcircle")
  return __circumcircle(p, q, r)

def orientation(p0: Point, p1: Point, p2: Point, p3 = None):
  if p3 is None:
    return numpy.sign(gp.orient2d(p0.coords, p1.coords, p2.coords))
  else:
    return numpy.sign(gp.incircle(p0.coords, p1.coords, p2.coords, p3.coords))
  
# idea borrowed from CGAL
def __compare(a, b):
  if (a < b):
    return SMALLER
  if (a > b):
    return LARGER
  return EQUAL

# Source: adapted from CGAL's compare_{x,y}
# return true if point r is strictly between p and q
# p, q and r are supposed to be collinear points
def in_between(p, q, r):
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