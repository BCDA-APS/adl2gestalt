# ADL to Gestalt Converter

Convert MEDM ADL files to Gestalt YAML format for modern EPICS displays.

## Features

- Convert single files or entire directories
- Validate and test converted files
- Generate Qt, CSS-Phoebus, and PyDM displays
- Command-line tools

## Installation

```bash
git clone https://github.com/BCDA-APS/adl2gestalt.git
cd adl2gestalt
git clone https://github.com/BCDA-APS/gestalt.git src/gestalt
pip install -e .
```

Optional for development:
```bash
pip install -e ".[dev]"
```

## Usage

### Basic Commands

```bash
# Convert single file
adl2gestalt convert file.adl -o file.yml

# Convert directory
adl2gestalt convert medm_files/ --batch -o gestalt_files/

# Complete workflow (convert + test)
adl2gestalt workflow medm_files/ gestalt_files/

# Generate UI files
adl2gestalt generate file.yml --format qt -o file.ui
gestalt file.yml -t qt -o file.ui

# Check status
adl2gestalt status medm_files/ gestalt_files/
```

## Output Format

Generates Gestalt YAML files:

```yaml
#include colors.yml
#include widgets.yml

display_name: !Form
    geometry: 437x274 x 2917x77
    title: "Display Title"
    
widget_name: !TextMonitor
    geometry: 50x14 x 30x8
    pv: "IOC:PV:NAME"
    text: "Label"
```

Main widget mappings:
- `text update` → `!TextMonitor`
- `text entry` → `!TextEntry` 
- `choice button` → `!ChoiceButton`
- `message button` → `!MessageButton`
- `related display` → `!RelatedDisplay`

## Development

```bash
# Setup
pip install -e ".[dev]"

# Test
pytest

# Format
black src/ tests/
ruff check src/ tests/ --fix
```

## License

MIT License