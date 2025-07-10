Time Series Analysis
====================

Loading Time Series Data
-------------------------

.. code-block:: python

   import xamr
   import numpy as np
   import matplotlib.pyplot as plt
   
   # Load time series using glob pattern
   ds = xamr.AMReXDataset("plt*")
   
   # Or specify files explicitly
   # ds = xamr.AMReXDataset(["plt00000", "plt00001", "plt00002"])
   
   print(f"Loaded {ds.attrs['n_timesteps']} time steps")
   print(f"Time range: {ds.coords['time'][0]:.3f} to {ds.coords['time'][-1]:.3f}")

Temperature Evolution
---------------------

.. code-block:: python

   temp = ds['temperature']
   times = ds.coords['time']
   
   # Temperature at a specific point over time
   point_temp = temp[:, 50, 50, 50]  # Adjust indices for your grid
   
   plt.figure(figsize=(10, 6))
   plt.plot(times, point_temp)
   plt.xlabel('Time')
   plt.ylabel('Temperature')
   plt.title('Temperature Evolution at Fixed Point')
   plt.grid(True)
   plt.show()

Global Statistics Over Time
---------------------------

.. code-block:: python

   # Calculate statistics for each time step
   n_times = len(times)
   mean_temps = np.zeros(n_times)
   max_temps = np.zeros(n_times)
   min_temps = np.zeros(n_times)
   
   for i in range(n_times):
       temp_slice = temp[i, :, :, :]
       mean_temps[i] = temp_slice.mean()
       max_temps[i] = temp_slice.max()
       min_temps[i] = temp_slice.min()
   
   # Plot evolution
   plt.figure(figsize=(12, 8))
   plt.subplot(2, 1, 1)
   plt.plot(times, mean_temps, label='Mean', linewidth=2)
   plt.fill_between(times, min_temps, max_temps, alpha=0.3, label='Range')
   plt.ylabel('Temperature')
   plt.legend()
   plt.title('Global Temperature Statistics')
   plt.grid(True)
   
   # Temperature range over time
   plt.subplot(2, 1, 2)
   plt.plot(times, max_temps - min_temps, 'r-', linewidth=2)
   plt.xlabel('Time')
   plt.ylabel('Temperature Range')
   plt.title('Temperature Range Over Time')
   plt.grid(True)
   plt.tight_layout()
   plt.show()

Spatial Patterns Over Time
---------------------------

.. code-block:: python

   # Create animation-like sequence of plots
   fig, axes = plt.subplots(2, 3, figsize=(15, 10))
   axes = axes.flatten()
   
   # Select time steps to show
   time_indices = np.linspace(0, n_times-1, 6, dtype=int)
   
   for i, t_idx in enumerate(time_indices):
       if len(temp.shape) == 4:  # 3D + time
           mid_z = temp.shape[1] // 2
           temp_slice = temp[t_idx, mid_z, :, :]
       else:  # 2D + time
           temp_slice = temp[t_idx, :, :]
       
       im = axes[i].imshow(temp_slice, cmap='hot', origin='lower')
       axes[i].set_title(f'Time = {times[t_idx]:.3f}')
       axes[i].set_aspect('equal')
       plt.colorbar(im, ax=axes[i])
   
   plt.tight_layout()
   plt.show()

Temporal Derivatives
--------------------

.. code-block:: python

   # Calculate time derivative of temperature
   dt = np.diff(times)
   temp_evolution = np.array([temp[i, :, :, :].mean() for i in range(n_times)])
   dtemp_dt = np.diff(temp_evolution) / dt
   
   plt.figure(figsize=(10, 6))
   plt.plot(times[1:], dtemp_dt)
   plt.xlabel('Time')
   plt.ylabel('dT/dt')
   plt.title('Rate of Temperature Change')
   plt.grid(True)
   plt.show()

Correlation Analysis
--------------------

.. code-block:: python

   # Analyze correlation between different points
   point1_temp = temp[:, 30, 30, 30]
   point2_temp = temp[:, 70, 70, 70]
   
   correlation = np.corrcoef(point1_temp, point2_temp)[0, 1]
   
   plt.figure(figsize=(12, 5))
   
   plt.subplot(1, 2, 1)
   plt.plot(times, point1_temp, label='Point 1', linewidth=2)
   plt.plot(times, point2_temp, label='Point 2', linewidth=2)
   plt.xlabel('Time')
   plt.ylabel('Temperature')
   plt.title('Temperature at Two Points')
   plt.legend()
   plt.grid(True)
   
   plt.subplot(1, 2, 2)
   plt.scatter(point1_temp, point2_temp, alpha=0.7)
   plt.xlabel('Temperature at Point 1')
   plt.ylabel('Temperature at Point 2')
   plt.title(f'Correlation = {correlation:.3f}')
   plt.grid(True)
   
   plt.tight_layout()
   plt.show()

Frequency Analysis
------------------

.. code-block:: python

   # FFT analysis of temperature evolution
   from scipy import fft
   
   # Ensure even sampling
   if len(np.unique(np.diff(times))) == 1:  # Uniform time steps
       temp_signal = temp[:, 50, 50, 50]  # Temperature at one point
       
       # Remove mean
       temp_signal = temp_signal - temp_signal.mean()
       
       # FFT
       freq = fft.fftfreq(len(temp_signal), d=times[1]-times[0])
       temp_fft = fft.fft(temp_signal)
       
       # Plot power spectrum
       plt.figure(figsize=(10, 6))
       plt.loglog(freq[1:len(freq)//2], np.abs(temp_fft[1:len(freq)//2])**2)
       plt.xlabel('Frequency')
       plt.ylabel('Power')
       plt.title('Temperature Power Spectrum')
       plt.grid(True)
       plt.show()
   else:
       print("Non-uniform time sampling - FFT analysis not applicable")