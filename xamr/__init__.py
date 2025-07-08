"""
xamr: xarray-like interface for AMReX data via yt
"""

from .core import AMReXDataset, AMReXDataArray, AMReXCalculations
from .utils import open_amrex

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = ["AMReXDataset", "AMReXDataArray", "AMReXCalculations", "open_amrex"]
