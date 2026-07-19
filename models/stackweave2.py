from model_file_writer import ModelFileWriter
from pockets import AutoPocket
from sheets import render_complex_sheet
from wireframe_unit import WireframeUnit, mm_ratio
from vec import Vec

def write_files(writer: ModelFileWriter):
    tri_unit = WireframeUnit(
        2.61, AutoPocket(30, 0.3, extra=47.70, double_extra=False), AutoPocket(57.93, .8, extra=30, double_extra=False)
    )
    tri_connector_unit = WireframeUnit(
        3.87, AutoPocket(47.70, 1, extra=57.93, double_extra=True), AutoPocket(47.70, 1, extra=57.93, double_extra=True)
    )
    pent_unit = WireframeUnit(
        1.38, AutoPocket(68.31, 1.7, extra=54, double_extra=False), AutoPocket(54, .6, extra=38.27, double_extra=False)
    )
    pent_connector_unit = WireframeUnit(
        2.84, AutoPocket(38.27, .6, extra=68.31, double_extra=True), AutoPocket(38.27, .6, extra=68.31, double_extra=True)
    )

    unit_mm = 30
    width = (210 - 5) / unit_mm
    height = (297 - 5) / unit_mm
    writer.write_svg(
        "tri",
        render_complex_sheet(
            [],
            [],
            min(width, 9999),
            min(height, 9999), 
            unit_mm * mm_ratio,
            extra_vertical_units=[([tri_unit]*6, 
                                   Vec(0, tri_unit.length_ratio * i)) 
                                  for i in range(0,3)],
            extra_horizontal_units=[([tri_unit], 
                                     Vec(tri_unit.length_ratio * i, tri_unit.length_ratio*3)) 
                                    for i in range(0,2)]
        )
    )
    writer.write_svg(
        "triconnector_20",
        render_complex_sheet(
            [],
            [],
            min(300/unit_mm, 9999),
            min(height, 9999), 
            unit_mm * mm_ratio,
            
            extra_vertical_units=[([tri_connector_unit]*9, 
                                   Vec(0, tri_connector_unit.length_ratio * i)) 
                                  for i in range(0,2)],
            extra_horizontal_units=[([tri_connector_unit], 
                                     Vec(tri_connector_unit.length_ratio * i, tri_connector_unit.length_ratio*2)) 
                                    for i in range(0,2)]
        )
    )
    writer.write_svg(
        "triconnector_9",
        render_complex_sheet(
            [],
            [],
            min(300/unit_mm, 9999),
            min(height, 9999), 
            unit_mm * mm_ratio,
            
            extra_vertical_units=[([tri_connector_unit]*4, 
                                   Vec(0, tri_connector_unit.length_ratio * i)) 
                                  for i in range(0,2)],
            extra_horizontal_units=[([tri_connector_unit], 
                                     Vec(tri_connector_unit.length_ratio * i, tri_connector_unit.length_ratio*2)) 
                                    for i in range(0,1)]
        )
    )
    writer.write_svg(
        "pent",
        render_complex_sheet(
            [pent_unit] * 3,
            [],
            min(height, 9999),
            min(width, 9999), 
            unit_mm * mm_ratio,
            extra_vertical_units=[(
                [pent_unit] * 9, 
                Vec(0, pent_unit.length_ratio * i)) for i in range(1, 4)
            ]
        )
    )
    writer.write_svg(
        "pentconnector_18",
        render_complex_sheet(
            [pent_connector_unit] * 9,
            [],
            min(height, 9999),
            min(width, 9999), 
            unit_mm * mm_ratio,
            extra_vertical_units=[(
                [pent_connector_unit] * 9, 
                Vec(0, pent_connector_unit.length_ratio ))
            ]
        )
    )
    writer.write_svg(
        "pentconnector_12",
        render_complex_sheet(
            [pent_connector_unit] * 9,
            [pent_connector_unit] * 2,
            min(height, 9),
            min(width, pent_connector_unit.length_ratio + 2),
            unit_mm * mm_ratio,
            extra_horizontal_units=[(
                [pent_connector_unit], 
                Vec(0, pent_connector_unit.length_ratio))
            ]
        )
    )
