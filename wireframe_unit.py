
from typing import List

import svg

from line import Line
from matrix import Matrix, offset_by, rotate_around_point
from sheets import BaseUnit
from vec import Vec


class WireframeUnit(BaseUnit):
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

#SVG unit to mm ratio used by tools like leonardo design studio
mm_ratio = 72/25.4