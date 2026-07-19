from model_file_writer import ModelFileWriter
from pockets import AutoPocket
from sheets import render_complex_sheet
from wireframe_unit import WireframeUnit, mm_ratio
from vec import Vec

def write_files(writer: ModelFileWriter):
    connector_unit = WireframeUnit(
        4.21, 
        AutoPocket(28.35, 0, extra=23.79*2, double_extra=True), #large triangle pocket
        AutoPocket(28.89, 0.333, extra=41.63, double_extra=False) #small triangle pocket
    )
    small_triangle_unit = WireframeUnit(
        2.92, 
        AutoPocket(41.63, 0.1, extra=30, double_extra=False), #small triangle pocket pocket
        AutoPocket(30, 0, extra=28.8, double_extra=False) #connector pocket
    )
    large_triangle_unit = WireframeUnit(
        4.61, 
        AutoPocket(23.79, 0, extra=30, double_extra=False), #large triangle pocket
        AutoPocket(30, 0, extra=28.35, double_extra=False) #connector pocket
    )



    unit_mm = 31
    height = (297 - 5) / unit_mm
    full_width = (420 - 10) / unit_mm
    square_height = 300 / unit_mm
    writer.write_svg(
        f"connector",
        render_complex_sheet(
            [],
            [],
            min(full_width, 9999),
            min(height, 9999), 
            unit_mm * mm_ratio,
            extra_vertical_units=[([connector_unit]*6, Vec(0, connector_unit.length_ratio * i)) for i in range(0, 2)]
        )
    )
    writer.write_svg(
        f"small_triangle",
        render_complex_sheet(
            [],
            [],
            min(full_width, 9999),
            min(height, 9999), 
            unit_mm * mm_ratio,
            extra_vertical_units=[([small_triangle_unit]*4, Vec(0, small_triangle_unit.length_ratio * i)) for i in range(0, 3)]
        )
    )
    writer.write_svg(
        f"large_triangle_unit",
        render_complex_sheet(
            [],
            [],
            min(full_width, 9999),
            min(height, 9999), 
            unit_mm * mm_ratio,
            extra_vertical_units=[([large_triangle_unit]*6, Vec(0, large_triangle_unit.length_ratio * i)) for i in range(0, 2)]
        )
    )
