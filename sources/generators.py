# -*- coding: utf-8 -*-
"""\
This is file `generators.py'.

Random generators of planar point sets.

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
import random

from .utils import Point

def random_points_on_axes(n, rnd = random.random):
  sd = 1.0e-2 # standard deviation  
  half = n // 2
  points = []

  # Points around x-axis
  for i in range(half):
    x = rnd() + sd*rnd()
    y = sd*rnd()
    points.append(Point(x,y))

  # Points around y-axis
  for i in range(half, n):
    x = sd*rnd()
    y = rnd() + sd*rnd()
    points.append(Point(x,y))

  return numpy.array(points)

def random_points_in_square(n, rnd = random.random):
  points = []
  for i in range(n):
    points.append(Point(rnd(), rnd()))
  return numpy.array(points)

def random_points_in_disc(n, rnd = random.random):
  R = 1.0 # radius
  points = []
  for i in range(n):
    theta = 2 * numpy.pi * rnd()
    r = R * numpy.sqrt(rnd())
    x = r * numpy.sin(theta)
    y = r * numpy.cos(theta)

    # add gaussian noise
    sd = 1e-2 # standard deviation
    x = x + sd * rnd()
    y = y + sd * rnd()

    points.append(Point(x,y))

  return numpy.array(points)

def random_points_on_parabola(n, rnd = random.random):
  R = 1.0 # radius
  points = []
  for i in range(n):
    theta = 2 * numpy.pi * rnd()
    r = R * numpy.sqrt(rnd())
    x = r * numpy.sin(theta)
    y = x**2 #r * numpy.cos(theta)
    #z = pow(x, 2) + pow(y, 2)

    # add gaussian noise
    sd = 1e-2 # standard deviation in x
    x = x + sd * rnd()
    y = y + sd * rnd()

    points.append(Point(x,y))

  return numpy.array(points)