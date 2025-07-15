# xamr: xarray-like interface for AMReX data

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**xamr** provides an xarray-like interface for AMReX plot files using yt as the backend. It maintains the native AMR (Adaptive Mesh Refinement) structure while providing familiar xarray-style data access and operations.

## Features

- **xarray-like interface**: Familiar syntax for scientists already using xarray
- **Native AMR support**: Works with the full AMR hierarchy, no interpolation required
- **Lazy loading**: Data is loaded only when needed
- **Built-in calculations**: Gradient, divergence, and vorticity calculations across AMR levels
- **Spatial selection**: Select regions across all AMR levels
- **Level selection**: Work with specific AMR levels when needed

## Installation

### From source

```bash
git clone https://github.com/yourusername/xamr.git
cd xamr
pip install -e .
```

### Development installation

```bash
git clone https://github.com/yourusername/xamr.git
cd xamr
pip install -e ".[dev]"
```

## Quick Start

For a comprehensive tutorial, see the **[Quick Start Guide](docs/quick_start.md)** or try the interactive **[Jupyter notebook](XAMR_Quick_Start_Guide.ipynb)**.

```python
import xamr

# Load an AMReX plot file
ds = xamr.open_amrex('plt00100')

# Access data fields (works across all AMR levels)
temperature = ds['temperature']
u_velocity = ds['x_velocity']
v_velocity = ds['y_velocity']

# Basic statistics (volume-weighted across AMR structure)
print(f"Mean temperature: {temperature.mean()}")
print(f"Max temperature: {temperature.max()}")

# Spatial selection across all levels
region_temp = temperature.sel(x=slice(100, 200), y=slice(50, 150))

# Level selection
finest_level = temperature.level_select(ds.attrs['max_level'])
coarse_levels = temperature.level_select([0, 1, 2])

# Built-in calculations
temp_gradient_x = ds.calc.gradient('temperature', 'x')
vorticity = ds.calc.vorticity('x_velocity', 'y_velocity')
divergence = ds.calc.divergence('x_velocity', 'y_velocity')
```

## API Reference

### Core Classes

#### `AMReXDataset`

The main dataset class that provides an xarray-like interface to AMReX data.

**Properties:**
- `attrs`: Dataset attributes (max_level, dimensionality, current_time, etc.)
- `coords`: Coordinate information
- `data_vars`: Available data variables
- `levels`: Available AMR levels
- `calc`: Access to calculation methods

**Methods:**
- `__getitem__(field_name)`: Access data fields like `ds['temperature']`

#### `AMReXDataArray`

Represents a single data field across the AMR hierarchy.

**Properties:**
- `data`: The actual data (lazy loaded)
- `coords`: Coordinate arrays
- `dims`: Dimension names

**Methods:**
- `sel(**kwargs)`: Spatial selection
- `level_select(level)`: Select specific AMR levels
- `mean()`, `max()`, `min()`: Statistical operations
- `spatial_select(**kwargs)`: Spatial region selection

#### `AMReXCalculations`

Provides atmospheric/oceanic calculations using yt's AMR-native operations.

**Methods:**
- `gradient(field, dim)`: Calculate gradient
- `divergence(u_field, v_field, w_field=None)`: Calculate divergence
- `vorticity(u_field, v_field)`: Calculate vertical vorticity

### Functions

#### `open_amrex(filename)`

Open an AMReX plot file and return a xamr dataset.

**Parameters:**
- `filename` (str): Path to the AMReX plot file

**Returns:**
- `AMReXDataset`: Dataset with xarray-like interface

## Examples

### Working with AMR levels

```python
import xamr

ds = xamr.open_amrex('plt00100')
temp = ds['temperature']

# Work with all levels (default)
mean_temp_all = temp.mean()

# Work with finest level only
temp_finest = temp.level_select(ds.attrs['max_level'])
mean_temp_finest = temp_finest.mean()

# Work with coarse levels
temp_coarse = temp.level_select([0, 1])
mean_temp_coarse = temp_coarse.mean()
```

### Spatial selection

```python
# Select a rectangular region
region = ds['temperature'].sel(
    x=slice(100, 200),
    y=slice(50, 150)
)

# Point selection (creates small region around point)
point = ds['temperature'].sel(x=150, y=75)
```

### Calculations

```python
# Calculate gradients
temp_grad_x = ds.calc.gradient('temperature', 'x')
temp_grad_y = ds.calc.gradient('temperature', 'y')

# Calculate divergence of velocity field
div = ds.calc.divergence('x_velocity', 'y_velocity', 'z_velocity')

# Calculate vorticity
vort = ds.calc.vorticity('x_velocity', 'y_velocity')

# Combine operations
temp_anomaly = ds['temperature'] - ds['temperature'].mean()
```

## Requirements

- Python 3.8+
- yt >= 4.0.0
- numpy >= 1.19.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on top of [yt](https://yt-project.org/) for AMR data handling
- Inspired by [xarray](https://xarray.pydata.org/) for the API design
- Designed for [AMReX](https://amrex-codes.github.io/) simulation data
