import math

from bezier import Bezier
from curved_unit import TransformStackUnit, lerp
from line import Line
from matrix import offset_by, rotate_around_point, scale_around_point
from model_file_writer import ModelFileWriter
from sheets import render_print_sheet
from vec import Vec


def write_files(writer: ModelFileWriter):
    """Notes for next iteration:
    
    Pocket is tricky, could just extend unit for a pointy thing enough that it works?
    Not even sure that works of course. The issue is partly that the tab ends up "thinner"
    than the pocket. The reason is simple - the tab cutoff line is NOT arbitrarily pickable any more.
    It has to be a reflection of the pocket line, over the tab fold
    The only way this turns out to be the correct length is if the tab fold is right down the centre, which doesn't work with this design!

    The double-fold, sort of boxy connection might be worth a look as a result even though it's messy. Otherwise...
    need to find some way to centre the line... or to adjust the geometry so it works without doing so.
    
    Not sure if the aesthetics are right yet though. Showing messy reverse of unit... 
    curves don't seem captivating exactly.
    
    Centre mostly works well, just needs tweaks and POSSIBLY extra line where the curve "starts".
    """

    ratio = 3.4
    base_narrowing_multiplier = 0.95
    centre = Vec(0.5, ratio * 0.5)
    adjustment_angle = math.atan((1 - base_narrowing_multiplier) / ratio)
    scaling_factor = 1 / math.cos(adjustment_angle)
    narrowing_factor = (
        scaling_factor * base_narrowing_multiplier / math.cos(adjustment_angle)
    )
    narrowed_ratio = ratio / narrowing_factor
    unit = TransformStackUnit(
        length_ratio=narrowed_ratio,
        initial_transform=offset_by(Vec(0, (narrowed_ratio - ratio) * 0.5))
        @ scale_around_point(centre, scaling_factor / narrowing_factor)
        @ rotate_around_point(centre, math.degrees(-adjustment_angle)),
    )
    unit.add_rotational_symmetry(centre)
    unit.add_fold(Line(Vec(0.25, 0), Vec(0.25, unit.length_ratio)), centre)

    pocket_angle = 32
    reverse_pocket = 18
    tab_angle = pocket_angle * 2 + reverse_pocket

    pocket_direction = Vec(1, math.tan(math.radians(90 - pocket_angle)))

    curve_endpoint = Vec(0.5, 0)
    pocket_endpoint = curve_endpoint + pocket_direction * 0.25
    pocket_line = Line(
        curve_endpoint + Vec(0.0001, 0),
        curve_endpoint + pocket_direction * 0.25,
    )

    tab_line = Line(
        curve_endpoint - Vec(0.0001, 0),
        curve_endpoint + Vec(-1, math.tan(math.radians(90 - tab_angle))) * 0.25,
    )

    reverse_pocket_direction = Vec(-1, math.tan(math.radians(90 - reverse_pocket)))
    reverse_pocket_endpoint = curve_endpoint + reverse_pocket_direction * 0.25
    reverse_pocket_line = Line(
        curve_endpoint - Vec(0.0001, 0),
        reverse_pocket_endpoint,
    )

    unit.add_fold(pocket_line, centre)
    unit.add_simple_fold(reverse_pocket_line)
    unit.add_simple_fold(tab_line)

    edge_intercept = 1.00
    centre_parallels = Vec(0.1, 0.28)
    unit.add_simple_fold(Line(centre, centre - centre_parallels))
    unit.add_bezier_crease(
        Bezier(
            [
                centre - centre_parallels,
                centre - centre_parallels * 2,
                Vec(0.24995, edge_intercept + 0.23),
                Vec(0.24995, edge_intercept),
            ]
        )
    )
    unit.add_bezier_crease(
        Bezier(
            [
                Vec(0.24995, edge_intercept),
                Vec(0.24995, edge_intercept - 0.2),
                pocket_endpoint+Vec(-0.4, 0.1),
                pocket_endpoint-Vec(0.0001, 0)
            ]
        )
    )

    line3_start = Vec(0.75, ratio*.5 - 0.1)
    unit.add_simple_fold(Line(line3_start, line3_start - centre_parallels*1))
    unit.add_bezier_crease(
        Bezier(
            [
                line3_start - centre_parallels*1,
                line3_start - centre_parallels*2,
                pocket_endpoint+Vec(-0.2, 0.3),
                pocket_endpoint-Vec(0.0001, 0)
            ]
        )
    )

    centre_line_intercept = centre_parallels * (0.25/ centre_parallels.x) + centre
    line2_start = (centre_line_intercept + line3_start) * 0.5
    unit.add_simple_fold(Line(line2_start, line2_start - centre_parallels*3))
    unit.add_bezier_crease(
        Bezier(
            [
                line2_start - centre_parallels*3,
                line2_start - centre_parallels*4,
                pocket_endpoint+Vec(-0.32, 0.18),
                pocket_endpoint-Vec(0.0001, 0)
            ]
        )
    )

    """midpoint = centre + Vec(0.00, -0.1)
    direction = Vec(0.45, 0.55)
    a = Bezier(
        [pocket_endpoint + Vec(0, 0.25), Vec(0.35, 1), midpoint - direction * 0.2, midpoint]
    )
    b = Bezier([midpoint, midpoint + direction * 0.25, Vec(0.68, 1.80), Vec(0.75, 1.85)])
    unit.add_bezier_crease(a)
    unit.add_bezier_crease(b)

    unit.add_bezier_crease(
        Bezier(
            [
                Vec(lerp(v.x, 0.75, shift), v.y)
                for v, shift in zip(a.control_points, [0.5, 0.5, 0.5, 0.5])
            ]
        )
    )
    unit.add_bezier_crease(
        Bezier(
            [
                Vec(lerp(v.x, 0.75, shift), v.y)
                for v, shift in zip(b.control_points, [0.5, 0.5, 0.5, 0.5])
            ]
        )
    )"""

    """unit.add_bezier_crease(Bezier([pocket_endpoint, Vec(0.2, 1), Vec(0.1, 1.8), centre]))
    unit.add_bezier_crease(Bezier([Vec(1, pocket_endpoint.y+.2), Vec(0.2, 1), Vec(0.1, 2), centre + Vec(0.3, -0.1)]))
    unit.add_bezier_crease(Bezier([Vec(1.5, pocket_endpoint.y+.4), Vec(0.2, 1), Vec(0.1, 2.1), centre + Vec(0.6, -0.3)]))"""

    writer.write_svg("5", render_print_sheet(unit, 200, 5))
    writer.write_svg("1", render_print_sheet(unit, 200, 1))
