"""Main conversion logic from MEDM to Gestalt."""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from .parser import MedmMainWidget
from .widget_mapper import (
    WIDGET_TYPE_MAP,
)

logger = logging.getLogger(__name__)


class MedmToGestaltConverter:
    """Convert MEDM ADL files to Gestalt YAML format."""

    def __init__(self):
        """Initialize converter with widget mappings."""
        self.widget_map = WIDGET_TYPE_MAP
        self.color_map = {}
        self.color_aliases = {}
        self.converted_widgets = []
        self.calc_node_counter = 0

    def convert_file(self, adl_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Convert a single ADL file to Gestalt YAML.

        Parameters
        ----------
        adl_path : Path
            Path to the ADL file to convert
        output_path : Path, optional
            Output path for YAML file. If None, uses same name with .yml extension

        Returns
        -------
        Path
            Path to the generated YAML file
        """
        adl_path = Path(adl_path)
        if not adl_path.exists():
            raise FileNotFoundError(f"ADL file not found: {adl_path}")

        # Parse the ADL file
        logger.info(f"Parsing ADL file: {adl_path}")
        medm = MedmMainWidget(str(adl_path))
        buf = medm.getAdlLines()
        medm.parseAdlBuffer(buf)

        # Convert to Gestalt format
        logger.info("Converting to Gestalt format")
        gestalt_content = self.convert_display(medm)

        # Determine output path
        if output_path is None:
            output_path = adl_path.with_suffix(".yml")
        else:
            output_path = Path(output_path)
            if output_path.is_dir():
                # If output_path is a directory, create filename inside it
                output_path = output_path / adl_path.with_suffix(".yml").name
            # If output_path is not a directory, use it as-is (assumes it's a file path)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write YAML file
        logger.info(f"Writing Gestalt file: {output_path}")
        with open(output_path, "w") as f:
            # Write the content
            f.write(gestalt_content)

        return output_path

    def convert_display(self, medm: MedmMainWidget) -> str:
        """
        Convert MEDM display to Gestalt format.

        Parameters
        ----------
        medm : MedmMainWidget
            Parsed MEDM display object

        Returns
        -------
        str
            Gestalt display YAML content
        """
        # Build color map and aliases
        self.build_color_map(medm.color_table)

        # Set display dimensions for widget filtering
        if hasattr(medm, "geometry") and medm.geometry:
            self.display_width = medm.geometry.width
            self.display_height = medm.geometry.height
        else:
            # Default dimensions if not available
            self.display_width = 437
            self.display_height = 274

        # Start building the YAML content
        lines = []

        # Add includes first (before comments)
        lines.append("#include colors.yml")
        lines.append("#include widgets.yml")
        lines.append("")

        # Add header comments after includes
        lines.append("# Gestalt display file generated from MEDM ADL")
        lines.append(f"# Source: {Path(medm.given_filename).name}")
        lines.append("# Generator: adl2gestalt")
        lines.append("")

        # Add color definitions if we have custom colors
        if self.color_aliases:
            lines.append("")
            lines.append("# Custom colors from MEDM color table")
            for alias, color in self.color_aliases.items():
                lines.append(f"{alias}: &{alias[1:]} {color}")

        lines.append("")

        # Build display node
        lines.append("Form: !Form")

        # Add display geometry if available
        if hasattr(medm, "geometry") and medm.geometry:
            lines.append(f"    geometry: {medm.geometry.width}x{medm.geometry.height}")

        # Add margins (standard for Form nodes)
        lines.append("    margins: 10x0x10x10")

        # Add display colors
        if medm.color:
            fg_color = self.get_color_reference(medm.color, medm.color_table)
            if fg_color:
                lines.append(f"    foreground: {fg_color}")

        if medm.background_color:
            bg_color = self.get_color_reference(medm.background_color, medm.color_table)
            if bg_color:
                lines.append(f"    background: {bg_color}")

        lines.append("")

        # Convert all widgets
        for i, widget in enumerate(medm.widgets):
            widget_lines = self.convert_widget_to_lines(widget, i, medm.color_table)
            if widget_lines:
                lines.extend(widget_lines)
                lines.append("")

        # Generate Calc nodes for complex visibility (only once, after all widgets)
        if hasattr(self, "calc_nodes") and self.calc_nodes:
            for i, calc_info in enumerate(self.calc_nodes):
                lines.append(f"")
                lines.append(f"{calc_info['name']}: !Calc")
                # Convert MEDM expression to Python syntax
                python_expression = self.convert_medm_to_python(calc_info["expression"])
                lines.append(f'    calc: "{python_expression}"')
                lines.append(f"    A: \"{calc_info['channel_a']}\"")
                if calc_info["channel_b"]:
                    lines.append(f"    B: \"{calc_info['channel_b']}\"")
                if calc_info["channel_c"]:
                    lines.append(f"    C: \"{calc_info['channel_c']}\"")
                if calc_info["channel_d"]:
                    lines.append(f"    D: \"{calc_info['channel_d']}\"")
                lines.append(f"    pv: \"{calc_info['name']}.CALC\"")

        return "\n".join(lines)

    def build_color_map(self, color_table: List) -> None:
        """
        Build color mapping from MEDM color table.

        Parameters
        ----------
        color_table : List
            List of Color namedtuples from MEDM
        """
        self.color_map = {}
        self.color_aliases = {}

        # Standard color names that might be in Gestalt's colors.yml
        standard_colors = {
            (255, 255, 255): "white",
            (0, 0, 0): "black",
            (255, 0, 0): "red",
            (0, 255, 0): "green",
            (0, 0, 255): "blue",
            (255, 255, 0): "yellow",
            (0, 255, 255): "cyan",
            (255, 0, 255): "magenta",
            (128, 128, 128): "gray",
            (192, 192, 192): "silver",
        }

        for i, color in enumerate(color_table):
            color_hex = f"${color.r:02x}{color.g:02x}{color.b:02x}"
            self.color_map[i] = color_hex

            # Check if this is a standard color
            rgb_tuple = (color.r, color.g, color.b)
            if rgb_tuple in standard_colors:
                # Use direct hex for standard colors instead of aliases
                self.color_map[i] = color_hex
            else:
                # Create a custom color alias
                alias_name = f"medm_color_{i}"
                self.color_aliases[f"_{alias_name}"] = color_hex
                self.color_map[i] = f"*{alias_name}"

    def get_color_reference(self, color, color_table: List) -> str:
        """
        Get Gestalt color reference from MEDM color.

        Parameters
        ----------
        color : Any
            MEDM color (Color object or index)
        color_table : List
            MEDM color table

        Returns
        -------
        str
            Gestalt color reference (hex or alias)
        """
        if color is None:
            return None

        # If it's a Color object, find its index
        try:
            if hasattr(color, "r"):
                color_index = color_table.index(color)
            else:
                color_index = int(color)

            return self.color_map.get(color_index, "$000000")
        except (ValueError, IndexError, TypeError):
            return "$000000"

    def convert_widget_to_lines(
        self, widget: Any, index: int, color_table: List
    ) -> List[str]:
        """
        Convert a MEDM widget to Gestalt YAML lines.

        Parameters
        ----------
        widget : Any
            MEDM widget object
        index : int
            Widget index for naming
        color_table : List
            MEDM color table

        Returns
        -------
        List[str]
            Lines of YAML for this widget
        """
        # Skip widgets that are completely outside the display area
        if hasattr(widget, "geometry") and widget.geometry:
            # Get display dimensions from the converter instance
            display_width = getattr(self, "display_width", 437)  # Default fallback
            display_height = getattr(self, "display_height", 274)  # Default fallback

            # Check if widget is completely outside the display area
            if (
                widget.geometry.x + widget.geometry.width < 0
                or widget.geometry.x > display_width
                or widget.geometry.y + widget.geometry.height < 0
                or widget.geometry.y > display_height
            ):
                logger.info(
                    f"Skipping widget outside display area: {widget.symbol} at {widget.geometry.x},{widget.geometry.y}"
                )
                return []

        widget_type = self.widget_map.get(widget.symbol)
        if widget_type is None:
            logger.warning(
                f"Widget type '{widget.symbol}' has no match in Gestalt - skipping"
            )
            return []

        lines = []

        # Generate widget name
        widget_name = f"{widget.symbol.replace(' ', '_')}_{index}"
        if hasattr(widget, "title") and widget.title:
            # Use title for naming if available and reasonable
            safe_title = (
                widget.title[:20].replace(" ", "_").replace("/", "_").replace(":", "")
            )
            widget_name = f"{safe_title}_{index}"

        # Start widget definition
        lines.append(f"{widget_name}: !{widget_type}")

        # Add geometry if available
        if hasattr(widget, "geometry") and widget.geometry:
            geom = widget.geometry
            # All widgets use x x y x width x height for geometry
            lines.append(f"    geometry: {geom.x}x{geom.y}x{geom.width}x{geom.height}")

        # Add colors (except for shapes which are handled in add_widget_properties_lines)
        shapes = ["Arc", "Ellipse", "Rectangle", "Polygon"]
        if hasattr(widget, "color") and widget.color:
            fg_color = self.get_color_reference(widget.color, color_table)
            if fg_color and widget_type not in shapes:
                # Use border-color for Polyline widgets, foreground for others
                if widget_type == "Polyline":
                    lines.append(f"    border-color: {fg_color}")
                else:
                    lines.append(f"    foreground: {fg_color}")

        if hasattr(widget, "background_color") and widget.background_color:
            bg_color = self.get_color_reference(widget.background_color, color_table)
            if bg_color and widget_type not in shapes:
                lines.append(f"    background: {bg_color}")

        # Add widget-specific properties
        if hasattr(widget, "contents") and widget.contents:
            self.add_widget_properties_lines(widget, lines, widget_type, color_table)

        return lines

    def convert_medm_to_python(self, medm_expression: str) -> str:
        """
        Convert MEDM C-like expression syntax to Python syntax.

        MEDM uses: # (not equal), = (equal), && (and), || (or), ! (not)
        Python needs: !=, ==, and, or, not
        """
        if not medm_expression:
            return medm_expression

        # Replace MEDM operators with Python equivalents
        # MEDM uses: # (not equal), = (equal), && (and), || (or), ! (not)
        # Python needs: !=, ==, and, or, not

        # Initialize the Python expression with the MEDM expression
        python_expr = medm_expression

        # Replace != (MEDM uses #) - do this FIRST to avoid interference
        python_expr = python_expr.replace("#", "!=")
        python_expr = python_expr.replace("!=", "___NE___")

        # Now do all replacements safely (___NE___ contains no special chars)
        python_expr = python_expr.replace("=", "==")
        python_expr = python_expr.replace(" !", " not ")
        python_expr = python_expr.replace("! ", " not ")
        python_expr = python_expr.replace("!", " not ")

        # Finally restore # as !=
        python_expr = python_expr.replace("___NE___", "!=")

        # Replace logical operators
        python_expr = python_expr.replace("&&", " and ")
        python_expr = python_expr.replace("||", " or ")

        # Replace MEDM mathematical functions with Python equivalents
        # Note: Python math functions need to be prefixed with math. or imported
        # For now, we'll use the Python math module functions
        function_mappings = {
            "ABS": "abs",
            "SQR": "math.sqrt",  # MEDM SQR is square root
            "MIN": "min",
            "MAX": "max",
            "CEIL": "math.ceil",
            "FLOOR": "math.floor",
            "LOG": "math.log10",  # MEDM LOG is base-10 logarithm
            "LOGE": "math.log",  # MEDM LOGE is natural logarithm
            "EXP": "math.exp",
            "SIN": "math.sin",
            "SINH": "math.sinh",
            "ASIN": "math.asin",
            "COS": "math.cos",
            "COSH": "math.cosh",
            "ACOS": "math.acos",
            "TAN": "math.tan",
            "TANH": "math.tanh",
            "ATAN": "math.atan",
        }

        # Replace functions
        for medm_func, python_func in function_mappings.items():
            python_expr = python_expr.replace(medm_func.upper(), python_func)

        return python_expr

    def add_widget_properties_lines(
        self, widget: Any, lines: List[str], widget_type: str, color_table: List
    ) -> None:
        """
        Add widget-specific properties to YAML lines.

        Parameters
        ----------
        widget : Any
            MEDM widget object
        lines : List[str]
            List to append lines to
        widget_type : str
            Gestalt widget type
        color_table : List
            MEDM color table
        """
        contents = widget.contents

        # Process control/monitor properties
        if "control" in contents:
            control = contents["control"]
            if isinstance(control, dict):
                if "chan" in control:
                    lines.append(f'    pv: "{control["chan"]}"')

        if "monitor" in contents:
            monitor = contents["monitor"]
            if isinstance(monitor, dict):
                if "chan" in monitor:
                    lines.append(f'    pv: "{monitor["chan"]}"')

        # Text widget properties
        if widget_type == "Text" and hasattr(widget, "title"):
            lines.append(f'    text: "{widget.title}"')

        # Text entry/update properties
        if widget_type in ["TextEntry", "TextMonitor"]:
            if "format" in contents:
                format_map = {
                    "decimal": "Decimal",
                    "exponential": "Exponential",
                    "engr. notation": "Engineering",
                    "compact": "Compact",
                    "hexadecimal": "Hexadecimal",
                    "string": "String",
                    "binary": "Binary",
                }
                fmt = format_map.get(contents["format"], "Decimal")
                lines.append(f"    format: {fmt}")

            if "align" in contents:
                align_map = {
                    "horiz. left": "Left",
                    "horiz. centered": "Center",
                    "horiz. right": "Right",
                }
                alignment = align_map.get(contents["align"], "Left")
                lines.append(f"    alignment: {alignment}")

        # Bar/Slider properties
        if widget_type in ["Scale", "Slider"]:
            if "direction" in contents and contents["direction"] in ["up", "down"]:
                lines.append("    horizontal: false")
            else:
                lines.append("    horizontal: true")

        # Button properties
        if widget_type in ["MessageButton"]:
            if "label" in contents:
                lines.append(f'    text: "{contents["label"]}"')
            if "press_msg" in contents:
                lines.append(f'    value: "{contents["press_msg"]}"')
            # if "release_msg" in contents: # no release value in gestalt
            #     lines.append(f'    release-value: "{contents["release_msg"]}"')

        # Helper function to remove leading "-" from MEDM labels
        def clean_medm_label(label):
            """Remove leading '-' from MEDM labels to avoid folder icons"""
            if label and label.startswith("-"):
                return label[1:]  # Remove the leading "-"
            return label

        # Related display properties
        if widget_type == "RelatedDisplay" and hasattr(widget, "displays"):
            # Add text property for the button label
            if "label" in contents:
                clean_label = clean_medm_label(contents["label"])
                lines.append(f'    text: "{clean_label}"')

            if widget.displays:
                lines.append("    links:")
                for display in widget.displays:
                    if "name" in display:
                        label = display.get("label", display["name"])
                        clean_label = clean_medm_label(label)
                        macros = display.get("args", "")
                        lines.append(
                            f'        - {{ label: "{clean_label}", file: "{display["name"]}", macros: "{macros}" }}'
                        )

        # Shell command properties
        if widget_type == "ShellCommand" and hasattr(widget, "commands"):
            # Add text property for the button label
            if "label" in contents:
                lines.append(f'    text: "{contents["label"]}"')

            if widget.commands:
                lines.append("    commands:")
                for cmd in widget.commands:
                    # Shell commands use 'name' for the command, not 'command'
                    if "name" in cmd:
                        label = cmd.get("label", "Command")
                        lines.append(
                            f'        - {{ label: "{label}", command: "{cmd["name"]}" }}'
                        )

        # Polyline/Polygon points
        if widget_type in ["Polyline", "Polygon"] and hasattr(widget, "points"):
            if widget.points:
                # Calculate relative coordinates based on widget geometry
                widget_x = (
                    widget.geometry.x
                    if hasattr(widget, "geometry") and widget.geometry
                    else 0
                )
                widget_y = (
                    widget.geometry.y
                    if hasattr(widget, "geometry") and widget.geometry
                    else 0
                )

                # Convert absolute points to relative points
                relative_points = []
                for p in widget.points:
                    rel_x = p.x - widget_x
                    rel_y = p.y - widget_y
                    relative_points.append(f"{rel_x}x{rel_y}")

                points_str = ", ".join(relative_points)
                lines.append(f"    points: [ {points_str} ]")

        # Polyline properties - always outlined, never filled
        if widget_type == "Polyline" and hasattr(widget, "color") and widget.color:
            fg_color = self.get_color_reference(widget.color, color_table)
            if fg_color:
                # Polyline is always outlined - only border-color
                lines.append(f"    border-color: {fg_color}")

        # Closed shapes (Arc, Ellipse, Rectangle, Polygon) - can be filled or outlined
        closed_shapes = ["Arc", "Ellipse", "Rectangle", "Polygon"]
        if widget_type in closed_shapes and hasattr(widget, "color") and widget.color:
            fg_color = self.get_color_reference(widget.color, color_table)
            if fg_color:
                # Check if shape is outlined
                is_outlined = False
                if "basic attribute" in contents:
                    basic_attrs = contents["basic attribute"]
                    if (
                        isinstance(basic_attrs, dict)
                        and basic_attrs.get("fill") == "outline"
                    ):
                        is_outlined = True

                if is_outlined:
                    # For outlined shapes: only border-color, no background
                    lines.append(f"    border-color: {fg_color}")
                else:
                    # For filled shapes: both background and border-color
                    lines.append(f"    background: {fg_color}")
                    lines.append(f"    border-color: {fg_color}")
        # Border properties for all shapes (width and style)
        all_shapes = ["Arc", "Ellipse", "Rectangle", "Polygon", "Polyline"]
        if widget_type in all_shapes and "basic attribute" in contents:
            basic_attrs = contents["basic attribute"]
            if isinstance(basic_attrs, dict):
                if "width" in basic_attrs:
                    lines.append(f'    border-width: {basic_attrs["width"]}')
                if "style" in basic_attrs:
                    # Map MEDM style to Gestalt border-style
                    style_map = {
                        "solid": "Solid",
                        "dash": "Dashed",
                    }
                    medm_style = basic_attrs["style"].lower()
                    gestalt_style = style_map.get(medm_style, "Solid")
                    lines.append(f"    border-style: {gestalt_style}")

        # Image properties
        if widget_type == "Image":
            if "image name" in contents:
                lines.append(f'    file: "{contents["image name"]}"')

        # Visibility properties (common to all widgets)
        if "dynamic attribute" in contents and isinstance(
            contents["dynamic attribute"], dict
        ):
            dynamic_attrs = contents["dynamic attribute"]

            # Check for visibility mode and channel
            if "vis" in dynamic_attrs and "chan" in dynamic_attrs:
                visibility_mode = dynamic_attrs["vis"]
                chan_a = dynamic_attrs["chan"]

                if visibility_mode == "if not zero":
                    # Widget visible when PV ≠ 0, hidden when PV = 0
                    lines.append(f'    visibility: "{chan_a}"')
                elif visibility_mode == "if zero":
                    # Widget visible when PV = 0, hidden when PV ≠ 0 (use !Not tag)
                    lines.append(f'    visibility: !Not "{chan_a}"')
                elif visibility_mode == "calc":
                    # Complex calculation-based visibility - use Calc node
                    calc_expression = dynamic_attrs.get("calc", "")
                    chan_b = dynamic_attrs.get("chanB", "")
                    chan_c = dynamic_attrs.get("chanC", "")
                    chan_d = dynamic_attrs.get("chanD", "")

                    if calc_expression and chan_a:
                        # Create a Calc node for complex visibility
                        self.calc_node_counter += 1
                        calc_name = f"EnableCalc_{self.calc_node_counter}"

                        # Set visibility to reference the Calc node's output PV
                        lines.append(f'    visibility: "{calc_name}.CALC"')

                        # Store calc info for later processing
                        if not hasattr(self, "calc_nodes"):
                            self.calc_nodes = []

                        self.calc_nodes.append(
                            {
                                "name": calc_name,
                                "expression": calc_expression,
                                "channel_a": chan_a,
                                "channel_b": chan_b,
                                "channel_c": chan_c,
                                "channel_d": chan_d,
                            }
                        )
                # Note: "static" visibility doesn't need a visibility property

        # ByteMonitor properties
        if widget_type == "ByteMonitor":
            sbit = int(contents.get("sbit", 15))
            ebit = int(contents.get("ebit", 0))
            # Calculate number of bits to display
            num_bits = abs(sbit - ebit) + 1
            # Use the smaller value as start-bit
            start_bit = min(sbit, ebit)
            lines.append(f"    bits: {num_bits}")
            lines.append(f"    start-bit: {start_bit}")
            # Map colors - widget.color is the on-color, widget.background_color is the off-color
            if hasattr(widget, "color") and widget.color:
                on_color = self.get_color_reference(widget.color, color_table)
                lines.append(f"    on-color: {on_color}")
            if hasattr(widget, "background_color") and widget.background_color:
                off_color = self.get_color_reference(
                    widget.background_color, color_table
                )
                lines.append(f"    off-color: {off_color}")

        # Choice button properties
        if widget_type == "ChoiceButton" and isinstance(contents, dict):
            if "stacking" in contents:
                lines.append("    horizontal: True")
            else:
                lines.append("    horizontal: False")

        # Arc properties
        if widget_type == "Arc":
            if "beginAngle" in contents:
                # Convert to integer to avoid float issues
                angle = int(float(contents["beginAngle"]))
                lines.append(f"    start-angle: {angle}")
            if "pathAngle" in contents:
                # Convert to integer to avoid float issues
                span = int(float(contents["pathAngle"]))
                lines.append(f"    span: {span}")

        # Composite/Group properties
        if widget_type == "Group" and hasattr(widget, "widgets"):
            # Recursively convert child widgets
            if widget.widgets:
                lines.append("    children:")

                # Get the group's absolute position for calculating relative child coordinates
                group_x = (
                    widget.geometry.x
                    if hasattr(widget, "geometry") and widget.geometry
                    else 0
                )
                group_y = (
                    widget.geometry.y
                    if hasattr(widget, "geometry") and widget.geometry
                    else 0
                )

                for i, child in enumerate(widget.widgets):
                    # Create a copy of the child with relative coordinates
                    from .parser import Geometry

                    if hasattr(child, "geometry") and child.geometry:
                        # Calculate relative coordinates: child_absolute - group_absolute
                        relative_x = child.geometry.x - group_x
                        relative_y = child.geometry.y - group_y

                        # Create a new geometry object with relative coordinates
                        relative_geometry = Geometry(
                            relative_x,
                            relative_y,
                            child.geometry.width,
                            child.geometry.height,
                        )

                        # Temporarily replace the child's geometry with relative coordinates
                        original_geometry = child.geometry
                        child.geometry = relative_geometry

                        child_lines = self.convert_widget_to_lines(
                            child, i, color_table
                        )

                        # Restore original geometry
                        child.geometry = original_geometry
                    else:
                        child_lines = self.convert_widget_to_lines(
                            child, i, color_table
                        )

                    if child_lines:
                        # Indent child lines
                        for line in child_lines:
                            lines.append(f"        {line}")
