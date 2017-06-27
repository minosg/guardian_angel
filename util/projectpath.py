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

max_depth = 3
include_path = ["util", "messenger", "zero", "node"]
iframe = inspect.getouterframes(inspect.currentframe())
if len(iframe) > 1:
    frame_idx = 1
else:
    frame_idx = 0
# Find the name of the file calling the import
importer = inspect.getframeinfo(iframe[frame_idx][0])[0]
importer = os.path.split(importer)[1]

# Get the directory that the import happens
f_path = os.path.join(os.path.dirname(__file__))

cwd = "./"
for n in range(max_depth + 1):
    if set(include_path).issubset(os.listdir(cwd)):
        break

    cwd = os.path.join("../", cwd)
    if n == max_depth:
        raise ValueError("Could not find %s module in %d steps" % (importer,
                                                                   max_depth))

# Include the path to the project
for pth in include_path:
    imp_path = os.path.join(cwd, pth)
    sys.path.insert(0, imp_path)
