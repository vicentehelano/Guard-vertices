# -*- coding: utf-8 -*-
"""\
This is file `test_DelaunayTriangulation.py'.

Tests for the DelaunayTriangulation class.

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

from sources.utils import Point
from sources.links import LinkVertices
from sources.delaunay import DelaunayTriangulation

def exampleBlandford():
  points = [ Point(0.0, 1.0),
             Point(3.0, 0.0),
             Point(6.0, 1.0),
             Point(9.0, 0.0),
             Point(9.0, 2.0),
             Point(6.0, 3.0),
             Point(3.0, 2.0),
             Point(3.0, 4.0),
             Point(9.0, 4.0) ]
  return numpy.array(points)

def testDelaunayTriangulation():
  Dt = DelaunayTriangulation(LinkVertices)
  points = exampleBlandford()
  Dt.insert(points)
  Dt.draw()
  

if __name__ == '__main__':
  testDelaunayTriangulation()
