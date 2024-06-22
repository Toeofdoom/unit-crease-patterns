from typing import List
import svg
from vec import Vec
from line import Line
from matrix import *
from sheets import *
from pockets import *
from curved_unit import RectangularCurvedUnit
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
