import math
import svg
from matrix import *
from vec import Vec
from line import Line
from sheets import common_elements


def lerp(a, b, n):
    return b * n + (1 - n) * a

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
                                **(
                                    t
                                    * Vec(
                                        lerp(end_x, centre_x, 0.8),
                                        lerp(y1, centre_y, 0.4),
                                    )
                                ).v1,
                                **(t * Vec(centre_x, lerp(y1, centre_y, 0.7))).v2,
                                **(t * Vec(centre_x, centre_y)),
                            ),
                            svg.CubicBezier(
                                **(t * Vec(centre_x, lerp(centre_y, y2, 0.4))).v1,
                                **(
                                    t
                                    * Vec(
                                        lerp(end_x, centre_x, 0.8),
                                        lerp(centre_y, y2, 0.8),
                                    )
                                ).v2,
                                **(t * Vec(end_x, y2)),
                            ),
                        ],
                    )
                ]

            def render_central_curve(t):
                return render_curve(
                    t,
                    0.25 * width,
                    0.5 * width,
                    curve_endpoint.y,
                    height * 0.5,
                    height * 0.36,
                )

            def render_second_curve(t):
                return render_curve(
                    t,
                    0.32 * width,
                    0.75 * width,
                    pocket_endpoint.y,
                    height * 0.48,
                    height * 0.39,
                )

            def render_third_curve(t):
                return render_curve(
                    t,
                    0.39 * width,
                    0.75 * width,
                    pocket_endpoint.y + height * 0.09,
                    height * 0.45,
                    height * 0.41,
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
                    **(t * Vec(pocket_endpoint.x, 0)).v1,
                    **(t * pocket_endpoint).v2,
                ),
                svg.Line(class_=["valley"], **pocket_line),
                svg.Line(
                    class_=["valley"],
                    **((t @ reflect_x_at(width * 0.75)) * curve_endpoint).v1,
                    **(t * pocket_endpoint).v2,
                ),
                svg.Line(class_=["valley"], **left_bookcase),
                svg.Line(class_=["valley"], **right_bookcase),
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
