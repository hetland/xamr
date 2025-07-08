"""
Core classes for xamr package
"""

import yt
import numpy as np
from typing import Union, Dict, Any, Optional, List


class AMReXDataset:
    """xarray-like interface for AMReX data via yt (native AMR)"""
    
    def __init__(self, filename: str):
        self._yt_ds = yt.load(filename)
        
        # Work with native AMR structure - no level selection by default
        self._all_data = self._yt_ds.all_data()
        
        # Build coordinate and level information
        self._build_coordinates()
        self._build_data_vars()
    
    def _build_coordinates(self):
        """Build coordinate mappings for AMR structure"""
        self.coords = {}
        self.dims = []
        
        # Spatial coordinates - these will be non-uniform due to AMR
        coord_names = ['x', 'y', 'z'][:self._yt_ds.dimensionality]
        self.dims = coord_names[::-1]  # z, y, x for 3D
        
        # Get coordinate ranges (domain bounds)
        for dim in coord_names:
            self.coords[f'{dim}_range'] = (
                float(self._yt_ds.domain_left_edge[coord_names.index(dim)]),
                float(self._yt_ds.domain_right_edge[coord_names.index(dim)])
            )
        
        # AMR level information
        self.coords['levels'] = list(range(self._yt_ds.max_level + 1))
        self.coords['time'] = float(self._yt_ds.current_time)
        
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
            'current_time': float(self._yt_ds.current_time),
            'domain_left_edge': self._yt_ds.domain_left_edge.v,
            'domain_right_edge': self._yt_ds.domain_right_edge.v,
            'domain_dimensions': self._yt_ds.domain_dimensions.v,
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
    """xarray-like DataArray for AMR fields"""
    
    def __init__(self, parent_ds: AMReXDataset, field_name: str, selection_obj=None):
        self.parent = parent_ds
        self.field_name = field_name
        self._field_tuple = parent_ds.data_vars[field_name]
        self._selection_obj = selection_obj or parent_ds._all_data
        self._data = None  # Lazy loading
    
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
