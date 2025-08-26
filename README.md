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
adl2gestalt list-medm /path/to/medm/files

# List with count only
adl2gestalt list-medm /path/to/medm/files --count

# Non-recursive search
adl2gestalt list-medm /path/to/medm/files --no-recursive
```

#### List Gestalt Files

```bash
# List all YAML files in a directory
adl2gestalt list-gestalt /path/to/gestalt/files

# List with count only
adl2gestalt list-gestalt /path/to/gestalt/files --count
```

#### Check Conversion Status

```bash
# Show which files need conversion
adl2gestalt status /path/to/medm /path/to/gestalt

# Show detailed status
adl2gestalt status /path/to/medm /path/to/gestalt --verbose
```

#### Convert Files

```bash
# Convert a single file
adl2gestalt convert input.adl -o output.yml

# Convert with overwrite
adl2gestalt convert input.adl -o output.yml --force

# Batch convert a directory
adl2gestalt convert /path/to/medm --batch -o /path/to/gestalt

# Batch convert in place
adl2gestalt convert /path/to/medm --batch --force
```

### Python API

```python
from adl2gestalt import MedmToGestaltConverter
from pathlib import Path

# Create converter
converter = MedmToGestaltConverter()

# Convert a single file
input_file = Path("examples/medm/29id.adl")
output_file = Path("examples/gestalt/29id.yml")
converter.convert_file(input_file, output_file)

# Scan for files needing conversion
from adl2gestalt import identify_pending_conversions
pending = identify_pending_conversions(
    Path("examples/medm"),
    Path("examples/gestalt")
)
for medm_file, status in pending:
    print(f"{medm_file}: {status}")
```

## Widget Mapping

The converter maps MEDM widgets to their Gestalt equivalents:

| MEDM Widget | Gestalt Widget |
|-------------|----------------|
| arc | Arc |
| rectangle | Rectangle |
| text | Text |
| text update | TextUpdate |
| text entry | TextEntry |
| bar | ProgressBar |
| meter | Gauge |
| cartesian plot | XYPlot |
| strip chart | StripChart |
| choice button | ChoiceButton |
| message button | PushButton |
| menu | ComboBox |
| related display | RelatedDisplay |
| composite | Group |

## Project Structure

```
adl2gestalt/
├── src/adl2gestalt/     # Source code
│   ├── parser.py        # ADL file parser
│   ├── converter.py     # ADL to Gestalt converter
│   ├── scanner.py       # File discovery utilities
│   ├── widget_mapper.py # Widget mapping definitions
│   └── cli.py          # Command-line interface
├── examples/
│   ├── medm/           # Example MEDM files
│   └── gestalt/        # Converted Gestalt files
├── tests/              # Unit tests
└── docs/               # Documentation
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