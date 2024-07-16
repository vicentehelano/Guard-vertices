import numpy
import copy as cp
import random as rd
from queue import Queue

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
import seaborn as sns
sns.set_theme(style="darkgrid")

from .utils import Point, BoundingBox

class Canvas:
  def __init__(self, bbox):
    self.__figure, self.__axes = plt.subplots()
    plt.gca().set_aspect('equal')

    # initialize bounding box
    self.__bbox = bbox

    plt.close(self.__figure)

  def begin(self):
    plt.figure(self.__figure)
    plt.xlim(self.__bbox.min.x, self.__bbox.max.x)
    plt.ylim(self.__bbox.min.y, self.__bbox.max.y)

  def end(self):
    plt.gca().set_aspect('equal')
    plt.gcf().canvas.draw_idle()
    plt.draw()
    plt.waitforbuttonpress(0) # this will wait for indefinite time

  def clear(self):
    plt.clf()

  def draw_circle(self, circles):
    patches = []
    for c in circles:
      circle = Circle(c.center.coords, radius=c.radius)
      patches.append(circle)

    collection = PatchCollection(patches, edgecolor='magenta', facecolor='none', linewidth=2)
    ax = plt.gca()
    ax.add_collection(collection)

  def draw_label(self, label, p):
    plt.annotate(label, xy=p.coords)
  
  def draw_point(self, p):
    plt.plot(p.x, p.y, 'ro', linewidth=3)

  def draw_segment(self, p, q):
    plt.plot([p.x, q.x], [p.y, q.y], 'r-', linewidth=3, zorder=3)

  def draw_triangle(self, p, q, r, filled=False):
    x = [p.x, q.x, r.x]
    y = [p.y, q.y, r.y]

    if filled:
      plt.fill(x, y, 'b', facecolor='magenta', edgecolor='none', alpha=0.2, zorder=1)
    else:
      plt.fill(x, y, 'b', facecolor='none', edgecolor='blue', linewidth=1.5, zorder=2)