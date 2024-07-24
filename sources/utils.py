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
def cw(i):
  """Returns the next index after `i` in a clockwise (backward) circular permutation."""
  return (i-1)%3

def ccw(i):
  """Returns the next index after `i` in a counter-clockwise (forward) circular permutation."""
  return (i+1)%3