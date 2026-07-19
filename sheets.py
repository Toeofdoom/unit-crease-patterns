from enum import IntEnum

import svg
from textwrap import dedent
from line_simplifier import LineSimplifier
from vec import Vec
from matrix import *
from typing import List, Protocol


class BaseUnit(Protocol):
    length_ratio: float

    def render_elements(self, width: float, t: Matrix, with_hints=False) -> List: ...

    def height(self, width: float) -> float: ...


def common_elements():
    return [svg.Style(text=dedent("""
.valley {stroke: #00f; stroke-width: 2px; fill:none}
.mountain {stroke: #f00; stroke-width: 2px; fill:none }
.cut {stroke: #000; stroke-width: 3px; fill:none } 
.hint {stroke: #000; stroke-width: 1px; fill:none } 
"""))]


def render_print_sheet(unit: BaseUnit, width: float, unit_count: int) -> svg.SVG:
    elements = [
        common_elements(),
        svg.Rect(
            class_=["cut"],
            x=0,
            y=0,
            width=width * unit_count,
            height=width * unit.length_ratio,
        ),
        *[
            svg.Line(
                class_=["cut"],
                x1=i * width,
                y1=0,
                x2=i * width,
                y2=width * unit.length_ratio,
            )
            for i in range(1, unit_count)
        ],
    ]

    for i in range(0, unit_count):
        elements += unit.render_elements(width, offset_by(Vec(i * width, 0)))

    return svg.SVG(
        width=width * unit_count, height=width * unit.length_ratio, elements=elements
    )


def render_complex_sheet(
    vertical_units: list[BaseUnit],
    horizontal_units: list[BaseUnit],
    sheet_width: float,
    sheet_height: float,
    width: float,
    extra_vertical_units: list[tuple[list[BaseUnit], Vec]] = [],
    extra_horizontal_units: list[tuple[list[BaseUnit], Vec]] = [],
) -> svg.SVG:
    elements: list[svg.Element] = [
        *common_elements(),
    ]

    lines = LineSimplifier()

    for index, unit in enumerate(vertical_units):
        elements += unit.render_elements(width, offset_by(Vec(index * width, 0)))
        lines.add_rectangle(index, index + 1, 0, unit.length_ratio)

    for index, unit in enumerate(reversed(horizontal_units)):
        elements += unit.render_elements(
            width,
            offset_by(Vec(sheet_width * width, (sheet_height - index - 1) * width))
            @ rotate_around_point(Vec(0, 0), 90),
        )
        lines.add_rectangle(
            sheet_width - unit.length_ratio,
            sheet_width,
            sheet_height - index - 1,
            sheet_height - index,
        )

    for units, offset in extra_vertical_units:
        for index, unit in enumerate(units):
            elements += unit.render_elements(
                width, offset_by(offset * width + Vec(index * width, 0))
            )
            lines.add_rectangle(
                offset.x + index,
                offset.x + index + 1,
                offset.y,
                offset.y + unit.length_ratio,
            )

    for units, offset in extra_horizontal_units:
        for index, unit in enumerate(units):
            elements += unit.render_elements(
                width,
                offset_by(offset * width + Vec(0, (index + 1) * width))
                @ rotate_around_point(Vec(0, 0), -90),
            )
            lines.add_rectangle(
                offset.x,
                offset.x + unit.length_ratio,
                offset.y + index,
                offset.y + index + 1,
            )

    elements += lines.render(width)

    return svg.SVG(
        width=width * sheet_width, height=width * sheet_height, elements=elements
    )


def render_hex_grid(size, scaling):
    width_ratio = math.sqrt(3) * 2.0 / 3
    centre = Vec(size * width_ratio * scaling * 0.5, size * scaling * 0.5)

    def efficient_path(start, transformations):
        return [
            svg.MoveTo(*start),
            *[svg.LineTo(*(t * start)) for t in transformations],
        ]

    start = Vec(size * width_ratio * scaling * 0.25, 0)
    hex = svg.Path(
        class_=["cut"],
        d=efficient_path(
            start,
            [rotate_around_point(centre, 60 * i) for i in range(1, 7)],
        ),
    )
    elements = [common_elements(), hex]
    elements += [
        svg.Path(
            class_=["valley"],
            d=efficient_path(
                Vec(abs(size * 0.5 - i) * width_ratio * scaling * 0.5, i * scaling),
                [
                    reflect_x_at(centre.x),
                    rotate_around_point(centre, 240),
                    rotate_around_point(centre, 240) @ reflect_x_at(centre.x),
                    rotate_around_point(centre, 120),
                    rotate_around_point(centre, 120) @ reflect_x_at(centre.x),
                    identity(),
                ],
            ),
        )
        for i in list(range(1, size // 4))
    ]

    elements += [
        svg.Path(
            class_=["valley"],
            d=efficient_path(
                Vec(abs(size * 0.5 - i) * width_ratio * scaling * 0.5, i * scaling),
                [
                    reflect_x_at(centre.x),
                    rotate_around_point(centre, 120),
                    rotate_around_point(centre, 120) @ reflect_x_at(centre.x),
                    rotate_around_point(centre, 240),
                    rotate_around_point(centre, 240) @ reflect_x_at(centre.x),
                    identity(),
                ],
            ),
        )
        for i in range((3 * size + 4) // 4, size)
    ]

    if size % 4 == 0:
        elements += [
            svg.Path(
                class_=["valley"],
                d=efficient_path(
                    Vec(abs(size * 0.5 - i) * width_ratio * scaling * 0.5, i * scaling),
                    [
                        rotate_around_point(centre, 120),
                        rotate_around_point(centre, 240),
                        identity(),
                    ],
                ),
            )
            for i in [size // 4, 3 * size // 4]
        ]
    if size % 2 == 0:
        elements += [
            svg.Line(
                class_=["valley"],
                **(
                    rotate_around_point(centre, 60 * i)
                    * Line(start, rotate_around_point(centre, 180) * start)
                ),
            )
            for i in range(0, 3)
        ]
    return svg.SVG(
        width=size * width_ratio * scaling, height=size * scaling, elements=elements
    )


class HintType(IntEnum):
    POCKET_EDGE = -2
    POCKET_BOOKCASE = -1
    CENTRE = 0
    BOOKCASE = 1
    EDGE = 2


def render_cheatsheet(units: list[BaseUnit], width: float, padding: float) -> svg.SVG:
    def x_offset_for(i):
        return (padding + width) * i + padding

    height = max(unit.height(width) for unit in units) + padding * 2

    def unit_elements_for(unit: BaseUnit, i):
        x = x_offset_for(i)
        return [
            svg.Text(
                text=f"{unit.name} Unit x{unit.count}",
                x=x,
                y=padding - svg.mm(13),
                font_size=20,
                font_weight="bold",
                font_family="sans-serif",
            ),
            svg.Text(
                text=f"Length ratio {unit.length_ratio:.2f}",
                x=x,
                y=padding - svg.mm(5),
                font_size=20,
                font_weight="bold",
                font_family="sans-serif",
            ),
            svg.Rect(
                class_=["cut"],
                x=x,
                y=padding,
                width=width,
                height=width * unit.length_ratio,
            ),
            *unit.render_elements(width, Vec(x, padding), with_hints=True),
        ]

    elements = [
        *common_elements(),
        *[unit_elements_for(unit, i) for i, unit in enumerate(units)],
    ]
    return svg.SVG(
        width=x_offset_for(len(units)),
        height=height,
        elements=elements,
    )
