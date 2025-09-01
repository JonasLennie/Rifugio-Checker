#!/usr/bin/env python3
"""
Pytest configuration and fixtures
"""

import os
import sys
import pytest
from pathlib import Path

# Add src directory to Python path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session") 
def src_directory(project_root):
    """Get src directory path"""
    return project_root / "src"


@pytest.fixture(scope="session")
def test_data_directory(project_root):
    """Get test data directory path"""
    test_data_dir = project_root / "tests" / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    return test_data_dir


@pytest.fixture
def mock_env_vars():
    """Common environment variables for testing"""
    return {
        'EMAIL_FROM': 'test@example.com',
        'EMAIL_TO': 'notify@example.com', 
        'EMAIL_PASSWORD': 'test_password',
        'TARGET_DATES': '2025-09-12,2025-09-15,2025-09-21'
    }


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    return b"""
    %PDF-1.4
    1 0 obj
    <<
    /Type /Catalog
    /Pages 2 0 R
    >>
    endobj
    2 0 obj
    <<
    /Type /Pages
    /Kids [3 0 R]
    /Count 1
    >>
    endobj
    3 0 obj
    <<
    /Type /Page
    /Parent 2 0 R
    /MediaBox [0 0 612 792]
    /Contents 4 0 R
    >>
    endobj
    4 0 obj
    <<
    /Length 44
    >>
    stream
    BT
    /F1 12 Tf
    100 700 Td
    (September 2025) Tj
    ET
    endstream
    endobj
    xref
    0 5
    0000000000 65535 f 
    0000000009 00000 n 
    0000000058 00000 n 
    0000000115 00000 n 
    0000000196 00000 n 
    trailer
    <<
    /Size 5
    /Root 1 0 R
    >>
    startxref
    290
    %%EOF
    """


@pytest.fixture
def sample_availability_result():
    """Sample availability analysis result"""
    return {
        'timestamp': '2025-09-01T12:00:00',
        'target_dates': ['2025-09-12', '2025-09-15', '2025-09-21'],
        'method_used': 'text_extraction',
        'availability': {
            '2025-09-12': 'available',
            '2025-09-15': 'booked', 
            '2025-09-21': 'day_use'
        },
        'success': True,
        'error': None
    }


# Configure pytest to show full diff for assertions
def pytest_configure(config):
    """Configure pytest settings"""
    config.option.tb = "short"