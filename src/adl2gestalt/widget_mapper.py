"""Widget mapping definitions from MEDM to Gestalt."""

from typing import Dict, Any

# MEDM widget to Gestalt widget type mapping
# Based on official mapping from Gestalt author
WIDGET_TYPE_MAP = {
    # Graphics Objects
    "arc": "Arc",
    "image": "Image",
    "line": "Polyline",
    "oval": "Ellipse",
    "polygon": "Polygon",
    "polyline": "Polyline",
    "rectangle": "Rectangle",
    "text": "Text",
    # Monitor Objects
    "bar": "Scale",
    "byte": "ByteMonitor",
    "cartesian plot": None,  # No match in Gestalt
    "meter": None,  # No match in Gestalt
    "strip chart": None,  # No match in Gestalt
    "text update": "TextMonitor",
    "indicator": "Scale",  # indicator = Scale Monitor
    # Controller Objects
    "choice button": "ChoiceButton",
    "menu": "Menu",
    "message button": "MessageButton",
    "related display": "RelatedDisplay",
    "shell command": "ShellCommand",
    "slider": "Slider",
    "valuator": "Slider",
    "text entry": "TextEntry",
    "wheel switch": None,  # No match in Gestalt
    # Special Objects
    "composite": "Group",  # GroupNode & IncludeNode
    # Display (main container) - maps to Form node
    "display": "Form",
}
