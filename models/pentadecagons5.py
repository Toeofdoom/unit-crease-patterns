from model_file_writer import ModelFileWriter
from pockets import AutoPocket
from sheets import render_complex_sheet
from wireframe_unit import WireframeUnit, mm_ratio
from vec import Vec


def write_files(writer: ModelFileWriter):
    asymm_unit = WireframeUnit(
        1.88,
        AutoPocket(79.82, 2.5, extra=56.53, double_extra=True),  # symm_unit pocket
        AutoPocket(
            53.25, 1, extra=53.25, double_extra=True
        ),  # asymm_unit unit pocket  (itself)
    )
    symm_unit = WireframeUnit(
        2.65,
        AutoPocket(56.53, 1.3, extra=79.82, double_extra=True),
        AutoPocket(56.53, 1.3, extra=79.82, double_extra=True),
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
            extra_vertical_units=[
                (
                    [symm_unit] * n,
                    Vec(asymm_unit.length_ratio, symm_unit.length_ratio * i),
                )
                for i, n in enumerate([2, 2, 1])
            ],
            extra_horizontal_units=[([asymm_unit] * 10, Vec(0, 0))],
        ),
    )
