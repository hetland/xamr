Time Series Data
================

Loading Multiple Files
-----------------------

xamr can load time series data from multiple plotfiles:

.. code-block:: python

   import xamr
   
   # Using glob pattern
   ds = xamr.AMReXDataset("plt*")
   
   # Using explicit file list
   ds = xamr.AMReXDataset(["plt00000", "plt00001", "plt00002"])

Files are automatically sorted by simulation time, regardless of the input order.

Time Dimension
--------------

When multiple files are loaded, time becomes the leftmost dimension:

.. code-block:: python

   temp = ds['temperature']
   
   # Check dimensions
   print(temp.dims)      # ['time', 'z', 'y', 'x'] for 3D
   print(temp.shape)     # (n_times, nz, ny, nx)
   
   # Access time coordinates
   print(ds.coords['time'])
   print(f"Number of time steps: {ds.attrs['n_timesteps']}")

Time-based Indexing
-------------------

With time series data, indexing follows the pattern ``[time, z, y, x]``:

.. code-block:: python

   # Single time step
   temp_t0 = temp[0, :, :, :]     # First time step, all spatial points
   temp_t1 = temp[1, :, :, :]     # Second time step
   
   # Specific point over time
   temp_series = temp[:, 10, 20, 30]  # All times, specific spatial point
   
   # Time slice
   temp_range = temp[5:10, :, :, :]   # Time steps 5-9

Temporal Analysis
-----------------

Analyze how fields evolve over time:

.. code-block:: python

   # Temperature at a specific point over time
   point_temp = temp[:, 50, 50, 50]
   
   # Maximum temperature at each time step
   max_temps = [temp[t, :, :, :].max() for t in range(len(ds.coords['time']))]
   
   # Average temperature evolution
   mean_temps = [temp[t, :, :, :].mean() for t in range(len(ds.coords['time']))]

Mixing Single and Time Series
-----------------------------

The same code works for both single files and time series:

.. code-block:: python

   # This works for both single files and time series
   def analyze_temperature(dataset):
       temp = dataset['temperature']
       
       if len(dataset._times) > 1:
           # Time series: analyze evolution
           return temp[:, :, :, :].mean(axis=(1,2,3))  # Mean temp per time step
       else:
           # Single file: analyze spatial distribution
           return temp.values().mean()  # Overall mean temperature