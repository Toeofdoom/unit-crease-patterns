from model_file_writer import ModelFileWriter
from pockets import AutoPocket
from sheets import render_complex_sheet
from wireframe_unit import WireframeUnit, mm_ratio
from vec import Vec


def write_files(writer: ModelFileWriter):
    fairway_unit = WireframeUnit(
        1.31,
        AutoPocket(56.97, 1, extra=60.37, double_extra=True),
        AutoPocket(70.69, 1.99, extra=70.69, double_extra=True),
    )
    rose_unit = WireframeUnit(
        1.30,
        AutoPocket(60.37, 0.9, extra=33.01, double_extra=True),
        AutoPocket(78.69, 3.2, extra=57.14, double_extra=True),
    )
    kunzite_outer_unit = WireframeUnit(
        3.29,
        AutoPocket(33.01, 0.35, extra=56.97, double_extra=True),
        AutoPocket(33.01, 0.35, extra=56.97, double_extra=True),
    )
    kunzite_inner_unit = WireframeUnit(
        2.58,
        AutoPocket(35.13, 0.48, extra=78.69, double_extra=False),
        AutoPocket(35.13, 0.48, extra=78.69, double_extra=False),
    )
    jupiter_unit = WireframeUnit(
        3.39,
        AutoPocket(57.14, 1, extra=35.13, double_extra=False),
        AutoPocket(57.14, 1, extra=35.13, double_extra=False),
    )

    unit_mm = 29
    height = (297 - 5) / unit_mm
    full_width = (420 - 10) / unit_mm

    width = (210 - 2) / unit_mm
    square_height = 310 / unit_mm
    writer.write_svg(
        f"jupiter",
        render_complex_sheet(
            [],
            [],
            min(square_height, 9999),
            min(height, 9999),
            unit_mm * mm_ratio,
            extra_horizontal_units=[
                ([jupiter_unit] * 10, Vec(jupiter_unit.length_ratio * i, 0))
                for i in range(0, 2)
            ],
        ),
    )
    writer.write_svg(
        f"jupiter_10",
        render_complex_sheet(
            [],
            [],
            min(square_height, 9999),
            min(height, 9999),
            unit_mm * mm_ratio,
            extra_horizontal_units=[
                ([jupiter_unit] * 10, Vec(jupiter_unit.length_ratio * i, 0))
                for i in range(0, 1)
            ],
        ),
    )
    writer.write_svg(
        f"fairway",
        render_complex_sheet(
            [],
            [],
            min(square_height, 9999),
            min(height, 9999),
            unit_mm * mm_ratio,
            extra_horizontal_units=[
                ([fairway_unit] * 10, Vec(fairway_unit.length_ratio * i, 0))
                for i in range(0, 6)
            ],
        ),
    )
    writer.write_svg(
        f"rose",
        render_complex_sheet(
            [],
            [],
            min(square_height, 9999),
            min(height, 9999),
            unit_mm * mm_ratio,
            extra_horizontal_units=[
                *[
                    ([rose_unit] * 10, Vec(rose_unit.length_ratio * i, 0))
                    for i in range(0, 6)
                ]
            ],
        ),
    )
    writer.write_svg(
        f"kunzite_inner",
        render_complex_sheet(
            [],
            [],
            min(square_height, 9999),
            min(height, 9999),
            unit_mm * mm_ratio,
            extra_horizontal_units=[
                ([kunzite_inner_unit] * 10, Vec(kunzite_inner_unit.length_ratio * i, 0))
                for i in range(0, 3)
            ],
        ),
    )
    writer.write_svg(
        f"kunzite_outer",
        render_complex_sheet(
            [],
            [],
            min(square_height, 9999),
            min(height, 9999),
            unit_mm * mm_ratio,
            extra_horizontal_units=[
                ([kunzite_outer_unit] * 10, Vec(kunzite_outer_unit.length_ratio * i, 0))
                for i in range(0, 3)
            ],
        ),
    )

    writer.write_svg(
        f"kunzite_inner_oops",
        render_complex_sheet(
            [],
            [],
            min(square_height, 9999),
            min(height, 9999),
            unit_mm * mm_ratio,
            extra_horizontal_units=[
                ([kunzite_inner_unit] * 1, Vec(kunzite_inner_unit.length_ratio * i, 0))
                for i in range(0, 2)
            ],
        ),
    )
