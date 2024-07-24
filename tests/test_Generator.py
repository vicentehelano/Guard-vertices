# -*- coding: utf-8 -*-
"""\
This is file `test_Generator.py'.

Tests for the random points generators.

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
import matplotlib.pyplot as plt

from sources.canvas import Canvas
from sources.geometry import BoundingBox
from sources.generators import *

def testGenerator():
  n = int(input("Enter the desired number of points: "))

  generate = Generator()
  points = generate.random_points_on_axes(n)
  bbox = BoundingBox()
  bbox.expand(points)
  bbox.scale(1.25)
  canvas = Canvas(bbox)

  canvas.begin()
  for p in points:
    canvas.draw_point(p)
  canvas.end()
  canvas.close()

  points = generate.random_points_in_square(n)
  bbox = BoundingBox()
  bbox.expand(points)
  bbox.scale(1.25)
  canvas = Canvas(bbox)

  canvas.begin()
  for p in points:
    canvas.draw_point(p)
  canvas.end()
  canvas.close()

  points = generate.random_points_in_disc(n)
  bbox = BoundingBox()
  bbox.expand(points)
  bbox.scale(1.25)
  canvas = Canvas(bbox)

  canvas.begin()
  for p in points:
    canvas.draw_point(p)
  canvas.end()
  canvas.close()

  points = generate.random_points_on_parabola(n)
  bbox = BoundingBox()
  bbox.expand(points)
  bbox.scale(1.25)
  canvas = Canvas(bbox)

  canvas.begin()
  for p in points:
    canvas.draw_point(p)
  canvas.end()
  canvas.close()

if __name__ == '__main__':
  testGenerator()
