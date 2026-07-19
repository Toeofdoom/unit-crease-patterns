from model_file_writer import ModelFileWriter
from pockets import AutoPocket
from sheets import render_complex_sheet
from wireframe_unit import WireframeUnit, mm_ratio
from vec import Vec


def write_files(writer: ModelFileWriter):
    asymm_unit = WireframeUnit(
        2.72,
        AutoPocket(60.32, 1, extra=56.06, double_extra=True),  # symm_unit pocket
        AutoPocket(
            64.78, 1.5, extra=64.78, double_extra=True
        ),  # asymm_unit unit pocket  (itself)
    )
    symm_unit = WireframeUnit(
        4.80,
        AutoPocket(56.06, 1, extra=60.32, double_extra=True),
        AutoPocket(56.06, 1, extra=60.32, double_extra=True),
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

            extra_horizontal_units=[([*[asymm_unit] * 5,  *[symm_unit] * 5], Vec(0, 0)),
                                    ([asymm_unit] * 5, Vec(asymm_unit.length_ratio, 0))],
        ),
    )
    writer.write_svg(
        f"oops",
        render_complex_sheet(
            [],
            [],
            min(square_height, 9999),
            min(height, 9999),
            unit_mm * mm_ratio,

            extra_horizontal_units=[([asymm_unit] * 2, Vec(0, 0)),
                                    ([asymm_unit] * 2, Vec(asymm_unit.length_ratio, 0))],
        ),
    )
