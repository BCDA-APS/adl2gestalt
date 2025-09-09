# ADL to Gestalt Converter

Convert MEDM ADL files to [Gestalt](https://github.com/BCDA-APS/gestalt) YAML format for modern EPICS displays.

## Features

- Convert single files or entire directories
- Validate and test converted files
- Generate Qt, CSS-Phoebus, and PyDM displays using [Gestalt](https://github.com/BCDA-APS/gestalt)
- Command-line tools

## Installation

```bash
git clone https://github.com/BCDA-APS/adl2gestalt.git
cd adl2gestalt
git clone https://github.com/BCDA-APS/gestalt.git src/gestalt
pip install .
```

For development (editable install with dev tools):
```bash
pip install -e ".[dev]"
```

## Usage

### Basic Commands

```bash
# Convert single file
adl2gestalt convert path/to/file.adl -o path/to/file.yml

# Convert directory
adl2gestalt convert path/to/medm_folder/ --batch -o path/to/gestalt_folder/

# Complete workflow (convert + test)
adl2gestalt workflow path/to/medm_folder/ path/to/gestalt_folder/

# Check status
adl2gestalt status path/to/medm_folder/ path/to/gestalt_folder/

# Generate UI files
adl2gestalt generate path/to/file.yml --format qt -o path/to/file.ui
# Or using gestalt directly
gestalt path/to/file.yml -t qt -o path/to/file.ui
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
