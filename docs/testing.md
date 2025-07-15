# Testing

The XAMR package includes comprehensive test suites to ensure reliability and functionality.

## Test Types

### Unit Tests (`test_xamr.py`)
- **Purpose**: Test individual components with mocked yt dependencies
- **Location**: `tests/test_xamr.py`
- **Coverage**: Core functionality, edge cases, error handling
- **Runtime**: Fast (~0.2s)

### Integration Tests (`test_integration.py`)
- **Purpose**: Test complete workflows with real AMReX data
- **Location**: `tests/test_integration.py`
- **Coverage**: End-to-end functionality, gradient calculations, time series analysis
- **Runtime**: Moderate (~30s)
- **Data**: Uses real AMReX plotfiles in `data/` directory

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Only Unit Tests
```bash
pytest tests/test_xamr.py
```

### Run Only Integration Tests
```bash
pytest tests/test_integration.py -m integration
```

### Run with Coverage
```bash
pytest --cov=xamr --cov-report=html
```

## Test Data

The integration tests use real AMReX data located in the `data/` directory:
- `data/plt00000/` - Single timestep data
- `data/plt00010/` - Second timestep 
- `data/plt00020/` - Third timestep

This data includes:
- Temperature field (`temp`)
- Salinity field (`salt`)
- Velocity fields (`x_velocity`, `y_velocity`, `z_velocity`)
- 3D domain with AMR structure

## Continuous Integration

The CI pipeline (`.github/workflows/ci.yml`) runs:
1. **Unit tests** - Fast validation with mocked dependencies
2. **Integration tests** - Complete validation with real data
3. **Code coverage** - Ensures adequate test coverage
4. **Linting** - Code quality checks
5. **Type checking** - Static type validation

## Test Coverage

Current test coverage focuses on:
- ✅ Dataset loading (single files and time series)
- ✅ Field access and indexing
- ✅ Gradient calculations with ghost zones
- ✅ Vorticity and divergence calculations
- ✅ Statistical methods
- ✅ Error handling
- ✅ Memory efficiency
- ✅ Regression tests for specific fixes

## Adding New Tests

### For New Features
1. Add unit tests to `tests/test_xamr.py` with appropriate mocks
2. Add integration tests to `tests/test_integration.py` using real data
3. Mark integration tests with `@pytest.mark.integration`

### For Bug Fixes
1. Add regression tests to verify the fix
2. Include both unit and integration test coverage
3. Document the specific issue being tested

## Test Markers

- `@pytest.mark.integration` - Integration tests requiring real data
- Tests without markers are considered unit tests

Use `-m "not integration"` to skip integration tests during development.
