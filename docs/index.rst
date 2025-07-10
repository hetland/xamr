xamr: xarray-like interface for AMReX data
==========================================

**xamr** provides an xarray-like interface for AMReX simulation data via yt, offering:

- Native AMR (Adaptive Mesh Refinement) structure access
- Time series support from multiple plotfiles  
- Intuitive indexing at the coarsest refinement level
- Spatial and temporal selection methods
- AMR-aware calculations and derivatives

Quick Start
-----------

.. code-block:: python

   import xamr
   
   # Load single plotfile
   ds = xamr.AMReXDataset("plt00000")
   
   # Load time series
   ds = xamr.AMReXDataset("plt*")
   temp = ds['temperature']
   
   # Index data (time-first for time series)
   temp_point = temp[0, 10, 20]      # time=0, z=10, y=20
   temp_slice = temp[0, :, :]        # time=0, all z,y
   temp_series = temp[:, 10, 20]     # all times, specific point

Features
--------

**Time Series Support**
   Load multiple plotfiles representing different time steps with automatic time sorting.

**AMR-Aware Indexing**
   Index directly into simulation data at the coarsest level with numpy-like syntax.

**xarray-like Interface**
   Familiar data access patterns with ``.sel()``, ``.values()``, and coordinate information.

**Native AMR Operations**
   Calculate gradients, divergence, and vorticity that respect the AMR structure.

Installation
------------

.. code-block:: bash

   pip install xamr

Requirements:
- yt >= 4.0
- numpy
- Python >= 3.8

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   user_guide/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/index

.. toctree::
   :maxdepth: 1
   :caption: Examples:

   examples/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`