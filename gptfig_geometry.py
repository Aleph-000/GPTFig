"""Lightweight textbook-style geometry helpers for GPTFig."""

import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


EDGE = "#20242b"
HIDDEN = "#7b8491"
ACCENT = "#3976b7"
FACE = "#8db8df"


def _point(value, dimensions):
    point = np.asarray(value, dtype=float)
    if point.shape != (dimensions,):
        raise ValueError(f"Expected a {dimensions}D point, got {value!r}")
    return point


def _unit(vector):
    length = float(np.linalg.norm(vector))
    if length == 0:
        raise ValueError("Geometry points must be distinct")
    return vector / length


def midpoint(a, b):
    return (_point(a, 2) + _point(b, 2)) / 2


def distance(a, b):
    return float(np.linalg.norm(_point(a, 2) - _point(b, 2)))


def perpendicular_foot(p, a, b):
    p, a, b = _point(p, 2), _point(a, 2), _point(b, 2)
    direction = b - a
    denominator = float(direction @ direction)
    if denominator == 0:
        raise ValueError("A line needs two distinct points")
    return a + direction * float((p - a) @ direction) / denominator


def line_intersection(a, b, c, d):
    a, b, c, d = (_point(value, 2) for value in (a, b, c, d))
    first, second = b - a, d - c
    cross = first[0] * second[1] - first[1] * second[0]
    if abs(cross) < 1e-12:
        raise ValueError("Lines are parallel or coincident")
    delta = c - a
    t = (delta[0] * second[1] - delta[1] * second[0]) / cross
    return a + t * first


def centroid(a, b, c):
    return (_point(a, 2) + _point(b, 2) + _point(c, 2)) / 3


def circumcenter(a, b, c):
    a, b, c = (_point(value, 2) for value in (a, b, c))
    matrix = 2 * np.array([b - a, c - a])
    target = np.array([b @ b - a @ a, c @ c - a @ a])
    try:
        return np.linalg.solve(matrix, target)
    except np.linalg.LinAlgError as error:
        raise ValueError("Triangle points are collinear") from error


def incenter(a, b, c):
    a, b, c = (_point(value, 2) for value in (a, b, c))
    weights = np.array([np.linalg.norm(b - c), np.linalg.norm(c - a), np.linalg.norm(a - b)])
    if weights.sum() == 0:
        raise ValueError("Triangle points must be distinct")
    return (weights[0] * a + weights[1] * b + weights[2] * c) / weights.sum()


def orthocenter(a, b, c):
    a, b, c = (_point(value, 2) for value in (a, b, c))
    return a + b + c - 2 * circumcenter(a, b, c)


class Plane:
    """Draw consistent 2D geometry diagrams with named points."""

    def __init__(self, figsize=(6, 5), edge=EDGE):
        self.fig, self.ax = plt.subplots(figsize=figsize, layout="constrained")
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_facecolor("white")
        self.edge = edge
        self.points = {}
        self._bounds = []

    def _remember(self, *points):
        self._bounds.extend(_point(point, 2) for point in points)

    def resolve(self, value):
        if isinstance(value, str):
            if value not in self.points:
                raise KeyError(f"Unknown point {value!r}")
            return self.points[value]
        return _point(value, 2)

    def label(self, point, text, offset=(5, 5), **kwargs):
        point = self.resolve(point)
        return self.ax.annotate(
            text,
            point,
            xytext=offset,
            textcoords="offset points",
            ha=kwargs.pop("ha", "left"),
            va=kwargs.pop("va", "bottom"),
            fontsize=kwargs.pop("fontsize", 12),
            color=kwargs.pop("color", self.edge),
            **kwargs,
        )

    def point(self, name, xy, label=None, offset=(5, 5), color=None, size=24, **kwargs):
        xy = _point(xy, 2)
        self.points[str(name)] = xy
        self._remember(xy)
        artist = self.ax.scatter(*xy, s=size, color=color or self.edge, zorder=5, **kwargs)
        if label is not False:
            self.label(xy, str(name) if label is None else label, offset=offset)
        return artist

    def segment(self, a, b, label=None, label_offset=(0, 5), hidden=False, **kwargs):
        a, b = self.resolve(a), self.resolve(b)
        self._remember(a, b)
        artist, = self.ax.plot(
            [a[0], b[0]],
            [a[1], b[1]],
            color=kwargs.pop("color", HIDDEN if hidden else self.edge),
            linewidth=kwargs.pop("linewidth", 1.8),
            linestyle=kwargs.pop("linestyle", "--" if hidden else "-"),
            solid_capstyle="round",
            **kwargs,
        )
        if label:
            self.label((a + b) / 2, label, offset=label_offset, ha="center")
        return artist

    def auxiliary(self, a, b, **kwargs):
        kwargs.setdefault("color", HIDDEN)
        kwargs.setdefault("linestyle", "--")
        kwargs.setdefault("linewidth", 1.25)
        return self.segment(a, b, **kwargs)

    def polygon(self, *vertices, fill=False, facecolor=FACE, alpha=0.18, **kwargs):
        vertices = [self.resolve(vertex) for vertex in vertices]
        if len(vertices) < 3:
            raise ValueError("A polygon needs at least three vertices")
        self._remember(*vertices)
        patch = Polygon(
            vertices,
            closed=True,
            fill=fill,
            facecolor=facecolor if fill else "none",
            alpha=alpha if fill else 1,
            edgecolor=kwargs.pop("edgecolor", self.edge),
            linewidth=kwargs.pop("linewidth", 1.8),
            joinstyle="round",
            **kwargs,
        )
        self.ax.add_patch(patch)
        return patch

    def circle(self, center, radius, **kwargs):
        center = self.resolve(center)
        if radius <= 0:
            raise ValueError("Circle radius must be positive")
        fill = kwargs.pop("fill", False)
        self._remember(center - radius, center + radius)
        patch = Circle(
            center,
            radius,
            fill=fill,
            edgecolor=kwargs.pop("edgecolor", self.edge),
            facecolor=kwargs.pop("facecolor", FACE if fill else "none"),
            linewidth=kwargs.pop("linewidth", 1.8),
            **kwargs,
        )
        self.ax.add_patch(patch)
        return patch

    def arc(self, center, radius, theta1, theta2, **kwargs):
        center = self.resolve(center)
        if radius <= 0:
            raise ValueError("Arc radius must be positive")
        self._remember(center - radius, center + radius)
        patch = Arc(
            center,
            2 * radius,
            2 * radius,
            theta1=theta1,
            theta2=theta2,
            color=kwargs.pop("color", self.edge),
            linewidth=kwargs.pop("linewidth", 1.5),
            **kwargs,
        )
        self.ax.add_patch(patch)
        return patch

    def angle(self, a, vertex, c, label=None, radius=None, color=ACCENT, **kwargs):
        a, vertex, c = self.resolve(a), self.resolve(vertex), self.resolve(c)
        first, second = a - vertex, c - vertex
        _unit(first)
        _unit(second)
        radius = radius or 0.18 * min(np.linalg.norm(first), np.linalg.norm(second))
        start = math.degrees(math.atan2(first[1], first[0])) % 360
        end = math.degrees(math.atan2(second[1], second[0])) % 360
        sweep = (end - start) % 360
        if sweep > 180:
            start, end = end, start
            sweep = 360 - sweep
        patch = self.arc(vertex, radius, start, start + sweep, color=color, **kwargs)
        if label:
            middle = math.radians(start + sweep / 2)
            position = vertex + 1.35 * radius * np.array([math.cos(middle), math.sin(middle)])
            self.ax.text(*position, label, ha="center", va="center", fontsize=11, color=color)
        return patch

    def right_angle(self, a, vertex, c, size=None, color=ACCENT, **kwargs):
        a, vertex, c = self.resolve(a), self.resolve(vertex), self.resolve(c)
        first, second = a - vertex, c - vertex
        size = size or 0.14 * min(np.linalg.norm(first), np.linalg.norm(second))
        first, second = _unit(first), _unit(second)
        points = np.array([vertex + first * size, vertex + (first + second) * size, vertex + second * size])
        self._remember(*points)
        artist, = self.ax.plot(
            points[:, 0],
            points[:, 1],
            color=color,
            linewidth=kwargs.pop("linewidth", 1.4),
            **kwargs,
        )
        return artist

    def equal_marks(self, a, b, count=1, size=None, spacing=None, color=ACCENT, **kwargs):
        a, b = self.resolve(a), self.resolve(b)
        direction = _unit(b - a)
        normal = np.array([-direction[1], direction[0]])
        length = np.linalg.norm(b - a)
        size = size or 0.08 * length
        spacing = spacing or 0.07 * length
        artists = []
        for index in range(count):
            center = (a + b) / 2 + direction * (index - (count - 1) / 2) * spacing
            ends = np.array([center - normal * size / 2, center + normal * size / 2])
            artist, = self.ax.plot(ends[:, 0], ends[:, 1], color=color, linewidth=1.4, **kwargs)
            artists.append(artist)
        return artists

    def parallel_marks(self, a, b, count=1, size=None, spacing=None, color=ACCENT, **kwargs):
        a, b = self.resolve(a), self.resolve(b)
        direction = _unit(b - a)
        normal = np.array([-direction[1], direction[0]])
        length = np.linalg.norm(b - a)
        size = size or 0.11 * length
        spacing = spacing or 0.10 * length
        artists = []
        for index in range(count):
            center = (a + b) / 2 + direction * (index - (count - 1) / 2) * spacing
            tip = center + direction * size / 2
            wings = np.array([center - direction * size / 2 + normal * size / 3, tip,
                              center - direction * size / 2 - normal * size / 3])
            artist, = self.ax.plot(wings[:, 0], wings[:, 1], color=color, linewidth=1.4, **kwargs)
            artists.append(artist)
        return artists

    def finish(self, padding=0.12, axis=False):
        if self._bounds:
            points = np.array(self._bounds)
            low, high = points.min(axis=0), points.max(axis=0)
            scale = max(float(np.max(high - low)), 1.0)
            pad = scale * padding
            self.ax.set_xlim(low[0] - pad, high[0] + pad)
            self.ax.set_ylim(low[1] - pad, high[1] + pad)
        self.ax.set_aspect("equal", adjustable="box")
        if not axis:
            self.ax.axis("off")
        return self.fig, self.ax


class Space:
    """Draw textbook-style 3D solids with explicit hidden edges."""

    def __init__(self, figsize=(7, 6), elev=22, azim=-48, projection="ortho"):
        self.fig = plt.figure(figsize=figsize, layout="constrained")
        self.ax = self.fig.add_subplot(111, projection="3d", proj_type=projection)
        self.ax.view_init(elev=elev, azim=azim)
        self.points = {}
        self._bounds = []

    def _remember(self, *points):
        self._bounds.extend(_point(point, 3) for point in points)

    def resolve(self, value):
        if isinstance(value, str):
            if value not in self.points:
                raise KeyError(f"Unknown point {value!r}")
            return self.points[value]
        return _point(value, 3)

    def label(self, point, text, offset=(0.04, 0.04, 0.04), **kwargs):
        point = self.resolve(point) + _point(offset, 3)
        return self.ax.text(*point, text, fontsize=kwargs.pop("fontsize", 11), color=kwargs.pop("color", EDGE), **kwargs)

    def point(self, name, xyz, label=None, offset=(0.04, 0.04, 0.04), color=EDGE, size=16, **kwargs):
        xyz = _point(xyz, 3)
        self.points[str(name)] = xyz
        self._remember(xyz)
        artist = self.ax.scatter(*xyz, s=size, color=color, depthshade=False, **kwargs)
        if label is not False:
            self.label(xyz, str(name) if label is None else label, offset=offset)
        return artist

    def segment(self, a, b, hidden=False, **kwargs):
        a, b = self.resolve(a), self.resolve(b)
        self._remember(a, b)
        artist, = self.ax.plot(
            [a[0], b[0]], [a[1], b[1]], [a[2], b[2]],
            color=kwargs.pop("color", HIDDEN if hidden else EDGE),
            linewidth=kwargs.pop("linewidth", 1.6),
            linestyle=kwargs.pop("linestyle", "--" if hidden else "-"),
            **kwargs,
        )
        return artist

    def face(self, *vertices, color=FACE, alpha=0.16, **kwargs):
        vertices = [self.resolve(vertex) for vertex in vertices]
        self._remember(*vertices)
        patch = Poly3DCollection(
            [vertices],
            facecolor=color,
            edgecolor=kwargs.pop("edgecolor", "none"),
            alpha=alpha,
            shade=kwargs.pop("shade", False),
            **kwargs,
        )
        self.ax.add_collection3d(patch)
        return patch

    def polyhedron(self, vertices, faces, hidden_edges=(), labels=True, facecolor=FACE, alpha=0.16):
        for name, coordinates in vertices.items():
            self.point(name, coordinates, label=name if labels else False)
        hidden = {tuple(sorted(edge)) for edge in hidden_edges}
        edges = set()
        for face in faces:
            self.face(*face, color=facecolor, alpha=alpha)
            for index, start in enumerate(face):
                edges.add(tuple(sorted((start, face[(index + 1) % len(face)]))))
        for edge in sorted(edges):
            self.segment(*edge, hidden=edge in hidden)
        return vertices

    def box(self, origin=(0, 0, 0), size=(3, 2, 2), labels=("A", "B", "C", "D", "A₁", "B₁", "C₁", "D₁"), hidden_edges=()):
        x, y, z = _point(origin, 3)
        width, depth, height = _point(size, 3)
        coordinates = [
            (x, y, z), (x + width, y, z), (x + width, y + depth, z), (x, y + depth, z),
            (x, y, z + height), (x + width, y, z + height),
            (x + width, y + depth, z + height), (x, y + depth, z + height),
        ]
        vertices = dict(zip(labels, coordinates))
        faces = [labels[:4], labels[4:], (labels[0], labels[1], labels[5], labels[4]),
                 (labels[1], labels[2], labels[6], labels[5]),
                 (labels[2], labels[3], labels[7], labels[6]),
                 (labels[3], labels[0], labels[4], labels[7])]
        return self.polyhedron(vertices, faces, hidden_edges=hidden_edges)

    def pyramid(self, base, apex, labels=None, hidden_edges=()):
        labels = labels or tuple(chr(65 + index) for index in range(len(base))) + ("S",)
        if len(labels) != len(base) + 1:
            raise ValueError("Pyramid labels must name every base point and the apex")
        vertices = {name: point for name, point in zip(labels[:-1], base)}
        vertices[labels[-1]] = apex
        faces = [tuple(labels[:-1])]
        for index, name in enumerate(labels[:-1]):
            faces.append((name, labels[:-1][(index + 1) % (len(labels) - 1)], labels[-1]))
        return self.polyhedron(vertices, faces, hidden_edges=hidden_edges)

    def section(self, *vertices, color="#f0a44b", alpha=0.34, **kwargs):
        return self.face(*vertices, color=color, alpha=alpha, **kwargs)

    def sphere(self, center=(0, 0, 0), radius=1, resolution=32, color=FACE, alpha=0.28):
        center = _point(center, 3)
        if radius <= 0:
            raise ValueError("Sphere radius must be positive")
        u = np.linspace(0, 2 * np.pi, resolution)
        v = np.linspace(0, np.pi, max(12, resolution // 2))
        x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
        y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
        z = center[2] + radius * np.outer(np.ones_like(u), np.cos(v))
        self._remember(center - radius, center + radius)
        return self.ax.plot_surface(x, y, z, color=color, alpha=alpha, linewidth=0, shade=True)

    def cylinder(self, center=(0, 0, 0), radius=1, height=2, resolution=48, color=FACE, alpha=0.25):
        center = _point(center, 3)
        if radius <= 0 or height <= 0:
            raise ValueError("Cylinder radius and height must be positive")
        theta = np.linspace(0, 2 * np.pi, resolution)
        z = np.array([center[2], center[2] + height])
        theta, z = np.meshgrid(theta, z)
        x = center[0] + radius * np.cos(theta)
        y = center[1] + radius * np.sin(theta)
        surface = self.ax.plot_surface(x, y, z, color=color, alpha=alpha, linewidth=0, shade=True)
        angles = np.linspace(0, 2 * np.pi, resolution)
        for level in (center[2], center[2] + height):
            self.ax.plot(center[0] + radius * np.cos(angles), center[1] + radius * np.sin(angles), level,
                         color=EDGE, linewidth=1.2)
        self._remember(center + (-radius, -radius, 0), center + (radius, radius, height))
        return surface

    def cone(self, center=(0, 0, 0), radius=1, height=2, resolution=48, color=FACE, alpha=0.25):
        center = _point(center, 3)
        if radius <= 0 or height <= 0:
            raise ValueError("Cone radius and height must be positive")
        theta = np.linspace(0, 2 * np.pi, resolution)
        levels = np.linspace(0, height, max(12, resolution // 2))
        theta, levels = np.meshgrid(theta, levels)
        radii = radius * (1 - levels / height)
        x = center[0] + radii * np.cos(theta)
        y = center[1] + radii * np.sin(theta)
        z = center[2] + levels
        surface = self.ax.plot_surface(x, y, z, color=color, alpha=alpha, linewidth=0, shade=True)
        angles = np.linspace(0, 2 * np.pi, resolution)
        self.ax.plot(center[0] + radius * np.cos(angles), center[1] + radius * np.sin(angles), center[2],
                     color=EDGE, linewidth=1.2)
        self._remember(center + (-radius, -radius, 0), center + (radius, radius, height))
        return surface

    def finish(self, padding=0.08, axis=False):
        if self._bounds:
            points = np.array(self._bounds)
            low, high = points.min(axis=0), points.max(axis=0)
            scale = max(float(np.max(high - low)), 1.0)
            pad = scale * padding
            low, high = low - pad, high + pad
            self.ax.set_xlim(low[0], high[0])
            self.ax.set_ylim(low[1], high[1])
            self.ax.set_zlim(low[2], high[2])
            self.ax.set_box_aspect(high - low, zoom=1.05)
        if not axis:
            self.ax.set_axis_off()
        return self.fig, self.ax


__all__ = [
    "Plane", "Space", "midpoint", "distance", "perpendicular_foot",
    "line_intersection", "centroid", "circumcenter", "incenter", "orthocenter",
]
