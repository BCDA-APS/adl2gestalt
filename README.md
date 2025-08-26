# ADL to Gestalt Converter

Convert MEDM (Motif Editor and Display Manager) ADL files to Gestalt YAML format for modern EPICS display systems.

## Overview

This project provides a Python package to convert legacy MEDM `.adl` files into Gestalt `.yml` layout files. Gestalt can then generate equivalent UI displays in modern formats like caQtDM, CSS-Phoebus, or PyDM, enabling seamless migration from legacy MEDM screens to contemporary EPICS display technologies.

## Features

- **Complete ADL Parsing**: Reads and parses MEDM ADL files with all widget types
- **Gestalt YAML Generation**: Creates properly formatted Gestalt layout files
- **Batch Processing**: Convert single files or entire directories
- **Status Tracking**: Identify which files need conversion or updating
- **Modern CLI**: User-friendly command-line interface with progress bars
- **Gestalt Integration**: Built-in validation and testing using local Gestalt package
- **Workflow Automation**: Complete conversion and testing workflows
- **Multiple Output Formats**: Generate Qt, CSS-Phoebus, and PyDM formats through Gestalt
- **Extensible Architecture**: Easy to add new widget mappings

## Installation

### From Source

```bash
# Clone the main repository
git clone https://github.com/BCDA-APS/adl2gestalt.git
cd adl2gestalt

# Clone the official BCDA-APS gestalt package for local integration
git clone https://github.com/BCDA-APS/gestalt.git src/gestalt

# Install the package in development mode
pip install -e .

# Verify installation by checking available commands
adl2gestalt --help
```

### For Development

```bash
pip install -e ".[dev]"
```

### For GUI Support

```bash
# Install with PyQt5 support for Gestalt GUI functionality
pip install -e ".[gui]"
```

### Dependencies

The installation includes:
- **Core dependencies**: PyYAML, Click, lxml for ADL parsing and YAML generation
- **Gestalt integration**: Local gestalt package (BCDA-APS) for validation and UI generation
- **Development tools**: pytest, black, ruff, mypy for code quality
- **GUI support** (optional): PyQt5 for Gestalt GUI functionality

The gestalt package is cloned locally to ensure compatibility and enable testing of generated Gestalt files.

### Installation Troubleshooting

**Issue: `git clone` fails for gestalt package**
```bash
# Ensure you're using the correct BCDA-APS repository
git clone https://github.com/BCDA-APS/gestalt.git src/gestalt
```

**Issue: PyQt5 installation fails**
```bash
# On Ubuntu/Debian
sudo apt-get install python3-pyqt5-dev python3-pyqt5

# On macOS with Homebrew
brew install pyqt5

# Or skip GUI support and use headless mode
pip install -e . # (GUI commands will show warnings but still work)
```

**Issue: `adl2gestalt: command not found`**
```bash
# Ensure you're in the correct directory and using editable install
cd adl2gestalt
pip install -e .

# Verify entry points are working
python -m adl2gestalt --help
```

## Usage

### Command-Line Interface

The package provides several commands accessible through the `adl2gestalt` command or individual entry points:

**Two ways to run commands:**
1. **Grouped**: `adl2gestalt <command> [args]` (e.g., `adl2gestalt convert file.adl`)
2. **Individual**: `adl2gestalt-<command> [args]` (e.g., `adl2gestalt-convert file.adl`)

All examples below show the grouped format, but individual entry points work identically.

#### List MEDM Files

```bash
# List all ADL files in a directory
adl2gestalt list-medm examples/medm/
# Output:
# MEDM files in examples/medm:
#   29ID_ca_all.adl
#   29id.adl
#   29id_BL_User.adl
#   29id_Diagnostics.adl
#   IEXMachinePhysics.adl
# Total: 5 files

# List with count only
adl2gestalt list-medm examples/medm/ --count
# Output: Found 5 MEDM files


#### List Gestalt Files

```bash
# List all YAML files in a directory
adl2gestalt list-gestalt examples/gestalt/

# List with count only
adl2gestalt list-gestalt examples/gestalt/ --count
# Output: Found 5 Gestalt files
```

#### Check Conversion Status

```bash
# Show which files need conversion
adl2gestalt status examples/medm/ examples/gestalt/
# Output:
# Conversion Status Summary
# ========================================
# MEDM folder:     examples/medm
# Gestalt folder:  examples/gestalt
# Total MEDM files: 5
#   ✅ Up to date:  5
#   ⚠️  Outdated:    0
#   ❌ Pending:     0

# Show detailed status
adl2gestalt status examples/medm/ examples/gestalt/ --verbose
```

#### Convert Files

```bash
# Convert a single file
adl2gestalt convert examples/medm/29id.adl -o examples/gestalt/29id.yml

# Convert with overwrite
adl2gestalt convert examples/medm/29id.adl -o examples/gestalt/29id.yml --force

# Batch convert a directory
adl2gestalt convert examples/medm/ --batch -o examples/gestalt/
# Output:
# Found 5 MEDM files to convert
# Converting files
# Conversion Summary:
#   ✅ Successfully converted: 5

# Batch convert in place (overwrites existing)
adl2gestalt convert examples/medm/ --batch --force
```

#### Validate Gestalt Files

```bash
# Validate a single Gestalt file
adl2gestalt validate examples/gestalt/29id.yml
# Output: ✅ examples/gestalt/29id.yml is valid

# Validate with verbose output
adl2gestalt validate examples/gestalt/29id.yml --verbose
```

#### Generate UI Files from Gestalt

```bash
# Generate Qt UI file
adl2gestalt generate examples/gestalt/29id.yml --format qt -o 29id.ui

# Generate CSS-Phoebus BOB file
adl2gestalt generate examples/gestalt/29id.yml --format bob -o 29id.bob

# Generate PyDM file
adl2gestalt generate examples/gestalt/29id.yml --format dm -o 29id.dm

# Use test data for macro substitution
adl2gestalt generate examples/gestalt/29id.yml --data test_data.yml
```

#### Test Gestalt Files

```bash
# Test a Gestalt file with all output formats
adl2gestalt test-gestalt examples/gestalt/29id.yml
# Output:
# Testing examples/gestalt/29id.yml
# ==================================================
# ✅ File validation: PASSED
# 
# Format conversion tests:
#   qt: ✅ PASSED
#  bob: ✅ PASSED  
#   dm: ✅ PASSED
#
# ✅ Overall: PASSED

# Test with verbose output and custom test data
adl2gestalt test-gestalt examples/gestalt/29id.yml --verbose --data custom_test.yml
```

#### Complete Workflow

```bash
# Complete workflow: convert MEDM to Gestalt and test
adl2gestalt workflow examples/medm/ examples/gestalt/
# Output:
# Processing 5 MEDM files
# Processing workflow
# Workflow Summary:
#   ✅ Successfully processed: 5

# Workflow without testing
adl2gestalt workflow examples/medm/ examples/gestalt/ --no-test

# Workflow with verbose output
adl2gestalt workflow examples/medm/ examples/gestalt/ --verbose
```

### Python API

```python
from adl2gestalt import MedmToGestaltConverter, list_medm_files, get_conversion_summary
from adl2gestalt.gestalt_runner import (
    validate_gestalt_file,
    run_gestalt_file,
    test_gestalt_conversion,
    create_gestalt_workflow
)
from pathlib import Path

# Create converter
converter = MedmToGestaltConverter()

# Convert a single file
input_file = Path("examples/medm/29id.adl")
output_file = Path("examples/gestalt/29id.yml")
result_path = converter.convert_file(input_file, output_file)
print(f"Converted: {result_path}")

# Validate the converted Gestalt file
is_valid, error_msg = validate_gestalt_file(output_file)
if is_valid:
    print("✅ Gestalt file is valid")
else:
    print(f"❌ Validation failed: {error_msg}")

# Test Gestalt file conversion to different formats
test_results = test_gestalt_conversion(output_file)
if test_results["overall_success"]:
    print("✅ All format conversions passed")
    for fmt, result in test_results["conversions"].items():
        print(f"  {fmt}: {'✅' if result['success'] else '❌'}")

# Generate UI file from Gestalt
success, message = run_gestalt_file(output_file, "qt", Path("29id.ui"))
if success:
    print(f"✅ Generated Qt file: {message}")

# Complete workflow: convert and test
workflow_result = create_gestalt_workflow(
    input_file, 
    Path("examples/gestalt"), 
    test_conversion=True
)
if workflow_result["overall_success"]:
    print("✅ Complete workflow succeeded")

# List all MEDM files
medm_files = list_medm_files(Path("examples/medm"))
print(f"Found {len(medm_files)} MEDM files")

# Get conversion summary
summary = get_conversion_summary(
    Path("examples/medm"),
    Path("examples/gestalt")
)
print(f"Total: {summary['total_medm']}")
print(f"Up to date: {len(summary['up_to_date'])}")
print(f"Pending: {summary['total_pending']}")

# Batch convert and test multiple files
for medm_file in medm_files:
    gestalt_file = Path("examples/gestalt") / medm_file.with_suffix('.yml').name
    workflow_result = create_gestalt_workflow(medm_file, Path("examples/gestalt"))
    if workflow_result["overall_success"]:
        print(f"✅ {medm_file.name} -> {workflow_result['conversion']['gestalt_file']}")
```

## Widget Mapping

The converter maps MEDM widgets to their Gestalt equivalents:

| MEDM Widget | Gestalt Widget | Description |
|-------------|----------------|-------------|
| arc | Arc | Circular arc drawing |
| rectangle | Rectangle | Rectangular shape |
| oval | Ellipse | Elliptical shape |
| polygon | Polygon | Multi-sided shape |
| polyline | Polyline | Connected line segments |
| text | Text | Static text display |
| text update | TextMonitor | Dynamic text display with PV |
| text entry | TextEntry | Text input field |
| bar | Scale | Bar chart/progress indicator |
| meter | Meter | Gauge/meter display |
| cartesian plot | XYPlot | 2D plotting widget |
| strip chart | StripChart | Time-series plotting |
| choice button | ChoiceButton | Selection button |
| message button | MessageButton | Action button |
| menu | Menu | Dropdown menu |
| related display | RelatedDisplay | Screen navigation |
| shell command | ShellCommand | Command execution |
| composite | Group | Grouped widgets |
| embedded display | Embed | Embedded screen |
| indicator | LED | LED indicator |
| byte | ByteMonitor | Byte value display |

## Gestalt Output Format

The converter generates YAML files compatible with the [BCDA-APS Gestalt](https://github.com/BCDA-APS/gestalt) system:

### Basic Structure
```yaml
# Gestalt display file generated from MEDM ADL
# Source: 29id.adl
# Generator: adl2gestalt

#include colors.yml
#include widgets.yml

# Custom colors from MEDM color table
_medm_color_3: &medm_color_3 $c8c8c8
_medm_color_19: &medm_color_19 $216c00

display_name: !Display
    geometry: 437x274 x 2917x77
    title: "MEDM Display"
    foreground: *medm_color_19
    background: *medm_color_3

widget_name: !WidgetType
    geometry: 50x14 x 30x8
    pv: "IOC:PV:NAME"
    text: "Label"
```

### Key Features
- **Widget Tags**: Uses `!WidgetType` YAML tags (e.g., `!Rectangle`, `!TextMonitor`)
- **Geometry Format**: `WIDTHxHEIGHT x XxY` positioning
- **Color System**: Hex colors (`$RRGGBB`) with YAML aliases (`*colorname`)
- **PV Integration**: Proper EPICS process variable mapping
- **Includes**: References to `colors.yml` and `widgets.yml` for reusable components
- **MEDM Color Preservation**: Custom color definitions preserve original MEDM color schemes

## Project Structure

```
adl2gestalt/
├── pyproject.toml       # Modern Python packaging config
├── README.md           # Project documentation
├── LICENSE             # MIT license
├── src/
│   ├── adl2gestalt/    # Main package source code
│   │   ├── __init__.py     # Package initialization
│   │   ├── parser.py       # ADL file parser (from MEDM)
│   │   ├── converter.py    # ADL to Gestalt converter
│   │   ├── scanner.py      # File discovery utilities
│   │   ├── widget_mapper.py # Widget mapping definitions
│   │   ├── symbols.py      # MEDM widget constants
│   │   ├── gestalt_runner.py # Gestalt integration module
│   │   └── cli.py         # Command-line interface
│   └── gestalt/        # Local Gestalt package (cloned)
│       ├── gestalt.py      # Main Gestalt script
│       ├── gestalt/        # Gestalt package modules
│       └── layouts/        # Sample layouts and widgets
├── examples/
│   ├── medm/          # Example MEDM/ADL files
│   │   ├── 29id.adl                # Main beamline screen
│   │   ├── 29ID_ca_all.adl        # Current amplifier screen
│   │   ├── 29id_BL_User.adl       # Beamline user screen
│   │   ├── 29id_Diagnostics.adl   # Diagnostics screen
│   │   └── IEXMachinePhysics.adl  # Machine physics screen
│   └── gestalt/       # Converted Gestalt YAML files
│       ├── 29id.yml
│       ├── 29ID_ca_all.yml
│       ├── 29id_BL_User.yml
│       ├── 29id_Diagnostics.yml
│       └── IEXMachinePhysics.yml
├── tests/             # Comprehensive test suite
│   ├── conftest.py               # Test configuration and fixtures
│   ├── test_gestalt_integration.py  # Gestalt integration tests
│   ├── fixtures/                 # Test data and fixtures
│   │   ├── sample_data.yml       # Sample test data for Gestalt
│   │   ├── sample_gestalt.yml    # Sample Gestalt file
│   │   └── sample_medm.adl       # Sample MEDM file
│   ├── test_converter.py         # Converter unit tests
│   ├── test_parser.py            # Parser unit tests
│   ├── test_scanner.py           # Scanner unit tests
│   └── test_cli.py               # CLI integration tests
└── docs/              # Documentation
    ├── MEDM_DOC.md    # MEDM widget reference
    ├── PLAN.md        # Development plan
    └── PROJECT.md     # Project description
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest -m "not integration"

# Run integration tests (requires gestalt package)
pytest -m integration

# Run with coverage
pytest --cov=adl2gestalt --cov-report=html

# Run specific test file
pytest tests/test_gestalt_integration.py -v
```

### Code Formatting

```bash
# Format code
black src/ tests/

# Check code style
ruff check src/ tests/

# Fix code style issues
ruff check src/ tests/ --fix
```

### Type Checking

```bash
mypy src/
```

### Development Workflow

1. **Setup Development Environment**:
   ```bash
   # Clone both repositories correctly
   git clone https://github.com/BCDA-APS/adl2gestalt.git
   cd adl2gestalt
   git clone https://github.com/BCDA-APS/gestalt.git src/gestalt
   pip install -e ".[dev]"
   ```

2. **Run Tests**: `pytest`

3. **Test CLI Commands**:
   ```bash
   # Test conversion workflow
   adl2gestalt workflow examples/medm/ /tmp/test_output/ --verbose
   
   # Test individual commands
   adl2gestalt validate examples/gestalt/29id.yml
   adl2gestalt test-gestalt examples/gestalt/29id.yml --verbose
   ```

4. **Format and Check Code**: `black src/ && ruff check src/`

5. **Type Check**: `mypy src/`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Based on the ADL parser from the adl2pydm project
- Designed to work with the Gestalt layout system for EPICS displays