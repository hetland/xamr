AMR-Aware Calculations
======================

Overview
--------

xamr provides AMR-aware calculations through the ``.calc`` property. These operations respect the adaptive mesh refinement structure across all levels.

.. code-block:: python

   import xamr
   
   ds = xamr.AMReXDataset("plt00000")
   
   # Access calculations
   calc = ds.calc

Gradient Calculations
---------------------

Calculate gradients that properly handle AMR boundaries:

.. code-block:: python

   # Temperature gradients
   dT_dx = calc.gradient('temperature', 'x')
   dT_dy = calc.gradient('temperature', 'y')
   dT_dz = calc.gradient('temperature', 'z')
   
   # Access gradient values
   grad_x_values = dT_dx.values()
   
   # Gradients are AMReXDataArray objects
   print(f"Max gradient: {dT_dx.max()}")
   print(f"Min gradient: {dT_dx.min()}")

Divergence
----------

Calculate divergence of vector fields:

.. code-block:: python

   # Velocity divergence
   div_v = calc.divergence('x_velocity', 'y_velocity', 'z_velocity')
   
   # 2D case (no z-component)
   div_v_2d = calc.divergence('x_velocity', 'y_velocity')
   
   # Check for incompressible flow
   max_div = div_v.max()
   print(f"Maximum divergence: {max_div}")

Vorticity
---------

Calculate vertical vorticity (curl of velocity field):

.. code-block:: python

   # Vertical vorticity (∂v/∂x - ∂u/∂y)
   vorticity = calc.vorticity('x_velocity', 'y_velocity')
   
   # Find regions of high vorticity
   high_vort = vorticity.values() > 0.1

Working with Derived Fields
---------------------------

Calculated fields become part of the dataset:

.. code-block:: python

   # Calculate gradient
   dT_dx = calc.gradient('temperature', 'x')
   
   # The derived field is now available
   print('gradient_temperature_x' in ds.data_vars)  # True
   
   # Access it directly
   grad_field = ds['gradient_temperature_x']
   
   # Use like any other field
   grad_values = grad_field.values()
   grad_max = grad_field.max()

Time Series Calculations
------------------------

Calculations work with time series data:

.. code-block:: python

   ds = xamr.AMReXDataset("plt*")
   
   # Calculate gradient for all time steps
   dT_dx = ds.calc.gradient('temperature', 'x')
   
   # Access time evolution of gradient
   grad_evolution = dT_dx[:, 50, 50, 50]  # Gradient at point over time

Advanced Examples
-----------------

Combine calculations for complex analysis:

.. code-block:: python

   # Thermal diffusion analysis
   dT_dx = calc.gradient('temperature', 'x')
   dT_dy = calc.gradient('temperature', 'y')
   
   # Magnitude of temperature gradient
   grad_magnitude = np.sqrt(dT_dx.values()**2 + dT_dy.values()**2)
   
   # Velocity analysis
   div_v = calc.divergence('x_velocity', 'y_velocity', 'z_velocity')
   vort_z = calc.vorticity('x_velocity', 'y_velocity')
   
   # Find regions with high vorticity but low divergence
   interesting_regions = (np.abs(vort_z.values()) > 0.1) & (np.abs(div_v.values()) < 0.01)

Custom Calculations
-------------------

For calculations not provided by xamr, work with the underlying yt data:

.. code-block:: python

   # Access yt data directly
   temp_yt = ds['temperature'].data
   
   # Use yt's built-in operations
   # (These work across all AMR levels automatically)
   
   # Access specific AMR level for custom calculations
   temp_level0 = ds['temperature'].values(level=0)
   temp_level1 = ds['temperature'].values(level=1)

Performance Considerations
--------------------------

- AMR-aware calculations are computed across all refinement levels
- For performance-critical applications, consider using ``.values(level=0)`` for coarse-level approximations
- Derived fields are cached and reused automatically
- Use yt's native operations when possible for optimal AMR handling

.. code-block:: python

   # Fast approximation using coarsest level
   temp_coarse = ds['temperature'].values(level=0)
   rough_gradient = np.gradient(temp_coarse, axis=0)
   
   # Accurate AMR-aware calculation
   precise_gradient = ds.calc.gradient('temperature', 'x').values()