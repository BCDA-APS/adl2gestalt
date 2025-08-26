"""ADL widget symbols and constants."""

# MEDM widget types that can appear in ADL files
adl_widgets = {
    "arc",
    "bar",
    "byte",
    "cartesian plot",
    "choice button",
    "composite",
    "embedded display",
    "image",
    "indicator",
    "menu",
    "message button",
    "meter",
    "oval",
    "polygon",
    "polyline",
    "rectangle",
    "related display",
    "shell command",
    "strip chart",
    "text",
    "text entry",
    "text update",
    "valuator",
    "wheel switch",
}

# Special blocks that appear at the start of MEDM files
SPECIAL_BLOCKS = ["file", "display", "color map"]

# Internally the angles are specified in integer 1/64-degree units
MEDM_DEGREE_UNITS = 64.0