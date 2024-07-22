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

class Generator:
  """\
  Random point set generator.

  Creates an object with methods to generate random point sets with a given
  random number generator.
  A single generator can generate points on the principal axes
  (random_points_on_axes), points in a square (random_points_in_square), points
  in a disc (random_points_in_disc) and points on a parabola
  (random_points_on_parabola).

  Parameters
  ----------
    rnd : random number generator (default: random.random)

  Examples
  --------
  >>> generate = Generator()
  >>> generate.random_points_on_axes(10)
  """
  def __init__(self, rnd = random.random):
    """Initializes the Generator class."""
    self.__random = rnd

  def random(self):
    """Random number generator."""
    return self.__random()

  def random_points_in_square(self, n):
    """\
    Generate points in the unit square [0,1]^2.

    The algorithm draws floating points numbers for each coordinate in the
    interval [0,1] using the underlying random point generator.

    Parameters
    ----------
      n : (int)
        The number of points to be generated.

    Returns
    --------
      points : numpy.array
        An array of random points.
    """
    points = []
    for i in range(n):
      points.append(Point(self.random(), self.random()))
    return numpy.array(points)

  def random_points_on_axes(self, n, sd = 1.0e-2):
    """\
    Generate points around the principal axes.

    Points are generated along the principal axes perturbed by a gaussian
    noise with custom standard deviation `sd`.

    Parameters
    ----------
      n  : (int)
        Number of points to be generated.
      sd : (double)
        Standard deviation for the gaussian noise.

    Returns
    --------
      points : numpy.array
        An array of random points.
    """
    half = n // 2
    points = []

    # Points around x-axis
    for i in range(half):
      x = self.random() + sd*self.random()
      y = sd*self.random()
      points.append(Point(x,y))

    # Points around y-axis
    for i in range(half, n):
      x = sd*self.random()
      y = self.random() + sd*self.random()
      points.append(Point(x,y))

    return numpy.array(points)

  def random_points_in_disc(self, n, sd = 1.0e-2):
    """\
    Generate points in the unit disc.

    Points are generated in the unit disc centered at (0,0) using polar
    coordinates perturbed by a gaussian noise with custom standard
    deviation `sd`.

    Parameters
    ----------
      n  : (int)
        Number of points to be generated.
      sd : (double)
        Standard deviation for the gaussian noise.

    Returns
    --------
      points : numpy.array
        An array of random points.

    References
    ----------
    Andreas Lundblad, How to generate a random point within a circle of radius R, 2018.
    URL: https://stackoverflow.com/questions/5837572/generate-a-random-point-within-a-circle-uniformly/50746409#50746409
    """
    R = 1.0 # radius
    points = []
    for i in range(n):
      theta = 2 * numpy.pi * self.random()
      r = R * numpy.sqrt(self.random())
      x = r * numpy.cos(theta)
      y = r * numpy.sin(theta)

      # add gaussian noise with standard deviation `sd`
      x = x + sd * self.random()
      y = y + sd * self.random()

      points.append(Point(x,y))

    return numpy.array(points)

  def random_points_on_parabola(self, n, sd = 1.0e-2):
    """\
    Generate points around a parabola.

    Points are generated around a parabola as cut of the 3D paraboloid.
    We use polar coordinates and gaussian noise with standard deviation `sd`,
    as in the disc generator.

    Parameters
    ----------
      n  : (int)
        Number of points to be generated.
      sd : (double)
        Standard deviation for the gaussian noise.

    Returns
    --------
      points : numpy.array
        An array of random points.
    """
    R = 1.0 # radius
    points = []
    for i in range(n):
      theta = 2 * numpy.pi * self.random()
      r = R * numpy.sqrt(self.random())
      x = r * numpy.cos(theta)
      y = x**2

      # add gaussian noise with standard deviation `sd`
      x = x + sd * self.random()
      y = y + sd * self.random()

      points.append(Point(x,y))

    return numpy.array(points)