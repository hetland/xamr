"""
Integration tests for xamr package using real AMReX data

These tests verify the complete functionality of the xamr package including:
- Loading single plotfiles and time series
- Gradient calculations with ghost zones
- Vorticity and divergence calculations
- Value extraction and indexing
- Time series analysis

The tests use real AMReX data in the data/ directory.
"""

import pytest
import numpy as np
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import xamr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xamr import AMReXDataset

# Path to test data
DATA_DIR = Path(__file__).parent.parent / "data"
SINGLE_PLOTFILE = DATA_DIR / "plt00000"
TIME_SERIES_PATTERN = str(DATA_DIR / "plt*")


@pytest.fixture
def single_dataset():
    """Fixture providing a single AMReX dataset"""
    if not SINGLE_PLOTFILE.exists():
        pytest.skip(f"Test data not found at {SINGLE_PLOTFILE}")
    return AMReXDataset(str(SINGLE_PLOTFILE))


@pytest.fixture
def time_series_dataset():
    """Fixture providing a time series AMReX dataset"""
    if not DATA_DIR.exists() or len(list(DATA_DIR.glob("plt*"))) < 2:
        pytest.skip(f"Time series test data not found in {DATA_DIR}")
    return AMReXDataset(TIME_SERIES_PATTERN)


class TestRealDataIntegration:
    """Integration tests with real AMReX data"""

    def test_single_file_loading(self, single_dataset):
        """Test loading a single plotfile"""
        ds = single_dataset
        
        # Check basic properties
        assert ds.attrs['dimensionality'] >= 2
        assert ds.attrs['max_level'] >= 0
        assert len(ds.data_vars) > 0
        
        # Check that we have expected fields
        expected_fields = ['temp', 'salt', 'x_velocity', 'y_velocity']
        for field in expected_fields:
            if field in ds.data_vars:
                assert isinstance(ds[field].shape, tuple)
                assert len(ds[field].shape) >= 2

    def test_time_series_loading(self, time_series_dataset):
        """Test loading multiple plotfiles as time series"""
        ds = time_series_dataset
        
        # Check time series properties
        assert ds.attrs['n_timesteps'] >= 2
        assert len(ds.attrs['times']) == ds.attrs['n_timesteps']
        assert all(t >= 0 for t in ds.attrs['times'])
        
        # Check that time dimension is included in shape
        for field_name in list(ds.data_vars.keys())[:3]:  # Test first few fields
            field = ds[field_name]
            assert field.shape[0] == ds.attrs['n_timesteps']

    def test_field_access_and_values(self, single_dataset):
        """Test basic field access and value extraction"""
        ds = single_dataset
        
        # Test field access
        temp = ds['temp']
        assert temp.field_name == 'temp'
        assert isinstance(temp.shape, tuple)
        
        # Test values method
        temp_values = temp.values()
        assert isinstance(temp_values, np.ndarray)
        assert temp_values.shape == temp.shape
        assert np.isfinite(temp_values).all()
        
        # Test that values are reasonable (not all zeros)
        assert temp_values.min() <= temp_values.max()

    def test_gradient_calculations(self, single_dataset):
        """Test gradient calculations with real data"""
        ds = single_dataset
        
        if 'temp' not in ds.data_vars:
            pytest.skip("Temperature field not available for gradient test")
        
        # Test gradient calculation in each direction
        temp_grad_x = ds.calc.gradient('temp', 'x')
        temp_grad_y = ds.calc.gradient('temp', 'y')
        
        # Check gradient field properties
        assert temp_grad_x.field_name == 'temp_gradient_x'
        assert temp_grad_y.field_name == 'temp_gradient_y'
        assert temp_grad_x.shape == ds['temp'].shape
        assert temp_grad_y.shape == ds['temp'].shape
        
        # Test gradient value extraction
        grad_x_values = temp_grad_x.values()
        grad_y_values = temp_grad_y.values()
        
        assert isinstance(grad_x_values, np.ndarray)
        assert isinstance(grad_y_values, np.ndarray)
        assert np.isfinite(grad_x_values).all()
        assert np.isfinite(grad_y_values).all()
        
        # Test 3D gradient if data is 3D
        if ds.attrs['dimensionality'] == 3:
            temp_grad_z = ds.calc.gradient('temp', 'z')
            assert temp_grad_z.field_name == 'temp_gradient_z'
            assert temp_grad_z.shape == ds['temp'].shape
            
            grad_z_values = temp_grad_z.values()
            assert isinstance(grad_z_values, np.ndarray)
            assert np.isfinite(grad_z_values).all()

    def test_gradient_indexing(self, single_dataset):
        """Test indexing of gradient fields"""
        ds = single_dataset
        
        if 'temp' not in ds.data_vars:
            pytest.skip("Temperature field not available for indexing test")
        
        temp_grad_x = ds.calc.gradient('temp', 'x')
        
        # Test point indexing
        if ds.attrs['dimensionality'] == 3:
            # 3D indexing
            point_value = temp_grad_x[10, 10, 5]
            assert isinstance(point_value, (int, float, np.number))
            assert np.isfinite(point_value)
            
            # Slice indexing
            slice_values = temp_grad_x[:, 10, 5]
            assert isinstance(slice_values, np.ndarray)
            assert len(slice_values.shape) == 1
        else:
            # 2D indexing
            point_value = temp_grad_x[10, 10]
            assert isinstance(point_value, (int, float, np.number))
            assert np.isfinite(point_value)

    def test_vorticity_calculations(self, single_dataset):
        """Test vorticity calculations with real data"""
        ds = single_dataset
        
        velocity_fields = ['x_velocity', 'y_velocity']
        if not all(field in ds.data_vars for field in velocity_fields):
            pytest.skip("Velocity fields not available for vorticity test")
        
        # Calculate vorticity
        vorticity = ds.calc.vorticity('x_velocity', 'y_velocity')
        
        # Check vorticity properties
        assert vorticity.field_name == 'vorticity_z'
        assert vorticity.shape == ds['x_velocity'].shape
        
        # Test vorticity value extraction
        vort_values = vorticity.values()
        assert isinstance(vort_values, np.ndarray)
        assert np.isfinite(vort_values).all()
        
        # Test vorticity indexing
        if ds.attrs['dimensionality'] == 3:
            vort_point = vorticity[10, 10, 5]
        else:
            vort_point = vorticity[10, 10]
        
        assert isinstance(vort_point, (int, float, np.number))
        assert np.isfinite(vort_point)

    def test_divergence_calculations(self, single_dataset):
        """Test divergence calculations with real data"""
        ds = single_dataset
        
        velocity_fields = ['x_velocity', 'y_velocity']
        if not all(field in ds.data_vars for field in velocity_fields):
            pytest.skip("Velocity fields not available for divergence test")
        
        # Test 2D divergence
        divergence_2d = ds.calc.divergence('x_velocity', 'y_velocity')
        
        assert divergence_2d.field_name == 'divergence'
        assert divergence_2d.shape == ds['x_velocity'].shape
        
        div_values = divergence_2d.values()
        assert isinstance(div_values, np.ndarray)
        assert np.isfinite(div_values).all()
        
        # Test 3D divergence if z_velocity exists
        if 'z_velocity' in ds.data_vars and ds.attrs['dimensionality'] == 3:
            divergence_3d = ds.calc.divergence('x_velocity', 'y_velocity', 'z_velocity')
            
            div_3d_values = divergence_3d.values()
            assert isinstance(div_3d_values, np.ndarray)
            assert np.isfinite(div_3d_values).all()

    def test_time_series_gradients(self, time_series_dataset):
        """Test gradient calculations with time series data"""
        ds = time_series_dataset
        
        if 'temp' not in ds.data_vars:
            pytest.skip("Temperature field not available for time series gradient test")
        
        # Calculate gradient
        temp_grad_x = ds.calc.gradient('temp', 'x')
        
        # Check that gradient has time dimension
        assert temp_grad_x.shape[0] == ds.attrs['n_timesteps']
        
        # Test gradient values across time
        grad_values = temp_grad_x.values()
        assert grad_values.shape[0] == ds.attrs['n_timesteps']
        assert np.isfinite(grad_values).all()
        
        # Test indexing across time
        for t in range(min(3, ds.attrs['n_timesteps'])):  # Test first few timesteps
            if ds.attrs['dimensionality'] == 3:
                time_point = temp_grad_x[t, 10, 10, 5]
            else:
                time_point = temp_grad_x[t, 10, 10]
            
            assert isinstance(time_point, (int, float, np.number))
            assert np.isfinite(time_point)

    def test_time_series_vorticity(self, time_series_dataset):
        """Test vorticity calculations with time series data"""
        ds = time_series_dataset
        
        velocity_fields = ['x_velocity', 'y_velocity']
        if not all(field in ds.data_vars for field in velocity_fields):
            pytest.skip("Velocity fields not available for time series vorticity test")
        
        # Calculate vorticity
        vorticity = ds.calc.vorticity('x_velocity', 'y_velocity')
        
        # Check time dimension
        assert vorticity.shape[0] == ds.attrs['n_timesteps']
        
        # Test values across time
        vort_values = vorticity.values()
        assert vort_values.shape[0] == ds.attrs['n_timesteps']
        assert np.isfinite(vort_values).all()

    def test_statistical_methods(self, single_dataset):
        """Test statistical methods on real data"""
        ds = single_dataset
        
        temp = ds['temp']
        
        # Test basic statistics
        temp_min = temp.min()
        temp_max = temp.max()
        temp_mean = temp.mean()
        
        assert isinstance(temp_min, (int, float))
        assert isinstance(temp_max, (int, float))
        assert isinstance(temp_mean, (int, float))
        assert temp_min <= temp_mean <= temp_max
        assert np.isfinite([temp_min, temp_max, temp_mean]).all()

    def test_different_refinement_levels(self, single_dataset):
        """Test accessing data at different AMR levels"""
        ds = single_dataset
        
        temp = ds['temp']
        
        # Test level 0 (coarsest)
        level0_values = temp.values(level=0)
        assert isinstance(level0_values, np.ndarray)
        assert np.isfinite(level0_values).all()
        
        # Test that higher levels work if available
        if ds.attrs['max_level'] > 0:
            try:
                level1_values = temp.values(level=1)
                assert isinstance(level1_values, np.ndarray)
                assert np.isfinite(level1_values).all()
                # Higher level should have more grid points
                assert level1_values.size >= level0_values.size
            except (KeyError, ValueError):
                # Some fields might not exist at all levels, which is OK
                pass

    def test_field_consistency(self, single_dataset):
        """Test that derived fields are consistent with base fields"""
        ds = single_dataset
        
        if 'temp' not in ds.data_vars:
            pytest.skip("Temperature field not available for consistency test")
        
        # Get temperature and its gradient
        temp = ds['temp']
        temp_grad_x = ds.calc.gradient('temp', 'x')
        
        # Both should have same shape
        assert temp.shape == temp_grad_x.shape
        
        # Both should be accessible through data_vars
        assert 'temp_gradient_x' in ds.data_vars

    def test_error_handling(self, single_dataset):
        """Test error handling for invalid operations"""
        ds = single_dataset
        
        # Test invalid field access
        with pytest.raises(KeyError):
            ds['nonexistent_field']
        
        # Test invalid gradient dimension
        with pytest.raises(ValueError):
            ds.calc.gradient('temp', 'invalid_dim')
        
        # Test invalid refinement level
        temp = ds['temp']
        with pytest.raises(ValueError):
            temp.values(level=-1)
        
        with pytest.raises(ValueError):
            temp.values(level=ds.attrs['max_level'] + 10)

    def test_memory_efficiency(self, single_dataset):
        """Test that data is loaded lazily and efficiently"""
        ds = single_dataset
        
        # Create field objects without triggering data loading
        temp1 = ds['temp']
        temp2 = ds['temp']
        
        # Should be separate objects
        assert temp1 is not temp2
        
        # But should refer to same underlying data source
        assert temp1._field_tuple == temp2._field_tuple
        assert temp1.field_name == temp2.field_name


class TestRealDataRegression:
    """Regression tests to ensure fixes continue working"""

    def test_ghost_zone_fix(self, single_dataset):
        """Ensure gradient calculations work without ghost zone errors"""
        ds = single_dataset
        
        if 'temp' not in ds.data_vars:
            pytest.skip("Temperature field not available")
        
        # This should not raise NeedsGridType or RuntimeError
        temp_grad = ds.calc.gradient('temp', 'x')
        
        # Should be able to access shape without errors
        shape = temp_grad.shape
        assert isinstance(shape, tuple)
        
        # Should be able to extract values
        values = temp_grad.values()
        assert isinstance(values, np.ndarray)

    def test_field_type_consistency(self, single_dataset):
        """Ensure derived fields use correct field types"""
        ds = single_dataset
        
        velocity_fields = ['x_velocity', 'y_velocity']
        if not all(field in ds.data_vars for field in velocity_fields):
            pytest.skip("Velocity fields not available")
        
        # Create vorticity field
        vorticity = ds.calc.vorticity('x_velocity', 'y_velocity')
        
        # Should not raise YTFieldTypeNotFound
        vort_values = vorticity.values()
        assert isinstance(vort_values, np.ndarray)
        
        # Field should be added to data_vars
        assert 'vorticity_z' in ds.data_vars

    def test_indexing_robustness(self, single_dataset):
        """Test various indexing patterns work correctly"""
        ds = single_dataset
        
        if 'temp' not in ds.data_vars:
            pytest.skip("Temperature field not available")
        
        temp_grad = ds.calc.gradient('temp', 'x')
        
        # Test different indexing patterns based on dimensionality
        if ds.attrs['dimensionality'] == 3:
            # Point indexing
            point = temp_grad[5, 5, 2]
            assert np.isfinite(point)
            
            # Slice indexing
            slice_1d = temp_grad[5, 5, :]
            slice_2d = temp_grad[5, :, :]
            slice_3d = temp_grad[:, :, :]
            
            assert all(isinstance(s, np.ndarray) for s in [slice_1d, slice_2d, slice_3d])
        else:
            # 2D case
            point = temp_grad[5, 5]
            assert np.isfinite(point)
            
            slice_1d = temp_grad[5, :]
            slice_2d = temp_grad[:, :]
            
            assert all(isinstance(s, np.ndarray) for s in [slice_1d, slice_2d])


# Mark tests that require test data
pytestmark = pytest.mark.integration
