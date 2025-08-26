"""
Shared test configuration and fixtures for adl2gestalt tests.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from typing import Dict, Any

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_medm_dir(temp_dir):
    """Create a directory with sample MEDM files."""
    medm_dir = temp_dir / "medm"
    medm_dir.mkdir()
    
    # Copy sample MEDM file
    sample_medm = TEST_DATA_DIR / "sample_medm.adl"
    if sample_medm.exists():
        shutil.copy(sample_medm, medm_dir / "sample.adl")
    
    # Create additional test files
    (medm_dir / "test1.adl").write_text("""
file {
    name="test1.adl"
    version=030109
}
display {
    object {
        x=0
        y=0
        width=200
        height=100
    }
    clr=14
    bclr=4
}
text {
    object {
        x=10
        y=10
        width=50
        height=20
    }
    "basic attribute" {
        clr=14
    }
    textix="Test1"
}
""")
    
    (medm_dir / "test2.adl").write_text("""
file {
    name="test2.adl"
    version=030109
}
display {
    object {
        x=0
        y=0
        width=200
        height=100
    }
    clr=14
    bclr=4
}
text {
    object {
        x=10
        y=10
        width=50
        height=20
    }
    "basic attribute" {
        clr=14
    }
    textix="Test2"
}
""")
    
    return medm_dir


@pytest.fixture
def sample_gestalt_dir(temp_dir):
    """Create a directory with sample Gestalt files."""
    gestalt_dir = temp_dir / "gestalt"
    gestalt_dir.mkdir()
    
    # Copy sample Gestalt file
    sample_gestalt = TEST_DATA_DIR / "sample_gestalt.yml"
    if sample_gestalt.exists():
        shutil.copy(sample_gestalt, gestalt_dir / "sample.yml")
    
    # Create additional test files
    (gestalt_dir / "test1.yml").write_text("""
Form: !Form
    title: "Test 1"
    margins: 5x5x5x5

Test_Text: !Text
    geometry: 10x10
    text: "Hello Test1"
""")
    
    (gestalt_dir / "test2.yml").write_text("""
Form: !Form  
    title: "Test 2"
    margins: 5x5x5x5

Test_Monitor: !TextMonitor
    geometry: 100x20
    pv: "TEST:VALUE"
""")
    
    return gestalt_dir


@pytest.fixture
def sample_test_data():
    """Load sample test data for Gestalt files."""
    test_data_file = TEST_DATA_DIR / "sample_data.yml"
    if test_data_file.exists():
        import yaml
        with open(test_data_file, 'r') as f:
            return yaml.safe_load(f)
    else:
        return {
            "PREFIX": "TEST:",
            "DEVICE": "DEVICE01",
            "Inputs": ["INPUT1", "INPUT2"],
            "LEDs": ["LED1", "LED2"]
        }


@pytest.fixture
def mock_gestalt_success():
    """Mock successful gestalt execution."""
    from unittest.mock import MagicMock, patch
    
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Success"
    mock_result.stderr = ""
    
    with patch('subprocess.run', return_value=mock_result) as mock_run:
        yield mock_run


@pytest.fixture
def mock_gestalt_failure():
    """Mock failed gestalt execution."""
    from unittest.mock import MagicMock, patch
    
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Test error"
    
    with patch('subprocess.run', return_value=mock_result) as mock_run:
        yield mock_run


# Test data constants
SAMPLE_MEDM_CONTENT = '''
file {
    name="test.adl"
    version=030109
}
display {
    object {
        x=0
        y=0
        width=400
        height=300
    }
    clr=14
    bclr=4
    cmap=""
}
"color map" {
    ncolors=65
    colors {
        ffffff,
        ececec,
        000000,
    }
}
text {
    object {
        x=10
        y=10
        width=100
        height=20
    }
    "basic attribute" {
        clr=14
    }
    textix="Test Label"
    align="horiz. left"
}
"text update" {
    object {
        x=10
        y=40
        width=100
        height=20
    }
    monitor {
        chan="TEST:DEVICE:VALUE"
        clr=54
        bclr=4
    }
}
'''

SAMPLE_GESTALT_CONTENT = '''
#include colors.yml
#include widgets.yml

Form: !Form
    margins: 5x0x5x5
    title: "Test Display"

Test_Widget: !TextMonitor
    geometry: 100x20
    pv: "TEST:DEVICE:VALUE"
    alignment: Left
    font: -Liberation Sans - normal - 12
    background: "#FFFFFF"
    foreground: "#000000"
'''


@pytest.fixture
def sample_medm_content():
    """Sample MEDM content for creating test files."""
    return SAMPLE_MEDM_CONTENT


@pytest.fixture 
def sample_gestalt_content():
    """Sample Gestalt content for creating test files."""
    return SAMPLE_GESTALT_CONTENT


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests if gestalt package not available."""
    skip_integration = pytest.mark.skip(reason="gestalt package not available")
    
    # Try to import gestalt to see if it's available
    try:
        import sys
        from pathlib import Path
        
        # Add src/gestalt to path temporarily
        gestalt_path = Path(__file__).parent.parent / "src" / "gestalt"
        if gestalt_path.exists():
            sys.path.insert(0, str(gestalt_path))
            import gestalt
            gestalt_available = True
        else:
            gestalt_available = False
    except ImportError:
        gestalt_available = False
    
    if not gestalt_available:
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)


# Helper functions for tests
def create_test_medm_file(path: Path, content: str = None) -> Path:
    """Create a test MEDM file with optional custom content."""
    if content is None:
        content = SAMPLE_MEDM_CONTENT
    
    path.write_text(content)
    return path


def create_test_gestalt_file(path: Path, content: str = None) -> Path:
    """Create a test Gestalt file with optional custom content.""" 
    if content is None:
        content = SAMPLE_GESTALT_CONTENT
    
    path.write_text(content)
    return path