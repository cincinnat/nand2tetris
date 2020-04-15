import math

from .real import Real
from .linalg import Vector, Matrix


class Scene:
    # https://en.wikipedia.org/wiki/Octahedron
    __OCTAHEDRON = [
        Vector([1, 0, 0]), Vector([0,  1,  0]), Vector([0,  0,  1]),
        Vector([1, 1, 1]).norm(),
        Vector([1, 0, 0]), Vector([0,  0,  1]), Vector([0, -1,  0]),
        Vector([1, -1, 1]).norm(),
        Vector([1, 0, 0]), Vector([0,  0, -1]), Vector([0,  1,  0]),
        Vector([1, 1, -1]).norm(),
        Vector([1, 0, 0]), Vector([0, -1,  0]), Vector([0,  0, -1]),
        Vector([1, -1, -1]).norm(),

        Vector([-1, 0, 0]), Vector([0,  0,  1]), Vector([0,  1,  0]),
        Vector([-1, 1, 1]).norm(),
        Vector([-1, 0, 0]), Vector([0, -1,  0]), Vector([0,  0,  1]),
        Vector([-1, -1, 1]).norm(),
        Vector([-1, 0, 0]), Vector([0,  1,  0]), Vector([0,  0, -1]),
        Vector([-1, 1, -1]).norm(),
        Vector([-1, 0, 0]), Vector([0,  0, -1]), Vector([0, -1,  0]),
        Vector([-1, -1, -1]).norm(),
    ]


    def __init__(self, scale):
        def to_real(v):
            return Vector([
                Real(float(v.x)),
                Real(float(v.y)),
                Real(float(v.z)),
            ])
        self.octahedron = [to_real(v) for v in self.__OCTAHEDRON]

        self._scale = scale
        self._light = Vector([.5, 1, 0]).norm()
        self._color = 1


    def __get_color(self, norm):
        return int(self._color * self._light.norm().dot(norm))


    def __rot(self, direction):
        angle = 10 / 180 * math.pi
        cos = Real(math.cos(angle))
        sin = Real(math.sin(angle))
        if direction < 0:
            sin = -sin
        return sin, cos

    def rotate_x(self, direction):
        sin, cos = self.__rot(direction)
        m = Matrix([
            Real(1.), Real(0.), Real(0.),
            Real(0.), cos,      -sin,
            Real(0.), sin,      cos,
        ])
        self.octahedron = [m*v for v in self.octahedron]

    def rotate_y(self, direction):
        sin, cos = self.__rot(direction)
        m = Matrix([
            cos,      Real(0.), -sin,
            Real(0.), Real(1.), Real(0.),
            sin,      Real(0.), cos,
        ])
        self.octahedron = [m*v for v in self.octahedron]

    def scale(self, coef):
        self._scale *= coef

    def iter_facets(self):
        def to_float(v, scale=self._scale):
            return Vector([
                v.x.to_float(),
                v.y.to_float(),
                v.z.to_float(),
            ])
        def to_int(v, scale=self._scale):
            return Vector([
                int(v.x.to_float() * self._scale),
                int(v.y.to_float() * self._scale),
                int(v.z.to_float() * self._scale),
            ])

        for i in range(len(self.octahedron) // 4):
            v1, v2, v3, n = self.octahedron[i*4: (i+1)*4]
            if n.z.to_float() <= -.01:
                continue

            color = self._light.dot(to_float(n))
            color = max(-1, min(color, 1))
            color = math.acos(color) / math.pi
            if color < 0:
                color = 0
            yield to_int(v1), to_int(v2), to_int(v3), color
