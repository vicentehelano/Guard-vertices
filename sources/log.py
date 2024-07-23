# -*- coding: utf-8 -*-
"""\
This is file `log.py'.

Simple functions to do logging.

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
def __log(msg):
    print(msg)

def debug(msg):
    if __debug__:
        __log("Debug: " + msg)

def info(msg):
    __log("Info: " + msg)

def warning(msg):
    __log("Warning: " + msg)

def error(msg):
    __log("Error: " + msg)