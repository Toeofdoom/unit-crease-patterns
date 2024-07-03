
from vec import Vec
import svg
from line import Line
import numpy

class Bezier:
    def __init__(self, control_points: list[Vec]):
        self.control_points = control_points

    @property
    def order(self):
        return len(self.control_points)-1

    def _b(self, i: int, j: int, t: float) -> Vec:
        if j == 0:
            return self.control_points[i]
        return self._b(i, j - 1, t)*(1 - t) + self._b(i + 1, j - 1, t)*t

    def at(self, t):
        return self._b(0, self.order, t)
    
    def split_at(self, t: float):
        return (
            Bezier([self._b(0, i, t) for i in range(self.order + 1)]),
            Bezier([self._b(i, self.order - i, t) for i in range(self.order + 1)]),
        )
    
    def intersections(self, line: Line):
        vec, d = line.as_vec_d()
        dots = [vec.dot(v) for v in self.control_points]
        coefficients = [
            1*dots[0]-d,
            -3*dots[0] + 3*dots[1],
            3*dots[0] + -6*dots[1] + 3* dots[2],
            -1*dots[0] + 3*dots[1] + -3*dots[2] + 1*dots[3]
        ]
        """coefficients = [0, 0, 0, -d]
        coefficients += [-1, 3, -3, 1] * self.control_points[0].dot(vec)
        coefficients += [3, -6, 3, 0] * self.control_points[1].dot(vec)
        coefficients += [-3, 3, 0, 0] * self.control_points[2].dot(vec)
        coefficients += [1, 0, 0, 0] * self.control_points[3].dot(vec)"""
        p = numpy.polynomial.polynomial.Polynomial(coefficients)
        #p.domain = [0., 1.]
        roots = p.roots()
        return [complex(r).real for r in roots if complex(r).real >= 0 and complex(r).real <= 1 and complex(r).imag < 0.01 and complex(r).imag > -0.01]



    def _render(self, width, t):
        #Only cubic implemented.
        return svg.Path(
            class_=["valley"],
            d=[
                svg.MoveTo(*(t * (self.control_points[0]))),
                svg.CubicBezier(
                    **(t * (self.control_points[1])).v1,
                    **(t * (self.control_points[2])).v2,
                    **(t * (self.control_points[3])),
                ),
            ],
        )

