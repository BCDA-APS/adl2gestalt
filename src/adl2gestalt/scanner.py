"""File scanning and conversion status utilities."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def list_medm_files(folder: Path, recursive: bool = True) -> List[Path]:
    """
    Recursively find all .adl files in folder.

    Parameters
    ----------
    folder : Path
        Directory to search for MEDM files
    recursive : bool
        Whether to search subdirectories

    Returns
    -------
    List[Path]
        List of paths to .adl files found
    """
    folder = Path(folder)
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder}")

    if recursive:
        pattern = "**/*.adl"
    else:
        pattern = "*.adl"

    files = sorted(folder.glob(pattern))
    return files


def list_gestalt_files(folder: Path, recursive: bool = True) -> List[Path]:
    """
    Recursively find all .yml/.yaml files in folder.

    Parameters
    ----------
    folder : Path
        Directory to search for Gestalt files
    recursive : bool
        Whether to search subdirectories

    Returns
    -------
    List[Path]
        List of paths to .yml/.yaml files found
    """
    folder = Path(folder)
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder}")

    files = []
    patterns = ["**/*.yml", "**/*.yaml"] if recursive else ["*.yml", "*.yaml"]

    for pattern in patterns:
        files.extend(folder.glob(pattern))

    return sorted(files)


def get_gestalt_path_for_medm(
    medm_file: Path, medm_folder: Path, gestalt_folder: Path
) -> Path:
    """
    Calculate the expected Gestalt file path for a given MEDM file.

    Parameters
    ----------
    medm_file : Path
        Path to the MEDM file
    medm_folder : Path
        Root folder containing MEDM files
    gestalt_folder : Path
        Root folder for Gestalt files

    Returns
    -------
    Path
        Expected path for the corresponding Gestalt file
    """
    # Get relative path from medm_folder to medm_file
    try:
        relative_path = medm_file.relative_to(medm_folder)
    except ValueError:
        # If medm_file is not under medm_folder, use just the filename
        relative_path = medm_file.name

    # Change extension to .yml
    gestalt_relative = relative_path.with_suffix(".yml")

    # Construct full path in gestalt folder
    return gestalt_folder / gestalt_relative


def get_conversion_status(medm_file: Path, gestalt_folder: Path) -> Dict[str, Any]:
    """
    Check if MEDM file has been converted and if it's up to date.

    Parameters
    ----------
    medm_file : Path
        Path to the MEDM file
    gestalt_folder : Path
        Root folder containing Gestalt files

    Returns
    -------
    Dict
        Dictionary with conversion status information:
        - 'medm_file': Path to MEDM file
        - 'gestalt_file': Expected path to Gestalt file
        - 'exists': Whether Gestalt file exists
        - 'up_to_date': Whether Gestalt file is newer than MEDM file
        - 'medm_modified': Modification time of MEDM file
        - 'gestalt_modified': Modification time of Gestalt file (if exists)
        - 'status': Status string ('converted', 'outdated')
    """
    medm_file = Path(medm_file)
    gestalt_folder = Path(gestalt_folder)

    # Find expected gestalt file path
    gestalt_file = gestalt_folder / medm_file.with_suffix(".yml").name

    status = {
        "medm_file": medm_file,
        "gestalt_file": gestalt_file,
        "exists": gestalt_file.exists(),
        "up_to_date": False,
        "medm_modified": None,
        "gestalt_modified": None,
        "status": "needs_conversion",  # Default to needs conversion
    }

    if medm_file.exists():
        medm_stat = medm_file.stat()
        status["medm_modified"] = datetime.fromtimestamp(medm_stat.st_mtime)

    if gestalt_file.exists():
        gestalt_stat = gestalt_file.stat()
        status["gestalt_modified"] = datetime.fromtimestamp(gestalt_stat.st_mtime)

        if status["medm_modified"] and status["gestalt_modified"]:
            status["up_to_date"] = status["gestalt_modified"] >= status["medm_modified"]
            status["status"] = "converted"  # Always 'converted' if Gestalt file exists
            # The 'up_to_date' field tells us if it's current or outdated

    return status


def get_conversion_summary(
    medm_folder: Path, gestalt_folder: Path, recursive: bool = True
) -> Dict[str, Any]:
    """
    Get summary statistics for conversion status.

    Parameters
    ----------
    medm_folder : Path
        Root folder containing MEDM files
    gestalt_folder : Path
        Root folder for Gestalt files
    recursive : bool
        Whether to search subdirectories

    Returns
    -------
    Dict
        Summary with counts by status and file lists
    """
    medm_files = list_medm_files(medm_folder, recursive)

    summary = {
        "total_medm": len(medm_files),
        "converted": [],  # All converted files
        "up_to_date": [],  # Converted and current
        "outdated": [],  # Converted but MEDM is newer
        "needs_conversion": [],  # No Gestalt file exists
    }

    for medm_file in medm_files:
        expected_gestalt = get_gestalt_path_for_medm(
            medm_file, medm_folder, gestalt_folder
        )
        status = get_conversion_status(medm_file, expected_gestalt.parent)

        if status["status"] == "converted":
            summary["converted"].append(medm_file)
            if status["up_to_date"]:
                summary["up_to_date"].append(medm_file)
            else:
                summary["outdated"].append(medm_file)
        else:  # status == 'needs_conversion'
            summary["needs_conversion"].append(medm_file)

    summary["total_converted"] = len(summary["converted"])
    summary["total_outdated"] = len(summary["outdated"])
    summary["total_needs_conversion"] = len(summary["needs_conversion"])

    return summary
