AMR Visualization
=================

Visualizing AMR Structure
--------------------------

.. code-block:: python

   import xamr
   import numpy as np
   import matplotlib.pyplot as plt
   import matplotlib.patches as patches
   
   ds = xamr.AMReXDataset("plt00000")
   
   # Access yt dataset for AMR structure
   yt_ds = ds._yt_ds
   
   print(f"AMR levels: {ds.levels}")
   print(f"Max level: {ds.attrs['max_level']}")

Plotting Grid Structure
-----------------------

.. code-block:: python

   # Plot AMR grid structure
   fig, ax = plt.subplots(figsize=(12, 10))
   
   # Colors for different levels
   colors = ['blue', 'red', 'green', 'orange', 'purple']
   
   # Plot grids for each level
   for level in range(yt_ds.max_level + 1):
       level_grids = [g for g in yt_ds.index.grids if g.Level == level]
       
       for grid in level_grids:
           left_edge = grid.LeftEdge
           right_edge = grid.RightEdge
           
           # Create rectangle for 2D visualization
           width = right_edge[0] - left_edge[0]
           height = right_edge[1] - left_edge[1]
           
           rect = patches.Rectangle(
               (left_edge[0], left_edge[1]), width, height,
               linewidth=1, edgecolor=colors[level % len(colors)],
               facecolor='none', alpha=0.7
           )
           ax.add_patch(rect)
   
   ax.set_xlim(yt_ds.domain_left_edge[0], yt_ds.domain_right_edge[0])
   ax.set_ylim(yt_ds.domain_left_edge[1], yt_ds.domain_right_edge[1])
   ax.set_aspect('equal')
   ax.set_title('AMR Grid Structure')
   ax.set_xlabel('X')
   ax.set_ylabel('Y')
   
   # Add legend
   handles = [patches.Patch(color=colors[i % len(colors)], label=f'Level {i}') 
              for i in range(yt_ds.max_level + 1)]
   ax.legend(handles=handles)
   
   plt.show()

Multi-Level Data Visualization
------------------------------

.. code-block:: python

   temp = ds['temperature']
   
   # Compare different refinement levels
   fig, axes = plt.subplots(1, 3, figsize=(15, 5))
   
   levels_to_show = [0, min(1, ds.attrs['max_level']), ds.attrs['max_level']]
   
   for i, level in enumerate(levels_to_show):
       try:
           temp_level = temp.values(level=level)
           
           # Take middle slice for 3D data
           if len(temp_level.shape) == 3:
               mid_z = temp_level.shape[0] // 2
               data_slice = temp_level[mid_z, :, :]
           else:
               data_slice = temp_level
           
           im = axes[i].imshow(data_slice, cmap='hot', origin='lower')
           axes[i].set_title(f'Level {level} ({data_slice.shape[0]}x{data_slice.shape[1]})')
           axes[i].set_aspect('equal')
           plt.colorbar(im, ax=axes[i])
           
       except ValueError as e:
           axes[i].text(0.5, 0.5, f'Level {level}\nNot Available', 
                       ha='center', va='center', transform=axes[i].transAxes)
           axes[i].set_title(f'Level {level} (Not Available)')
   
   plt.tight_layout()
   plt.show()

AMR-aware Calculations Visualization
------------------------------------

.. code-block:: python

   # Calculate gradients using AMR-aware methods
   dT_dx = ds.calc.gradient('temperature', 'x')
   dT_dy = ds.calc.gradient('temperature', 'y')
   
   # Get coarsest level for visualization
   temp_coarse = temp.values(level=0)
   grad_x_coarse = dT_dx.values(level=0)
   grad_y_coarse = dT_dy.values(level=0)
   
   # Take middle slice if 3D
   if len(temp_coarse.shape) == 3:
       mid_z = temp_coarse.shape[0] // 2
       temp_slice = temp_coarse[mid_z, :, :]
       grad_x_slice = grad_x_coarse[mid_z, :, :]
       grad_y_slice = grad_y_coarse[mid_z, :, :]
   else:
       temp_slice = temp_coarse
       grad_x_slice = grad_x_coarse
       grad_y_slice = grad_y_coarse
   
   # Calculate gradient magnitude
   grad_magnitude = np.sqrt(grad_x_slice**2 + grad_y_slice**2)
   
   fig, axes = plt.subplots(2, 2, figsize=(12, 10))
   
   # Temperature
   im1 = axes[0,0].imshow(temp_slice, cmap='hot', origin='lower')
   axes[0,0].set_title('Temperature')
   plt.colorbar(im1, ax=axes[0,0])
   
   # X gradient
   im2 = axes[0,1].imshow(grad_x_slice, cmap='RdBu_r', origin='lower')
   axes[0,1].set_title('dT/dx')
   plt.colorbar(im2, ax=axes[0,1])
   
   # Y gradient
   im3 = axes[1,0].imshow(grad_y_slice, cmap='RdBu_r', origin='lower')
   axes[1,0].set_title('dT/dy')
   plt.colorbar(im3, ax=axes[1,0])
   
   # Gradient magnitude
   im4 = axes[1,1].imshow(grad_magnitude, cmap='viridis', origin='lower')
   axes[1,1].set_title('|∇T|')
   plt.colorbar(im4, ax=axes[1,1])
   
   plt.tight_layout()
   plt.show()

Refinement Criteria Visualization
----------------------------------

.. code-block:: python

   # Identify regions with high refinement
   # (areas where higher levels exist)
   
   domain_left = yt_ds.domain_left_edge
   domain_right = yt_ds.domain_right_edge
   domain_dims = yt_ds.domain_dimensions
   
   # Create refinement level map
   refinement_map = np.zeros((domain_dims[1], domain_dims[0]))
   
   for level in range(yt_ds.max_level + 1):
       level_grids = [g for g in yt_ds.index.grids if g.Level == level]
       
       for grid in level_grids:
           # Convert physical coordinates to grid indices
           left_edge = grid.LeftEdge
           right_edge = grid.RightEdge
           
           # Map to coarse grid indices
           i_start = int((left_edge[0] - domain_left[0]) / 
                        (domain_right[0] - domain_left[0]) * domain_dims[0])
           i_end = int((right_edge[0] - domain_left[0]) / 
                      (domain_right[0] - domain_left[0]) * domain_dims[0])
           j_start = int((left_edge[1] - domain_left[1]) / 
                        (domain_right[1] - domain_left[1]) * domain_dims[1])
           j_end = int((right_edge[1] - domain_left[1]) / 
                      (domain_right[1] - domain_left[1]) * domain_dims[1])
           
           # Ensure bounds
           i_start = max(0, min(i_start, domain_dims[0]-1))
           i_end = max(0, min(i_end, domain_dims[0]))
           j_start = max(0, min(j_start, domain_dims[1]-1))
           j_end = max(0, min(j_end, domain_dims[1]))
           
           refinement_map[j_start:j_end, i_start:i_end] = max(
               refinement_map[j_start:j_end, i_start:i_end].max(), level
           )
   
   fig, axes = plt.subplots(1, 2, figsize=(15, 6))
   
   # Temperature
   im1 = axes[0].imshow(temp_slice, cmap='hot', origin='lower')
   axes[0].set_title('Temperature')
   plt.colorbar(im1, ax=axes[0])
   
   # Refinement level map
   im2 = axes[1].imshow(refinement_map, cmap='viridis', origin='lower')
   axes[1].set_title('AMR Refinement Level')
   plt.colorbar(im2, ax=axes[1])
   
   plt.tight_layout()
   plt.show()
   
   print(f"Refinement statistics:")
   for level in range(yt_ds.max_level + 1):
       count = np.sum(refinement_map == level)
       percentage = count / refinement_map.size * 100
       print(f"  Level {level}: {count} cells ({percentage:.1f}%)")