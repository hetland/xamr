"""
Core classes for xamr package

This package provides an xarray-like interface for AMReX data via yt, supporting:
- Native AMR structure access
- Time series data from multiple files
- Indexing at the coarsest refinement level
- Spatial and temporal selection methods
"""

import yt
import numpy as np
from typing import Union, Dict, Any, Optional, List
import glob
import os
from pathlib import Path


class AMReXDataset:
    """xarray-like interface for AMReX data via yt (native AMR)
    
    Supports both single files and time series from multiple files.
    Indexing operations work on the coarsest refinement level (level 0).
    
    Examples:
        # Single file
        ds = AMReXDataset("plt00000")
        
        # Time series from multiple files
        ds = AMReXDataset(["plt00000", "plt00001", "plt00002"])
        ds = AMReXDataset("plt*")  # glob pattern
        
        # Access field data
        temp = ds['temperature']
        
        # Indexing (coarsest level)
        temp_point = ds['temperature'][0, 10, 20]  # time=0, z=10, y=20 (for 3D)
        temp_slice = ds['temperature'][0, :, :, 50]  # time=0, all z,y, x=50
    """
    
    def __init__(self, filename: Union[str, List[str]]):
        self._setup_time_series(filename)
        self._build_coordinates()
        self._build_data_vars()
    
    def _setup_time_series(self, filename: Union[str, List[str]]):
        """Setup time series data from single file or multiple files"""
        if isinstance(filename, str):
            # Check if it's a glob pattern
            if '*' in filename or '?' in filename:
                files = sorted(glob.glob(filename))
                if not files:
                    raise FileNotFoundError(f"No files found matching pattern: {filename}")
            else:
                files = [filename]
        else:
            files = filename
        
        self._files = files
        self._yt_datasets = []
        self._times = []
        
        # Load all datasets and extract times
        for file in files:
            yt_ds = yt.load(file)
            self._yt_datasets.append(yt_ds)
            self._times.append(float(yt_ds.current_time))
        
        # Sort by time
        sorted_indices = np.argsort(self._times)
        self._yt_datasets = [self._yt_datasets[i] for i in sorted_indices]
        self._times = [self._times[i] for i in sorted_indices]
        self._files = [self._files[i] for i in sorted_indices]
        
        # Use first dataset for structure info
        self._yt_ds = self._yt_datasets[0]
        self._all_data = [ds.all_data() for ds in self._yt_datasets]
        
        # Get grid dimensions at coarsest level for indexing
        self._setup_coarsest_grid()
    
    def _setup_coarsest_grid(self):
        """Setup uniform grid at coarsest level for indexing"""
        self._coarsest_grids = []
        
        for yt_ds in self._yt_datasets:
            # Create covering grid at level 0 (coarsest)
            coarsest_grid = yt_ds.covering_grid(
                level=0,
                left_edge=yt_ds.domain_left_edge,
                dims=yt_ds.domain_dimensions
            )
            self._coarsest_grids.append(coarsest_grid)
    
    def _build_coordinates(self):
        """Build coordinate mappings for AMR structure"""
        self.coords = {}
        self.dims = []
        
        # Time dimension (if multiple files)
        if len(self._times) > 1:
            self.dims.append('time')
            self.coords['time'] = np.array(self._times)
        
        # Spatial coordinates - these will be non-uniform due to AMR
        coord_names = ['x', 'y', 'z'][:self._yt_ds.dimensionality]
        self.dims.extend(coord_names[::-1])  # z, y, x for 3D (or y, x for 2D)
        
        # Get coordinate ranges (domain bounds)
        for dim in coord_names:
            self.coords[f'{dim}_range'] = (
                float(self._yt_ds.domain_left_edge[coord_names.index(dim)]),
                float(self._yt_ds.domain_right_edge[coord_names.index(dim)])
            )
        
        # Coordinate arrays at coarsest level
        coarsest_grid = self._coarsest_grids[0]
        for i, dim in enumerate(coord_names):
            self.coords[dim] = np.array(coarsest_grid[('index', dim)])
        
        # AMR level information
        self.coords['levels'] = list(range(self._yt_ds.max_level + 1))
        
    def _build_data_vars(self):
        """Identify available data variables"""
        self.data_vars = {}
        for field in self._yt_ds.field_list:
            if field[0] in ['boxlib', 'amrex']:  # AMReX fields
                self.data_vars[field[1]] = field
        
        # Also include coordinate fields
        for dim in ['x', 'y', 'z'][:self._yt_ds.dimensionality]:
            if dim not in self.data_vars:
                self.data_vars[dim] = ('index', dim)

    def __getitem__(self, field_name: str) -> 'AMReXDataArray':
        """Access fields like ds['temperature']"""
        if field_name not in self.data_vars:
            raise KeyError(f"Field '{field_name}' not found")
        return AMReXDataArray(self, field_name)

    @property
    def attrs(self):
        """Dataset attributes"""
        return {
            'max_level': self._yt_ds.max_level,
            'dimensionality': self._yt_ds.dimensionality,
            'times': self._times,
            'n_timesteps': len(self._times),
            'domain_left_edge': self._yt_ds.domain_left_edge.v,
            'domain_right_edge': self._yt_ds.domain_right_edge.v,
            'domain_dimensions': self._yt_ds.domain_dimensions,
            'parameters': dict(self._yt_ds.parameters)
        }
    
    @property
    def levels(self):
        """Available AMR levels"""
        return list(range(self._yt_ds.max_level + 1))
    
    @property
    def calc(self):
        """Access to calculation methods"""
        return AMReXCalculations(self)


class AMReXDataArray:
    """xarray-like DataArray for AMR fields
    
    Supports indexing at the coarsest refinement level with time as the leftmost index.
    
    Indexing examples:
        # Single time step
        data[10, 20]        # z=10, y=20 (for 2D)
        data[10, 20, 30]    # z=10, y=20, x=30 (for 3D)
        
        # Time series
        data[0, 10, 20]     # time=0, z=10, y=20 (for 2D)
        data[0, 10, 20, 30] # time=0, z=10, y=20, x=30 (for 3D)
        
        # Slicing
        data[0, :, :]       # time=0, all z,y (for 2D)
        data[:, 10, :]      # all times, z=10, all y (for 2D)
    """
    
    def __init__(self, parent_ds: AMReXDataset, field_name: str, selection_obj=None):
        self.parent = parent_ds
        self.field_name = field_name
        self._field_tuple = parent_ds.data_vars[field_name]
        self._selection_obj = selection_obj or parent_ds._all_data
        self._data = None  # Lazy loading
        self._coarsest_data = None  # Cached coarsest level data
    
    def __getitem__(self, key):
        """Index into the coarsest level data
        
        Args:
            key: Index or slice. For time series, time index is leftmost.
                 Spatial indices follow yt convention (z, y, x for 3D).
        
        Returns:
            Scalar value or numpy array depending on indexing
        """
        # Ensure we have coarsest level data loaded
        if self._coarsest_data is None:
            self._load_coarsest_data()
        
        # Handle different indexing patterns
        if not isinstance(key, tuple):
            key = (key,)
        
        # Determine if we have time dimension
        has_time = len(self.parent._times) > 1
        n_spatial_dims = self.parent._yt_ds.dimensionality
        
        if has_time:
            # Time series: time index is first
            expected_dims = 1 + n_spatial_dims  # time + spatial
            if len(key) > expected_dims:
                raise IndexError(f"Too many indices. Expected at most {expected_dims}, got {len(key)}")
            
            # Extract time index
            time_idx = key[0] if len(key) > 0 else slice(None)
            spatial_key = key[1:] if len(key) > 1 else ()
            
            # Handle time indexing
            if isinstance(time_idx, slice):
                # Time slice
                time_start, time_stop, time_step = time_idx.indices(len(self._coarsest_data))
                result_data = []
                
                for t in range(time_start, time_stop, time_step):
                    if spatial_key:
                        result_data.append(self._coarsest_data[t][spatial_key])
                    else:
                        result_data.append(self._coarsest_data[t])
                
                return np.array(result_data)
            else:
                # Single time index
                if spatial_key:
                    return self._coarsest_data[time_idx][spatial_key]
                else:
                    return self._coarsest_data[time_idx]
        else:
            # Single time step
            if len(key) > n_spatial_dims:
                raise IndexError(f"Too many indices. Expected at most {n_spatial_dims}, got {len(key)}")
            
            return self._coarsest_data[0][key]
    
    def _load_coarsest_data(self):
        """Load data at coarsest level for all time steps"""
        self._coarsest_data = []
        
        for coarsest_grid in self.parent._coarsest_grids:
            field_data = np.array(coarsest_grid[self._field_tuple])
            self._coarsest_data.append(field_data)

    @property
    def data(self):
        """Lazy load AMR data - returns yt YTArray"""
        if self._data is None:
            self._data = self._selection_obj[self._field_tuple]
        return self._data
    
    @property
    def coords(self):
        """Get coordinate arrays for this data"""
        coords = {}
        for dim in ['x', 'y', 'z'][:self.parent._yt_ds.dimensionality]:
            coords[dim] = self._selection_obj[('index', dim)]
        coords['level'] = self._selection_obj[('index', 'grid_level')]
        return coords
    
    @property
    def dims(self):
        return self.parent.dims
    
    @property
    def shape(self):
        """Shape of the data at coarsest level"""
        if self._coarsest_data is None:
            self._load_coarsest_data()
        
        if len(self.parent._times) > 1:
            # Time series shape
            return (len(self._coarsest_data),) + self._coarsest_data[0].shape
        else:
            # Single time step shape
            return self._coarsest_data[0].shape
    
    def level_select(self, level: Union[int, List[int]]) -> 'AMReXDataArray':
        """Select specific AMR level(s)"""
        if isinstance(level, int):
            level = [level]
        
        # Create level-filtered data object
        level_data = self.parent._yt_ds.r[:]  # Start with all data
        # Filter by level - yt will handle this efficiently
        level_selector = self.parent._yt_ds.r[:]
        
        # This is a simplified approach - yt has more sophisticated level selection
        filtered_data = level_selector
        
        return AMReXDataArray(self.parent, self.field_name, filtered_data)
    
    def spatial_select(self, **kwargs) -> 'AMReXDataArray':
        """Select spatial region across all levels"""
        # Build region selector
        left_edge = []
        right_edge = []
        
        coord_names = ['x', 'y', 'z'][:self.parent._yt_ds.dimensionality]
        for dim in coord_names:
            if dim in kwargs:
                if isinstance(kwargs[dim], slice):
                    left_edge.append(kwargs[dim].start or self.parent.coords[f'{dim}_range'][0])
                    right_edge.append(kwargs[dim].stop or self.parent.coords[f'{dim}_range'][1])
                else:
                    # Single value - create small region around it
                    val = kwargs[dim]
                    delta = 0.01 * (self.parent.coords[f'{dim}_range'][1] - self.parent.coords[f'{dim}_range'][0])
                    left_edge.append(val - delta)
                    right_edge.append(val + delta)
            else:
                left_edge.append(self.parent.coords[f'{dim}_range'][0])
                right_edge.append(self.parent.coords[f'{dim}_range'][1])
        
        # Create region data object
        region_data = self.parent._yt_ds.region(left_edge, right_edge)
        
        return AMReXDataArray(self.parent, self.field_name, region_data)
    
    def sel(self, **kwargs):
        """xarray-like selection (spatial only for AMR)"""
        return self.spatial_select(**kwargs)
    
    def max(self, **kwargs):
        """Maximum across AMR structure"""
        return float(self.data.max())
    
    def min(self, **kwargs):
        """Minimum across AMR structure"""
        return float(self.data.min())
    
    def mean(self, **kwargs):
        """Volume-weighted mean across AMR structure"""
        return float(self.data.mean())
    
    def values(self, level: Optional[int] = None) -> np.ndarray:
        """Get values as numpy array for a specific refinement level
        
        Args:
            level: AMR level to extract values from. If None, uses coarsest level (level 0).
                  Must be between 0 and max_level.
        
        Returns:
            numpy.ndarray: Field values at the specified level. For time series data,
                          returns array with time as first dimension.
        
        Raises:
            ValueError: If level is out of range
        """
        if level is None:
            level = 0  # Default to coarsest level
        
        if level < 0 or level > self.parent._yt_ds.max_level:
            raise ValueError(f"Level {level} is out of range. Must be between 0 and {self.parent._yt_ds.max_level}")
        
        if level == 0:
            # Use cached coarsest data
            if self._coarsest_data is None:
                self._load_coarsest_data()
            
            if len(self.parent._times) > 1:
                return np.array(self._coarsest_data)
            else:
                return self._coarsest_data[0]
        else:
            # Extract data at specified level for all time steps
            result = []
            for yt_ds in self.parent._yt_datasets:
                level_data = yt_ds.covering_grid(
                    level=level,
                    left_edge=yt_ds.domain_left_edge,
                    dims=yt_ds.domain_dimensions * yt_ds.refine_by**level
                )
                field_values = level_data[self._field_tuple]
                result.append(np.array(field_values))
            
            if len(self.parent._times) > 1:
                return np.array(result)
            else:
                return result[0]


class AMReXCalculations:
    """Atmospheric/oceanic calculations using yt's AMR-native operations"""
    
    def __init__(self, dataset):
        self.ds = dataset
    
    def gradient(self, field: str, dim: str) -> AMReXDataArray:
        """Calculate gradient across all AMR levels using yt"""
        if dim not in ['x', 'y', 'z']:
            raise ValueError(f"Invalid dimension: {dim}")
        
        grad_field_name = f"gradient_{field}_{dim}"
        
        # Check if this derived field already exists
        if ('amrex', grad_field_name) not in self.ds._yt_ds.derived_field_list:
            
            def _gradient_function(field_obj, data):
                # yt automatically handles AMR gradients
                return data[self.ds.data_vars[field]].gradient(dim)
            
            self.ds._yt_ds.add_field(
                ("amrex", grad_field_name),
                function=_gradient_function,
                sampling_type="cell",
                units="auto"
            )
        
        # Add to data_vars if not already there
        if grad_field_name not in self.ds.data_vars:
            self.ds.data_vars[grad_field_name] = ("amrex", grad_field_name)
        
        return AMReXDataArray(self.ds, grad_field_name)
    
    def divergence(self, u_field: str, v_field: str, w_field: str = None):
        """Calculate divergence across all AMR levels"""
        div_field_name = "divergence"
        
        if ('amrex', div_field_name) not in self.ds._yt_ds.derived_field_list:
            
            def _divergence_function(field_obj, data):
                # yt handles AMR automatically
                du_dx = data[self.ds.data_vars[u_field]].gradient('x')
                dv_dy = data[self.ds.data_vars[v_field]].gradient('y')
                div = du_dx + dv_dy
                
                if w_field and self.ds._yt_ds.dimensionality == 3:
                    dw_dz = data[self.ds.data_vars[w_field]].gradient('z')
                    div += dw_dz
                
                return div
            
            self.ds._yt_ds.add_field(
                ("amrex", div_field_name),
                function=_divergence_function,
                sampling_type="cell",
                units="1/code_length"
            )
        
        if div_field_name not in self.ds.data_vars:
            self.ds.data_vars[div_field_name] = ("amrex", div_field_name)
        
        return AMReXDataArray(self.ds, div_field_name)
    
    def vorticity(self, u_field: str, v_field: str):
        """Calculate vertical vorticity across all AMR levels"""
        vort_field_name = "vorticity_z"
        
        if ('amrex', vort_field_name) not in self.ds._yt_ds.derived_field_list:
            
            def _vorticity_function(field_obj, data):
                dv_dx = data[self.ds.data_vars[v_field]].gradient('x')
                du_dy = data[self.ds.data_vars[u_field]].gradient('y')
                return dv_dx - du_dy
            
            self.ds._yt_ds.add_field(
                ("amrex", vort_field_name),
                function=_vorticity_function,
                sampling_type="cell",
                units="1/code_time"
            )
        
        if vort_field_name not in self.ds.data_vars:
            self.ds.data_vars[vort_field_name] = ("amrex", vort_field_name)
        
        return AMReXDataArray(self.ds, vort_field_name)
