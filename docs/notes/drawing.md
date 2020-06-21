# Drawing Notes

A collection of AutoCAD behaviors determined experimentally. There may be mistakes and misunderstandings of the
inner workings of the algorithms. Not all edge cases may have been considered.

## Colors
- most entities are colored contextually, based on the layer or block that they reside in
- usually entity colors are not stored directly (e.g. as RGB), but are indices into a lookup table. Different 
  CAD applications may use different color palletes making consistent coloring difficult.
- if a block insert is placed on layer 'A', and the block contains an entity on layer 'B' with BYLAYER color: 
  the entity will be drawn with the color of layer 'B'.
- if a block insert is placed on layer 'A', and the block contains an entity on layer '0' with BYLAYER color: 
  the entity will be drawn with the color of layer 'A' 
    - it seems that layer '0' is the only special case for this.
- if an entity has BYBLOCK color set and it exists outside of a block: it will take on the layout default color 
  which is white in the modelspace and black in the paperspace.

## Layers and Draw Order
- layers are case insensitive, but are sometimes stored lowercase (e.g. document layers table) and sometimes stored 
  with the original mixture of upper and lower case (e.g. `entity.dxf.layer`).
- layers do not play a role in entity draw order, only whether they appear at all based on the visibility of the layer
- it appears that Insert entities have a single element in terms of draw order. 
    - Entities inside a block can overlap each other and so have a draw order inside the block, but two Insert entities 
      cannot interleave the contents of their blocks. One is completely drawn on top of the other.
- for entities inside a block, the visibility of the layer that the block is inserted does not affect the visibility of 
  the entity *unless* the entity was created on layer 0 in which case the reverse is true
  
    - scenario: block created containing entity A (layer 0) and entity B (layer 1). The block is inserted into layer 2
    - entity B visible if and only if layer 1 is visible
    - entity A visible if and only if layer 2 is visible 

    
## Text
- the 'char_height' in dxf corresponds to the cap-height of the font
- the default line spacing is 5/3 * cap-height between the previous baseline and the next baseline. The 'line space 
  factor' is a factor applied directly to this value, so a factor of 3/5 results in 0 space between lines, because 
  each baseline is 1 * cap-height apart.
- the middle (vertical) justification of MText entities seems to be midpoint between the x-height of the first line 
  to the baseline of the last line
- Attrib entities can have formatting commands in them
- MText word wrapping seems to only break on spaces, not underscores or dashes.
- MText word wrapping seems to treat multiple spaces between lines as if they were a single space
- alignment seems to ignore extra spaces at the start or end of lines except for the first line, where spaces at the 
  beginning of the string have an effect.
    - whitespace at the beginning of the text can trigger word wrapping, which creates a single blank line at the start
- if a line ends with an explicit newline character and is shorter than the column width, only one newline is inserted
- if a line is a single word wider than the column width, it will not be broken but will instead spill outside the 
  text box.
    - placing a space before this word will create an empty line and push the word onto the next line
- the anchor of single line TEXT entities (and ATTRIB entities) is *always* the left-baseline regardless of what 
  alignment parameters are stored in the dxf. Those are for re-adjusting the anchor when the text is edited.

## Draw Styles
- the style that points are drawn in might not be stored in the dxf file, but up to the CAD application
    - <https://knowledge.autodesk.com/support/autocad/learn-explore/caas/CloudHelp/cloudhelp/2019/ENU/AutoCAD-Core/files/GUID-48AD2AE9-1EDE-4BF1-B3FA-F5B15225189E-htm.html>
    - points can be drawn relative to the view scale or in absolute units