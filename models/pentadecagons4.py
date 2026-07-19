from model_file_writer import ModelFileWriter
from pockets import AutoPocket
from sheets import render_complex_sheet
from wireframe_unit import WireframeUnit, mm_ratio
from vec import Vec

def write_files(writer: ModelFileWriter):
    long_unit = WireframeUnit(
        6.71, 
        AutoPocket(63.11, 1.25, extra=69.82, double_extra=True), #large triangle pocket
        AutoPocket(54.37, 0.8, extra=54.37, double_extra=True) #long unit pocket  (itself)
    )
    short_unit = WireframeUnit(
        3.36, 
        AutoPocket(69.82, 1.5, extra=63.11, double_extra=True), #small triangle pocket pocket
        AutoPocket(69.82, 1.5, extra=63.11, double_extra=True) #connector pocket
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
            extra_vertical_units=[([short_unit]*3, Vec(long_unit.length_ratio, 0)),
                                  ([short_unit]*2, Vec(long_unit.length_ratio, short_unit.length_ratio))],
            extra_horizontal_units=[([long_unit]*10, Vec(0, 0))]
        )
    )
