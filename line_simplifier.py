import svg

class LineSimplifier:
    def __init__(self):
        self.vertical_lines = []
        self.horizontal_lines = []

    def add_rectangle(self, l, r, t, b):
        self.horizontal_lines.append((l, r, t))
        self.horizontal_lines.append((l, r, b))
        self.vertical_lines.append((l, t, b))
        self.vertical_lines.append((r, t, b))

    def render(self, width):
        all_y = set([y for _, _, y in self.horizontal_lines])
        simplified_horizontal_lines = [
            (
                min(x1 for x1, _, _y in self.horizontal_lines if y == _y),
                max(x2 for _, x2, _y in self.horizontal_lines if y == _y),
                y,
            )
            for y in all_y
        ]
        all_x = set([x for x, _, _ in self.vertical_lines])
        simplified_vertical_lines = [
            (
                x,
                min(y1 for _x, y1, _ in self.vertical_lines if x == _x),
                max(y2 for _x, _, y2 in self.vertical_lines if x == _x),
            )
            for x in all_x
        ]
        return [
            *[
                svg.Line(
                    class_=["cut"],
                    x1=x1 * width,
                    y1=y * width,
                    x2=x2 * width,
                    y2=y * width,
                )
                for x1, x2, y in simplified_horizontal_lines
            ],
            *[
                svg.Line(
                    class_=["cut"],
                    x1=x * width,
                    y1=y1 * width,
                    x2=x * width,
                    y2=y2 * width,
                )
                for x, y1, y2 in simplified_vertical_lines
            ],
        ]

