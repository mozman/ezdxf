#  Copyright (c) 2021, Matthew Broadway
#  License: MIT License
import argparse

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import ezdxf
from ezdxf.addons.drawing import Properties, RenderContext, Frontend
from ezdxf.addons.drawing.backend import prepare_string_for_rendering
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.properties import LayoutProperties
from ezdxf.math import Matrix44, X_AXIS


class FixedSizedTextMatplotlibBackend(MatplotlibBackend):
    """Export text in PDF as characters and not as PathPatch() for a smaller
    file size.

    This backend does not support reflections (mirroring), text width factor and
    oblique angles (slanted text).

    Each DXF file has its own individual text scaling factor, depending on the
    extents of the drawing and the output resolution (DPI), which must be
    determined by testing.

    The TrueType fonts are not embedded and may be replaced by other fonts in
    the PDF viewer.

    For more information see github discussion #582:
    https://github.com/mozman/ezdxf/discussions/582

    """
    def __init__(
        self,
        ax: plt.Axes,
        text_size_scale: float = 2,
        *,
        adjust_figure: bool = True,
        font: FontProperties = FontProperties(),
    ):
        self._text_size_scale = text_size_scale
        super().__init__(
            ax, adjust_figure=adjust_figure, font=font, use_text_cache=False
        )

    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
    ):
        if not text.strip():
            return  # no point rendering empty strings
        font_properties = self._text_renderer.get_font_properties(properties.font)
        assert self.current_entity is not None
        text = prepare_string_for_rendering(text, self.current_entity.dxftype())
        x, y, _, _ = transform.get_row(3)
        rotation = transform.transform_direction(X_AXIS).angle_deg
        self.ax.text(
            x,
            y,
            text.replace("$", "\\$"),
            color=properties.color,
            size=cap_height * self._text_size_scale,
            rotation=rotation,
            in_layout=True,
            fontproperties=font_properties,
            transform_rotates_text=True,
            zorder=self._get_z(),
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dxf_file')
    parser.add_argument('output_path')
    parser.add_argument(
        "--scale",
        "-s",
        type=float,
        default=1.0,
        help="text scaling factor",

    )
    args = parser.parse_args()

    doc = ezdxf.readfile(args.dxf_file)
    layout = doc.modelspace()

    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_axes((0, 0, 1, 1))
    ctx = RenderContext(layout.doc)
    layout_properties = LayoutProperties.from_layout(layout)
    out = FixedSizedTextMatplotlibBackend(ax, text_size_scale=args.scale)
    Frontend(ctx, out).draw_layout(
        layout,
        finalize=True,
        layout_properties=layout_properties,
    )
    fig.savefig(
        args.output_path,
        dpi=300,
        facecolor=ax.get_facecolor(),
        transparent=True,
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
