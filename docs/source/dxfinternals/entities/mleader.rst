.. _MLEADER Internals:

MLEADER Internals
=================

.. seealso::

    - DXF Reference: `MLEADER`_

Example BricsCAD MultiLeaderContext:

.. code-block::

    300 <str> CONTEXT_DATA{
    40 <float> 1.0    <<< content scale
    10 <point> (x, y, z)      <<< content base point
    41 <float> 4.0    <<< text height
    140 <float> 4.0   <<< arrowhead size
    145 <float> 2.0   <<< landing gap size
    174 <int> 1       <<< doc missing
    175 <int> 1       <<< doc missing
    176 <int> 0       <<< doc missing
    177 <int> 0       <<< doc missing
    290 <int> 1       <<< has_mtext_content
    START MText Content tags:
    304 <str> MLEADER
    11 <point> (0.0, 0.0, 1.0)    <<< text normal direction
    340 <hex> #A0                 <<< text style as handle
    12 <point> (x, y, z)          <<< text location
    13 <point> (1.0, 0.0, 0.0)    <<< text direction
    42 <float> 0.0        <<< text rotation
    43 <float> 0.0        <<< text width
    44 <float> 0.0        <<< text height
    45 <float> 1.0        <<< text line space factor
    170 <int> 1           <<< text line space style
    90 <int> -1056964608  <<< text raw color
    171 <int> 1           <<< text attachment
    172 <int> 1           <<< text flow direction
    91 <int> -939524096   <<< text raw background color
    141 <float> 1.5       <<< text background scale factor
    92 <int> 0            <<< text background transparency
    291 <int> 0           <<< has_text_bg_color
    292 <int> 0           <<< has_text_bg_fill
    173 <int> 0           <<< text column type
    293 <int> 0           <<< use text auto height
    142 <float> 0.0       <<< text column width
    143 <float> 0.0       <<< text column gutter width
    294 <int> 0           <<< text column flow reversed
    144 <float> missing   <<< text column height (optional?)
    295 <int> 0           <<< text use word break
    END MText Content tags:
    296 <int> 0       <<< has_block_content
    START Block content tags
    END Block content tags
    110 <point> (0.0, 0.0, 0.0)       <<< MLEADER plane origin point
    111 <point> (1.0, 0.0, 0.0)       <<< MLEADER plane x-axis direction
    112 <point> (0.0, 1.0, 0.0)       <<< MLEADER plane y-axis direction
    297 <int> 0                       <<< MLEADER normal reversed
    302 <str> LEADER{
    ...
    303 <str> }
    302 <str> LEADER{
    ...
    303 <str> }
    272 <int> 9       <<< doc missing
    273 <int> 9       <<< doc missing
    301 <str> }
    Example BricsCAD for block content:
    300 <str> CONTEXT_DATA{
    40 <float> 1.0
    10 <point> (x, y, z)
    41 <float> 4.0
    140 <float> 4.0
    145 <float> 2.0
    174 <int> 1
    175 <int> 1
    176 <int> 0
    177 <int> 0
    290 <int> 0       <<< has_mtext_content
    296 <int> 1       <<< has_block_content
    START Block content tags
    341 <hex> #94                 <<< dxf.block_record_handle
    14 <point> (0.0, 0.0, 1.0)    <<< Block normal direction
    15 <point> (x, y, z)          <<< Block location
    16 <point> (1.0, 1.0, 1.0)    <<< Block scale
    46 <float> 0.0                <<< Block rotation in radians!
    93 <int> -1056964608          <<< Block color (raw)
    47 <float> 1.0                <<< start of transformation matrix (16x47)
    47 <float> 0.0
    47 <float> 0.0
    47 <float> 18.427396871473
    47 <float> 0.0
    47 <float> 1.0
    47 <float> 0.0
    47 <float> 0.702618780008
    47 <float> 0.0
    47 <float> 0.0
    47 <float> 1.0
    47 <float> 0.0
    47 <float> 0.0
    47 <float> 0.0
    47 <float> 0.0
    47 <float> 1.0                <<< end of transformation matrix
    END Block content tags
    110 <point> (0.0, 0.0, 0.0)       <<< MLEADER plane origin point
    111 <point> (1.0, 0.0, 0.0)       <<< MLEADER plane x-axis direction
    112 <point> (0.0, 1.0, 0.0)       <<< MLEADER plane y-axis direction
    297 <int> 0                       <<< MLEADER normal reversed
    302 <str> LEADER{
    ...
    303 <str> }
    272 <int> 9
    273 <int> 9
    301 <str> }
    Attribute content and other redundant block data is stored in the AcDbMLeader
    subclass:
    100 <ctrl> AcDbMLeader
    270 <int> 2                   <<< dxf.version
    300 <str> CONTEXT_DATA{       <<< start context data
    ...
    301 <str> }                   <<< end context data
    340 <hex> #6D                 <<< dxf.style_handle
    90 <int> 6816768              <<< dxf.property_override_flags
    ...                           <<< property overrides
    292 <int> 0                   <<< dxf.has_frame_text
    Redundant block data or context data overrides?:
    344 <hex> #94                 <<< dxf.block_record_handle
    93 <int> -1056964608          <<< dxf.block_color
    10 <point> (1.0, 1.0, 1.0)    <<< dxf.block_scale_factor
    43 <float> 0.0                <<< dxf.block_rotation in radians!
    176 <int> 0                   <<< dxf.block_connection_type
    293 <int> 0                   <<< dxf.is_annotative
    REPEAT: (optional)
    94 <int>                      <<< arrow head index?
    345 <hex>                     <<< arrow head handle
    REPEAT: (optional)
    330 <hex> #A3                 <<< ATTDEF handle
    177 <int> 1                   <<< ATTDEF index
    44 <float> 0.0                <<< ATTDEF width
    302 <str> B                   <<< ATTDEF text (reused group code)
    ...  common group codes 294, 178, 179, ...

.. _MLEADER: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-72D20B8C-0F5E-4993-BEB7-0FCF94F32BE0