
# Widget Type Mapping

## Conversion table

| MEDM (ADL) | Gestalt (YML) | 
|-------------|---------------|
| arc | !Arc |  |
| bar | !Scale |  |
| byte | !ByteMonitor |  |
| cartesian plot |  | 
| choice button | !ChoiceButton |  |
| composite | !Group |  |
| embedded display | !Include |  |
| image | !Image |  |
| scale (indicator) | !Scale |  |
| menu | !Menu |  |
| message button | !MessageButton |  |
| meter |  |  |
| oval | !Ellipse |  |
| polygon | !Polygon |  |
| polyline | !Polyline |  |
| rectangle | !Rectangle |  |
| related display | !RelatedDisplay | |
| shell command | !ShellCommand |  |
| strip chart |  |  |
| text | !Text |  |
| text entry | !TextEntry |  |
| text update | !TextMonitor |  |
| slider (valuator) | !Slider |  |
| wheel switch |  |  |
| display | !Form |  |


## Notes

- **Not supported**: Cartesian plot, meter, strip chart and wheel switch widgets have no equivalent in Gestalt and will be skipped during conversion
- **Font sizing**: In MEDM, there is no font property - font size is determined by widget height rather than width. This can lead to text being troncated if the width vs height ratio is incorrect for text-based widgets (choice button, menu, message button, related display, shell command, text, text entry, text update)

## Missing properties in Gestalt

#### Color modes
- Static, alarm & discrete.
- Widgets: Bar, Byte, Choice Button, Menu, Message Button, Meter, Scale Monitor, Slider, Text Entry, Text Monitor, and all objects with dynamic attributes like Arc, Oval, Polygon, Polyline, Rectangle, Text.

#### Fille mode
- From edge or from center.
- Widget: bar monitor.


#### Label
- None, no decorations, outline, limits and channel
- Widgets: Meter, Bar Monitor, Scale Monitor, Slider

#### Limits attributes
- Low, high & precision
- Widgets: Meter, Bar Monitor, Scale Monitor, Slider, Text Monitor, Text Entry 

#### Message button
- "release message" property

#### Related Display
- Mode property: create new display vs replace display
- Visual property: pull down menu, row of buttons, column of button or invisible

#### Slider
- "increment" property