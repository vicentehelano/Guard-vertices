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
    """Print message to the standard output stream."""
    print(msg)

def debug(msg):
    """Show debug message in the standard output stream."""
    if __debug__:
        __log("Debug: " + msg)

def info(msg):
    """Show info message in the standard output stream."""
    __log("Info: " + msg)

def warning(msg):
    """Show warning message in the standard output stream."""
    __log("Warning: " + msg)

def error(msg):
    """Show error message in the standard output stream."""
    __log("Error: " + msg)