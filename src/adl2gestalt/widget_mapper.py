"""Widget mapping definitions from MEDM to Gestalt."""

from typing import Dict, Any

# MEDM widget to Gestalt widget type mapping
WIDGET_TYPE_MAP = {
    # Graphics Objects
    "arc": "Arc",
    "image": "Image",
    "line": "Polyline",  # Line is represented as Polyline in Gestalt
    "oval": "Ellipse",
    "polygon": "Polygon",
    "polyline": "Polyline",
    "rectangle": "Rectangle",
    "text": "Text",
    
    # Monitor Objects
    "bar": "Scale",  # Bar monitors map to Scale in Gestalt
    "byte": "ByteMonitor",
    "cartesian plot": "XYPlot",
    "meter": "Meter",  # Keep as Meter (exists in Gestalt)
    "scale": "Scale",
    "strip chart": "StripChart",
    "text update": "TextMonitor",  # TextUpdate -> TextMonitor in Gestalt
    "indicator": "LED",
    
    # Controller Objects
    "choice button": "ChoiceButton",
    "menu": "Menu",  # ComboBox -> Menu in Gestalt
    "message button": "MessageButton",  # PushButton -> MessageButton
    "related display": "RelatedDisplay",
    "shell command": "ShellCommand",
    "slider": "Slider",
    "valuator": "Slider",
    "text entry": "TextEntry",
    "wheel switch": "WheelSwitch",
    
    # Special Objects
    "composite": "Group",
    "embedded display": "Embed",  # EmbeddedDisplay -> Embed in Gestalt
}

# MEDM color modes to Gestalt color modes
COLOR_MODE_MAP = {
    "static": "Static",
    "alarm": "Alarm",
    "discrete": "Discrete",
}

# MEDM visibility modes
VISIBILITY_MODE_MAP = {
    "static": "Static",
    "if not zero": "IfNotZero",
    "if zero": "IfZero",
    "calc": "Calc",
}

# MEDM direction to Gestalt direction
DIRECTION_MAP = {
    "up": "Up",
    "down": "Down",
    "left": "Left",
    "right": "Right",
}

# Font mapping - MEDM to Gestalt font format
def map_font(medm_font: str) -> str:
    """
    Convert MEDM font specification to Gestalt format.
    
    MEDM format: "helvetica-medium-r-18.0"
    Gestalt format: "-Helvetica - regular - 18"
    """
    if not medm_font:
        return "-Liberation Sans - regular - 12"
    
    parts = medm_font.lower().split('-')
    
    # Extract font family, weight, and size
    family = parts[0] if len(parts) > 0 else "liberation sans"
    weight = "bold" if "bold" in medm_font.lower() else "regular"
    size = "12"
    
    # Try to extract size from the font string
    for part in parts:
        if '.' in part:
            try:
                size = str(int(float(part)))
                break
            except (ValueError, TypeError):
                pass
    
    # Map common MEDM fonts to modern equivalents
    font_family_map = {
        "helvetica": "Liberation Sans",
        "courier": "Liberation Mono",
        "times": "Liberation Serif",
    }
    
    family = font_family_map.get(family, family.title())
    
    return f"-{family} - {weight} - {size}"


def map_color(color_index: int, color_table: list) -> str:
    """
    Convert MEDM color index to hex color string.
    
    Parameters
    ----------
    color_index : int
        Index into MEDM color table
    color_table : list
        List of Color namedtuples with r, g, b values
        
    Returns
    -------
    str
        Hex color string like "#RRGGBB"
    """
    if color_table and 0 <= color_index < len(color_table):
        color = color_table[color_index]
        return f"#{color.r:02x}{color.g:02x}{color.b:02x}"
    
    # Default colors if index out of range
    defaults = {
        0: "#FFFFFF",  # White
        1: "#000000",  # Black
        14: "#F0F0F0", # Light gray
        19: "#808080", # Gray
    }
    
    return defaults.get(color_index, "#000000")


def map_geometry(geometry: Any) -> Dict[str, int]:
    """
    Convert MEDM geometry to Gestalt format.
    
    Parameters
    ----------
    geometry : Geometry namedtuple
        MEDM geometry with x, y, width, height
        
    Returns
    -------
    Dict
        Gestalt geometry specification
    """
    return {
        "x": geometry.x,
        "y": geometry.y,
        "width": geometry.width,
        "height": geometry.height,
    }


def map_pv_name(channel: str) -> str:
    """
    Convert MEDM channel to Gestalt PV name.
    
    In most cases this is a direct mapping, but handles
    special cases and macro substitutions.
    """
    if not channel:
        return ""
    
    # Handle macro substitutions - MEDM uses $(...) while Gestalt might differ
    # For now, keep the same format
    return channel


def map_limits(limits: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MEDM limits to Gestalt limits format.
    """
    gestalt_limits = {}
    
    if "loprSrc" in limits:
        source_map = {
            "0": "Default",
            "1": "Channel",
            "2": "User",
        }
        gestalt_limits["min_source"] = source_map.get(limits["loprSrc"], "Default")
    
    if "hoprSrc" in limits:
        source_map = {
            "0": "Default",
            "1": "Channel",
            "2": "User",
        }
        gestalt_limits["max_source"] = source_map.get(limits["hoprSrc"], "Default")
    
    if "loprDefault" in limits:
        gestalt_limits["min_value"] = float(limits["loprDefault"])
    
    if "hoprDefault" in limits:
        gestalt_limits["max_value"] = float(limits["hoprDefault"])
    
    return gestalt_limits