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

        # Add colors
        shapes = ["Arc", "Ellipse", "Rectangle", "Polygon"]
        if hasattr(widget, "color") and widget.color:
            fg_color = self.get_color_reference(widget.color, color_table)
            if fg_color and widget_type not in shapes:
                # Use border-color for Polyline widgets, foreground for others
                if widget_type == "Polyline":
                    lines.append(f"    border-color: {fg_color}")
                else:
                    lines.append(f"    foreground: {fg_color}")
            else:
                lines.append(f"    background: {fg_color}")
                lines.append(f"    border-color: {fg_color}")

        if hasattr(widget, "background_color") and widget.background_color:
            bg_color = self.get_color_reference(widget.background_color, color_table)
            if bg_color and widget_type not in shapes:
                lines.append(f"    background: {bg_color}")

        # Add widget-specific properties
        if hasattr(widget, "contents") and widget.contents:
            self.add_widget_properties_lines(widget, lines, widget_type, color_table)

        return lines

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
                if "clr" in control:
                    fg_color = self.get_color_reference(
                        int(control["clr"]), color_table
                    )
                    if fg_color:
                        lines.append(f"    foreground: {fg_color}")
                if "bclr" in control:
                    bg_color = self.get_color_reference(
                        int(control["bclr"]), color_table
                    )
                    if bg_color:
                        lines.append(f"    background: {bg_color}")

        if "monitor" in contents:
            monitor = contents["monitor"]
            if isinstance(monitor, dict):
                if "chan" in monitor:
                    lines.append(f'    pv: "{monitor["chan"]}"')
                if "clr" in monitor:
                    fg_color = self.get_color_reference(
                        int(monitor["clr"]), color_table
                    )
                    if fg_color:
                        lines.append(f"    foreground: {fg_color}")
                if "bclr" in monitor:
                    bg_color = self.get_color_reference(
                        int(monitor["bclr"]), color_table
                    )
                    if bg_color:
                        lines.append(f"    background: {bg_color}")

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
                    "engr_notation": "Engineering",
                    "compact": "Compact",
                    "hexadecimal": "Hexadecimal",
                    "octal": "Octal",
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

        # Bar/Meter properties
        if widget_type in ["ProgressBar", "Gauge", "Slider", "Scale"]:
            if "direction" in contents:
                orientation = (
                    "vertical"
                    if contents["direction"] in ["up", "down"]
                    else "horizontal"
                )
                lines.append(
                    f'    horizontal: {str(orientation == "horizontal").lower()}'
                )

            # Add limits if present
            if "limits" in contents:
                limits = contents.get("limits", {})
                if "loprDefault" in limits:
                    lines.append(f'    minimum: {limits["loprDefault"]}')
                if "hoprDefault" in limits:
                    lines.append(f'    maximum: {limits["hoprDefault"]}')

        # Button properties
        if widget_type in ["PushButton", "MessageButton"]:
            if "label" in contents:
                lines.append(f'    text: "{contents["label"]}"')
            if "press_msg" in contents:
                lines.append(f'    press-value: "{contents["press_msg"]}"')
            if "release_msg" in contents:
                lines.append(f'    release-value: "{contents["release_msg"]}"')

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
            elif widget.displays and len(widget.displays) > 0:
                # Use the first display's label as the button text
                first_display = widget.displays[0]
                if "label" in first_display:
                    clean_label = clean_medm_label(first_display["label"])
                    lines.append(f'    text: "{clean_label}"')
                elif "name" in first_display:
                    clean_label = clean_medm_label(first_display["name"])
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
            elif widget.commands and len(widget.commands) > 0:
                # Use the first command's label as the button text
                first_cmd = widget.commands[0]
                if "label" in first_cmd:
                    lines.append(f'    text: "{first_cmd["label"]}"')

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

            # Add border-width for polylines
            if widget_type == "Polyline" and "basic attribute" in contents:
                basic_attrs = contents["basic attribute"]
                if isinstance(basic_attrs, dict) and "width" in basic_attrs:
                    lines.append(f'    border-width: {basic_attrs["width"]}')

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
