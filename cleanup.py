import cv2 as cv
import numpy as np
import math
from unitsvg import Vec, Line, l
from typing import Tuple
import svg

img = cv.imread("twolayer_sevenfold_weave_cp-1016x1024.jpg")

blue, green, red = cv.split(img)
not_blue, not_green, not_red = cv.split(cv.bitwise_not(img))


def channel_filter(channels: list, shift=25, mul=1.2):
    current = channels[0]
    for next_channel in channels[1:]:
        current = cv.multiply(current, next_channel, scale=1 / 255)
    return cv.multiply(cv.subtract(current, shift), mul)


red_only = channel_filter([red, not_blue, not_green])
blue_only = channel_filter([blue, not_red, not_green])
black_only = channel_filter([not_red, not_blue, not_green], 130, 2)

greyish = cv.scaleAdd(red, 0.8, cv.multiply(blue, 0.2))


lines = cv.createLineSegmentDetector(cv.LSD_REFINE_ADV)
raw_red_lines, widths, somethings, blah = lines.detect(red_only)
raw_blue_lines, widths, somethings, blah = lines.detect(blue_only)
raw_black_lines, widths, somethings, blah = lines.detect(black_only)


def print_lines_on(target, lines):
    result = np.copy(target)
    for i in range(0, len(lines)):
        # if widths[i] > 2:
        line = lines[i]
        l = (
            (line.v1.x, line.v1.y, line.v2.x, line.v2.y)
            if type(line) is Line
            else lines[i][0]
        )
        cv.line(
            result,
            (int(l[0]), int(l[1])),
            (int(l[2]), int(l[3])),
            (0, 255, 0),
            1,
            cv.LINE_AA,
        )
        cv.circle(result, (round(l[0]), round(l[1])), 5, (0, 0, 255), 1, cv.LINE_AA)
        cv.circle(result, (round(l[2]), round(l[3])), 5, (0, 0, 255), 1, cv.LINE_AA)
    return result


def print_verts_on(target, verts: list[Vec]):
    result = np.copy(target)
    for vert in verts:
        cv.circle(result, (round(vert.x), round(vert.y)), 5, (0, 0, 255), 1, cv.LINE_AA)
    return result


# Filter exact parallels out first, by colour - more useful. Sort lines by angle, then compare to neighbors.
def simplify_lines(raw_lines):
    lines = sorted(
        [
            Line(Vec(line[0][0], line[0][1]), Vec(line[0][2], line[0][3]))
            for line in raw_lines
        ],
        key=lambda line: line.angle_radians,
    )
    simplified_lines = [lines[0]]
    angle_threshold = 0.3
    vert_threshold =10
    for line in lines[1:]:
        n = 1
        while (
            n <= len(simplified_lines)
            and abs(line.angle_radians - simplified_lines[-n].angle_radians)
            < angle_threshold
        ):
            other = simplified_lines[-n]

            if (
                line.v1.dist(other.v1) < vert_threshold
                and line.v2.dist(other.v2) < vert_threshold
            ):
                simplified_lines[-n] = Line(
                    (line.v1 + other.v1) * 0.5, (line.v2 + other.v2) * 0.5
                )
                break

            if (
                line.v2.dist(other.v1) < vert_threshold
                and line.v1.dist(other.v2) < vert_threshold
            ):
                simplified_lines[-n] = Line(
                    (line.v2 + other.v1) * 0.5, (line.v1 + other.v2) * 0.5
                )
                break

            n += 1
        else:
            simplified_lines.append(line)
    return simplified_lines


simplified_lines: list[tuple[Line, tuple[int, int, int]]] = [
    *[(line, (0, 0, 255)) for line in simplify_lines(raw_red_lines)],
    *[(line, (255, 0, 0)) for line in simplify_lines(raw_blue_lines)],
    *[(line, (0, 0, 0)) for line in simplify_lines(raw_black_lines)],
]


def simplify_verts(verts, threshold):
    vertex_groups: list[list[Vec]] = []
    for vertex in verts:
        for i, vertex_group in enumerate(vertex_groups):
            if min(vertex.dist(other) for other in vertex_group) < threshold:
                vertex_group.append(vertex)
                break
        else:
            vertex_groups.append([vertex])

    centres = [sum(group, Vec(0, 0)) * (1.0 / len(group)) for group in vertex_groups]
    return centres


corners = cv.goodFeaturesToTrack(greyish, 2700, 0.2, 10)

all_verts = np.array(
    [(line.v1.x, line.v1.y, line.v2.x, line.v2.y) for line, _ in simplified_lines],
    dtype=np.float32,
).reshape(len(simplified_lines) * 2, 2)

vert_ids = []
for line in simplified_lines:
    vert_ids.append((line, 0))
    vert_ids.append((line, 1))
# vert_ids = [(line, 0) for line in simplified_lines] + [(line, 1) for line in simplified_lines]

red_verts = raw_red_lines.reshape(raw_red_lines.shape[0] * 2, 2)
knn = cv.ml.KNearest.create()
knn.train(all_verts, cv.ml.ROW_SAMPLE, np.array(range(0, len(vert_ids))))
ret, results, all_neighbors, all_dist = knn.findNearest(all_verts, 10)

# Simplify parallel lines BEFORE the all-verts step.
# Tag lines with colours or something
# Use KNN on vertices to find clusters. Determine simplified vertices with line direction + vert (closest intercept)
# This part is the confusing one for processing, I guess. Maybe each vert should be id as line id + v1/v2
# Then you just go through one-by-one... Test vertex to be added. If it:
# Is not part of an already added line,
# and the intersect (or best trilateration point) is close, add it.
# Each line can only be processed into a cluster once.
# Generate clusters one by one, not vert by vert (can get all vert neighbors at once for simplicity though)
clusters = []
clustered_verts = set()
cluster_mapping = {}


def details(vert_index):
    id = vert_ids[vert_index]
    line: Line = id[0][0]
    if id[1] == 1:
        vert = line.v2
        direction = line.v2 - line.v1
    else:
        vert = line.v1
        direction = line.v1 - line.v2
    return id, line, vert, direction


cluster_map = {}
for i in range(0, len(all_verts)):
    id, line, vert, direction = details(i)
    if id in clustered_verts:
        continue

    clustered_verts.add(id)

    lines_in_cluster = []
    verts = []
    intercepts = []

    neighbors = [int(n) for n in all_neighbors[i]]
    # neighbors_actual = sorted(range(0, len(all_verts)), key = lambda n: details(n)[2].dist(vert))[0:11]
    cluster_centre = vert

    def add_to_cluster(id, line, vert, direction, new_intercepts):
        global intercepts
        global cluster_centre
        lines_in_cluster.append(line)
        verts.append(vert)
        cluster_mapping[id] = len(clusters)
        intercepts += new_intercepts
        cluster_centre = (
            sum(intercepts, Vec(0, 0)) * (1 / len(intercepts)) if intercepts else vert
        )

    add_to_cluster(id, line, vert, direction, [])

    for n in neighbors:
        n_id, n_line, n_vert, n_direction = details(n)
        if n_line in lines_in_cluster:
            continue

        new_intersections = [n_line.intersection(l) for l in lines_in_cluster]
        if (
            max(
                [min(i.dist(cluster_centre), i.dist(n_vert)) for i in new_intersections]
            )
            < 5
        ):
            add_to_cluster(n_id, n_line, n_vert, n_direction, new_intersections)

    # cluster_centre = sum(verts, Vec(0, 0)) * (1 / len(verts))
    cluster_centre = (
        sum(intercepts, Vec(0, 0)) * (1 / len(intercepts)) if intercepts else vert
    )
    clusters.append(cluster_centre)

    for vert in verts:
        cluster_map[vert] = cluster_centre


adjusted_lines = [
    (Line(cluster_map[line.v1], cluster_map[line.v2]), c) for line, c in simplified_lines
]
# cv.imshow("Original", img)
# cv.imshow("Red Bits", red_only)
# cv.imshow("Blue Bits", blue_only)
# cv.imshow("Black Bits", black_only)
cv.imshow("Simplified Red Lines", print_lines_on(img, simplify_lines(raw_red_lines)))
cv.imshow("Simplified Blue Lines", print_lines_on(img, simplify_lines(raw_blue_lines)))
cv.imshow(
    "Simplified Black Lines", print_lines_on(img, simplify_lines(raw_black_lines))
)
cv.imshow(
    "detected verts",
    print_verts_on(greyish, [Vec(*vec.ravel()) for vec in np.intp(corners)]),
)
cv.imshow(
    "Cluster test",
    print_verts_on(img, clusters),
)


def bgr_to_code(b, g, r):
    return f"#{r:02x}{g:02x}{b:02x}"


with open("SimplifiedLines.svg", "w") as f:
    f.write(
        svg.SVG(
            width=svg.px(img.shape[0]),
            height=svg.px(img.shape[1]),
            elements=[
                svg.Line(stroke=bgr_to_code(*colour), **l(line))
                for line, colour in simplified_lines
            ],
        ).as_str()
    )

with open("Complete.svg", "w") as f:
    f.write(
        svg.SVG(
            width=svg.px(img.shape[0]),
            height=svg.px(img.shape[1]),
            elements=[
                svg.Line(stroke=bgr_to_code(*colour), **l(line))
                for line, colour in adjusted_lines
            ],
        ).as_str()
    )
# cv.imshow("Blue", blue_bits)
# cv.imshow("Black", black_bits)
k = cv.waitKey(0)
