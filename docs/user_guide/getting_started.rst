Getting Started
===============

Basic Usage
-----------

xamr provides an xarray-like interface for AMReX simulation data. The main entry point is the :class:`~xamr.AMReXDataset` class:

.. code-block:: python

   import xamr
   
   # Load a single plotfile
   ds = xamr.AMReXDataset("plt00000")
   
   # Access field data
   temperature = ds['temperature']
   velocity_x = ds['x_velocity']
   
   # Get basic information
   print(ds.attrs)
   print(temperature.shape)

Dataset Structure
-----------------

An AMReX dataset contains:

- **Data variables**: Physical fields like temperature, velocity, pressure
- **Coordinates**: Spatial coordinates (x, y, z) and time (for time series)
- **Attributes**: Metadata like domain dimensions, AMR levels, parameters

.. code-block:: python

   # List available fields
   print(list(ds.data_vars.keys()))
   
   # Check coordinate information
   print(ds.coords)
   print(ds.dims)
   
   # Access dataset attributes
   print(f"Max AMR level: {ds.attrs['max_level']}")
   print(f"Domain dimensions: {ds.attrs['domain_dimensions']}")

Working with Fields
-------------------

Fields are accessed as :class:`~xamr.AMReXDataArray` objects:

.. code-block:: python

   temp = ds['temperature']
   
   # Get field statistics
   print(f"Min: {temp.min()}")
   print(f"Max: {temp.max()}")
   print(f"Mean: {temp.mean()}")
   
   # Get numpy array at coarsest level
   temp_array = temp.values()

AMR Levels
----------

xamr works primarily at the coarsest refinement level (level 0) for indexing, but you can access higher levels:

.. code-block:: python

   # Default: coarsest level (level 0)
   temp_coarse = temp.values()
   
   # Higher refinement level
   temp_fine = temp.values(level=2)
   
   # Check available levels
   print(f"Available levels: {ds.levels}")