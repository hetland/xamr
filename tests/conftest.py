"""
Pytest configuration and fixtures
"""

import pytest
import sys
from unittest.mock import Mock

# Mock yt before any imports
@pytest.fixture(autouse=True)
def mock_yt():
    """Mock yt module for all tests"""
    yt_mock = Mock()
    yt_mock.load = Mock()
    sys.modules['yt'] = yt_mock
    return yt_mock

@pytest.fixture(autouse=True)
def mock_numpy():
    """Mock numpy for tests that don't need real numpy"""
    if 'numpy' not in sys.modules:
        numpy_mock = Mock()
        numpy_mock.array = Mock()
        sys.modules['numpy'] = numpy_mock
    return sys.modules['numpy']
