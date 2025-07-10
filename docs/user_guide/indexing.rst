Indexing and Selection
======================

Basic Indexing
--------------

xamr supports numpy-like indexing at the coarsest AMR level:

.. code-block:: python

   import xamr
   
   ds = xamr.AMReXDataset("plt00000")
   temp = ds['temperature']
   
   # Point indexing (3D: z, y, x)
   temp_point = temp[10, 20, 30]
   
   # 2D case (y, x)
   temp_point_2d = temp[20, 30]

Slicing
-------

Use slices to extract regions:

.. code-block:: python

   # Slice along each dimension
   temp_slice = temp[10:20, :, 50:100]  # z=10-19, all y, x=50-99
   
   # Extract a 2D slice
   xy_slice = temp[25, :, :]            # z=25, all y and x
   yz_slice = temp[:, :, 50]            # x=50, all z and y

Time Series Indexing
--------------------

For time series data, time is the leftmost index:

.. code-block:: python

   ds = xamr.AMReXDataset("plt*")
   temp = ds['temperature']
   
   # Time + spatial indexing
   temp_point = temp[0, 10, 20, 30]     # time=0, z=10, y=20, x=30
   temp_slice = temp[0, :, :, :]        # time=0, all spatial points
   
   # Time evolution at a point
   temp_evolution = temp[:, 10, 20, 30] # all times, specific point
   
   # Time slice
   temp_subset = temp[5:10, :, :, :]    # times 5-9, all spatial

Advanced Selection
------------------

Use the ``.sel()`` method for more sophisticated selection:

.. code-block:: python

   # Spatial region selection
   region = temp.spatial_select(
       x=slice(0.0, 1.0),
       y=slice(0.0, 0.5)
   )
   
   # Alternative syntax
   region = temp.sel(x=slice(0.0, 1.0), y=slice(0.0, 0.5))

Level Selection
---------------

Select specific AMR levels:

.. code-block:: python

   # Select specific refinement level
   temp_level2 = temp.level_select(2)
   
   # Multiple levels
   temp_levels = temp.level_select([0, 1, 2])

Error Handling
--------------

xamr validates indexing operations:

.. code-block:: python

   # Too many indices
   try:
       temp[0, 1, 2, 3, 4]  # Error for 3D data
   except IndexError as e:
       print(f"IndexError: {e}")
   
   # Out of bounds
   try:
       temp[1000, 1000, 1000]  # Error if indices exceed array size
   except IndexError as e:
       print(f"IndexError: {e}")

Performance Tips
----------------

- Indexing operates on the coarsest level for speed
- Use ``.values()`` to get numpy arrays for intensive computation
- Cache frequently accessed slices
- Use spatial selection for large regions rather than explicit slicing

.. code-block:: python

   # Efficient: get numpy array once
   temp_array = temp.values()
   point1 = temp_array[10, 20, 30]
   point2 = temp_array[11, 20, 30]
   
   # Less efficient: repeated indexing
   point1 = temp[10, 20, 30]
   point2 = temp[11, 20, 30]