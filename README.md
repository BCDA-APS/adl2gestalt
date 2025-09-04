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
adl2gestalt generate $(pwd)/file.yml --format qt -o $(pwd)/file.ui
gestalt $(pwd)/file.yml -t qt -o file.ui

# Check status
adl2gestalt status medm_files/ gestalt_files/
```

## Output Format

Generates Gestalt YAML files:

```yaml
#include colors.yml
#include widgets.yml

Form: !Form
    geometry: 562x900
    margins: 10x0x10x10
    foreground: $000000
    background: *medm_color_4
    
text_update_8: !TextMonitor
    geometry: 41x183x188x38
    foreground: $000000
    background: *medm_color_2
    pv: "IOC:PV:NAME"
```
