# MEDM to Gestalt Conversion Issues

## TestDisplay Comparison Results

This document summarizes the issues found when comparing the original MEDM display (`TestDisplay.adl`) with the converted Gestalt UI (`TestDisplay.ui`).

## Widget Conversion Issues

### Graphics Objects

#### Rectangle
- **Issue**: No fill, wrong color border
- **Status**: ❌ Needs fixing
- **Details**: Should have proper fill and correct border color

#### Arc  
- **Issue**: Same as rectangle - no fill, wrong color border
- **Status**: ❌ Needs fixing
- **Details**: Should have proper fill and correct border color

#### Ellipse
- **Issue**: Same as rectangle - no fill, wrong color border  
- **Status**: ❌ Needs fixing
- **Details**: Should have proper fill and correct border color

#### Polyline
- **Issue**: Absent - not visible in converted UI
- **Status**: ❌ Critical issue
- **Details**: Lines are not being rendered at all

#### Polygon
- **Issue**: Absent - not visible in converted UI
- **Status**: ❌ Critical issue  
- **Details**: Polygon shapes are not being rendered

### Text Objects

#### Text
- **Issue**: Wrong font, does not scale to the text box size
- **Status**: ❌ Needs fixing
- **Details**: Font rendering and text scaling issues

#### Text Entry
- **Issue**: None
- **Status**: ✅ Working correctly

#### Text Monitor  
- **Issue**: None
- **Status**: ✅ Working correctly

### Control Objects

#### Choice Button
- **Issue**: Wrong orientation, weird green shadow at the bottom
- **Status**: ❌ Needs fixing
- **Details**: Layout and visual rendering issues

#### Message Button
- **Issue**: Does not send message
- **Status**: ❌ Functional issue
- **Details**: Button appears but doesn't execute the expected action

#### Slider
- **Issue**: Wrong color
- **Status**: ❌ Needs fixing
- **Details**: Color mapping issue

### Monitor Objects

#### Bar
- **Issue**: None
- **Status**: ✅ Working correctly

#### Scale
- **Issue**: OK for vertical scale, wrong filling orientation for horizontal scale
- **Status**: ⚠️ Partially working
- **Details**: Vertical scales work, horizontal scales have orientation issues

#### Byte Monitor
- **Issue**: Wrong color, and does not display the same data as the ADL screen
- **Status**: ❌ Needs investigation
- **Details**: Using motor set point as channel (limits -10/+10), unclear if this is appropriate for Byte Monitor

### Special Objects

#### Image
- **Issue**: Absent - not visible in converted UI
- **Status**: ❌ Critical issue
- **Details**: Image widgets are not being rendered

#### NOT TESTED ⚠️
- **Embed display**
- **Grid on/off**
- **Calcs**
- **Alarms**

## Summary

### Working Correctly (✅)
- Text Entry
- Text Monitor  
- Bar Monitor

### Partially Working (⚠️)
- Scale Monitor (vertical OK, horizontal has orientation issues)

### Needs Fixing (❌)
- Rectangle, Arc, Ellipse (fill and border color issues)
- Polyline, Polygon (not rendering)
- Text (font and scaling issues)
- Choice Button (orientation and visual issues)
- Message Button (functional issues)
- Slider (color issues)
- Byte Monitor (color and data display issues)
- Image (not rendering)

### Needs testing (⚠️)
- Embed display
- Grid on/off
- Calcs
- Alarms

### Critical Issues
The most critical issues are the completely absent widgets:
- Polyline (lines not visible)
- Polygon (shapes not visible)  
- Image (images not visible)

These suggest fundamental problems with how these widget types are being converted or rendered in Gestalt.

## Next Steps

1. **Investigate polyline/polygon rendering** - Check if these are being converted correctly to YAML
2. **Fix graphics object fills and borders** - Rectangle, Arc, Ellipse
3. **Investigate text scaling and font issues**
4. **Fix control widget visual issues** - Choice Button, Slider
5. **Investigate functional issues** - Message Button, Byte Monitor
6. **Fix scale orientation for horizontal scales**
7. **Investigate image widget conversion** 