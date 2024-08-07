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

#from sources.canvas import Canvas
#from sources.geometry import BoundingBox
from sources.generators import *
#from sources.brio.kdtree import KdTree, Node
#from sources.log import *
from sources.brio import Brio
from sources.brio import BRIO_KDTREE, BRIO_HILBERT, BRIO_NONE, BRIO_RANDOM

def testBrio():
  generate = Generator()
  points = generate.uniform_distribution(64)
  xpoints = [Point(2.880, -64.490),
    Point(22.320, -56.810),
    Point(38.640, -64.730),
    Point(47.520, -50.090),
    Point(64.920, -40.490),
    Point(66.480, -19.730),
    Point(90.840, -4.010),
    Point(98.280, -43.730),
    Point(102.840, -70.970),
    Point(119.760, -59.810),
    Point(125.400, -17.330),
    Point(142.680, -44.330),
    Point(162.480, -22.130),
    Point(182.400, -11.450),
    Point(199.680, -18.770)]

  brio = Brio(BRIO_KDTREE)
  brio(points)

if __name__ == '__main__':
  testBrio()
