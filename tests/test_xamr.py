"""
Unit tests for xamr package
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import xamr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock yt before importing xamr
yt_mock = Mock()
yt_mock.load = Mock()
sys.modules['yt'] = yt_mock

from xamr.core import AMReXDataset, AMReXDataArray, AMReXCalculations
from xamr.utils import open_amrex


class TestAMReXDataset:
    """Test cases for AMReXDataset class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a mock yt dataset
        self.mock_yt_ds = MagicMock()
        self.mock_yt_ds.dimensionality = 3
        self.mock_yt_ds.max_level = 2
        self.mock_yt_ds.current_time = 1.5
        self.mock_yt_ds.domain_left_edge = np.array([0.0, 0.0, 0.0])
        self.mock_yt_ds.domain_right_edge = np.array([100.0, 100.0, 100.0])
        self.mock_yt_ds.domain_dimensions = np.array([64, 64, 64])
        self.mock_yt_ds.field_list = [('amrex', 'temperature'), ('amrex', 'density')]
        self.mock_yt_ds.parameters = {'param1': 'value1'}
        
        # Mock covering_grid
        self.mock_coarsest_grid = MagicMock()
        self.mock_coarsest_grid.__getitem__.return_value = np.zeros(64)
        self.mock_yt_ds.covering_grid.return_value = self.mock_coarsest_grid
        
        # Mock all_data method
        self.mock_all_data = MagicMock()
        self.mock_yt_ds.all_data.return_value = self.mock_all_data
        
        # Mock yt.load
        yt_mock.load.return_value = self.mock_yt_ds
    
    def test_init(self):
        """Test AMReXDataset initialization"""
        ds = AMReXDataset('test_file.plt')
        
        assert ds._yt_ds == self.mock_yt_ds
        assert ds._all_data[0] == self.mock_all_data
        yt_mock.load.assert_called_once_with('test_file.plt')
    
    def test_build_coordinates(self):
        """Test coordinate building"""
        ds = AMReXDataset('test_file.plt')
        
        # Check dims
        assert ds.dims == ['z', 'y', 'x']
        
        # Check coordinate ranges
        assert 'x_range' in ds.coords
        assert 'y_range' in ds.coords
        assert 'z_range' in ds.coords
        
        # Check levels
        assert ds.coords['levels'] == [0, 1, 2]
        
        # Check time (single file)
        assert 'time' not in ds.coords
    
    def test_build_data_vars(self):
        """Test data variable building"""
        ds = AMReXDataset('test_file.plt')
        
        # Check AMReX fields
        assert 'temperature' in ds.data_vars
        assert 'density' in ds.data_vars
        assert ds.data_vars['temperature'] == ('amrex', 'temperature')
        
        # Check coordinate fields
        assert 'x' in ds.data_vars
        assert 'y' in ds.data_vars
        assert 'z' in ds.data_vars
    
    def test_attrs_property(self):
        """Test attrs property"""
        ds = AMReXDataset('test_file.plt')
        attrs = ds.attrs
        
        assert attrs['max_level'] == 2
        assert attrs['dimensionality'] == 3
        assert attrs['times'] == [1.5]
        assert 'parameters' in attrs
    
    def test_levels_property(self):
        """Test levels property"""
        ds = AMReXDataset('test_file.plt')
        assert ds.levels == [0, 1, 2]
    
    def test_getitem(self):
        """Test field access via __getitem__"""
        ds = AMReXDataset('test_file.plt')
        
        # Test valid field
        temp = ds['temperature']
        assert isinstance(temp, AMReXDataArray)
        assert temp.field_name == 'temperature'
        
        # Test invalid field
        with pytest.raises(KeyError):
            ds['invalid_field']
    
    def test_calc_property(self):
        """Test calc property"""
        ds = AMReXDataset('test_file.plt')
        calc = ds.calc
        
        assert isinstance(calc, AMReXCalculations)
        assert calc.ds == ds


class TestAMReXDataArray:
    """Test cases for AMReXDataArray class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a mock dataset
        self.mock_ds = Mock()
        self.mock_ds.data_vars = {'temperature': ('amrex', 'temperature')}
        self.mock_ds._yt_ds = Mock()
        self.mock_ds._yt_ds.dimensionality = 3
        self.mock_ds._times = [1.5]
        self.mock_ds.dims = ['z', 'y', 'x']
        self.mock_ds.coords = {
            'x_range': (0.0, 100.0),
            'y_range': (0.0, 100.0),
            'z_range': (0.0, 100.0)
        }
        
        # Mock selection object
        self.mock_selection = Mock()
        self.mock_selection.__getitem__ = Mock()
        
        # Mock data
        self.mock_data = Mock()
        self.mock_data.max.return_value = 300.0
        self.mock_data.min.return_value = 200.0
        self.mock_data.mean.return_value = 250.0
        self.mock_selection.__getitem__.return_value = self.mock_data
    
    def test_init(self):
        """Test AMReXDataArray initialization"""
        arr = AMReXDataArray(self.mock_ds, 'temperature', self.mock_selection)
        
        assert arr.parent == self.mock_ds
        assert arr.field_name == 'temperature'
        assert arr._field_tuple == ('amrex', 'temperature')
        assert arr._selection_obj == self.mock_selection
        assert arr._data is None
    
    def test_data_property(self):
        """Test lazy data loading"""
        arr = AMReXDataArray(self.mock_ds, 'temperature', self.mock_selection)
        
        # First access should load data
        data = arr.data
        assert data == self.mock_data
        assert arr._data == self.mock_data
        
        # Second access should return cached data
        data2 = arr.data
        assert data2 == self.mock_data
        assert self.mock_selection.__getitem__.call_count == 1
    
    def test_dims_property(self):
        """Test dims property"""
        arr = AMReXDataArray(self.mock_ds, 'temperature', self.mock_selection)
        assert arr.dims == ['z', 'y', 'x']
    
    def test_statistical_methods(self):
        """Test statistical methods"""
        arr = AMReXDataArray(self.mock_ds, 'temperature', self.mock_selection)
        
        assert arr.max() == 300.0
        assert arr.min() == 200.0
        assert arr.mean() == 250.0
    
    def test_spatial_select(self):
        """Test spatial selection"""
        # Mock region method
        self.mock_ds._yt_ds.region = Mock()
        mock_region = Mock()
        self.mock_ds._yt_ds.region.return_value = mock_region
        
        arr = AMReXDataArray(self.mock_ds, 'temperature', self.mock_selection)
        
        # Test slice selection
        result = arr.spatial_select(x=slice(10, 20), y=slice(30, 40))
        
        assert isinstance(result, AMReXDataArray)
        assert result.field_name == 'temperature'
        self.mock_ds._yt_ds.region.assert_called_once()
    
    def test_sel_method(self):
        """Test sel method (alias for spatial_select)"""
        arr = AMReXDataArray(self.mock_ds, 'temperature', self.mock_selection)
        
        # Mock spatial_select
        arr.spatial_select = Mock()
        mock_result = Mock()
        arr.spatial_select.return_value = mock_result
        
        result = arr.sel(x=slice(10, 20))
        
        assert result == mock_result
        arr.spatial_select.assert_called_once_with(x=slice(10, 20))


class TestAMReXCalculations:
    """Test cases for AMReXCalculations class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a mock dataset
        self.mock_ds = MagicMock()
        self.mock_ds.data_vars = {
            'temperature': ('amrex', 'temperature'),
            'x_velocity': ('amrex', 'x_velocity'),
            'y_velocity': ('amrex', 'y_velocity')
        }
        self.mock_ds._yt_ds = MagicMock()
        self.mock_ds._yt_ds.derived_field_list = []
        self.mock_ds._yt_ds.add_field = Mock()
        self.mock_ds._yt_ds.add_gradient_fields = Mock()
        
        self.calc = AMReXCalculations(self.mock_ds)
    
    def test_init(self):
        """Test AMReXCalculations initialization"""
        assert self.calc.ds == self.mock_ds
    
    def test_gradient_invalid_dimension(self):
        """Test gradient with invalid dimension"""
        with pytest.raises(ValueError):
            self.calc.gradient('temperature', 'invalid_dim')
    
    def test_gradient_new_field(self):
        """Test gradient calculation for new field"""
        result = self.calc.gradient('temperature', 'x')
        
        # Check that add_gradient_fields was called
        self.mock_ds._yt_ds.add_gradient_fields.assert_called_once_with(('amrex', 'temperature'))
        
        # Check that the field was added to data_vars
        assert 'temperature_gradient_x' in self.mock_ds.data_vars
        
        # Check return type
        assert isinstance(result, AMReXDataArray)
        assert result.field_name == 'temperature_gradient_x'
    
    def test_divergence(self):
        """Test divergence calculation"""
        self.mock_ds._yt_ds.dimensionality = 2
        result = self.calc.divergence('x_velocity', 'y_velocity')
        
        # Check that add_gradient_fields was called for both velocity components
        self.mock_ds._yt_ds.add_gradient_fields.assert_any_call(('amrex', 'x_velocity'))
        self.mock_ds._yt_ds.add_gradient_fields.assert_any_call(('amrex', 'y_velocity'))
        
        # Check that add_field was called for the divergence field itself
        self.mock_ds._yt_ds.add_field.assert_called_once()
        
        # Check that the field was added to data_vars
        assert 'divergence' in self.mock_ds.data_vars
        
        # Check return type
        assert isinstance(result, AMReXDataArray)
        assert result.field_name == 'divergence'
    
    def test_vorticity(self):
        """Test vorticity calculation"""
        result = self.calc.vorticity('x_velocity', 'y_velocity')
        
        # Check that add_gradient_fields was called for both velocity components
        self.mock_ds._yt_ds.add_gradient_fields.assert_any_call(('amrex', 'x_velocity'))
        self.mock_ds._yt_ds.add_gradient_fields.assert_any_call(('amrex', 'y_velocity'))

        # Check that add_field was called for the vorticity field itself
        self.mock_ds._yt_ds.add_field.assert_called_once()
        
        # Check that the field was added to data_vars
        assert 'vorticity_z' in self.mock_ds.data_vars
        
        # Check return type
        assert isinstance(result, AMReXDataArray)
        assert result.field_name == 'vorticity_z'


class TestUtils:
    """Test cases for utility functions"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Mock yt.load
        mock_ds = MagicMock()
        mock_ds.current_time = 1.5
        mock_ds.covering_grid.return_value.__getitem__.return_value = np.zeros(64)
        yt_mock.load.return_value = mock_ds
    
    def test_open_amrex(self):
        """Test open_amrex function"""
        ds = open_amrex('test_file.plt')
        
        assert isinstance(ds, AMReXDataset)
        yt_mock.load.assert_called_with('test_file.plt')


if __name__ == '__main__':
    pytest.main([__file__])
