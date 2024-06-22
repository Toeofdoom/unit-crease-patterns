import math
import svg
from vec import Vec
from line import Line

class AutoPocket:
    def __init__(self, angle_degrees, con, extra=None):
        self.angle_radians = math.radians(angle_degrees)
        self.inv_angle_radians = math.radians(90 - angle_degrees)
        self.con = con
        self.inv_extra_angle_radians = []
        if extra:
            self.inv_extra_angle_radians.append(
                math.radians(90 - extra) if extra else None
            )
            self.inv_extra_angle_radians.append(math.radians(90 - extra * 2))
        self.hints = []

    def extra_length(self):
        return self.con * math.tan(self.inv_angle_radians) * 0.25

    def render(self, t, width, with_hints):
        start_x = 0.5 - self.con * 0.25
        end_x = 0.75
        end_y = (end_x - start_x) * math.tan(self.inv_angle_radians)
        edge_y = end_y - math.tan(self.inv_angle_radians) * 0.25

        pocket_vert = t * Vec(width * end_x, width * end_y)

        lines = [
            svg.Line(
                class_=["valley"],
                **(Line(t * Vec(width * start_x, svg.mm(0)), pocket_vert)),
            ),
            svg.Line(
                class_=["valley"],
                **(Line(pocket_vert, t * Vec(width * 1, width * edge_y))),
            ),
        ]

        for extra_angle in self.inv_extra_angle_radians:

            mid_x = 0.5
            mid_y = (mid_x - start_x) * math.tan(self.inv_angle_radians)

            extra_x = 0.25
            extra_y = mid_y + (mid_x - extra_x) * math.tan(extra_angle)
            extra_vert = t * Vec(width * extra_x, width * extra_y)

            lines += [
                svg.Line(
                    class_=["valley"],
                    **(Line(t * Vec(width * mid_x, width * mid_y), extra_vert)),
                ),
                svg.Line(
                    class_=["valley"],
                    **(Line(extra_vert, t * Vec(svg.mm(0), width * mid_y))),
                ),
            ]

        if with_hints:
            for hint in self.hints:
                lines.append(hint.render(t, width))

        return lines

    def with_hint_from(self, from_x):
        start_x = 0.5 - self.con * 0.25
        from_x_normalised = 0.5 - from_x * 0.25
        segment_length = from_x_normalised - start_x
        segment_radians = self.inv_angle_radians * 2
        to_x = start_x + segment_length * math.cos(segment_radians)
        to_y = segment_length * math.sin(segment_radians)
        self.hints.append(self.Hint(from_x_normalised, to_x, to_y))
        return self

    def with_hint_to(self, to_x):
        start_x = 0.5 - self.con * 0.25
        to_x_normalised = 0.5 - to_x * 0.25
        segment_radians = self.inv_angle_radians * 2
        x_diff = start_x - to_x_normalised
        to_y = -x_diff * math.tan(segment_radians)
        segment_length = math.sqrt(x_diff * x_diff + to_y * to_y)
        from_x = start_x + segment_length
        self.hints.append(self.Hint(from_x, to_x_normalised, to_y))
        return self

    class Hint:
        def __init__(self, from_x, to_x, to_y):
            self.from_x = from_x
            self.to_x = to_x
            self.to_y = to_y

        def render(self, t, width):
            from_ = t * Vec(self.from_x * width, 0)
            to = t * Vec(self.to_x * width, self.to_y * width)
            return [
                svg.Circle(class_=["hint"], r=svg.mm(2), **from_.c),
                svg.Circle(class_=["hint"], r=svg.mm(2), **to.c),
                svg.Line(class_=["hint"], **from_.v1, **to.v2),
            ]
