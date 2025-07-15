# XAMR Quick Start Guide

Welcome to **XAMR** - an xarray-like interface for AMReX data via yt!

This guide provides a quick introduction to the main features of XAMR, demonstrating how to analyze AMReX plotfile data with a familiar, xarray-like interface.

## What makes XAMR special?

- **xarray-like interface**: Familiar `.sel()`, indexing, and attribute access
- **Native AMR support**: Works directly with yt's AMR-aware operations  
- **Time series handling**: Seamlessly load and analyze multiple plotfiles
- **Scientific calculations**: Built-in gradient, divergence, and vorticity calculations
- **Efficient indexing**: Smart indexing at the coarsest level for quick analysis

## Installation

```bash
pip install xamr
```

Or for development:

```bash
git clone https://github.com/hetland/xamr.git
cd xamr
pip install -e .
```

## Quick Start

### 1. Import XAMR

```python
import numpy as np
import matplotlib.pyplot as plt
from xamr import AMReXDataset
```

### 2. Load AMReX Data

XAMR makes it easy to load AMReX plotfile data. You can load a single file or an entire time series:

```python
# Single file
ds = AMReXDataset('plt00000')

# Time series from multiple files
ds = AMReXDataset('plt*')  # Uses glob pattern

# Explicit list
ds = AMReXDataset(['plt00000', 'plt00010', 'plt00020'])
```

### 3. Explore Your Data

```python
# Check dataset information
print(f"Time steps: {ds.attrs['n_timesteps']}")
print(f"Dimensions: {ds.dims}")
print(f"Available fields: {list(ds.data_vars.keys())}")

# Access field data
temp = ds['temperature']
print(f"Temperature shape: {temp.shape}")
```

### 4. Data Indexing

XAMR provides intuitive indexing similar to xarray/numpy:

```python
# For time series: data[time, z, y, x]
temp_point = temp[0, 15, 15, 15]  # Single point at first time
temp_timeseries = temp[:, 15, 15, 15]  # Time series at fixed point
temp_slice = temp[0, :, :, 15]  # 2D slice at fixed x

# Extract numpy arrays
temp_data = temp.values()  # Coarsest level
temp_level1 = temp.values(level=1)  # Specific AMR level
```

### 5. Scientific Calculations

XAMR provides built-in AMR-native calculations:

```python
# Gradient calculations
temp_grad_x = ds.calc.gradient('temperature', 'x')
temp_grad_y = ds.calc.gradient('temperature', 'y')
temp_grad_z = ds.calc.gradient('temperature', 'z')

# Vorticity (requires velocity fields)
vorticity = ds.calc.vorticity('x_velocity', 'y_velocity')

# Divergence
divergence = ds.calc.divergence('x_velocity', 'y_velocity', 'z_velocity')
```

### 6. Time Series Analysis

```python
# Extract time evolution at a point
times = np.array(ds.attrs['times'])
temp_evolution = temp[:, 10, 10, 10]

# Plot evolution
plt.plot(times, temp_evolution)
plt.xlabel('Time')
plt.ylabel('Temperature')
plt.title('Temperature Evolution')
```

### 7. Visualization

XAMR data works seamlessly with matplotlib and other visualization tools:

```python
# 2D slice visualization
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.imshow(temp[0, 16, :, :], origin='lower', cmap='viridis')
plt.colorbar(label='Temperature')
plt.title('Temperature at t=0, z=16')

plt.subplot(1, 2, 2)
plt.imshow(temp_grad_x[0, 16, :, :], origin='lower', cmap='RdBu_r')
plt.colorbar(label='∂T/∂x')
plt.title('Temperature Gradient')

plt.show()
```

## Key Features

### AMR-Aware Operations
- All calculations properly handle adaptive mesh refinement
- Built on yt's robust AMR infrastructure
- Efficient operations across multiple refinement levels

### Time Series Support
- Automatic detection and sorting of time-ordered files
- Consistent indexing across time steps
- Time-based analysis and visualization

### xarray-like Interface
- Familiar attribute access (`ds.attrs`, `ds.coords`, `ds.data_vars`)
- Dictionary-style field access (`ds['field_name']`)
- NumPy-compatible indexing and slicing

### Scientific Computing
- Gradient calculations: `ds.calc.gradient(field, direction)`
- Vorticity calculations: `ds.calc.vorticity(u_field, v_field)`
- Divergence calculations: `ds.calc.divergence(u_field, v_field, w_field)`

## Advanced Examples

### Multi-level Analysis

```python
# Compare data at different refinement levels
level0_data = temp.values(level=0)  # Coarsest
level1_data = temp.values(level=1)  # Finer

print(f"Level 0 shape: {level0_data.shape}")
print(f"Level 1 shape: {level1_data.shape}")
```

### Statistical Analysis

```python
# Domain-averaged evolution
domain_avg = [temp[t].mean() for t in range(len(times))]
domain_std = [temp[t].std() for t in range(len(times))]

plt.plot(times, domain_avg, label='Mean')
plt.plot(times, domain_std, label='Std Dev')
plt.legend()
```

### Complex Calculations

```python
# Temperature gradient magnitude
grad_x = ds.calc.gradient('temperature', 'x')
grad_y = ds.calc.gradient('temperature', 'y')
grad_z = ds.calc.gradient('temperature', 'z')

# Calculate magnitude manually
grad_mag = np.sqrt(grad_x.values()**2 + grad_y.values()**2 + grad_z.values()**2)
```

## Integration with Other Tools

XAMR works well with the broader Python scientific ecosystem:

- **pandas**: Convert extracted data to DataFrames for analysis
- **xarray**: Use XAMR to load data, then convert to xarray for advanced operations
- **scipy**: Apply signal processing and statistical functions
- **matplotlib/seaborn/plotly**: Create publication-quality visualizations
- **dask**: Scale computations to larger datasets

## Next Steps

1. **Try the interactive notebook**: `XAMR_Quick_Start_Guide.ipynb` provides hands-on examples
2. **Explore the API documentation**: Detailed reference for all methods and classes
3. **Check out examples**: Real-world use cases in the `examples/` directory
4. **Join the community**: Contribute issues, suggestions, and improvements

## Getting Help

- **Documentation**: [https://xamr.readthedocs.io](https://xamr.readthedocs.io)
- **GitHub Issues**: [https://github.com/hetland/xamr/issues](https://github.com/hetland/xamr/issues)
- **Examples**: See the `examples/` directory in the repository

Happy analyzing! 🎉
