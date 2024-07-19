# -*- coding: utf-8 -*-
"""\
This is file `test_LinkVertices.py'.

Tests for the LinkVertices class.

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
from sources.links import LinkVertices

def testLinkVertices():
  t = LinkVertices()

  for i in range(9):
    t.create_vertex()

  # infinite faces
  t.insert_face(6,0,3)
  t.insert_face(2,0,6)
  t.insert_face(4,7,0)
  t.insert_face(1,4,0)
  t.insert_face(5,0,2)
  t.insert_face(0,5,1)
  t.insert_face(7,3,0)

  # check if convex hull is OK
  halls = map(str, 2*[1,4,7,3,6,2,5])
  hull  = map(str, t.vertices[0].links[0][:-1])
  assert ''.join(hull) in ''.join(halls)

  # finite faces
  t.insert_face(1,5,4)
  t.insert_face(3,8,6)
  t.insert_face(9,5,2)
  t.insert_face(4,8,7)
  t.insert_face(9,2,6)
  t.insert_face(4,9,8)
  t.insert_face(5,9,4)
  t.insert_face(9,6,8)
  t.insert_face(8,3,7)

  print("BEFORE")
  t.print()

  # remove algumas faces para testar
  # infinite faces
  t.remove_face(6,0,3)
  t.remove_face(2,0,6)
  t.remove_face(4,7,0)
  t.remove_face(1,4,0)
  t.remove_face(5,0,2)
  t.remove_face(0,5,1)
  t.remove_face(7,3,0)

  # finite faces
  t.remove_face(1,5,4)
  t.remove_face(3,8,6)
  t.remove_face(9,5,2)
  t.remove_face(4,8,7)
  t.remove_face(9,2,6)
  t.remove_face(4,9,8)
  t.remove_face(5,9,4)
  t.remove_face(9,6,8)
  t.remove_face(8,3,7)
  print("AFTER")
  t.print()


if __name__ == '__main__':
  testLinkVertices()
