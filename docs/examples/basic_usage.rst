Basic Usage Examples
====================

Loading and Exploring Data
---------------------------

.. code-block:: python

   import xamr
   import numpy as np
   import matplotlib.pyplot as plt
   
   # Load a single plotfile
   ds = xamr.AMReXDataset("plt00000")
   
   # Explore the dataset
   print("Available fields:", list(ds.data_vars.keys()))
   print("Dataset info:", ds.attrs)
   print("AMR levels:", ds.levels)

Working with Fields
-------------------

.. code-block:: python

   # Access temperature field
   temp = ds['temperature']
   
   # Basic statistics
   print(f"Temperature range: {temp.min():.2f} to {temp.max():.2f}")
   print(f"Mean temperature: {temp.mean():.2f}")
   print(f"Data shape: {temp.shape}")

Simple Visualization
--------------------

.. code-block:: python

   # Get 2D slice at middle z-level
   nz = temp.shape[0] if len(temp.shape) == 3 else temp.shape[1]
   mid_z = nz // 2
   
   if len(temp.shape) == 3:  # 3D data
       temp_slice = temp[mid_z, :, :]
   else:  # 2D data  
       temp_slice = temp[:, :]
   
   # Plot
   plt.figure(figsize=(10, 8))
   plt.imshow(temp_slice, origin='lower', cmap='hot')
   plt.colorbar(label='Temperature')
   plt.title('Temperature Field')
   plt.show()

Comparing Fields
----------------

.. code-block:: python

   # Load multiple fields
   temp = ds['temperature']
   pressure = ds['pressure'] if 'pressure' in ds.data_vars else None
   
   if pressure is not None:
       # Extract values at same location
       temp_vals = temp.values()
       pres_vals = pressure.values()
       
       # Flatten for scatter plot
       temp_flat = temp_vals.flatten()
       pres_flat = pres_vals.flatten()
       
       # Temperature vs pressure scatter plot
       plt.figure(figsize=(8, 6))
       plt.scatter(temp_flat[::100], pres_flat[::100], alpha=0.5)
       plt.xlabel('Temperature')
       plt.ylabel('Pressure')
       plt.title('Temperature vs Pressure')
       plt.show()

Extracting Line Profiles
-------------------------

.. code-block:: python

   # Extract temperature along a line (e.g., x-direction at center)
   ny, nx = temp.shape[-2:]
   center_y = ny // 2
   
   if len(temp.shape) == 3:  # 3D
       center_z = temp.shape[0] // 2
       line_profile = temp[center_z, center_y, :]
   else:  # 2D
       line_profile = temp[center_y, :]
   
   # Plot line profile
   plt.figure(figsize=(10, 6))
   plt.plot(line_profile)
   plt.xlabel('Grid Point (x-direction)')
   plt.ylabel('Temperature')
   plt.title('Temperature Profile')
   plt.grid(True)
   plt.show()

Working with Coordinates
------------------------

.. code-block:: python

   # Access coordinate information
   print("Coordinate ranges:")
   for dim in ['x', 'y', 'z']:
       if f'{dim}_range' in ds.coords:
           x_min, x_max = ds.coords[f'{dim}_range']
           print(f"  {dim}: {x_min:.3f} to {x_max:.3f}")
   
   # Create physical coordinate arrays
   if 'x' in ds.coords:
       x_coords = ds.coords['x']
       y_coords = ds.coords['y']
       
       # Plot with physical coordinates
       plt.figure(figsize=(10, 8))
       plt.imshow(temp_slice, extent=[x_coords.min(), x_coords.max(), 
                                     y_coords.min(), y_coords.max()],
                  origin='lower', cmap='hot')
       plt.colorbar(label='Temperature')
       plt.xlabel('X coordinate')
       plt.ylabel('Y coordinate')
       plt.title('Temperature Field (Physical Coordinates)')
       plt.show()