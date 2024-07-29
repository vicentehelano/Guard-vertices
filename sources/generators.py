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

from .geometry import Point

class Generator:
  """\
  Synthetic point set generator.

  This class has methods to generate the following point sets:
    - points uniformly distributed in the unit square [0,1)^2;
    - points normally distributed in the unit square [0,1)^2;
    - points distributed according to the Kuzmin distribution;
    - points distributed along the line segment [0,1).

  Parameters
  ----------
    seed : int (default: None)
      A seed for the random number generator.

  Examples
  --------
  >>> generate = Generator()
  >>> generate.uniform_distribution(10)

  References
  ----------
    BLELLOCH, Guy E. et al. Design and implementation of a practical parallel
      Delaunay algorithm. Algorithmica, v. 24, p. 243-269, 1999.
  """
  def __init__(self, seed = None):
    """Initializes the Generator class."""
    self.__seed = seed
    self.__random  = numpy.random.default_rng(seed)

  @property
  def seed(self):
    """Returns a reference to the generator seed."""
    return self.__seed
  
  @property
  def random(self):
    """Returns a reference to the random number generator."""
    return self.__random

  def uniform(self):
    """Draws random samples from a uniform distribution."""
    return self.random.uniform()
  
  def normal(self):
    """Draws random samples from a normal distribution."""
    return self.random.normal()

  def uniform_distribution(self, n):
    """\
    Generate points uniformly in the unit square [0,1)^2.

    The algorithm draws floating points numbers for each coordinate in the
    interval [0,1) using `numpy` uniform generator.

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
      points.append(Point(self.uniform(), self.uniform()))
    return numpy.array(points)
  
  def normal_distribution(self, n):
    """\
    Generate points normally in the unit square [0,1)^2.

    The algorithm draws floating points numbers for each coordinate in the
    interval [0,1) using `numpy` normal generator.

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
      points.append(Point(self.normal(), self.normal()))
    return numpy.array(points)

  def __kuzmin_radius(self):
    """Kuzmin radius generator."""
    X = self.uniform()
    return numpy.sqrt( (1.0/(1.0 - X))**2 - 1 )

  def kuzmin_distribution(self, n):
    """\
    Generate points according to the Kuzmin distribution.

    This is a normalized implementation of the Kuzmin distribution defined
    by Blelloch et al. (1999).

    Parameters
    ----------
      n : (int)
        The number of points to be generated.

    Returns
    --------
      points : numpy.array
        An array of random points.

    References
    ----------
      Blelloch, Guy E. et al. Design and implementation of a practical parallel
        Delaunay algorithm. Algorithmica, v. 24, p. 243-269, 1999.
    """
    s = 0.0
    points = []
    while len(points) < n:
      theta = 2 * numpy.pi * self.uniform()
      r = self.__kuzmin_radius()
      x = r * numpy.cos(theta)
      y = r * numpy.sin(theta)
      points.append(Point(x,y))
      s = max(r, s) # inverse scale
      
    # apply scale so as to get points inside unit disk
    for p in points:
      p.set_coords(p.x/s, p.y/s)

    return numpy.array(points)
  
  def line_distribution(self, n, b = 0.001):
    """\
    Generate points according to the Line distribution.

    This is an implementation of the Line distribution defined in the paper
    of Blelloch et al. (1999).

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
      Blelloch, Guy E. et al. Design and implementation of a practical parallel
        Delaunay algorithm. Algorithmica, v. 24, p. 243-269, 1999.
    """
    points = []
    for i in range(n):
      u = self.uniform()
      v = self.uniform()
      x = u
      y = b/(v - b*v + b)
      points.append(Point(x,y))
      
    return numpy.array(points)