# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from .dxfobjects import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .dxfobjects import none_subclass, DXFObject


_SUNSTUDY_TPL = """0
SUNSTUDY
5
0
330
0
100
AcDbSunStudy
90
1
1

2

"""

sunstudy_subclass = DefSubclass('AcDbSun', {
    'version': DXFAttr(90),
    'name': DXFAttr(1),
    'description': DXFAttr(2),
    'output_type': DXFAttr(70),
    'sheet_set_name': DXFAttr(3),  # Included only if Output type is Sheet Set.
    'use_subset': DXFAttr(290),  # Included only if Output type is Sheet Set.
    'sheet_subset_name': DXFAttr(4),  # Included only if Output type is Sheet Set.
    'dates_from_calender': DXFAttr(291),
    'date_input_array_size': DXFAttr(91),  # represents the number of dates picked
        # 90 Julian day; represents the date. One entry for each date picked.
        # 90 Seconds past midnight; represents the time of day. One entry for each date picked.
    'range_of_dates': DXFAttr(292),
        # 93 Start time. If range of dates flag is true.
        # 94 End time. If range of dates flag is true.
        # 95 Interval in seconds. If range of dates flag is true.
    'hours_count': DXFAttr(73),
        # 290 Hour. One entry for every hour as specified by the number of hours entry above.
    'page_setup_wizard_id': DXFAttr(340),  # Page setup wizard hard pointer ID
    'view_id': DXFAttr(341),  # View hard pointer ID
    'visual_style_id': DXFAttr(342),  # Visual Style ID
    'shade_plot_type': DXFAttr(74),
    'viewports_per_page': DXFAttr(75),
    'nrows': DXFAttr(76),  # Number of rows for viewport distribution
    'ncols': DXFAttr(77),  # Number of columns for viewport distribution
    'spacing': DXFAttr(40),
    'lock_viewports': DXFAttr(293),
    'label_viewports': DXFAttr(294),
    'text_style_id': DXFAttr(343),
})


class SunStudy(DXFObject):
    # Requires AC1021/R2007
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_SUNSTUDY_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, sunstudy_subclass)


