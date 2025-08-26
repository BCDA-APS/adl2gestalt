# Plan for MEDM to Gestalt Converter

## 1. Overall Architecture

The converter will be a Python script that:

1. Parses MEDM .adl files using the existing adl_parser.py
2. Maps MEDM widgets to Gestalt equivalents
3. Generates Gestalt layout files (.yml)
4. Handles geometry, colors, PVs, and other properties

## 2. Implementation Strategy

### Phase 1: Basic Structure
1. Create the main converter class
2. Implement basic widget type mapping
3. Handle geometry conversion
4. Generate simple YAML output

### Phase 2: Property Mapping
1. Map colors (MEDM color table → Gestalt colors)
2. Handle PV assignments
3. Convert text properties
4. Map visibility and limits

### Phase 3: Advanced Features
1. Handle composite widgets (nested structures)
2. Support for complex widgets (plots, charts)
3. Color scheme generation
4. Template usage for common patterns

### Phase 4: Polish
1. Error handling and validation
2. Command-line interface
3. Documentation and examples
4. Testing with real MEDM files

## 4. Key Conversion Examples

### Geometry
```
MEDM: x=100, y=200, width=150, height=75
Gestalt: geometry: "150x75 x 100x200"
```

### Colors
```
MEDM: clr=14 (index into color map)
Gestalt: background: *color_name
```

### PVs
```
MEDM: chan="xxx:yyy:zzz"
Gestalt: pv: "xxx:yyy:zzz"
```

## 5. Output Format

The converter will generate YAML files in this format:

```yaml
#include colors.yml
#include widgets.yml

Display_Name: !Display
    geometry: 800x600 x 0x0
    title: "Converted MEDM Display"

Widget_Name: !WidgetClass
    geometry: 150x75 x 100x200
    background: black
    foreground: white
    pv: "xxx:yyy:zzz"
    font: "-Liberation Sans - bold - 12"
```

## 6. File Organization

```
adl2gestalt/
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── adl2gestalt.py            # Main converter script
├── widget_mapper.py          # MEDM to Gestalt widget mapping
├── color_converter.py        # MEDM color indices to Gestalt colors
├── geometry_converter.py     # Coordinate and size conversion
├── adl_parser.py             # MEDM file parser (from adl2pydm)
├── cli.py                    # Command-line interface
└── examples/                 # Example conversions
```
