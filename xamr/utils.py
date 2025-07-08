"""
Utility functions for xamr package
"""

from .core import AMReXDataset


def open_amrex(filename: str) -> AMReXDataset:
    """
    Open an AMReX plot file and return a xamr dataset.
    
    Parameters
    ----------
    filename : str
        Path to the AMReX plot file
        
    Returns
    -------
    AMReXDataset
        Dataset with xarray-like interface
        
    Examples
    --------
    >>> ds = open_amrex('plt00100')
    >>> temp = ds['temperature']
    >>> print(temp.mean())
    """
    return AMReXDataset(filename)
