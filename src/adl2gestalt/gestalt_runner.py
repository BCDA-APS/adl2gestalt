#!/usr/bin/env python3
"""
Gestalt runner module for executing and validating Gestalt YAML files.
Integrates with the local gestalt package for validation and execution.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import yaml
import traceback

def validate_gestalt_file(gestalt_file: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate a Gestalt YAML file using the local gestalt package.
    
    Args:
        gestalt_file: Path to the Gestalt YAML file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # First, basic YAML validation
        with open(gestalt_file, 'r') as f:
            yaml_content = yaml.safe_load(f)
            
        if not yaml_content:
            return False, "Empty YAML file"
            
        # Try to import and use gestalt validation
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "gestalt"))
            from gestalt import Stylesheet, Datasheet
            
            # Parse the stylesheet
            styles = Stylesheet.parse(str(gestalt_file), ["."])
            return True, None
            
        except ImportError as e:
            # Fall back to basic validation if gestalt import fails
            return True, f"Warning: Could not import gestalt for full validation: {e}"
            
    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"


def run_gestalt_file(gestalt_file: Path, output_format: str = "qt", 
                    output_file: Optional[Path] = None,
                    data_file: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Run a Gestalt file through the gestalt converter.
    
    Args:
        gestalt_file: Path to the Gestalt YAML file
        output_format: Output format (qt, bob, dm)
        output_file: Optional output file path
        data_file: Optional data file for macros
        
    Returns:
        Tuple of (success, message)
    """
    try:
        gestalt_script = Path(__file__).parent.parent / "gestalt" / "gestalt.py"
        
        if not gestalt_script.exists():
            return False, f"Gestalt script not found at {gestalt_script}"
            
        cmd = [sys.executable, str(gestalt_script)]
        
        # Add arguments
        cmd.extend(["-t", output_format])
        
        if output_file:
            cmd.extend(["-o", str(output_file)])
            
        if data_file:
            cmd.extend(["-i", str(data_file)])
            
        cmd.append(str(gestalt_file))
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=gestalt_file.parent
        )
        
        if result.returncode == 0:
            output_msg = f"Successfully generated {output_format} output"
            if output_file:
                output_msg += f" to {output_file}"
            return True, output_msg
        else:
            return False, f"Gestalt execution failed: {result.stderr or result.stdout}"
            
    except Exception as e:
        return False, f"Error running gestalt: {e}"


def test_gestalt_conversion(gestalt_file: Path, test_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Test a Gestalt file conversion to multiple formats.
    
    Args:
        gestalt_file: Path to the Gestalt YAML file
        test_data: Optional test data for macro substitution
        
    Returns:
        Dictionary with test results
    """
    results = {
        "file": str(gestalt_file),
        "validation": {},
        "conversions": {},
        "overall_success": False
    }
    
    # Validate the file
    is_valid, error_msg = validate_gestalt_file(gestalt_file)
    results["validation"] = {
        "valid": is_valid,
        "error": error_msg
    }
    
    if not is_valid:
        return results
    
    # Test conversions to different formats
    formats_to_test = ["qt", "bob", "dm"]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test data file if provided
        data_file = None
        if test_data:
            data_file = temp_path / "test_data.yml"
            with open(data_file, 'w') as f:
                yaml.dump(test_data, f)
        
        for fmt in formats_to_test:
            output_file = temp_path / f"test_output.{fmt}"
            
            success, message = run_gestalt_file(
                gestalt_file, fmt, output_file, data_file
            )
            
            results["conversions"][fmt] = {
                "success": success,
                "message": message,
                "output_exists": output_file.exists() if success else False,
                "output_size": output_file.stat().st_size if output_file.exists() else 0
            }
    
    # Overall success if validation passed and at least one conversion worked
    results["overall_success"] = (
        results["validation"]["valid"] and
        any(conv["success"] for conv in results["conversions"].values())
    )
    
    return results


def batch_validate_gestalt_files(gestalt_dir: Path) -> List[Dict[str, Any]]:
    """
    Validate all Gestalt files in a directory.
    
    Args:
        gestalt_dir: Directory containing Gestalt YAML files
        
    Returns:
        List of validation results
    """
    results = []
    
    if not gestalt_dir.exists():
        return results
    
    gestalt_files = list(gestalt_dir.glob("*.yml")) + list(gestalt_dir.glob("*.yaml"))
    
    for gestalt_file in gestalt_files:
        result = test_gestalt_conversion(gestalt_file)
        results.append(result)
    
    return results


def generate_test_data_for_gestalt(gestalt_file: Path) -> Dict[str, Any]:
    """
    Generate sample test data for a Gestalt file by analyzing its content.
    
    Args:
        gestalt_file: Path to the Gestalt YAML file
        
    Returns:
        Dictionary of sample test data
    """
    try:
        with open(gestalt_file, 'r') as f:
            content = f.read()
        
        test_data = {}
        
        # Look for common macro patterns in the content
        import re
        
        # Find patterns like {MACRO} or ${MACRO}
        macro_patterns = re.findall(r'\{([A-Za-z_][A-Za-z0-9_]*)\}', content)
        for macro in macro_patterns:
            if macro not in test_data:
                # Provide reasonable defaults based on common EPICS naming
                if 'PREFIX' in macro.upper():
                    test_data[macro] = "TEST:"
                elif 'PV' in macro.upper():
                    test_data[macro] = "TEST:DEVICE:VALUE"
                elif 'COLOR' in macro.upper():
                    test_data[macro] = "#FF0000"
                elif macro.upper() in ['N', 'INDEX', 'NUM']:
                    test_data[macro] = "1"
                else:
                    test_data[macro] = f"test_{macro.lower()}"
        
        # Add some common test data
        common_test_data = {
            "PREFIX": "TEST:",
            "DEVICE": "DEVICE01",
            "Inputs": ["INPUT1", "INPUT2", "INPUT3"],
            "LEDs": ["LED1", "LED2", "LED3", "LED4"],
            "Enable_Shapes": True,
            "Tank_Color": "#4169E1"
        }
        
        # Merge common test data (don't override specific ones found)
        for key, value in common_test_data.items():
            if key not in test_data:
                test_data[key] = value
        
        return test_data
        
    except Exception as e:
        # Return minimal test data if analysis fails
        return {
            "PREFIX": "TEST:",
            "DEVICE": "DEVICE01"
        }


def create_gestalt_workflow(medm_file: Path, output_dir: Path, 
                          test_conversion: bool = True) -> Dict[str, Any]:
    """
    Complete workflow: convert MEDM to Gestalt, validate, and test.
    
    Args:
        medm_file: Path to MEDM ADL file
        output_dir: Directory for output files
        test_conversion: Whether to test the conversion
        
    Returns:
        Dictionary with workflow results
    """
    from .converter import MedmToGestaltConverter
    from .parser import parse_medm_file
    
    results = {
        "medm_file": str(medm_file),
        "conversion": {},
        "validation": {},
        "testing": {},
        "overall_success": False
    }
    
    try:
        # Step 1: Convert MEDM to Gestalt
        medm_data = parse_medm_file(medm_file)
        converter = MedmToGestaltConverter()
        gestalt_yaml = converter.convert_display(medm_data)
        
        # Save Gestalt file
        gestalt_file = output_dir / f"{medm_file.stem}.yml"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(gestalt_file, 'w') as f:
            f.write(gestalt_yaml)
            
        results["conversion"] = {
            "success": True,
            "gestalt_file": str(gestalt_file),
            "message": "Successfully converted MEDM to Gestalt"
        }
        
        if test_conversion:
            # Step 2: Validate and test the Gestalt file
            test_data = generate_test_data_for_gestalt(gestalt_file)
            test_results = test_gestalt_conversion(gestalt_file, test_data)
            
            results["validation"] = test_results["validation"]
            results["testing"] = test_results["conversions"]
            
            results["overall_success"] = test_results["overall_success"]
        else:
            results["overall_success"] = True
            
    except Exception as e:
        results["conversion"] = {
            "success": False,
            "message": f"Conversion failed: {e}"
        }
        
    return results