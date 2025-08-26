#!/usr/bin/env python3
"""
Entry point wrapper for the gestalt command-line tool.
This provides a clean entry point without modifying the original gestalt code.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Main entry point that calls the gestalt.py script with proper path setup."""
    # Find the gestalt script in the package
    package_dir = Path(__file__).parent.parent
    gestalt_script = package_dir / "gestalt" / "gestalt.py"
    
    if not gestalt_script.exists():
        print(f"Error: gestalt.py not found at {gestalt_script}")
        sys.exit(1)
    
    # Execute the gestalt script with the original arguments
    cmd = [sys.executable, str(gestalt_script)] + sys.argv[1:]
    
    # Change to the gestalt directory so relative imports work properly
    gestalt_dir = gestalt_script.parent
    old_cwd = os.getcwd()
    
    try:
        os.chdir(gestalt_dir)
        # Run the gestalt script in its proper environment
        result = subprocess.run(cmd, cwd=gestalt_dir)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Error running gestalt: {e}")
        sys.exit(1)
    finally:
        os.chdir(old_cwd)


if __name__ == "__main__":
    main()