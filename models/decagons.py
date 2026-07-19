import svg

from model_file_writer import ModelFileWriter
from pockets import AutoPocket
from sheets import HintType, render_cheatsheet, render_complex_sheet
from wireframe_unit import WireframeUnit, mm_ratio
from vec import Vec


def write_files(writer: ModelFileWriter):
    short_unit = WireframeUnit(
        2.5,
        AutoPocket(80.63, 5.5, extra=60.05, double_extra=True)
        .with_hint_from(HintType.POCKET_EDGE)
        .with_hint_from(1.8),
        AutoPocket(80.63, 5.5, extra=60.05, double_extra=True).with_hint_from(
            HintType.POCKET_EDGE
        ),
        name="Short",
        count=30,
    )
    long_unit = WireframeUnit(
        2.85,
        AutoPocket(60.05, 2, extra=80.63, double_extra=True).with_hint_from(
            HintType.POCKET_EDGE
        ),
        AutoPocket(60.05, 2, extra=80.63, double_extra=True).with_hint_from(
            HintType.POCKET_EDGE
        ),
        name="Long",
        count=30,
    )

    unit_mm = 29
    height = (297 - 5) / unit_mm
    full_width = (420 - 10) / unit_mm
    square_height = 300 / unit_mm
    writer.write_svg(
        f"all",
        render_complex_sheet(
            [],
            [],
            min(square_height, 9999),
            min(height, 9999),
            unit_mm * mm_ratio,
            extra_vertical_units=[([*[short_unit] * 5, *[long_unit] * 5], Vec(0, 0))],
        ),
    )

    writer.write_svg(
        f"cheatsheet",
        render_cheatsheet(
            [short_unit, long_unit],
            svg.mm(40),
            svg.mm(30),
        ),
    )
