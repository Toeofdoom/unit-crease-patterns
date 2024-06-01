from typing import List
import svg
import math
from textwrap import dedent
from copy import copy


class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Vec(self.x, self.y)

    def __mul__(self, n: float):
        return Vec(self.x * n, self.y * n)

    def __add__(self, v: "Vec"):
        return Vec(self.x + v.x, self.y + v.y)

    def __iter__(self):
        yield self.x
        yield self.y


class Line:
    def __init__(self, x1, y1, x2, y2):
        self.v1 = Vec(x1, y1)
        self.v2 = Vec(x2, y2)

    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2


# supports quick unpacking for svg funcs
# Also supports readers thinking "why would you do this??"
def v(v: Vec):
    return {"x": v.x, "y": v.y}


def v1(v: Vec):
    return {"x1": v.x, "y1": v.y}


def v2(v: Vec):
    return {"x2": v.x, "y2": v.y}


def l(l: Line):
    return {**v1(l.v1), **v2(l.v2)}


border = "#000000"
mountain = "#ff00ff"
valley = "#ff00ff"


def lerp(a, b, n):
    return b * n + (1 - n) * a


def common_elements():
    return [
        svg.Style(
            text=dedent(
                """
.valley {stroke: #00f; stroke-width: 2px; fill:none}
.mountain {stroke: #f00; stroke-width: 2px; fill:none }
.cut {stroke: #000; stroke-width: 3px; fill:none } 
"""
            )
        )
    ]


class RectangularCurvedUnit:
    def __init__(
        self, length_ratio: float, end_angle: float, pocket_angle: float
    ) -> None:
        self.length_ratio = length_ratio
        self.end_angle = end_angle
        self.pocket_angle = pocket_angle

    def height(self, width) -> float:
        return self.length_ratio * width

    def render(self, width) -> svg.SVG:
        elements = [
            *common_elements(),
            svg.Rect(class_=["cut"], x=0, y=0, width=width, height="100%"),
            self.render_elements(width, 0),
        ]
        return svg.SVG(width=width, height=self.height(width), elements=elements)

    def render_sheet(self, width, unit_count):
        elements = [
            *common_elements(),
            svg.Rect(class_=["cut"], x=0, y=0, width=width * unit_count, height="100%"),
            *[
                svg.Line(
                    class_=["cut"],
                    x1=i * width,
                    y1=0,
                    x2=i * width,
                    y2="100%",
                )
                for i in range(1, unit_count)
            ],
        ]

        for i in range(0, unit_count):
            elements += self.render_elements(width, Vec(i * width, 0))

        return svg.SVG(
            width=width * unit_count,
            height=width * self.length_ratio,
            elements=elements,
        )

    def render_elements(self, width, offset: Vec):
        height = self.height(width)
        end_direction = Vec(1, math.tan(math.radians(self.end_angle)))
        pocket_direction = Vec(1, math.tan(math.radians(90 - self.pocket_angle)))

        def render_half(t):
            curve_endpoint = end_direction * width * 0.5
            pocket_endpoint = curve_endpoint + pocket_direction * width * 0.25
            pocket_line = Line(
                t
                * (
                    curve_endpoint
                    + pocket_direction * (-curve_endpoint.y / pocket_direction.y)
                ),
                t * pocket_endpoint,
            )
            left_bookcase = Line(
                t * Vec(width * 0.25, 0), t * Vec(width * 0.25, height * 0.5)
            )
            right_bookcase = Line(
                t * pocket_endpoint, t * Vec(width * 0.75, height * 0.5)
            )

            def render_curve(t, centre_x, end_x, y1, y2, centre_y):
                return [
                    svg.Path(  # Central curve
                        class_=["valley"],
                        d=[
                            svg.MoveTo(*(t * Vec(end_x, y1))),
                            svg.CubicBezier(
                                **v1(
                                    t
                                    * Vec(
                                        lerp(end_x, centre_x, 0.8),
                                        lerp(y1, centre_y, 0.4),
                                    )
                                ),
                                **v2(t * Vec(centre_x, lerp(y1, centre_y, 0.7))),
                                **v(t * Vec(centre_x, centre_y))
                            ),
                            svg.CubicBezier(
                                **v1(t * Vec(centre_x, lerp(centre_y, y2, 0.4))),
                                **v2(
                                    t
                                    * Vec(
                                        lerp(end_x, centre_x, 0.8),
                                        lerp(centre_y, y2, 0.8),
                                    )
                                ),
                                **v(t * Vec(end_x, y2))
                            ),
                        ],
                    )
                ]

            def render_central_curve(t):
                return render_curve(
                    t,
                    0.32 * width,
                    0.5 * width,
                    curve_endpoint.y,
                    height * 0.5,
                    height * 0.36,
                )

            def render_second_curve(t):
                return render_curve(
                    t,
                    0.39 * width,
                    0.75 * width,
                    pocket_endpoint.y,
                    height * 0.48,
                    height * 0.36,
                )

            def render_third_curve(t):
                return render_curve(
                    t,
                    0.57 * width,
                    0.75 * width,
                    pocket_endpoint.y,
                    height * 0.48,
                    height * 0.36,
                )

            """def render_4th_curve(t):
                return render_curve(
                    t,
                    0.59 * width,
                    0.75 * width,
                    pocket_endpoint.y + height * 0.16,
                    height * 0.36,
                    height * 0.32,
                )"""

            return [
                svg.Line(
                    class_=["valley"],
                    **v1(t * Vec(pocket_endpoint.x, 0)),
                    **v2(t * pocket_endpoint)
                ),
                svg.Line(class_=["valley"], **l(pocket_line)),
                svg.Line(
                    class_=["valley"],
                    **v1((t @ reflect_x_at(width * 0.75)) * curve_endpoint),
                    **v2(t * pocket_endpoint)
                ),
                svg.Line(class_=["valley"], **l(left_bookcase)),
                svg.Line(class_=["valley"], **l(right_bookcase)),
                *render_central_curve(t),
                *render_central_curve(t @ reflect_x_at(width * 0.25)),
                *render_second_curve(t),
                *render_second_curve(t @ reflect_x_at(width * 0.75)),
                *render_third_curve(t),
                *render_third_curve(t @ reflect_x_at(width * 0.75)),
            ]

        return [
            *render_half(offset_by(offset)),
            *render_half(
                offset_by(offset) @ rotate_around_point(Vec(width, height) * 0.5, 180)
            ),
        ]


class Matrix:
    def __init__(self, data):
        self.data = data

    def __mul__(self, vec):
        els = [vec.x, vec.y, 1]
        x, y, _ = [sum([a * b for a, b in zip(els, row)]) for row in self.data]
        return Vec(x, y)

    def __matmul__(self, mat):  # This is almost certainly wrong
        cols = [
            [sum([a * b for a, b in zip(col, row)]) for row in self.data]
            for col in mat.transposed().data
        ]
        return Matrix(cols).transposed()

    def transposed(self):
        return Matrix([[self.data[j][i] for j in range(0, 3)] for i in range(0, 3)])


def identity():
    return Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])


def rotate_around_point(point: Vec, angle_degrees):
    a = math.radians(angle_degrees)
    return Matrix(
        [
            [math.cos(a), -math.sin(a), point.x * 2],
            [math.sin(a), math.cos(a), point.y * 2],
            [0, 0, 1],
        ]
    )


def reflect_over_line(v1: Vec, v2: Vec):
    return identity()


def reflect_x_at(x):
    return Matrix([[-1, 0, x * 2], [0, 1, 0], [0, 0, 1]])


def reflect_y_at(y):
    return Matrix([[1, 0, 0], [0, -1, y * 2], [0, 0, 1]])


def offset_by(point: Vec):
    return Matrix([[1, 0, point.x], [0, 1, point.y], [0, 0, 1]])


class WireframeUnit:
    def __init__(self, internal_length_ratio, p1, p2):
        self.internal_length_ratio = internal_length_ratio
        self.p1 = p1
        self.p2 = p2
        self.length_ratio = self.internal_length_ratio + self.p1.extra_length() + self.p2.extra_length()

    def render_elements(self, width, offset: Vec) -> List:
        t = offset_by(offset)
        height = self.height(width)
        verticals = [
            svg.Line(
                class_=["valley"],
                **l(Line(t * Vec(width * x, svg.mm(0)), t * Vec(width * x, height)))
            )
            for x in [0.25, 0.5, 0.75]
        ]
        return [*verticals, *self.p1.render(t, width), *self.p2.render(t @ rotate_around_point(Vec(width, height) * 0.5, 180), width)]

    def height(self, width):
        return self.length_ratio * width


class InstructionSheet:
    def __init__(self, units):
        self.units = units

    def render(self, width, padding) -> svg.SVG:
        def x_offset_for(i):
            return (padding + width) * i + padding

        elements = [
            *common_elements(),
            [
                self.units[i].render_elements(width, Vec(x_offset_for(i), padding))
                for i in range(0, len(self.units))
            ],
        ]
        return svg.SVG(
            width=x_offset_for(len(self.units)),
            height=self.height(width, padding),
            elements=elements,
        )

    def height(self, width, padding):
        return max([unit.height(width) for unit in self.units]) + padding * 2


class Frac:
    def __init__(self, num, den):
        self.num = num
        self.den = den


class NormalPocket:
    def __init__(
        self,
        start_point: Frac | int,
        intersect_line: Frac | int,
        intersect_point: Frac | int,
    ):
        # on top of unit
        self.start_point = start_point
        self.intersect_line = intersect_line
        self.intersect_point = intersect_point


class LongTabPocket:
    def __init__(
        self,
        start_point: Frac | int,
        intersect_line: Frac | int,
        intersect_point: Frac | int,
    ):
        # on side of unit
        self.start_point = start_point
        self.intersect_line = intersect_line
        self.intersect_point = intersect_point

class AutoPocket:
    def __init__(self, angle_degrees, con):
        self.angle_radians = math.radians(angle_degrees)
        self.inv_angle_radians = math.radians(90-angle_degrees)
        self.con = con

    def extra_length(self):
        return self.con * math.tan(self.inv_angle_radians) * 0.25
    
    def render(self, t, width):
        start_x = 0.5 - self.con*0.25
        end_x = 0.75
        end_y = (end_x - start_x) * math.tan(self.inv_angle_radians)
        edge_y = end_y - math.tan(self.inv_angle_radians) * 0.25

        pocket_vert = t * Vec(width * end_x, width*end_y)

        return [svg.Line(class_=["valley"], **l(Line(t * Vec(width * start_x, svg.mm(0)), pocket_vert))),
                svg.Line(class_=["valley"], **l(Line(pocket_vert, t* Vec(width * 1, width * edge_y))))]


def render_print_sheet(unit, width, unit_count):
    elements = [
        common_elements(),
        svg.Rect(class_=["cut"], x=0, y=0, width=width * unit_count, height="100%"),
        *[
            svg.Line(
                class_=["cut"],
                x1=i * width,
                y1=0,
                x2=i * width,
                y2="100%",
            )
            for i in range(1, unit_count)
        ],
    ]

    for i in range(0, unit_count):
        elements += unit.render_elements(width, Vec(i * width, 0))

    return svg.SVG(
        width=width * unit_count, height=width * unit.length_ratio, elements=elements
    )


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

with open("testunit.svg", "w") as f:
    unit = RectangularCurvedUnit(length_ratio=3, end_angle=15, pocket_angle=45)
    f.write(unit.render_sheet(200, 6).as_str())

"""with open("FiveTwistedTetrahedra.svg", "w") as f:
    unit1 = WireframeUnit(138/30, LongTabPocket(Frac(1, 5), 0, Frac(2, 3)), NormalPocket(0, Frac(1, 2), 2))
    unit2 = WireframeUnit(128/30, NormalPocket(0, 1, 2), NormalPocket(0, Frac(1, 3), Frac(3, 2)))
    sheet = InstructionSheet(units = [unit1, unit2])
    f.write(sheet.render(150, 30).as_str())"""

with open("TriangleSeriesOctahedra2_InternalUnit.svg", "w") as f:
    internal_unit = WireframeUnit(
        3.05, AutoPocket(56.03, 1), AutoPocket(24.51, 0.25)
    )
    f.write(render_print_sheet(internal_unit, svg.mm(30), 3).as_str())

with open("TriangleSeriesOctahedra2_TriangleUnit.svg", "w") as f:
    triangle_unit = WireframeUnit(
        3.73, AutoPocket(37.95, 0), AutoPocket(30, 0)
    )
    f.write(render_print_sheet(triangle_unit, svg.mm(30), 3).as_str())
