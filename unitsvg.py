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
    return b * n + (1-n) * a

def common_elements():
    return [
        svg.Style(
            text=dedent(
                """
.valley {stroke: #00f; stroke-width: 2px; fill:none}
.mountain {stroke: #f00; stroke-width: 2px; fill:none }
.cut {stroke: #000; stroke-width: 5px; fill:none } 
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
            self._render_elements(width, 0),
        ]
        return svg.SVG(width=width, height=self.height(width), elements=elements)

    def render_sheet(self, width, units):
        elements = [
            *common_elements(),
            svg.Rect(class_=["cut"], x=0, y=0, width=width * units, height="100%"),
            *[
                svg.Line(
                    class_=["cut"],
                    x1=i * width,
                    y1=0,
                    x2=i * width,
                    y2="100%",
                )
                for i in range(1, units)
            ],
        ]

        for i in range(0, units):
            elements += self._render_elements(width, Vec(i * width, 0))

        return svg.SVG(
            width=width * units, height=width * self.length_ratio, elements=elements
        )

    def _render_elements(self, width, offset: Vec):
        height = self.height(width)
        end_direction = Vec(1, math.tan(math.radians(self.end_angle)))
        pocket_direction = Vec(1, math.tan(math.radians(90 - self.pocket_angle)))

        def render_half(t):
            curve_endpoint = end_direction * width * 0.5
            pocket_endpoint = curve_endpoint + pocket_direction * width * 0.25
            pocket_line = Line(t * curve_endpoint, t * pocket_endpoint)
            left_bookcase = Line(
                t * (curve_endpoint * 0.5), t * Vec(width * 0.25, height * 0.5)
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
                                **v1(t * Vec(lerp(end_x, centre_x, 0.8), lerp(y1, centre_y, 0.4))),
                                **v2(t * Vec(centre_x, lerp(y1, centre_y, 0.6))),
                                **v(t * Vec(centre_x, centre_y))
                            ),
                            svg.SmoothCubicBezier(
                                **v2(t * Vec(centre_x, (y2 - height * 0.025))),
                                **v(t * Vec(end_x, y2))
                            ),
                        ],
                    )
                ]

            def render_central_curve(t):
                return render_curve(
                    t,
                    0.28 * width,
                    0.5 * width,
                    curve_endpoint.y,
                    height * 0.5,
                    height * 0.35,
                )

            def render_second_curve(t):
                return render_curve(
                    t,
                    0.39 * width,
                    0.75 * width,
                    pocket_endpoint.y,
                    height * 0.5,
                    height * 0.35,
                )
            
            
            def render_third_curve(t):
                return render_curve(
                    t,
                    0.5 * width,
                    0.75 * width,
                    pocket_endpoint.y + height * 0.1,
                    height * 0.45,
                    height * 0.35,
                )

            return [
                svg.Line(  # Skew unit end line
                    class_=["valley"], **v1(t * Vec(0, 0)), **v2(t * curve_endpoint)
                ),
                svg.Line(class_=["valley"], **v1(t*Vec(pocket_endpoint.x, 0)), **v2(t*pocket_endpoint)),
                svg.Line(class_=["valley"], **l(pocket_line)),
                svg.Line(class_=["valley"], **v1((t@reflect_x_at(width * 0.75))*curve_endpoint), **v2(t* pocket_endpoint)),
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


unit = RectangularCurvedUnit(length_ratio=4, end_angle=15, pocket_angle=30)
with open("testunit.svg", "w") as f:
    f.write(unit.render_sheet(200, 2).as_str())
