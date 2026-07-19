import math
import svg
from matrix import *
from vec import Vec
from line import Line, lerp
from sheets import BaseUnit
from bezier import Bezier


class TransformStackZone:
    def __init__(self, initial_verts, transform):
        self.transform = transform
        self.verts = list(initial_verts)

    @property
    def edges(self):
        return [
            Line(v1, v2) for v1, v2 in zip(self.verts, [*self.verts[1:], self.verts[0]])
        ]

    def clip_line_and_split(
        self, line, unfolded_tangent
    ) -> tuple[Line | None, list["TransformStackZone"]]:
        current_segment_verts = []
        other_segment_verts = []
        intersection_verts = []
        for edge in self.edges:
            intersect = edge.intersection(line)
            current_segment_verts.append(edge.v1)
            if intersect:
                segment_check = (intersect - edge.v1).dot(edge.direction.normalised)
                if segment_check >= 0 and segment_check < edge.length:
                    intersection_verts.append(intersect)
                    current_segment_verts.append(intersect)
                    other_segment_verts.append(intersect)
                    tmp = current_segment_verts
                    current_segment_verts = other_segment_verts
                    other_segment_verts = tmp

        if len(intersection_verts) > 1:
            dots = [
                unfolded_tangent.dot(vert - line.v1) for vert in current_segment_verts
            ]
            unfolded, folded = (
                (current_segment_verts, other_segment_verts)
                if sum(dots) > 0
                else (other_segment_verts, current_segment_verts)
            )
            # Need to pick flipped transform correctly!
            return Line(*intersection_verts), [
                TransformStackZone(unfolded, self.transform),
                TransformStackZone(folded, reflect_over_line(line) @ self.transform),
            ]
        return None, [self]

    def clip_line(self, line) -> Line | None:
        intersection_verts = []
        for edge in self.edges:
            intersect = edge.intersection(line)
            if intersect:
                segment_check = (intersect - edge.v1).dot(edge.direction.normalised)
                if segment_check >= 0 and segment_check < edge.length:
                    intersection_verts.append(intersect)

        if len(intersection_verts) > 1:
            ts = [
                (intersect - line.v1).dot(line.direction.normalised)
                for intersect in intersection_verts
            ]
            start_t = max(0, min(ts))
            end_t = min(line.length, max(ts))
            if start_t > end_t:
                return None
            return Line(
                line.v1 + line.direction.normalised * start_t,
                line.v1 + line.direction.normalised * end_t,
            )
        return None

    def clip_bezier(self, bezier: Bezier) -> list[Bezier]:
        all_curves = [bezier]
        for edge in self.edges:
            clipped_curves = []
            for curve in all_curves:
                intercepts = curve.intersections(edge)
                current_segment = curve
                last_intercept = 0.0
                for intercept in intercepts:
                    before, after = current_segment.split_at(
                        (intercept - last_intercept) / (1 - last_intercept)
                    )
                    last_intercept = intercept
                    clipped_curves.append(before)
                    current_segment = after
                clipped_curves.append(current_segment)
            all_curves = [
                c for c in clipped_curves if (c.at(0.5) - edge.v1).dot(edge.tangent) < 0
            ]
        return all_curves


class CreaseLine:
    def __init__(self, line: Line):
        self.line = line

    def render_elements(self, width: float, t: Matrix, with_hints=False):
        transformed_line = Line(self.line.v1 * width, self.line.v2 * width)
        return [svg.Line(class_=["valley"], **(t * transformed_line))]


class CreaseBezier:
    def __init__(self, bezier: Bezier):
        self.bezier = bezier

    def render_elements(self, width: float, t: Matrix, with_hints=False):
        transformed_bezier: Bezier = t * Bezier(
            [v * width for v in self.bezier.control_points]
        )

        """return svg.Path(  # Central curve
            class_=["valley"],
            clip_path=
            d=[
                svg.MoveTo(*transformed_bezier.control_points[0].bla),
                svg.CubicBezier(
                    **transformed_bezier.control_points[1].bla.v1,
                    **transformed_bezier.control_points[2].bla.v2,
                    **transformed_bezier.control_points[3].bla,
                ),
            ]
        )"""

        return svg.Path(  # Central curve
            class_=["valley"],
            d=[
                svg.MoveTo(*(transformed_bezier.control_points[0])),
                svg.CubicBezier(
                    **transformed_bezier.control_points[1].v1,
                    **transformed_bezier.control_points[2].v2,
                    **transformed_bezier.control_points[3],
                ),
            ],
        )


# Intended to be built up over several steps.
class TransformStackUnit(BaseUnit):
    def __init__(self, length_ratio: float, initial_transform: Matrix | None = None):
        # Could allow non-rectangles?
        self.zones = [
            TransformStackZone(
                [Vec(0, 0), Vec(1, 0), Vec(1, length_ratio), Vec(0, length_ratio)],
                initial_transform or identity(),
            )
        ]
        self.symmetries = [identity()]
        self.elements = []
        self.length_ratio = length_ratio

    #
    def add_rotational_symmetry(self, point: Vec):
        self.symmetries += [rotate_around_point(point, 180)]

    def add_fold(
        self, line: Line, unfolded_point
    ):  # direction means which part is being flipped
        unfolded_tangent = line.tangent
        if unfolded_tangent.dot(unfolded_point - line.v1) < 0:
            unfolded_tangent = -unfolded_tangent

        for symmetry in self.symmetries:
            symm_line = symmetry * line
            symm_unfolded_tangent = symmetry.multiply_direction(unfolded_tangent)

            new_zones = []
            for zone in self.zones:
                transformed_line = zone.transform * symm_line
                transformed_unfolded_tangent = zone.transform.multiply_direction(
                    symm_unfolded_tangent
                )
                line_segment, split_zones = zone.clip_line_and_split(
                    transformed_line, transformed_unfolded_tangent
                )
                new_zones += split_zones
                if line_segment:
                    self.elements.append(CreaseLine(line_segment))
            self.zones = new_zones

    def add_simple_fold(
        self, line: Line
    ):  # direction means which part is being flipped
        for symmetry in self.symmetries:
            symm_line = symmetry * line

            for zone in self.zones:
                transformed_line = zone.transform * symm_line
                line_segment = zone.clip_line(transformed_line)
                if line_segment:
                    self.elements.append(CreaseLine(line_segment))

    def add_bezier_crease(self, bezier: Bezier):
        for symmetry in self.symmetries:
            symm_bezier = symmetry * bezier
            for zone in self.zones:
                self.elements += [
                    CreaseBezier(segment)
                    for segment in zone.clip_bezier(zone.transform * symm_bezier)
                ]

    def render_elements(self, width: float, t: Matrix, with_hints=False) -> list:
        return [
            element.render_elements(width, t, with_hints) for element in self.elements
        ]


# Think about it as folding the paper, building up a state. Each task happens differently based on the current state.
# Rotational doubling is simply done as you complete EACH task. e.g. double(actual_operation)
# Add bookcase
# Add pocket - the line should be reflected by the bookcases.
# Add lines

# Base zone - has borders, and a transform (which is obviously very basic.)
# CAN actually represent reflection as a zone which does NOT change the borders, but changes the transform
# Adding a bookcase splits the main zone polygon into a new, smaller main zone, and a reflected zone (with a matching transform)
# Adding the pocket is evaluated in EACH zone (according to the transform + borders) - when it actually crosses a zone, it splits and reflects that zone
# Every normal line or curve added is evaluated in each zone according to the transform and borders


# Then rotation around centre?
# Then add lines.
