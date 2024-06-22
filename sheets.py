import svg
from textwrap import dedent
from line_simplifier import LineSimplifier
from vec import Vec
from matrix import *
from typing import Protocol


class BaseUnit(Protocol):
    length_ratio: float

    def render_elements(
        self, width: svg.Length, offset: Vec | Matrix, with_hints=False
    ):
        pass


def common_elements():
    return [
        svg.Style(
            text=dedent(
                """
.valley {stroke: #00f; stroke-width: 2px; fill:none}
.mountain {stroke: #f00; stroke-width: 2px; fill:none }
.cut {stroke: #000; stroke-width: 3px; fill:none } 
.hint {stroke: #000; stroke-width: 1px; fill:none } 
"""
            )
        )
    ]


def render_print_sheet(unit: BaseUnit, width: svg.Length, unit_count: int) -> svg.SVG:
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
        elements += unit.render_elements(width, Vec(i * width, 0))

    return svg.SVG(
        width=width * unit_count, height=width * unit.length_ratio, elements=elements
    )


def render_complex_sheet(
    vertical_units: list[BaseUnit],
    horizontal_units: list[BaseUnit],
    sheet_width: float,
    sheet_height: float,
    width: svg.Length,
) -> svg.SVG:
    elements = [
        common_elements(),
    ]

    lines = LineSimplifier()

    for index, unit in enumerate(vertical_units):
        elements += unit.render_elements(width, Vec(index * width, 0))
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

    elements += lines.render(width)

    return svg.SVG(
        width=width * sheet_width, height=width * sheet_height, elements=elements
    )


def render_cheatsheet(
    units: list[BaseUnit], width: svg.Length, padding: svg.Length
) -> svg.SVG:
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
