"""
Tests for Gestalt integration functionality.
"""

import pytest
import tempfile
from pathlib import Path
import yaml
from unittest.mock import patch, MagicMock

from adl2gestalt.gestalt_runner import (
    validate_gestalt_file,
    run_gestalt_file,
    test_gestalt_conversion,
    generate_test_data_for_gestalt,
    create_gestalt_workflow
)


@pytest.fixture
def sample_gestalt_content():
    """Sample Gestalt YAML content for testing."""
    return """#include colors.yml
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

Test_Button: !MessageButton
    geometry: 80x30 x 120x0
    text: "Test"
    pv: "TEST:DEVICE:CMD"
    value: "1"
"""


@pytest.fixture
def sample_gestalt_file(tmp_path, sample_gestalt_content):
    """Create a temporary Gestalt YAML file for testing."""
    gestalt_file = tmp_path / "test.yml"
    gestalt_file.write_text(sample_gestalt_content)
    return gestalt_file


@pytest.fixture
def sample_medm_file(tmp_path):
    """Create a temporary MEDM ADL file for testing."""
    medm_content = """
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
    gridSpacing=10
    gridOn=0
    snapToGrid=0
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
"""
    medm_file = tmp_path / "test.adl"
    medm_file.write_text(medm_content)
    return medm_file


class TestGestaltValidation:
    """Test Gestalt file validation functionality."""
    
    def test_validate_valid_gestalt_file(self, sample_gestalt_file):
        """Test validation of a valid Gestalt file."""
        is_valid, error_msg = validate_gestalt_file(sample_gestalt_file)
        assert is_valid
        # Error message might be a warning about gestalt import
        if error_msg:
            assert "Warning" in error_msg
    
    def test_validate_empty_file(self, tmp_path):
        """Test validation of an empty file."""
        empty_file = tmp_path / "empty.yml"
        empty_file.write_text("")
        
        is_valid, error_msg = validate_gestalt_file(empty_file)
        assert not is_valid
        assert "Empty YAML file" in error_msg
    
    def test_validate_invalid_yaml(self, tmp_path):
        """Test validation of invalid YAML."""
        invalid_file = tmp_path / "invalid.yml"
        invalid_file.write_text("invalid: yaml: content: [\n")
        
        is_valid, error_msg = validate_gestalt_file(invalid_file)
        assert not is_valid
        assert "YAML parsing error" in error_msg
    
    def test_validate_nonexistent_file(self, tmp_path):
        """Test validation of nonexistent file."""
        nonexistent = tmp_path / "nonexistent.yml"
        
        is_valid, error_msg = validate_gestalt_file(nonexistent)
        assert not is_valid
        assert error_msg is not None


class TestGestaltExecution:
    """Test Gestalt file execution functionality."""
    
    @patch('subprocess.run')
    def test_run_gestalt_file_success(self, mock_run, sample_gestalt_file, tmp_path):
        """Test successful execution of Gestalt file."""
        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        output_file = tmp_path / "output.ui"
        success, message = run_gestalt_file(sample_gestalt_file, "qt", output_file)
        
        assert success
        assert "Successfully generated qt output" in message
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_gestalt_file_failure(self, mock_run, sample_gestalt_file):
        """Test failed execution of Gestalt file."""
        # Mock failed subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error message"
        mock_run.return_value = mock_result
        
        success, message = run_gestalt_file(sample_gestalt_file, "qt")
        
        assert not success
        assert "Gestalt execution failed" in message
        assert "Error message" in message
    
    def test_run_gestalt_file_missing_script(self, sample_gestalt_file):
        """Test execution when gestalt script is missing."""
        # This should fail because gestalt.py doesn't exist at expected location
        success, message = run_gestalt_file(sample_gestalt_file, "qt")
        
        assert not success
        assert "Gestalt script not found" in message


class TestGestaltTesting:
    """Test Gestalt conversion testing functionality."""
    
    @patch('adl2gestalt.gestalt_runner.validate_gestalt_file')
    @patch('adl2gestalt.gestalt_runner.run_gestalt_file')
    def test_test_gestalt_conversion_success(self, mock_run, mock_validate, sample_gestalt_file):
        """Test successful Gestalt conversion testing."""
        # Mock validation success
        mock_validate.return_value = (True, None)
        
        # Mock conversion success for all formats
        mock_run.return_value = (True, "Success")
        
        results = test_gestalt_conversion(sample_gestalt_file)
        
        assert results["validation"]["valid"]
        assert results["overall_success"]
        
        # Check that all three formats were tested
        assert "qt" in results["conversions"]
        assert "bob" in results["conversions"]
        assert "dm" in results["conversions"]
        
        for fmt_result in results["conversions"].values():
            assert fmt_result["success"]
    
    @patch('adl2gestalt.gestalt_runner.validate_gestalt_file')
    def test_test_gestalt_conversion_validation_failure(self, mock_validate, sample_gestalt_file):
        """Test Gestalt conversion testing with validation failure."""
        # Mock validation failure
        mock_validate.return_value = (False, "Validation error")
        
        results = test_gestalt_conversion(sample_gestalt_file)
        
        assert not results["validation"]["valid"]
        assert not results["overall_success"]
        assert results["validation"]["error"] == "Validation error"
    
    def test_generate_test_data_for_gestalt(self, sample_gestalt_file):
        """Test generation of test data for Gestalt file."""
        test_data = generate_test_data_for_gestalt(sample_gestalt_file)
        
        assert isinstance(test_data, dict)
        # Should include default test data
        assert "PREFIX" in test_data
        assert "DEVICE" in test_data
        
        # Should detect TEST:DEVICE:VALUE pattern and create related test data
        assert test_data["PREFIX"] == "TEST:"
        assert test_data["DEVICE"] == "DEVICE01"


class TestGestaltWorkflow:
    """Test complete Gestalt workflow functionality."""
    
    @patch('adl2gestalt.gestalt_runner.test_gestalt_conversion')
    def test_create_gestalt_workflow_success(self, mock_test, sample_medm_file, tmp_path):
        """Test successful complete workflow."""
        # Mock successful testing
        mock_test.return_value = {
            "validation": {"valid": True, "error": None},
            "conversions": {"qt": {"success": True}},
            "overall_success": True
        }
        
        output_dir = tmp_path / "output"
        results = create_gestalt_workflow(sample_medm_file, output_dir, test_conversion=True)
        
        assert results["conversion"]["success"]
        assert results["overall_success"]
        
        # Check that Gestalt file was created
        gestalt_file = output_dir / f"{sample_medm_file.stem}.yml"
        assert gestalt_file.exists()
        
        # Verify content contains expected Gestalt format
        content = gestalt_file.read_text()
        assert "#include colors.yml" in content
        assert "#include widgets.yml" in content
        assert "!Form" in content
    
    def test_create_gestalt_workflow_conversion_failure(self, tmp_path):
        """Test workflow with conversion failure."""
        # Create invalid MEDM file
        invalid_medm = tmp_path / "invalid.adl"
        invalid_medm.write_text("invalid medm content")
        
        output_dir = tmp_path / "output"
        results = create_gestalt_workflow(invalid_medm, output_dir, test_conversion=False)
        
        assert not results["conversion"]["success"]
        assert not results["overall_success"]
        assert "Conversion failed" in results["conversion"]["message"]


class TestFixtures:
    """Test that fixtures work correctly."""
    
    def test_sample_gestalt_file_fixture(self, sample_gestalt_file):
        """Test that the sample Gestalt file fixture works."""
        assert sample_gestalt_file.exists()
        content = sample_gestalt_file.read_text()
        assert "!Form" in content
        assert "Test_Widget" in content
    
    def test_sample_medm_file_fixture(self, sample_medm_file):
        """Test that the sample MEDM file fixture works."""
        assert sample_medm_file.exists()
        content = sample_medm_file.read_text()
        assert 'name="test.adl"' in content
        assert "text update" in content


@pytest.mark.integration
class TestIntegration:
    """Integration tests that require the actual gestalt package."""
    
    def test_full_integration_with_real_files(self, sample_medm_file, tmp_path):
        """Test full integration with real file conversion."""
        output_dir = tmp_path / "output"
        
        # This will only work if gestalt package is properly installed
        results = create_gestalt_workflow(sample_medm_file, output_dir, test_conversion=False)
        
        # At minimum, conversion should succeed
        assert results["conversion"]["success"]
        
        # Check that output file exists and has correct content
        gestalt_file = Path(results["conversion"]["gestalt_file"])
        assert gestalt_file.exists()
        
        # Verify it's valid YAML
        with open(gestalt_file, 'r') as f:
            yaml_content = yaml.safe_load(f)
        assert yaml_content is not None