#!/usr/bin/env python3
"""
Gestalt runner module for executing and validating Gestalt YAML files.
Integrates with the local gestalt package for validation and execution.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


def validate_gestalt_file(gestalt_file: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate a Gestalt YAML file using the local gestalt package.

    Args:
        gestalt_file: Path to the Gestalt YAML file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Try to import and use gestalt validation first
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "gestalt"))
            from gestalt import Stylesheet

            # Parse the stylesheet using Gestalt's parser
            # Add the gestalt widgets directory to the include path
            gestalt_widgets_path = str(
                Path(__file__).parent.parent / "gestalt" / "widgets"
            )
            styles = Stylesheet.parse(str(gestalt_file), [".", gestalt_widgets_path])
            return True, None

        except ImportError as e:
            # Fall back to basic YAML validation if gestalt import fails
            with open(gestalt_file) as f:
                yaml_content = yaml.safe_load(f)

            if not yaml_content:
                return False, "Empty YAML file"
            return True, f"Warning: Could not import gestalt for full validation: {e}"

    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"


def run_gestalt_file(
    gestalt_file: Path,
    output_format: str = "qt",
    output_file: Optional[Path] = None,
) -> Tuple[bool, str]:
    """
    Run a Gestalt file through the gestalt converter.

    Args:
        gestalt_file: Path to the Gestalt YAML file
        output_format: Output format (qt, bob, dm)
        output_file: Optional output file path

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

        cmd.append(str(gestalt_file.resolve()))  # Convert to absolute path

        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            output_msg = f"Successfully generated {output_format} output"
            if output_file:
                output_msg += f" to {output_file}"
            return True, output_msg
        else:
            return False, f"Gestalt execution failed: {result.stderr or result.stdout}"

    except Exception as e:
        return False, f"Error running gestalt: {e}"


def test_gestalt_conversion(gestalt_file: Path) -> Dict[str, Any]:
    """
    Test a Gestalt file conversion to multiple formats.

    Args:
        gestalt_file: Path to the Gestalt YAML file

    Returns:
        Dictionary with test results
    """
    results = {
        "file": str(gestalt_file),
        "validation": {},
        "conversions": {},
        "overall_success": False,
    }

    # Validate the file
    is_valid, error_msg = validate_gestalt_file(gestalt_file)
    results["validation"] = {"valid": is_valid, "error": error_msg}

    if not is_valid:
        return results

    # Test conversions to different formats
    formats_to_test = ["qt", "bob", "dm"]
    # formats_to_test = ["qt"]

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        for fmt in formats_to_test:
            output_file = temp_path / f"test_output.{fmt}"

            success, message = run_gestalt_file(gestalt_file, fmt, output_file)

            results["conversions"][fmt] = {
                "success": success,
                "message": message,
                "output_exists": output_file.exists() if success else False,
                "output_size": (
                    output_file.stat().st_size if output_file.exists() else 0
                ),
            }

    # Overall success if validation passed and at least one conversion worked
    results["overall_success"] = results["validation"]["valid"] and any(
        conv["success"] for conv in results["conversions"].values()
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


def create_gestalt_workflow(
    medm_file: Path, output_dir: Path, test_conversion: bool = True
) -> Dict[str, Any]:
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

    results = {
        "medm_file": str(medm_file),
        "conversion": {},
        "validation": {},
        "testing": {},
        "overall_success": False,
    }

    try:
        # Step 1: Convert MEDM to Gestalt
        gestalt_file = output_dir / f"{medm_file.stem}.yml"
        converter = MedmToGestaltConverter()
        gestalt_file = converter.convert_file(medm_file, gestalt_file)

        results["conversion"] = {
            "success": True,
            "gestalt_file": str(gestalt_file),
            "message": "Successfully converted MEDM to Gestalt",
        }

        if test_conversion:
            # Step 2: Validate and test the Gestalt file
            test_results = test_gestalt_conversion(gestalt_file)

            results["validation"] = test_results["validation"]
            results["testing"] = test_results["conversions"]

            results["overall_success"] = test_results["overall_success"]
        else:
            results["overall_success"] = True

    except Exception as e:
        results["conversion"] = {"success": False, "message": f"Conversion failed: {e}"}

    return results
