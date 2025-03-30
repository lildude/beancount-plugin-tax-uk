"""
Test fixtures for beancount_plugin_tax_uk.

This module provides fixtures for testing Beancount ledger files and report generation.
"""

import os
import pytest
from beancount.loader import load_file


def pytest_addoption(parser):
    """Add command line options for pytest."""
    parser.addoption(
        "--capture-output",
        action="store_true",
        help="Capture test output files (Excel and pickle) for reference",
    )


@pytest.fixture
def capture_output(request):
    """Fixture to determine if we should capture output files."""
    return request.config.getoption("--capture-output")


@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def sample_ledger(test_data_dir):
    """Load a sample Beancount ledger file for testing."""
    ledger_path = os.path.join(test_data_dir, "sample.bean")
    entries, errors, options = load_file(ledger_path)
    if errors:
        pytest.fail(f"Failed to load test ledger: {errors}")
    return entries, errors, options


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a temporary directory for test output files."""
    return tmp_path
