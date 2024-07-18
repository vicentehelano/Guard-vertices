# -*- coding: utf-8 -*-
"""
Automatically generated by Colab.

Tips: 
  1. Configuration of Workspace: https://k0nze.dev/posts/python-relative-imports-vscode/#:%7E:text=Inside%20the-,launch.json,-you%20have%20to
"""
import numpy

from sources.utils import Point
from sources.stars import StarVertices
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

def exampleDelaunayTriangulation():
  Dt = DelaunayTriangulation(StarVertices)
  points = exampleBlandford()
  Dt.visual_insert(points)

if __name__ == '__main__':
  exampleDelaunayTriangulation()
