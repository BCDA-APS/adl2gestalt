
# Widget Type Mapping

| MEDM (ADL) | Python Class | Gestalt (YML) |
|-------------|--------------|---------------|
| arc | MedmArcWidget | !Arc |
| bar | MedmBarWidget | !Scale |
| byte | MedmByteWidget | !ByteMonitor |
| cartesian plot | MedmCartesianPlotWidget | None |
| choice button | MedmChoiceButtonWidget | !ChoiceButton |
| composite | MedmCompositeWidget | !Group |
| embedded display | MedmEmbeddedDisplayWidget | !Embed |
| image | MedmImageWidget | !Image |
| indicator | MedmIndicatorWidget | !Scale |
| menu | MedmMenuWidget | !Menu |
| message button | MedmMessageButtonWidget | !MessageButton |
| meter | MedmMeterWidget | None |
| oval | MedmOvalWidget | !Ellipse |
| polygon | MedmPolygonWidget | !Polygon |
| polyline | MedmPolylineWidget | !Polyline |
| rectangle | MedmRectangleWidget | !Rectangle |
| related display | MedmRelatedDisplayWidget | !RelatedDisplay |
| shell command | MedmShellCommandWidget | !ShellCommand |
| strip chart | MedmStripChartWidget | None |
| text | MedmTextWidget | !Text |
| text entry | MedmTextEntryWidget | !TextEntry |
| text update | MedmTextUpdateWidget | !TextMonitor |
| valuator | MedmValuatorWidget | !Slider |
| wheel switch | MedmWheelSwitchWidget | None |
| display | MedmMainWidget | !Form |


# MEDM Objects and Attributes Reference

## Object Index

### Graphics Objects
- **Arc** - Circular arc drawing
- **Image** - Image display
- **Line** - Straight line drawing
- **Oval** - Elliptical shape
- **Polygon** - Multi-sided shape
- **Polyline** - Connected line segments
- **Rectangle** - Rectangular shape
- **Text** - Text display

### Monitor Objects
- **Bar Monitor** - Bar chart display
- **Byte Monitor** - Byte value display
- **Cartesian Plot** - 2D plotting
- **Meter** - Meter/gauge display
- **Scale Monitor** - Scaled value display
- **Strip Chart** - Time-series plotting
- **Text Monitor** - Text value display

### Controller Objects
- **Choice Button** - Selection button
- **Menu** - Dropdown menu
- **Message Button** - Action button
- **Related Display** - Display navigation
- **Shell Command** - Command execution
- **Slider** - Value slider control
- **Text Entry** - Text input field
- **Wheel Switch** - Numeric wheel control

### Special Objects
- **Composite** - Grouped objects
- **Display** - Display container

## Attribute Index

### Compound Attributes (Multiple Properties)

#### Object Attributes
*All objects have Object attributes*
- **X Position** - X coordinate of top-left corner relative to display
- **Y Position** - Y coordinate of top-left corner relative to display  
- **Width** - Width of the object
- **Height** - Height of the object

#### Basic Attributes
*Applies to: Arc, Oval, Polygon, Polyline, Rectangle, Text*
- **Foreground** - Foreground color (opens Color Palette)
- **Style** - Edge style for the object
- **Fill** - Fill style for the object
- **Line Width** - Line width in pixels (0 allowed)

#### Dynamic Attributes
*Applies to: Arc, Oval, Polygon, Polyline, Rectangle, Text, Image, Composite*
- **Color Mode** - Color mode for the object (not used for Image and Composite)
- **Visibility** - Visibility mode for the object
- **Color Rule** - Integer color rule number
- **Visibility Calc** - CALC expression for display (0=False, other=True)
- **Channel A** - Main process variable name (replaces 'A' in CALC)
- **Channel B** - Second process variable name (replaces 'B' in CALC)
- **Channel C** - Third process variable name (replaces 'C' in CALC)
- **Channel D** - Fourth process variable name (replaces 'D' in CALC)

#### Monitor Attributes
*Applies to: Bar, Byte, Meter, Scale Monitor, Text Monitor*
- **Readback Channel** - Process variable to be read
- **Foreground** - Foreground color
- **Background** - Background color

#### Control Attributes
*Applies to: Choice Button, Menu, Message Button, Slider, Text Entry*
- **Control Channel** - Process variable to be controlled
- **Foreground** - Foreground color
- **Background** - Background color

#### Limits Attributes
*Applies to: Meter, Bar Monitor, Scale Monitor, Slider, Text Monitor, Text Entry*

- **Low Limit Source** - Source for low limit value (Channel, Default, User Specified)
- **Low Limit Channel Value** - Value when source is Channel (floating point number)
- **Low Limit Default Value** - Value when source is Default (floating point number)
- **Low Limit User Value** - Value when source is User Specified (floating point number)
- **High Limit Source** - Source for high limit value (Channel, Default, User Specified)
- **High Limit Channel Value** - Value when source is Channel (floating point number)
- **High Limit Default Value** - Value when source is Default (floating point number)
- **High Limit User Value** - Value when source is User Specified (floating point number)
- **Precision Source** - Source for precision value (Channel, Default, User Specified)
- **Precision Channel Value** - Value when source is Channel (floating point number)
- **Precision Default Value** - Value when source is Default (floating point number)
- **Precision User Value** - Value when source is User Specified (floating point number)

#### Plot Attributes
*Applies to: Cartesian Plot, Strip Chart*

- **Title** - Title for the plot object
- **X Label** - X-axis label for the plot object
- **Y Label** - Y-axis label for the plot object
- **Foreground** - Foreground plot color (opens Color Palette)
- **Background** - Background plot color (opens Color Palette)
- **Package** - (Not Implemented)

#### Plot Axis Attributes
*Applies to: Cartesian Plot*

- **Axis Style** - Axis style for the plot axis
- **Axis Range** - Source of the range for the plot axis
- **Minimum Value** - Minimum value shown on the plot axis (floating point number)
- **Maximum Value** - Maximum value shown on the plot axis (floating point number)
- **Time Format** - Time format for the axis

### Simple Attributes (Single Property with Multiple Values)

#### Cartesian Plot Axis Style
*Applies to: Cartesian Plot*
- **linear** - Use a linear axis
- **log10** - Use a log axis  
- **time** - Use a time axis

#### Cartesian Plot Range Style
*Applies to: Cartesian Plot*
- **from channel** - Get the axis range from the process variable (LOPR and HOPR fields)
- **user-specified** - Specifically specify the minimum and maximum values for the axis
- **auto-scale** - Let the graph routine decide on the axis range depending on the data

#### Cartesian Plot Style
*Applies to: Cartesian Plot*
- **point** - Plot the data as points
- **line** - Plot the data as lines
- **fill-under** - Plot the data as lines which are filled under (or over) from the line to the axis

#### Cartesian Plot Time Format
*Applies to: Cartesian Plot when there is a time axis*
- **hh:mm:ss** - Example: 22:05:10, 05:43:35
- **hh:mm** - Example: 22:05, 05:44
- **hh:00** - Example: 22:00, 06:00
- **MMM DD YYY** - Example: Jun 27, 1997
- **MMM DD** - Example: Jun 27
- **MMM DD hh:00** - Example: Jun 27 22:00
- **wd hh: 00** - Example: Tue 22:00

#### Color Mode
*Applies to: Bar, Byte, Choice Button, Menu, Message Button, Meter, Scale Monitor, Slider, Text Entry, Text Monitor, and all objects with Dynamic attribute*
- **static** - Show the object in its normal colors
- **alarm** - Show the object in alarm colors based on the severity of the associated process variable:
  - Green for NO_ALARM
  - Yellow for MINOR_ALARM
  - Red for MAJOR_ALARM
  - White for INVALID_ALARM
  - Gray if the alarm has an unknown value
- **discrete** - If color rules are implemented and the object has a Dynamic attribute, use the color rules. Otherwise, behaves same as "static"

#### Color Rule
*Part of the Dynamic attribute used when color rules are implemented*
- **set #1** - Use color rules defined by set #1
- **set #2** - Use color rules defined by set #2
- **set #3** - Use color rules defined by set #3
- **set #4** - Use color rules defined by set #4

#### Direction
*Applies to: Bar Monitor, Byte Monitor, Scale Monitor, Slider*
- **up** - Direction for the object is up or up/down
- **right** - Direction for the object is right or left/right
- **down** - Only used in the Bar Monitor. Otherwise, MEDM treats this the same as "up"
- **left** - Only used in the Bar Monitor. Otherwise, MEDM treats this the same as "right"

#### Edge Style
*Part of the Basic attribute*
- **solid** - Use solid lines
- **dash** - Use dashed lines

#### Erase Mode
*Applies to: Cartesian Plot with an erase channel*
- **if not zero** - Erase the plot if the erase-channel process variable is not zero
- **if zero** - Erase the plot if the erase-channel process variable is zero

#### Fill Mode
*Applies to: Bar Monitor*
- **from edge** - Fill from the lower end to the current value
- **from center** - Fill from zero to the current value

#### Fill Style
*Part of the Basic attribute*
- **solid** - Fill the whole shape with color
- **outline** - Only color the outline

#### Image Type
*Applies to: Image object*
- **no image** - Do not display any image
- **gif** - The image is Graphics Interchange Format (GIF), which is the only allowable image type at this time

#### Label
*Applies to: Meter, Bar Monitor, Scale Monitor, Slider*
- **none** - No extra features are shown, except that limits are displayed for the meter (which can be hidden by vertically resizing the meter)
- **no decorations** - Similar to "none", but specifically for the Bar Monitor, only the background and the bar are shown, allowing for bar graph creation in MEDM
- **outline** - Show limits
- **limits** - Show limits and a box for the value (note: there is no box for the Slider)
- **channel** - Show limits, a box for the value, and the process variable name (note: there is no box for the Slider)

#### Plot Mode
*Applies to: Cartesian Plot with a scalar process variable*
- **plot n pts & stop** - Plots 'n' points corresponding to the first 'n' changes of the process variable, then stops plotting any more points
- **plot last n pts** - Plots 'n' points corresponding to the last 'n' changes of the process variable, overwriting previous points as new data arrives

#### Related Display Mode
*Applies to: Related Display*
- **create new display** - Creates a new display while leaving the current one open
- **replace display** - Creates a new display that replaces the current one

#### Related Display Visual
*Applies to: Related Display*
- **menu** - Uses a pull-down menu for the choices
- **a row of buttons** - Uses a row of buttons for the choices
- **a column of buttons** - Uses a column of buttons for the choices
- **invisible** - Does not show anything for the choices. This mode is intended for use with a graphic or other object on top of the related display. The graphic should clarify the operation. In EXECUTE mode, the "Execute-Mode Popup Menu" contains an item to toggle the marking of hidden buttons if the user cannot find them

#### Stacking
*Applies to: Choice Button*
- **column** - Buttons are arranged in a row (Note: The documentation states this appears to be a mistake and will not be corrected due to existing screens)
- **row** - Buttons are arranged in a column (Note: The documentation states this appears to be a mistake and will not be corrected due to existing screens)
- **row column** - Buttons are automatically arranged in rows and columns

#### Text Align
*Applies to: Text and Text Monitor*
- **horiz. left** - Aligns text at the top-left of the object. Capital letters align with the top of the object, and text starts at the left
- **horiz. centered** - Aligns text at the top-center of the object. Capital letters align with the top, and text is horizontally centered
- **horiz. right** - Aligns text at the top-right of the object. Capital letters align with the top, and text ends at the right
- **vert. top** - No longer used. In ADL files, MEDM treats this the same as "horiz. left" for backward compatibility
- **vert. centered** - No longer used. In ADL files, MEDM treats this the same as "horiz. center" for backward compatibility
- **vert. bottom** - No longer used. In ADL files, MEDM treats this the same as "horiz. right" for backward compatibility

#### Text Format
*Applies to: Text Entry, Text Monitor*
- **decimal** - Number with or without a decimal point, not exponential (e.g., 10000.00). Uses `cvtDoubleToString()`.
- **exponential** - Exponential notation (e.g., 1.00e+04).
- **eng. notation** - Engineering notation (e.g., 10.00e+03).
- **compact** - Most compact decimal or exponential form (similar to C's %g). Uses `cvtDoubleToCompactString()`.
- **truncated** - Truncated to the largest integer (e.g., 10000).
- **hexadecimal** - Truncated to nearest integer, shown in hexadecimal (e.g., 0x3e8). Input interpreted as hexadecimal.
- **octal** - Truncated to nearest integer, shown in octal (e.g., 01750). Input interpreted as octal.
- **string** - Same as decimal, but can be exponential for large numbers/precision. Uses `cvtDoubleToString()`.
- **sexagesimal** - Degrees/hours, minutes, seconds with colons (e.g., 12:45:10.2).
- **sexagesimal-dms** - Sexagesimal format assuming radians (2π = 360 degrees).
- **sexagesimal-hms** - Sexagesimal format assuming radians (2π = 24 hours).

#### Time Units
*Applies to: Strip Chart*
- **milli-second** - Update period in milliseconds.
- **second** - Update period in seconds.
- **minute** - Update period in minutes.

#### Visibility Mode
*Part of the Dynamic attribute*
- **static** - Object is always displayed.
- **if not zero** - Object displayed if process variable is not zero.
- **if zero** - Object displayed if process variable is zero.
- **calc** - Use a calc expression to determine visibility.

#### Visibility Calc
*Part of the Dynamic attribute - CALC expression for conditional visibility*

**Purpose:** CALC expressions determine object visibility and image frame numbers. For visibility, expression must return `0` for `False` (hidden) and any other value for `True` (visible).

**Syntax:** Case-independent C expressions with standard operators and mathematical functions (ABS, SQR, MIN, MAX, CEIL, FLOOR, LOG, EXP, SIN, COS, TAN, ATAN, etc.)

**Key Syntax Differences:**
- `!=` is replaced by `#`
- `=` is used as in C

**Channel Values (A-L):**
- **A, B, C, D** - Direct values of Channel A, B, C, D
- **E, F** - Reserved
- **G** - COUNT of Channel A
- **H** - HOPR (High Operating Range) of Channel A
- **I** - STATUS of Channel A
- **J** - SEVERITY of Channel A
- **K** - PRECISION of Channel A
- **L** - LOPR (Low Operating Range) of Channel A

**Examples:**
- `!A` - Show if Channel A is zero
- `A` - Show if Channel A is not zero
- `A=12` - Show if Channel A equals 12
- `A#12` - Show if Channel A is not 12
- `A<0&&B<0&&C<0` - Show if all channels A, B, C are negative
- `A<.9*L||A>.9*H` - Show if Channel A is outside 90% of its limits
- `!J` - Show if SEVERITY of Channel A is not 0







