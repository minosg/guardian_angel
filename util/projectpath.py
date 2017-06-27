#!/usr/bin/env python

"""projectpath.py: Relative PEP8 import project path helper ..."""

import os
import sys
import inspect

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "codename"
__date__ = "27-06-2017"

importer = inspect.getframeinfo(inspect.getouterframes(inspect.currentframe()))

# Get the folder name that contains the projectpath file
f_path = os.path.join(os.path.dirname(__file__))
f_path = os.path.split(f_path)[1]

# List all the folders that contain modules
include_path = ["util", "messenger", "zero"]

# Correctly set the relative path based on current file folder
dirc = ".." if f_path in include_path else "."

# Include the path to the project
for pth in include_path:
    sys.path.insert(0, '%s/%s' % (dirc, pth))
