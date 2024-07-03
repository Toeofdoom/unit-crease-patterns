from typing import List
import svg
from vec import Vec
from line import Line
from matrix import *
from sheets import *
from pockets import *
from curved_unit import RectangularCurvedUnit, TransformStackUnit, lerp
from bezier import Bezier

border = "#000000"
mountain = "#ff00ff"
valley = "#ff00ff"


class WireframeUnit:
    def __init__(
        self,
        internal_length_ratio,
        p1,
        p2,
        name: str | None = None,
        count: int | None = None,
    ):
        self.internal_length_ratio = internal_length_ratio
        self.p1 = p1
        self.p2 = p2
        self.length_ratio = (
            self.internal_length_ratio + self.p1.extra_length() + self.p2.extra_length()
        )
        self.name = name
        self.count = count

    def render_elements(self, width, offset: Vec | Matrix, with_hints=False) -> List:
        t = offset if type(offset) is Matrix else offset_by(offset)
        height = self.height(width)
        verticals = [
            svg.Line(
                class_=["valley"],
                **(Line(t * Vec(width * x, svg.mm(0)), t * Vec(width * x, height))),
            )
            for x in [0.25, 0.5, 0.75]
        ]
        return [
            *verticals,
            *self.p1.render(t, width, with_hints),
            *self.p2.render(
                t @ rotate_around_point(Vec(width, height) * 0.5, 180),
                width,
                with_hints,
            ),
        ]

    def height(self, width):
        return self.length_ratio * width


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

with open("testunit.svg", "w") as f:
    unit = RectangularCurvedUnit(length_ratio=3.5, end_angle=15, pocket_angle=45)
    f.write(unit.render_sheet(200, 6).as_str())

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
        curve_endpoint- Vec(0.0001, 0),
        reverse_pocket_endpoint,
    )
    
    unit.add_fold(pocket_line, centre)
    unit.add_simple_fold(reverse_pocket_line)
    unit.add_simple_fold(tab_line)
    unit.add_bezier_crease(Bezier([pocket_endpoint, Vec(0.23, 1), Vec(0.12, 1.64), centre]))

    midpoint = centre + Vec(0.0, -0.1)
    dir = Vec(0.45, 0.55)
    unit.add_bezier_crease(Bezier([Vec(0.75, 0.76), Vec(0.15, 1.35), midpoint - dir * .3, midpoint]))
    unit.add_bezier_crease(Bezier([midpoint, midpoint + dir * .25, Vec(0.72, 2.05), Vec(0.76, 2.5)]))

    midpoint = centre + Vec(0.03, -0.17)
    dir = Vec(0.4, 0.6)
    unit.add_bezier_crease(Bezier([Vec(0.75, 1.02), Vec(0.34, 1.4), midpoint - dir * .3, midpoint]))
    unit.add_bezier_crease(Bezier([midpoint, midpoint + dir * .25, Vec(0.73, 1.95), Vec(0.775, 2.5)]))

    midpoint = centre + Vec(0.1, -0.21)
    dir = Vec(0.4, 0.6)
    unit.add_bezier_crease(Bezier([Vec(0.75, 1.3), Vec(0.55, 1.4), midpoint - dir * .3, midpoint]))
    unit.add_bezier_crease(Bezier([midpoint, midpoint + dir * .25, Vec(0.74, 1.95), Vec(0.79, 2.5)]))

    """unit.add_bezier_crease(Bezier([pocket_endpoint, Vec(0.2, 1), Vec(0.1, 1.8), centre]))
    unit.add_bezier_crease(Bezier([Vec(1, pocket_endpoint.y+.2), Vec(0.2, 1), Vec(0.1, 2), centre + Vec(0.3, -0.1)]))
    unit.add_bezier_crease(Bezier([Vec(1.5, pocket_endpoint.y+.4), Vec(0.2, 1), Vec(0.1, 2.1), centre + Vec(0.6, -0.3)]))"""

    f.write(render_print_sheet(unit, 200, 6).as_str())

with open("simplified_curved_unit.svg", "w") as f:
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
        curve_endpoint- Vec(0.0001, 0),
        reverse_pocket_endpoint,
    )
    
    unit.add_fold(pocket_line, centre)
    unit.add_simple_fold(reverse_pocket_line)
    unit.add_simple_fold(tab_line)
    unit.add_bezier_crease(Bezier([pocket_endpoint, Vec(0.23, 1), Vec(0.12, 1.64), centre]))

    midpoint = centre + Vec(0.0, -0.1)
    dir = Vec(0.45, 0.55)
    a = Bezier([Vec(0.75, 0.85), Vec(0.15, 1.35), midpoint - dir * .3, midpoint])
    b = Bezier([midpoint, midpoint + dir * .25, Vec(0.65, 2.0), Vec(0.75, 2.15)])
    unit.add_bezier_crease(a)
    unit.add_bezier_crease(b)

    shift = 0.5
    unit.add_bezier_crease(Bezier([Vec(lerp(v.x, 0.75, shift), v.y) for v in a.control_points]))
    unit.add_bezier_crease(Bezier([Vec(lerp(v.x, 0.75, shift), v.y) for v in b.control_points]))



    """unit.add_bezier_crease(Bezier([pocket_endpoint, Vec(0.2, 1), Vec(0.1, 1.8), centre]))
    unit.add_bezier_crease(Bezier([Vec(1, pocket_endpoint.y+.2), Vec(0.2, 1), Vec(0.1, 2), centre + Vec(0.3, -0.1)]))
    unit.add_bezier_crease(Bezier([Vec(1.5, pocket_endpoint.y+.4), Vec(0.2, 1), Vec(0.1, 2.1), centre + Vec(0.6, -0.3)]))"""

    f.write(render_print_sheet(unit, 200, 6).as_str())

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


with open("5Icosahedra_sharper_AllUnitSheet.svg", "w") as f:
    triangle_unit = WireframeUnit(
        4.09, AutoPocket(38.17, 0.33, extra=40.22), AutoPocket(45.79, 0.5, extra=38.17)
    )
    odd_unit = WireframeUnit(
        5.45, AutoPocket(38.17, 0.33, extra=45.79), AutoPocket(27.72, 0.25, extra=38.17)
    )
    symmetrical_unit = WireframeUnit(
        5.85, AutoPocket(40.22, 0.33, extra=27.72), AutoPocket(40.22, 0.33, extra=27.72)
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

POCKET_EDGE = -2
POCKET_BOOKCASE = -1
CENTRE = 0
BOOKCASE = 1
EDGE = 2

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
        2.88, AutoPocket(71.23, 1.5, extra=44.38), AutoPocket(41.47, 0.5)
    )
    symmetrical_unit = WireframeUnit(
        3.34, AutoPocket(44.38, 0.6667, extra=59.07), AutoPocket(44.38, 0.6667, extra=59.07)
    )
    small_tri_unit = WireframeUnit(
        1.53, AutoPocket(59.07, 1, extra=71.23), AutoPocket(53.88, .6667)
    )

    f.write(
        render_complex_sheet(
            [*([symmetrical_unit] * 3), *([large_tri_unit] * 6)],
            [small_tri_unit]*8,
            9 * 6/5,
            8.12, #203mm
            svg.mm(25),
            extra_vertical_units=[([symmetrical_unit] * 3, Vec(0, symmetrical_unit.length_ratio)),
                                  ([large_tri_unit] * 6, Vec(3, large_tri_unit.length_ratio)),
                                  ([small_tri_unit] * 4, Vec(3, large_tri_unit.length_ratio*2))]
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
            297/29,
            210/29, #203mm
            svg.mm(29),
            extra_vertical_units=[([large_unit] * 10, Vec(0, small_unit.length_ratio))]
        ).as_str()
    )

with open("Flowers_PentagonSheet.svg", "w") as f:
    pentagon_unit = WireframeUnit(
        1.46, AutoPocket(55.71, 1, extra=60.18), AutoPocket(53.88, 1, extra=55.71)
    )

    f.write(
        render_complex_sheet(
            [pentagon_unit]*10,
            [],
            297/29,
            297/29, #203mm
            svg.mm(29),
            extra_vertical_units=[([pentagon_unit]*10, Vec(0, pentagon_unit.length_ratio * i))
                                  for i in range(1, 0)]
        ).as_str()
    )