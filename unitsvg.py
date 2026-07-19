from pathlib import Path
from typing import List
import svg
from model_file_writer import ModelFileWriter
from vec import Vec
from line import Line
from matrix import *
from sheets import *
from pockets import *
from curved_unit import TransformStackUnit, lerp
from bezier import Bezier
from wireframe_unit import WireframeUnit, mm_ratio

border = "#000000"
mountain = "#ff00ff"
valley = "#ff00ff"


class Frac:
    def __init__(self, num, den):
        self.num = num
        self.den = den


svg.Length.__mul__ = lambda self, o: svg.Length(self.value * o, self.unit)
svg.Length.__rmul__ = lambda self, o: svg.Length(self.value * o, self.unit)


def add(self, o):
    if o == 0:
        return self
    if self.value == 0:
        return o
    if self.unit != o.unit:
        raise Exception()
    return svg.Length(self.value + o.value, self.unit)


svg.Length.__add__ = add
svg.Length.__radd__ = add

def sub(self, o):
    if o == 0:
        return self
    if self.value == 0:
        return o
    if self.unit != o.unit:
        raise Exception()
    return svg.Length(self.value - o.value, self.unit)


svg.Length.__sub__ = sub
svg.Length.__rsub__ = sub


def gt(self, o):
    if self.unit != o.unit:
        raise Exception()
    return self.value > o.value


test_line = Line(Vec(1, 0), Vec(0, 2))
test_bezier = Bezier([Vec(0, 0), Vec(4, 0), Vec(0, 3), Vec(0, 0)])
roots = test_bezier.intersections(test_line)
intersects = [test_bezier.at(t) for t in roots]
manual_intersects = [test_bezier.at(t) for t in [0.098503, 0.79164]]
section1 = test_bezier.split_at(roots[0])[0]
section2 = test_bezier.split_at(roots[1])[1]


svg.Length.__gt__ = gt

with open("transform_stack_unit.svg", "w") as f:
    unit = TransformStackUnit(length_ratio=4)
    centre = sum(unit.zones[0].verts, Vec(0, 0)) * (1 / len(unit.zones[0].verts))
    unit.add_rotational_symmetry(centre)
    unit.add_fold(Line(Vec(0.25, 0), Vec(0.25, unit.length_ratio)), centre)

    pocket_angle = 27
    reverse_pocket = 11
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
    unit.add_bezier_crease(
        Bezier([pocket_endpoint, Vec(0.23, 1), Vec(0.12, 1.64), centre])
    )

    midpoint = centre + Vec(0.0, -0.1)
    direction = Vec(0.45, 0.55)
    unit.add_bezier_crease(
        Bezier([Vec(0.75, 0.76), Vec(0.15, 1.35), midpoint - direction * 0.3, midpoint])
    )
    unit.add_bezier_crease(
        Bezier([midpoint, midpoint + direction * 0.25, Vec(0.72, 2.05), Vec(0.76, 2.5)])
    )

    midpoint = centre + Vec(0.03, -0.17)
    direction = Vec(0.4, 0.6)
    unit.add_bezier_crease(
        Bezier([Vec(0.75, 1.02), Vec(0.34, 1.4), midpoint - direction * 0.3, midpoint])
    )
    unit.add_bezier_crease(
        Bezier([midpoint, midpoint + direction * 0.25, Vec(0.73, 1.95), Vec(0.775, 2.5)])
    )

    midpoint = centre + Vec(0.1, -0.21)
    direction = Vec(0.4, 0.6)
    unit.add_bezier_crease(
        Bezier([Vec(0.75, 1.3), Vec(0.55, 1.4), midpoint - direction * 0.3, midpoint])
    )
    unit.add_bezier_crease(
        Bezier([midpoint, midpoint + direction * 0.25, Vec(0.74, 1.95), Vec(0.79, 2.5)])
    )

    """unit.add_bezier_crease(Bezier([pocket_endpoint, Vec(0.2, 1), Vec(0.1, 1.8), centre]))
    unit.add_bezier_crease(Bezier([Vec(1, pocket_endpoint.y+.2), Vec(0.2, 1), Vec(0.1, 2), centre + Vec(0.3, -0.1)]))
    unit.add_bezier_crease(Bezier([Vec(1.5, pocket_endpoint.y+.4), Vec(0.2, 1), Vec(0.1, 2.1), centre + Vec(0.6, -0.3)]))"""

    f.write(render_print_sheet(unit, 200, 6).as_str())

with open("simplified_curved_unit.svg", "w") as f:
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

    pocket_angle = 27
    reverse_pocket = 11
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
    unit.add_bezier_crease(
        Bezier([pocket_endpoint, Vec(0.34, 0.8), Vec(0.16, 1.34), centre])
    )

    midpoint = centre + Vec(0.00, -0.1)
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
    )

    """unit.add_bezier_crease(Bezier([pocket_endpoint, Vec(0.2, 1), Vec(0.1, 1.8), centre]))
    unit.add_bezier_crease(Bezier([Vec(1, pocket_endpoint.y+.2), Vec(0.2, 1), Vec(0.1, 2), centre + Vec(0.3, -0.1)]))
    unit.add_bezier_crease(Bezier([Vec(1.5, pocket_endpoint.y+.4), Vec(0.2, 1), Vec(0.1, 2.1), centre + Vec(0.6, -0.3)]))"""

    f.write(render_print_sheet(unit, 200, 6).as_str())


with open("reversed_curved_unit.svg", "w") as f:
    ratio = 3.6
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

    pocket_angle = 42
    reverse_pocket = 11
    tab_angle = pocket_angle * 2 + reverse_pocket

    pocket_direction = Vec(1, math.tan(math.radians(90 - pocket_angle)))

    curve_endpoint = Vec(0.5, 0.1)
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
    reverse_pocket_endpoint = curve_endpoint + reverse_pocket_direction * 0.25 * 0.45
    reverse_pocket_line = Line(
        curve_endpoint - Vec(0.0001, 0),
        reverse_pocket_endpoint,
    )

    pocket_curve_length = 0.3
    unit.add_fold(pocket_line, centre)
    unit.add_simple_fold(reverse_pocket_line)
    unit.add_bezier_crease(Bezier([reverse_pocket_endpoint, 
                                   reverse_pocket_endpoint + reverse_pocket_direction.normalised * pocket_curve_length * 0.3, 
                                   Vec(0.35, reverse_pocket_endpoint.y + pocket_curve_length * 0.8), 
                                   Vec(0.25, reverse_pocket_endpoint.y + pocket_curve_length)]))
    unit.add_simple_fold(tab_line)
    unit.add_bezier_crease(
        Bezier([pocket_endpoint, Vec(0.40, 0.8), Vec(0.16, 1.44), centre])
    )

    midpoint = centre + Vec(0.00, -0.1)
    direction = Vec(0.45, 0.55)
    a = Bezier(
        [pocket_endpoint + Vec(0, 0.25), Vec(0.38, 1), midpoint - direction * 0.3, midpoint]
    )
    b = Bezier([midpoint, midpoint + direction * 0.55, Vec(0.68, 1.97), Vec(0.75, 2.05)])
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
    )

    """unit.add_bezier_crease(Bezier([pocket_endpoint, Vec(0.2, 1), Vec(0.1, 1.8), centre]))
    unit.add_bezier_crease(Bezier([Vec(1, pocket_endpoint.y+.2), Vec(0.2, 1), Vec(0.1, 2), centre + Vec(0.3, -0.1)]))
    unit.add_bezier_crease(Bezier([Vec(1.5, pocket_endpoint.y+.4), Vec(0.2, 1), Vec(0.1, 2.1), centre + Vec(0.6, -0.3)]))"""

    f.write(render_print_sheet(unit, 200, 6).as_str())


with open("new_curved_unit.svg", "w") as f:
    ratio = 5.5
    base_narrowing_multiplier = 0.9
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

    pocket_angle = 50
    reverse_pocket = 10
    tab_angle = pocket_angle * 2 + reverse_pocket

    pocket_direction = Vec(1, math.tan(math.radians(90 - pocket_angle)))

    curve_endpoint = Vec(0.5, 0.2)
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
    pocket_curve_section = 0.7
    reverse_pocket_endpoint = curve_endpoint + reverse_pocket_direction * 0.25 * 0.3
    reverse_pocket_line = Line(
        curve_endpoint - Vec(0.0001, 0),
        reverse_pocket_endpoint,
    )

    pocket_curve_length = 0.4
    unit.add_fold(pocket_line, centre)
    unit.add_simple_fold(reverse_pocket_line)
    unit.add_bezier_crease(Bezier([reverse_pocket_endpoint, 
                                   reverse_pocket_endpoint + reverse_pocket_direction.normalised * pocket_curve_length * 0.3, 
                                   Vec(0.35, reverse_pocket_endpoint.y + pocket_curve_length * 0.8), 
                                   Vec(0.25, reverse_pocket_endpoint.y + pocket_curve_length)]))
    unit.add_simple_fold(tab_line)
    unit.add_bezier_crease(
        Bezier([pocket_endpoint, Vec(0.42, 0.7), Vec(0.16, 1.44), centre])
    )

    start_y = pocket_endpoint.y + 0.4
    end_y = centre.y - 0.1
    unit.add_bezier_crease(
        Bezier(
            [
                Vec(0.75, start_y),
                Vec(0.3, lerp(start_y, end_y, 0.15)),
                Vec(0.3, lerp(start_y, end_y, 0.5)),
                Vec(0.75, end_y),
            ]
        )
    )

    start_y, end_y = (lerp(start_y, end_y, 0.15), lerp(end_y, start_y, 0.25))
    unit.add_bezier_crease(
        Bezier(
            [
                Vec(0.75, start_y),
                Vec(0.4, lerp(start_y, end_y, 0.15)),
                Vec(0.4, lerp(start_y, end_y, 0.5)),
                Vec(0.75, end_y),
            ]
        )
    )

    """unit.add_bezier_crease(Bezier([pocket_endpoint, Vec(0.2, 1), Vec(0.1, 1.8), centre]))
    unit.add_bezier_crease(Bezier([Vec(1, pocket_endpoint.y+.2), Vec(0.2, 1), Vec(0.1, 2), centre + Vec(0.3, -0.1)]))
    unit.add_bezier_crease(Bezier([Vec(1.5, pocket_endpoint.y+.4), Vec(0.2, 1), Vec(0.1, 2.1), centre + Vec(0.6, -0.3)]))"""

    f.write(render_print_sheet(unit, 200, 8).as_str())

"""with open("FiveTwistedTetrahedra.svg", "w") as f:
    unit1 = WireframeUnit(138/30, LongTabPocket(Frac(1, 5), 0, Frac(2, 3)), NormalPocket(0, Frac(1, 2), 2))
    unit2 = WireframeUnit(128/30, NormalPocket(0, 1, 2), NormalPocket(0, Frac(1, 3), Frac(3, 2)))
    sheet = InstructionSheet(units = [unit1, unit2])
    f.write(sheet.render(150, 30).as_str())"""

with open("TriangleSeriesOctahedra2_InternalUnit.svg", "w") as f:
    internal_unit = WireframeUnit(3.05, AutoPocket(56.03, 1), AutoPocket(24.51, 0.25))
    f.write(render_print_sheet(internal_unit, svg.mm(30), 6).as_str())

with open("TriangleSeriesOctahedra2_TriangleUnit.svg", "w") as f:
    triangle_unit = WireframeUnit(3.73, AutoPocket(37.95, 0), AutoPocket(30, 0))
    f.write(render_print_sheet(triangle_unit, svg.mm(30), 6).as_str())

POCKET_EDGE = -2
POCKET_BOOKCASE = -1
CENTRE = 0
BOOKCASE = 1
EDGE = 2

with open("5Icosahedra_sharper_AllUnitSheet.svg", "w") as f:
    triangle_unit = WireframeUnit(
        4.09, AutoPocket(38.17, 0.33, extra=40.22).with_hint_from(POCKET_EDGE), 
        AutoPocket(45.79, 0.5, extra=38.17).with_hint_from(POCKET_EDGE),
        name="Small Eq. Triangle", count=60
    )
    odd_unit = WireframeUnit(
        5.45, AutoPocket(38.17, 0.33, extra=45.79).with_hint_from(POCKET_EDGE), 
        AutoPocket(27.72, 0.25, extra=38.17).with_hint_from(POCKET_BOOKCASE),
        name="Large Eq. Triangle", count=60
    )
    symmetrical_unit = WireframeUnit(
        5.85, AutoPocket(40.22, 0.33, extra=27.72).with_hint_from(POCKET_EDGE), 
        AutoPocket(40.22, 0.33, extra=27.72).with_hint_from(POCKET_EDGE),
        name="Symmetrical", count=30
    )

    f.write(
        render_complex_sheet(
            [*([symmetrical_unit] * 2), *([odd_unit] * 2), *([triangle_unit] * 3)],
            [triangle_unit, odd_unit, odd_unit],
            7,
            odd_unit.length_ratio + 3,
            svg.mm(30),
        ).as_str()
    )

    with open("5Icosahedra_Cheatsheet.svg", "w") as cheatsheet:
        cheatsheet.write(
            render_cheatsheet(
                [triangle_unit, odd_unit, symmetrical_unit],
                svg.mm(40),
                svg.mm(30),
            ).as_str()
        )



with open("TriangleSeriesIcosahedra2_Cheatsheet.svg", "w") as f:
    triangle_unit = WireframeUnit(
        3.76,
        AutoPocket(42.25, 0.333).with_hint_from(POCKET_EDGE),
        AutoPocket(30, 0).with_hint_from(POCKET_EDGE),
        name="Triangle",
        count=60,
    )
    star_unit = WireframeUnit(
        3.3,
        AutoPocket(43.23, 0.63).with_hint_from(POCKET_EDGE),
        AutoPocket(32.63, 0.333).with_hint_to(BOOKCASE),
        name="Star",
        count=60,
    )
    f.write(
        render_cheatsheet(
            [triangle_unit, star_unit],
            svg.mm(40),
            svg.mm(25),
        ).as_str()
    )

with open("Pincers_Cheatsheet.svg", "w") as f:
    trivert_unit = WireframeUnit(
        3.16,
        AutoPocket(83.47, 6).with_hint_from(POCKET_EDGE),
        AutoPocket(41.06, 0.3333).with_hint_from(POCKET_EDGE),
        name="Tri-vert",
        count=24,
    )
    long_unit = WireframeUnit(
        3.3,
        AutoPocket(28.63, 0.3333).with_hint_from(POCKET_EDGE),
        AutoPocket(28.63, 0.3333).with_hint_from(POCKET_EDGE),
        name="Long",
        count=12,
    )
    f.write(
        render_cheatsheet(
            [trivert_unit, long_unit],
            svg.mm(40),
            svg.mm(25),
        ).as_str()
    )


with open("PentagonThing_AllUnitSheet.svg", "w") as f:
    pentagon_unit = WireframeUnit(1.65, AutoPocket(55.83, 0.33), AutoPocket(49.67, 0.5))
    odd_unit = WireframeUnit(4.49, AutoPocket(66.09, 0.33), AutoPocket(55, 0.25))
    f.write(
        render_complex_sheet(
            [*([odd_unit] * 1), *([pentagon_unit] * 6)],
            [odd_unit] * 5,
            7,
            odd_unit.length_ratio + 3,
            svg.mm(30),
        ).as_str()
    )


with open("5Dodecahedra_AllUnitSheet.svg", "w") as f:
    large_tri_unit = WireframeUnit(
        2.88, 
        AutoPocket(71.23, 1.5, extra=44.38).with_hint_to(POCKET_BOOKCASE), 
        AutoPocket(41.47, 0.5).with_hint_from(POCKET_EDGE),
        name = "Outer tri-vertex", count=60
    )
    symmetrical_unit = WireframeUnit(
        3.34,
        AutoPocket(44.38, 0.6667, extra=59.07).with_hint_from(POCKET_EDGE),
        AutoPocket(44.38, 0.6667, extra=59.07).with_hint_from(POCKET_EDGE),
        name = "Symmetrical", count=30
    )
    small_tri_unit = WireframeUnit(
        1.53, 
        AutoPocket(59.07, 1, extra=71.23).with_hint_to(CENTRE),
        AutoPocket(53.88, 0.6667).with_hint_to(CENTRE),
        name = "Inner tri-vertex", count=60
    )

    f.write(
        render_complex_sheet(
            [*([symmetrical_unit] * 3), *([large_tri_unit] * 6)],
            [small_tri_unit] * 8,
            9 * 6 / 5,
            8.12,  # 203mm
            svg.mm(25),
            extra_vertical_units=[
                ([symmetrical_unit] * 3, Vec(0, symmetrical_unit.length_ratio)),
                ([large_tri_unit] * 6, Vec(3, large_tri_unit.length_ratio)),
                ([small_tri_unit] * 4, Vec(3, large_tri_unit.length_ratio * 2)),
            ],
        ).as_str()
    )

    with open("5Dodecahedra_Cheatsheet.svg", "w") as cheatsheet:
        cheatsheet.write(
            render_cheatsheet(
                [large_tri_unit, small_tri_unit, symmetrical_unit],
                svg.mm(40),
                svg.mm(30),
            ).as_str()
        )

with open("Flowers_WhirlSheet.svg", "w") as f:
    small_unit = WireframeUnit(
        1.9, AutoPocket(60.18, 1, extra=53.88), AutoPocket(45.61, 0.6666, extra=57.90)
    )
    large_unit = WireframeUnit(
        2.57, AutoPocket(54.41, 1, extra=45.61), AutoPocket(57.90, 1, extra=54.41)
    )

    f.write(
        render_complex_sheet(
            [small_unit] * 10,
            [],
            297 / 29,
            210 / 29,  # 203mm
            svg.mm(29),
            extra_vertical_units=[([large_unit] * 10, Vec(0, small_unit.length_ratio))],
        ).as_str()
    )

with open("Flowers_PentagonSheet.svg", "w") as f:
    pentagon_unit = WireframeUnit(
        1.46, AutoPocket(55.71, 1, extra=60.18), AutoPocket(53.88, 1, extra=55.71)
    )

    f.write(
        render_complex_sheet(
            [pentagon_unit] * 10,
            [],
            297 / 29,
            297 / 29,  # 203mm
            svg.mm(29),
            extra_vertical_units=[
                ([pentagon_unit] * 10, Vec(0, pentagon_unit.length_ratio * i))
                for i in range(1, 0)
            ],
        ).as_str()
    )


with open("MiniKaleidoscope_AllUnitSheet.svg", "w") as f:
    pentagon_unit = WireframeUnit(
        1.09, AutoPocket(54.93, 1.5), AutoPocket(35.56, 0.3333, extra=54.93)
    )
    long_unit = WireframeUnit(
        2.35, AutoPocket(64.64, .66666, extra=35.56), AutoPocket(64.64, .66666, extra=35.56)
    )

    f.write(
        render_complex_sheet(
            [pentagon_unit] * 5,
            [],
            297 / 29,
            210 / 29,  # 203mm
            svg.mm(25),
            extra_vertical_units=[([pentagon_unit] * 5, Vec(0, pentagon_unit.length_ratio)),
                                  ([long_unit] * 5, Vec(0, pentagon_unit.length_ratio * 2))],
        ).as_str()
    )


with open("MiniKaleidoscope2_AllUnitSheet.svg", "w") as f:
    pentagon_unit = WireframeUnit(
        3.90, AutoPocket(44.52, 1, extra=54, double_extra=False), AutoPocket(54, 0.5, extra=24.68, double_extra=False)
    )
    long_unit = WireframeUnit(
        3.51, AutoPocket(24.68, 0.25, extra=44.52, double_extra=False), AutoPocket(24.68, 0.25, extra=44.52, double_extra=False)
    )

    f.write(
        render_complex_sheet(
            [pentagon_unit] * 5,
            [],
            216 / 22,
            279 / 22,  # 203mm
            svg.mm(22),
            extra_vertical_units=[([pentagon_unit] * 5, Vec(0, pentagon_unit.length_ratio)),
                                  ([long_unit] * 5, Vec(0, pentagon_unit.length_ratio * 2))],
        ).as_str()
    )

with open("Braids_AllUnitSheet.svg", "w") as f:
    long_unit = WireframeUnit(
        5.54, AutoPocket(66.08, 1, extra=61.04), AutoPocket(57.95, 1, extra=57.95)
    )
    short_unit = WireframeUnit(
        3.55, AutoPocket(61.04, 1, extra=66.08), AutoPocket(61.04, 1, extra=66.08)
    )

    f.write(
        render_complex_sheet(
            [short_unit] * 2,
            [long_unit] * 10 + [short_unit],
            long_unit.length_ratio+2,
            11,  # 203mm
            svg.mm(26), #286mm
            extra_vertical_units=[([short_unit] * 2, Vec(0, short_unit.length_ratio))],
        ).as_str()
    )

with open("Braids_b_AllUnitSheet.svg", "w") as f:
    asymm_unit = WireframeUnit(
        2.67, AutoPocket(57.28, 1, extra=62.80), AutoPocket(64.61, 1, extra=64.61)
    )
    symm_unit = WireframeUnit(
        4.26, AutoPocket(62.80, 1, extra=57.28), AutoPocket(62.80, 1, extra=57.28)
    )

    """f.write(
        render_complex_sheet(
            [symm_unit] * 3 + [asymm_unit] * 3,
            [],
            long_unit.length_ratio+2,
            11,  # 203mm
            svg.mm(26), #286mm
            extra_vertical_units=[([symm_unit] * 2, Vec(0, symm_unit.length_ratio)),
                                  ([asymm_unit] * 3, Vec(3, asymm_unit.length_ratio)),
                                  ([asymm_unit] * 4, Vec(2, asymm_unit.length_ratio*2))],
        ).as_str()
    )"""
    """f.write(
        render_complex_sheet(
            [symm_unit] * 5 + [asymm_unit] * 3,
            [],
            10,
            11,  # 203mm
            svg.mm(26), #286mm
            extra_vertical_units=[([asymm_unit] * 8, Vec(0, symm_unit.length_ratio))],
        ).as_str()
    )"""

    f.write(
        render_complex_sheet(
            [symm_unit] * 5 + [asymm_unit] * 4,
            [],
            10,
            11,  # 203mm
            svg.mm(26), #286mm
            extra_vertical_units=[([asymm_unit] * 8, Vec(0, symm_unit.length_ratio))],
        ).as_str()
    )


with open("Braids_c_AllUnitSheet.svg", "w") as f:
    asymm_unit = WireframeUnit(
        4.63, AutoPocket(49.45, 1, extra=66.76), AutoPocket(54.85, 1, extra=54.85)
    )
    symm_unit = WireframeUnit(
        2.43, AutoPocket(66.76, 1, extra=49.45), AutoPocket(66.76, 1, extra=49.45)
    )
    f.write(
        render_complex_sheet(
            [symm_unit] * 2,
            [asymm_unit] * 10,
            asymm_unit.length_ratio+2,
            10,  # 203mm
            svg.mm(29), #286mm
            extra_vertical_units=[([symm_unit] * 2, Vec(0, symm_unit.length_ratio)),
                                   ([symm_unit], Vec(0, symm_unit.length_ratio * 2))],
        ).as_str()
    )



with open("Whirlo_smallsheet.svg", "w") as f:
    pentagon_unit = WireframeUnit(
        2.39, AutoPocket(62.50, 1), AutoPocket(54.0, 1)
    )
    outer_unit = WireframeUnit(
        1.65, AutoPocket(44.25, 0.6666), AutoPocket(53.44, 1)
    )
    f.write(
        render_complex_sheet(
            [pentagon_unit] * 10,
            [],
            (297 - 10) / 27,
            (140 - 10) / 27,  # 203mm
            svg.mm(27), #286mm
            extra_vertical_units=[([outer_unit] * 10, Vec(0, pentagon_unit.length_ratio))]
        ).as_str()
    )

with open("Whirlo.svg", "w") as f:
    pentagon_unit = WireframeUnit(
        2.39, AutoPocket(62.50, 1), AutoPocket(54.0, 1)
    )
    outer_unit = WireframeUnit(
        1.65, AutoPocket(44.25, 0.6666), AutoPocket(53.44, 1)
    )
    f.write(
        render_complex_sheet(
            [pentagon_unit] * 10,
            [],
            (297 - 10) / 27,
            (1280 - 10) / 27,  # 203mm
            svg.mm(27), #286mm
            extra_vertical_units=[([pentagon_unit] * 10, Vec(0, pentagon_unit.length_ratio)),
            ([outer_unit] * 10, Vec(0, pentagon_unit.length_ratio*2)),
            ([outer_unit] * 10, Vec(0, pentagon_unit.length_ratio *2 + outer_unit.length_ratio))]
        ).as_str()
    )

with open("Hex32.svg", "w") as f:
    f.write(render_hex_grid(32, 10).as_str())

with open("Hex48.svg", "w") as f:
    f.write(render_hex_grid(48, 10).as_str())


with open("Hex40.svg", "w") as f:
    f.write(render_hex_grid(40, 10).as_str())

with open("Hex24.svg", "w") as f:
    f.write(render_hex_grid(24, 10).as_str())


with open("5twistedrons.svg", "w") as f:
    triangle_unit = WireframeUnit(
        6.61, AutoPocket(32.39, 0.2, extra=30, double_extra=False), AutoPocket(30, 0.5, extra=54.65)
    )
    connector_unit = WireframeUnit(
        5.62, AutoPocket(44.76, 0.5, extra=44.76, double_extra=False), AutoPocket(54.65, 0.75, extra=32.39, double_extra=False)
    )
    f.write(
        render_complex_sheet(
            [triangle_unit] * 4 + [connector_unit] * 4,
            [],
            (279 - 5) / 30,
            (216 - 5) / 30,  # 203mm
            svg.mm(30), #286mm
            extra_vertical_units=[]
        ).as_str()
    )

with open("pentathingo_inside.svg", "w") as f_i:
    with open("pentathingo_pentagon.svg", "w") as f_p:
        pentagon_unit = WireframeUnit(
            1.74, AutoPocket(54, 0.333, extra=36.15, double_extra=False), AutoPocket(48.09, 0.8, extra=54, double_extra=False)
        )
        tri_unit = WireframeUnit(
            2.56, AutoPocket(36.15, 0.333, extra=48.09, double_extra=False), AutoPocket(60.17, 1, extra=60.17, double_extra=True)
        )
        w = 29
        f_i.write(
            render_complex_sheet(
                [tri_unit] * 6,
                [],
                (297 - 5) / w,
                (210 - 5) / w,  # 203mm
                svg.mm(w), #286mm
                extra_vertical_units=[([tri_unit] * 6, Vec(0, tri_unit.length_ratio))]
            ).as_str()
        )
        f_p.write(
            render_complex_sheet(
                [pentagon_unit] * 10,
                [],
                (297 - 5) / w,
                (210 - 5) / w,  # 203mm
                svg.mm(w), #286mm
                extra_vertical_units=[([pentagon_unit] * 10, Vec(0, pentagon_unit.length_ratio)),
                                      ([pentagon_unit] * 10, Vec(0, pentagon_unit.length_ratio*2))]
            ).as_str()
        )

with open("TwistedTriangularPrisms.svg", "w") as f:
    connector_unit = WireframeUnit(
        1.79, AutoPocket(38.46, 0.5, extra=38.25, double_extra=False), AutoPocket(54.65, .75, extra=51.51, double_extra=False)
    )
    triangle1_unit = WireframeUnit(
        3.93, AutoPocket(38.25, 0.2, extra=30, double_extra=False), AutoPocket(30, 0.2, extra=38.46, double_extra=False)
    )
    triangle2_unit = WireframeUnit(
        3.11, AutoPocket(30, 0.333, extra=51.78, double_extra=False), AutoPocket(51.51, .75, extra=30, double_extra=False)
    )
    f.write(
        render_complex_sheet(
            [connector_unit] * 3 + [triangle1_unit] * 3,
            [],
            (279 - 5) / 35,
            (216 - 5) / 35,  # 203mm
            svg.mm(35), #286mm
            extra_vertical_units=[([triangle2_unit] * 3, Vec(0, connector_unit.length_ratio))]
        ).as_str()
    )

with open("Bauble_tri.svg", "w") as f:
    with open("Bauble_connector.svg", "w") as f2:
        tri_unit = WireframeUnit(
            2.35, AutoPocket(57.01, 1, extra=57.01, double_extra=True), AutoPocket(55.40, 0.75, extra=47.55, double_extra=False)
        )
        connector_unit = WireframeUnit(
            4.23, AutoPocket(47.55, 0.6, extra=55.40, double_extra=False), AutoPocket(47.55, 0.6, extra=55.40, double_extra=False)
        )
        height = (210 - 5) / 30
        width = (297 - 5) / 30
        f.write(
            render_complex_sheet(
                [],
                [tri_unit] * 6,
                width, 
                height,
                svg.mm(30),
                extra_vertical_units=[([tri_unit] * 2, Vec(width - tri_unit.length_ratio - 2 , height - tri_unit.length_ratio * 2)),
                                      ([tri_unit] * 2, Vec(width - tri_unit.length_ratio - 2, height - tri_unit.length_ratio))]
            ).as_str()
        )
        f2.write(
            render_complex_sheet(
                [connector_unit] * 5,
                [],
                (210 - 5) / 30,
                (297 - 5) / 30, 
                svg.mm(30),
                extra_vertical_units=[([connector_unit] * 5, Vec(0, connector_unit.length_ratio))]
            ).as_str()
        )


with open("triangleweave_tri.svg", "w") as f:
    with open("triangleweave_connector.svg", "w") as f2:
        with open("triangleweave_connector_b.svg", "w") as f3:
            tri_unit = WireframeUnit(
                1.69, AutoPocket(30, .25, extra=44.3, double_extra=False), AutoPocket(64.44, .75, extra=30, double_extra=False)
            )
            connector_unit = WireframeUnit(
                3.27, AutoPocket(44.3, .75, extra=64.44, double_extra=True), AutoPocket(44.3, .75, extra=64.44, double_extra=True)
            )
            width = (297 - 5) / 30
            f.write(
                render_complex_sheet(
                    [tri_unit] * 2,
                    [],
                    2,
                    tri_unit.length_ratio * 5, 
                    30 * 72/25.4, #svg.mm(30),
                    extra_vertical_units=[([tri_unit] * 2, Vec(0, tri_unit.length_ratio * 1)),
                                          ([tri_unit] * 2, Vec(0, tri_unit.length_ratio * 2)),
                                          ([tri_unit] * 2, Vec(0, tri_unit.length_ratio * 3)),
                                        ([tri_unit] * 2, Vec(0, tri_unit.length_ratio * 4))]
                ).as_str()
            )
            f2.write( #19
                render_complex_sheet(
                    [connector_unit] * 6,
                    [connector_unit] * 7,
                    width,
                    220 / 30, 
                    svg.mm(30),
                    extra_vertical_units=[([connector_unit] * 6, Vec(0, connector_unit.length_ratio))]
                ).as_str()
            )
            f3.write(
                render_complex_sheet(
                    [connector_unit] * 6,
                    [connector_unit] * 5,
                    width,
                    150/30, 
                    svg.mm(30)
                ).as_str()
            )

with open("pentagonweave_p.svg", "w") as f:
    with open("pentagonweave_connector.svg", "w") as f2:
        tri_unit = WireframeUnit(
            1.18, AutoPocket(68.82, 1.5, extra=54, double_extra=False), AutoPocket(54, 0.6666, extra=36.48, double_extra=False)
        )
        connector_unit = WireframeUnit(
            2.53, AutoPocket(36.48, 0.6, extra=68.82, double_extra=True), AutoPocket(36.48, 0.6, extra=68.82, double_extra=True)
        )
        unit_mm = 31
        width = 310 / unit_mm
        height = (297 - 5) / unit_mm
        f.write(
            render_complex_sheet(
                [tri_unit] * 10,
                [],
                width,
                height, 
                unit_mm * mm_ratio, #svg.mm(30),
                extra_vertical_units=[([tri_unit] * 10, Vec(0, tri_unit.length_ratio * i)) for i in range(1, 6)]
            ).as_str()
        )
        f2.write( #19
            render_complex_sheet(
                [connector_unit] * 2,
                [connector_unit] * 9,
                2 + connector_unit.length_ratio,
                9, 
                unit_mm * mm_ratio,
                extra_vertical_units=[([connector_unit] * 2, Vec(0, connector_unit.length_ratio)),
                                      ([connector_unit] * 2, Vec(0, connector_unit.length_ratio*2))]
            ).as_str()
        )


with open("stackweave_t_22.svg", "w") as f_t_22:
    with open("stackweave_t_16.svg", "w") as f_t_16:
        with open("stackweave_t_connector.svg", "w") as f2:
            with open("stackweave_t_connector_2.svg", "w") as f2b:
                with open("stackweave_p.svg", "w") as f3:
                    with open("stackweave_p_connector.svg", "w") as f4:
                        with open("stackweave_p_connector_2.svg", "w") as f5:
                            tri_unit = WireframeUnit(
                                2.54, AutoPocket(30, 0.25, extra=45.14, double_extra=False), AutoPocket(58.11, .8, extra=30, double_extra=False)
                            )
                            tri_connector_unit = WireframeUnit(
                                3.88, AutoPocket(45.14, .6, extra=58.11, double_extra=True), AutoPocket(45.14, .6, extra=58.11, double_extra=True)
                            )
                            pent_unit = WireframeUnit(
                                1.58, AutoPocket(65.35, 1.5, extra=54, double_extra=False), AutoPocket(54, .6, extra=39.63, double_extra=False)
                            )
                            pent_connector_unit = WireframeUnit(
                                3.33, AutoPocket(39.63, .6, extra=65.35, double_extra=True), AutoPocket(39.63, .6, extra=65.35, double_extra=True)
                            )
                            unit_mm = 30
                            width = (210 - 5) / unit_mm
                            height = (297 - 5) / unit_mm
                            f_t_22.write(
                                render_complex_sheet(
                                    [tri_unit] * 4,
                                    [tri_unit]*9,
                                    min(width, 4 + tri_unit.length_ratio),
                                    min(height, 1 + 3 * tri_unit.length_ratio), 
                                    unit_mm * mm_ratio, #svg.mm(30),
                                    extra_vertical_units=[([tri_unit] * 4, Vec(0, tri_unit.length_ratio * i)) for i in range(1, 3)],
                                    extra_horizontal_units=[([tri_unit], Vec(0, tri_unit.length_ratio * 3))]
                                ).as_str()
                            )
                            f_t_16.write(
                                render_complex_sheet(
                                    [tri_unit] * 5,
                                    [],
                                    min(width, 4 + tri_unit.length_ratio),
                                    min(height, 1 + 3 * tri_unit.length_ratio), 
                                    unit_mm * mm_ratio, #svg.mm(30),
                                    extra_vertical_units=[([tri_unit] * 5, Vec(0, tri_unit.length_ratio * i)) for i in range(1, 3)],
                                    extra_horizontal_units=[([tri_unit], Vec(0, tri_unit.length_ratio * 3))]
                                ).as_str()
                            )
                            f2.write( 
                                render_complex_sheet(
                                    [tri_connector_unit] * 2,
                                    [tri_connector_unit] * 9,
                                    min(width, 2 + tri_connector_unit.length_ratio),
                                    min(height, 9), 
                                    unit_mm * mm_ratio,
                                    extra_vertical_units=[([tri_connector_unit] * 2, Vec(0, tri_connector_unit.length_ratio))]
                                ).as_str()
                            )
                            f2b.write( 
                                render_complex_sheet(
                                    [tri_connector_unit],
                                    [] * 9,
                                    min(width, 2 + tri_connector_unit.length_ratio),
                                    min(height, 9), 
                                    unit_mm * mm_ratio,
                                    extra_vertical_units=[([tri_connector_unit], Vec(0, tri_connector_unit.length_ratio))]
                                ).as_str()
                            )
                            f3.write( 
                                render_complex_sheet(
                                    [pent_unit] * 6,
                                    [],
                                    min(width, 9999),
                                    min(height, 9999), 
                                    unit_mm * mm_ratio,
                                    extra_vertical_units=[([pent_unit] * 6, Vec(0, pent_unit.length_ratio * i)) for i in range(1, 5)]
                                ).as_str()
                            )
                            f4.write( 
                                render_complex_sheet(
                                    [pent_connector_unit] * 2,
                                    [pent_connector_unit] * 9,
                                    min(width*2, 2 + pent_connector_unit.length_ratio * 2),
                                    min(height, 9), 
                                    unit_mm * mm_ratio,
                                    extra_vertical_units=[([pent_connector_unit] * 1, Vec(0, pent_connector_unit.length_ratio))],
                                    extra_horizontal_units=[([pent_connector_unit] * 9, Vec(2 + pent_connector_unit.length_ratio * i, 0)) for i in range(0, 1)]
                                ).as_str()
                            )
                            f5.write( 
                                render_complex_sheet(
                                    [],
                                    [pent_connector_unit] * 9,
                                    min(width*2, 2 + pent_connector_unit.length_ratio * 2),
                                    min(height, 9), 
                                    unit_mm * mm_ratio
                                ).as_str()
                            )

import pkgutil
import importlib

for loader, module_name, is_pkg in pkgutil.iter_modules(["models"]):
    full_module_name = f"models.{module_name}"
    module = importlib.import_module(full_module_name)    
    module.write_files(ModelFileWriter(Path("output"), module_name))
