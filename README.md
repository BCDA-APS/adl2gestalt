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
- **Extensible Architecture**: Easy to add new widget mappings

## Installation

### From Source

```bash
git clone https://github.com/adl2gestalt/adl2gestalt.git
cd adl2gestalt
pip install -e .
```

### For Development

```bash
pip install -e ".[dev]"
```

## Usage

### Command-Line Interface

The package provides several commands accessible through the `adl2gestalt` command:

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

# Non-recursive search
adl2gestalt list-medm examples/medm/ --no-recursive
```

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

### Python API

```python
from adl2gestalt import MedmToGestaltConverter, list_medm_files, get_conversion_summary
from pathlib import Path

# Create converter
converter = MedmToGestaltConverter()

# Convert a single file
input_file = Path("examples/medm/29id.adl")
output_file = Path("examples/gestalt/29id.yml")
result_path = converter.convert_file(input_file, output_file)
print(f"Converted: {result_path}")

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

# Batch convert multiple files
for medm_file in medm_files:
    gestalt_file = Path("examples/gestalt") / medm_file.with_suffix('.yml').name
    converter.convert_file(medm_file, gestalt_file)
    print(f"Converted: {medm_file.name}")
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
├── src/adl2gestalt/    # Source code
│   ├── __init__.py     # Package initialization
│   ├── parser.py       # ADL file parser (from MEDM)
│   ├── converter.py    # ADL to Gestalt converter
│   ├── scanner.py      # File discovery utilities
│   ├── widget_mapper.py # Widget mapping definitions
│   ├── symbols.py      # MEDM widget constants
│   └── cli.py         # Command-line interface
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
├── tests/             # Unit tests
└── docs/              # Documentation
    ├── MEDM_DOC.md    # MEDM widget reference
    ├── PLAN.md        # Development plan
    └── PROJECT.md     # Project description
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

### Type Checking

```bash
mypy src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Based on the ADL parser from the adl2pydm project
- Designed to work with the Gestalt layout system for EPICS displays