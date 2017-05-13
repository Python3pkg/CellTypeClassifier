# -*- coding: utf-8 -*-

"""Kilosort/phy generated units classification by cell type."""


#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import numpy as np
from scipy import signal

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

import os, sys
sys.path.append("/Users/maximebeau/phy")
from phy.utils._types import _as_array # phy, kwikteam
from phy.io.array import _index_of, _unique # phy, kwikteam

#------------------------------------------------------------------------------
# Global variables and functions
#------------------------------------------------------------------------------

__title__ = 'Units Features Exctraction'
__package_name__ = 'FeaturesExtraction'
__author__ = 'Maxime Beau'
__email__ = 'm.beau047@gmail.com'
