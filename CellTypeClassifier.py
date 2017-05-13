# -*- coding utf-8 -*-

# This script allows to use a scikit-learn.org classifier (supervised or unsupervised),
# in order to sort kilosort/phy generated units according to their cell type
# using their features, extracted thanks to the DataManager class written in FeaturesExtraction.py.

# Maxime Beau, 2017-05-10

__title__ = 'CellTypeClassifier'
__package_name__ = 'CtClass'
__author__ = 'Maxime Beau'
__email__ = 'm.beau047@gmail.com'

import FeaturesExtraction as fe

import numpy as np

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

import os, sys
sys.path.append("/Users/maximebeau/phy")
from phy.utils._types import _as_array
from phy.io.array import _index_of, _unique


