from model_file_writer import ModelFileWriter
from pockets import AutoPocket
from sheets import render_complex_sheet
from wireframe_unit import WireframeUnit, mm_ratio
from vec import Vec

def write_files(writer: ModelFileWriter):
    sapphire_unit = WireframeUnit(
        1.70, 
        AutoPocket(53.9, 1, extra=56.7, double_extra=False), #goes into emerald pocket
        AutoPocket(56.75, 1.2, extra=56.75, double_extra=True) #sapphire pocket
    )
    fairway_unit = WireframeUnit(
        2.49, 
        AutoPocket(55.58, .9, extra=55.08, double_extra=True), #emerald pocket
        AutoPocket(60.72, 1.2, extra=55.58, double_extra=True) #fairway pocket
    )
    emerald_unit = WireframeUnit(
        1.53, 
        AutoPocket(56.7, .75, extra=44.51, double_extra=False), #flame pocket
        AutoPocket(55.08, 1, extra=60.72, double_extra=True) #fairway pocket
    )
    flame_unit = WireframeUnit(
        3.46, AutoPocket(44.51, .7, extra=53.9, double_extra=False), # goes into sapphire pocket
          AutoPocket(44.51, .7, extra=53.9, double_extra=False) 
    )



    unit_mm = 29
    width = (297 - 5) / unit_mm
    full_height = (420 - 10) / unit_mm
    square_height = 300 / unit_mm
    for rows in [1,2,3]:
        writer.write_svg(
            f"fairway_{rows}0",
            render_complex_sheet(
                [],
                [],
                min(width, 9999),
                min(full_height*3/5, 9999), 
                unit_mm * mm_ratio,
                extra_vertical_units=[([fairway_unit]*10, Vec(0, fairway_unit.length_ratio * i)) for i in range(0, rows)]
            )
        )

    for rows in [3]:
        writer.write_svg(
            f"emerald_{rows}0",
            render_complex_sheet(
                [],
                [],
                min(width, 9999),
                min(full_height/2, 9999), 
                unit_mm * mm_ratio,
                extra_vertical_units=[([emerald_unit]*10, Vec(0, emerald_unit.length_ratio * i)) for i in range(0, rows)]
            )
        )

    for rows in [1,2]:
        writer.write_svg(
            f"flame_{rows}0",
            render_complex_sheet(
                [],
                [],
                min(width, 9999),
                min(full_height*2/3, 9999), 
                unit_mm * mm_ratio,
                extra_vertical_units=[([flame_unit]*10, Vec(0, flame_unit.length_ratio * i)) for i in range(0, rows)]
            )
        )

    for rows in [3]:
        writer.write_svg(
            f"sapphire_{rows}0",
            render_complex_sheet(
                [],
                [],
                min(width, 9999),
                min(full_height*1/2, 9999), 
                unit_mm * mm_ratio,
                extra_vertical_units=[([sapphire_unit]*10, Vec(0, sapphire_unit.length_ratio * i)) for i in range(0, rows)]
            )
        )