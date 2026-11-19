"""Blender 4.3: blender -b --python-exit-code 1 --python scripts/build_character.py"""

import bpy
import math
from math import sin, cos, pi, sqrt
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "models"
VIEWS = ROOT / "renders"
for folder in (OUT, VIEWS):
    folder.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.cycles.max_bounces = 4
scene.cycles.use_denoising = False
scene.view_settings.view_transform = "AgX"
scene.render.resolution_x = 680
scene.render.resolution_y = 880
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world = bpy.data.worlds.new("Softbox ambient")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.54, 0.60, 0.72, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.65
current = None


def group(name):
    global current
    current = bpy.data.collections.new(name)
    scene.collection.children.link(current)


def material(name, rgb, rough=0.45, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    for key, val in [("Base Color", (*rgb, 1)), ("Metallic", metallic), ("Roughness", rough)]:
        bs.inputs[key].default_value = val
    return m


skin = material("Porcelain • warm", (0.98, 0.695, 0.61), 0.75)
ink = material("Lashes • charcoal", (0.012, 0.006, 0.013))
lip = material("Rose • lip", (0.42, 0.088, 0.105))
pearl = material("Ivory • parade silk", (0.91, 0.89, 0.90), 0.33)
white = material("Catchlight", (1, 0.97, 0.90))
black = material("Onyx • patent", (0.016, 0.018, 0.029), 0.24, 0.25)
cloth = material("Officer wool", (0.021, 0.022, 0.034), 0.61)
hair = material("Graphite hair", (0.045, 0.044, 0.061), 0.34)
silver = material("Silver-grey hair", (0.134, 0.142, 0.173), 0.35)
wine = material("Velvet • oxblood", (0.23, 0.008, 0.032), 0.52)
red = material("Carmine satin", (0.59, 0.013, 0.046), 0.32)
ruby = material("Ruby iris", (0.47, 0.012, 0.025), 0.24)
gold = material("Champagne brass", (0.74, 0.49, 0.20), 0.30, 0.73)
lightgold = material("Polished edges", (0.94, 0.72, 0.35), 0.24, 0.65)
meshmat = material("Smoke • hosiery", (0.33, 0.242, 0.24), 0.65)
blue = material("Ribbon • midnight blue", (0.02, 0.046, 0.15))
steel = material("Gunmetal", (0.16, 0.17, 0.19), 0.24, 0.72)


def attach(o, name, mat):
    o.name = name
    for c in list(o.users_collection):
        c.objects.unlink(o)
    current.objects.link(o)
    o.data.materials.append(mat)
    return o


def mesh(name, vs, fs, mat, sub=0):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vs, [], fs)
    data.update()
    o = bpy.data.objects.new(name, data)
    current.objects.link(o)
    data.materials.append(mat)
    for p in data.polygons:
        p.use_smooth = True
    if sub:
        mod = o.modifiers.new("Rounded seams", "SUBSURF")
        mod.levels = sub
        mod.render_levels = sub
    return o


def oval(name, loc, scale, mat, tilt=0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=9, location=loc)
    o = attach(bpy.context.object, name, mat)
    o.scale = scale
    o.rotation_euler.y = tilt
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def loft(name, rows, mat, n=18, sub=1, slope=0):
    # Each horizontal ring encodes centre x, y, height and two radii.
    vs = [
        (x + a * cos(2 * pi * j / n), y + b * sin(2 * pi * j / n), z + slope * a * cos(2 * pi * j / n))
        for x, y, z, a, b in rows
        for j in range(n)
    ]
    fs = [tuple(reversed(range(n)))]
    for i in range(len(rows) - 1):
        for j in range(n):
            k = i * n + j
            l = i * n + (j + 1) % n
            fs.append((k, l, l + n, k + n))
    fs.append(tuple(range(len(vs) - n, len(vs))))
    if rows[0][2] > rows[-1][2]:
        fs = [face[::-1] for face in fs]
    return mesh(name, vs, fs, mat, sub)


def cord(name, pts, r, mat):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 4
    data.bevel_depth = r
    data.bevel_resolution = 1
    data.use_fill_caps = True
    sp = data.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, data)
    current.objects.link(o)
    data.materials.append(mat)
    return o


def badge(name, x, y, z, w, h, mat):
    return mesh(
        name,
        [(x - w, y, z), (x, y, z - h), (x + w, y, z), (x, y, z + h), (x, y - 0.055, z)],
        [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)],
        mat,
    )


def centered(name, profile, mat, **kw):
    return loft(name, [(0, y, z, a, b) for z, a, b, y in profile], mat, **kw)


group("01 • Face and eyes")
face = centered(
    "Face | jaw to crown",
    [
        (6.23, 0.06, 0.07, -0.13),
        (6.32, 0.22, 0.20, -0.09),
        (6.50, 0.385, 0.315, -0.045),
        (6.75, 0.475, 0.387, 0.0),
        (7.02, 0.50, 0.41, 0.015),
        (7.26, 0.46, 0.385, 0.018),
        (7.44, 0.32, 0.29, 0.02),
        (7.52, 0.10, 0.12, 0.02),
    ],
    skin,
    n=48,
    sub=2,
)
centered("Neck", [(5.94, 0.20, 0.20, 0), (6.12, 0.158, 0.163, 0), (6.48, 0.18, 0.17, 0)], skin)
centered("Choker", [(6.135, 0.17, 0.174, 0), (6.15, 0.175, 0.18, 0), (6.205, 0.17, 0.175, 0)], black)
# Sculpt the bridge, tip and cheekbones into the subdivided head surface.
bpy.context.view_layer.objects.active = face
bpy.ops.object.modifier_apply(modifier=face.modifiers[0].name)


def bump(value, width):
    return math.exp(-((value / width) ** 2))


for vertex in face.data.vertices:
    x, y, z = vertex.co
    if y < -0.22:
        bridge = 0.060 * bump(x, 0.055) * bump(z - 6.73, 0.16)
        tip = 0.065 * bump(x, 0.064) * bump(z - 6.625, 0.05)
        cheek = 0.018 * bump(abs(x) - 0.25, 0.14) * bump(z - 6.64, 0.13)
        vertex.co.y -= bridge + tip + cheek
cord(
    "Mouth • rose bow",
    [
        (-0.093, -0.322, 6.478),
        (-0.025, -0.344, 6.483),
        (0, -0.347, 6.477),
        (0.029, -0.342, 6.483),
        (0.088, -0.324, 6.489),
    ],
    0.009,
    lip,
)
for s in (-1, 1):
    oval("Ear", (s * 0.447, 0.004, 6.72), (0.077, 0.065, 0.145), skin)

    # Convex almond with outer corner receding around the cheek.
    def eyept(u, v):
        return (s * (0.209 + 0.157 * u), -0.389 + 0.088 * u + 0.014 * u * u, 6.853 + 0.043 * u + v)

    vs = [eyept(0, 0)]
    for j in range(32):
        t = 2 * pi * j / 32
        vs.append(eyept(cos(t), sin(t) * (0.062 if sin(t) > 0 else 0.046)))
    vs[0] = (vs[0][0], vs[0][1] - 0.023, vs[0][2])
    mesh("Eyes • almond", vs, [(0, 1 + j, 1 + (j + 1) % 32) for j in range(32)], pearl)

    # Conform the iris to the convex eye; the upper lid clips its edge.
    # Nested elliptical discs share a gaze direction and stay below the lash.
    def eye_disc(name, uc, vc, ru, rv, offset, mat):
        def surface(u, v):
            radius = sqrt(u * u + (v / (0.062 if v >= 0 else 0.046)) ** 2)
            x, y, z = eyept(u, v)
            return (x, y - 0.024 * max(0, 1 - radius) - offset, z)

        points = [surface(uc, vc)]
        for i in range(40):
            t = 2 * pi * i / 40
            u = uc + ru * cos(t)
            limit = sqrt(max(0, 1 - u * u))
            v = min(0.060 * limit, max(-0.045 * limit, vc + rv * sin(t)))
            points.append(surface(u, v))
        faces = [(0, i + 1, 1 + (i + 1) % 40) for i in range(40)]
        return mesh(name, points, faces if s > 0 else [f[::-1] for f in faces], mat)

    eye_disc("Eyes • limbal rim", -0.14, 0.017, 0.49, 0.069, 0.006, wine)
    eye_disc("Eyes • garnet iris", -0.14, 0.011, 0.44, 0.060, 0.009, ruby)
    eye_disc("Eyes • pupil", -0.14, 0.020, 0.17, 0.041, 0.013, ink)
    eye_disc("Eyes • catchlight", -0.14 - 0.12 * s, 0.039, 0.08, 0.010, 0.017, white)
    for label, sign, r in [("Upper lash", 1, 0.019), ("Lower line", -1, 0.007)]:
        pts = [
            eyept(cos(t * pi / 8), sign * sin(t * pi / 8) * (0.062 if sign == 1 else 0.046)) for t in range(9)
        ]
        cord(label, pts, r, ink)
    cord("Winged lash", [eyept(0.74, 0.055), eyept(1, 0.009), eyept(1.20, 0.037)], 0.014, ink)
    cord("Brow", [eyept(-0.85, 0.135), eyept(0.16, 0.151), eyept(0.83, 0.114)], 0.019, hair)

group("02 • Hair and bows")
# Crown overlaps the brow only at the sides. Fringe is built strand by strand.
oval("UNVERIFIED_Hair • occipital mass", (0, 0.17, 6.96), (0.508, 0.38, 0.56), hair)


def lock(name, rows, mat):
    return loft(name, rows, mat, n=12, sub=1)


for s in (-1, 1):
    for j in range(5):
        u = j / 4
        rows = [
            (s * 0.40, 0.16 + u * 0.09, 7.19, 0.15, 0.14),
            (s * (0.51 + 0.11 * u), 0.20 + 0.08 * u, 6.78, 0.19, 0.12),
            (s * (0.70 + 0.17 * u), 0.28 + 0.15 * u, 5.98, 0.19 - 0.035 * u, 0.10),
            (s * (0.78 + 0.27 * u), 0.35 + 0.24 * u, 5.04, 0.17, 0.09),
            (s * (0.71 + 0.37 * u), 0.30 + 0.27 * u, 4.02, 0.15, 0.08),
            (s * (0.65 + 0.48 * u), 0.12 + 0.37 * u, 3.32 + 0.32 * u, 0.13, 0.06),
            (s * (0.91 + 0.37 * u), -0.04 + 0.32 * u, 3.11 + 0.42 * u, 0.017, 0.012),
        ]
        lock("Hair • long tapered layer", rows, [wine, hair, silver, hair, hair][j])
    # Foreground tresses turn across the red underlayer; tapered tips flick outward.
    for j in range(3):
        u = j / 2
        lock(
            "Hair • outer swept ribbon",
            [
                (s * (0.46 + 0.035 * u), 0.03, 7.12, 0.11, 0.072),
                (s * (0.55 + 0.08 * u), 0.028, 6.76, 0.122, 0.073),
                (s * (0.72 + 0.13 * u), 0.083, 6.10, 0.135, 0.073),
                (s * (0.87 + 0.14 * u), 0.097, 5.41, 0.125, 0.065),
                (s * (0.94 + 0.15 * u), 0.11, 4.83, 0.105, 0.055),
                (s * (0.96 + 0.13 * u), 0.07, 4.18, 0.094, 0.053),
                (s * (0.89 + 0.13 * u), -0.018, 3.75, 0.10, 0.050),
                (s * (0.94 + 0.16 * u), -0.115, 3.49 + 0.06 * u, 0.065, 0.038),
                (s * (1.10 + 0.16 * u), -0.146, 3.57 + 0.10 * u, 0.006, 0.009),
            ],
            [hair, silver, hair][j],
        )
    for j in range(3):
        u = j / 2
        lock(
            "Hair • cheek curl",
            [
                (s * (0.37 + 0.09 * u), -0.16, 7.31, 0.142, 0.104),
                (s * (0.44 + 0.07 * u), -0.20, 7.04, 0.13, 0.10),
                (s * (0.43 + 0.09 * u), -0.24, 6.76, 0.105, 0.085),
                (s * (0.40 + 0.09 * u), -0.26, 6.52, 0.087, 0.058),
                (s * (0.29 + 0.09 * u), -0.30, 6.40 - 0.04 * u, 0.05, 0.04),
                (s * (0.24 + 0.07 * u), -0.35, 6.45 - 0.09 * u, 0.008, 0.008),
            ],
            [wine, hair, silver][j],
        )
    for j in range(2):
        # Folded ribbon loops taper into the temple knot.
        z = 7.11
        coords = [
            (0.45, -0.09, z),
            (0.58, -0.075, z + 0.18),
            (0.72, -0.015, z + 0.20),
            (0.68, -0.06, z + 0.065),
            (0.61, -0.132, z + 0.045),
            (0.54, -0.093, z + 0.020),
        ]
        coords = [(s * x, y, zz if j else 2 * z - zz) for x, y, zz in coords]
        bow = mesh(
            "Bows • folded taffeta", coords, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 5, 4), (5, 0, 4)], red
        )
        lining = bow.modifiers.new("Fold thickness", "SOLIDIFY")
        lining.thickness = 0.024
        cord(
            "Bows • fold",
            [
                (s * 0.48, -0.105, 7.11),
                (s * 0.55, -0.108, 7.10 + 0.09 * j),
                (s * 0.62, -0.066, 7.05 + 0.18 * j),
            ],
            0.012,
            wine,
        )
    oval("Bows • knot", (s * 0.49, -0.094, 7.12), (0.083, 0.07, 0.09), wine)
    lock(
        "Bows • streamer",
        [
            (s * 0.50, 0.01, 7.11, 0.09, 0.06),
            (s * 0.61, 0.08, 6.95, 0.098, 0.039),
            (s * 0.65, 0.11, 6.70, 0.085, 0.027),
            (s * 0.70, 0.10, 6.57, 0.013, 0.018),
        ],
        red,
    )
for j, (base, tip, height) in enumerate(
    [
        (-0.31, -0.36, 6.84),
        (-0.21, -0.29, 6.78),
        (-0.09, -0.19, 6.89),
        (0.055, -0.073, 6.73),
        (0.19, 0.02, 6.84),
        (0.32, 0.18, 6.96),
        (0.40, 0.31, 6.99),
    ]
):
    lock(
        "Hair • swept fringe",
        [
            (base + 0.05, -0.19, 7.41, 0.122, 0.081),
            (base + 0.045, -0.31, 7.24, 0.145, 0.092),
            (base, -0.364 + 0.07 * abs(base), 7.095, 0.115, 0.076),
            (tip + 0.045, -0.406 + 0.16 * abs(tip), height + 0.10, 0.081, 0.049),
            (tip, -0.413 + 0.20 * abs(tip), height, 0.008, 0.01),
        ],
        silver if j in (0, 5) else hair,
    )

group("03 • Shako")
slope = 0.33
centered(
    "Cap • angled crown",
    [
        (7.16, 0.505, 0.406, 0.02),
        (7.20, 0.533, 0.442, 0.01),
        (7.49, 0.505, 0.412, 0.05),
        (7.70, 0.461, 0.37, 0.08),
        (7.73, 0.43, 0.34, 0.08),
    ],
    cloth,
    slope=slope,
)
centered(
    "Cap • patent visor",
    [
        (7.12, 0.47, 0.44, -0.08),
        (7.15, 0.552, 0.515, -0.083),
        (7.20, 0.535, 0.454, -0.04),
        (7.235, 0.51, 0.409, 0),
    ],
    black,
    slope=slope,
)


def front_arc(rad, depth, z, y=0):
    return [
        (rad * sin(t * pi / 16), y - depth * cos(t * pi / 16), z + slope * rad * sin(t * pi / 16))
        for t in range(-7, 8)
    ]


cord("Cap • visor piping", front_arc(0.525, 0.493, 7.187, -0.056), 0.012, gold)


def grillpoint(u, h):
    x = 0.46 * u
    return (x, 0.025 + 0.21 * h - 0.447 * sqrt(1 - (x / 0.55) ** 2), 7.23 + slope * x + h)


for u in [-0.90, -0.68, -0.43, -0.17, 0.10, 0.37, 0.64, 0.9]:
    cord(
        "Cap • fluted grille",
        [grillpoint(u, 0), grillpoint(u - 0.10, 0.44 * (1 - abs(u) * 0.67))],
        0.016,
        gold,
    )
cord(
    "Cap • heraldic arch",
    [grillpoint(u, 0.45 * (1 - abs(u) * 0.68)) for u in [-1, -0.72, -0.40, 0, 0.43, 0.74, 1]],
    0.026,
    lightgold,
)
cord("Cap • grille sill", [grillpoint(u, 0) for u in [-1, -0.7, -0.3, 0, 0.3, 0.7, 1]], 0.021, gold)
badge("Cap • crest", 0, -0.334, 7.70, 0.063, 0.09, gold)

group("04 • Jacket, shoulder and medals")
centered(
    "Jacket • fitted ivory tunic",
    [
        (4.15, 0.49, 0.327, -0.015),
        (4.19, 0.55, 0.35, 0),
        (4.48, 0.51, 0.338, 0),
        (4.74, 0.394, 0.279, 0),
        (4.98, 0.408, 0.29, 0),
        (5.29, 0.492, 0.345, -0.014),
        (5.54, 0.586, 0.393, -0.044),
        (5.72, 0.605, 0.37, -0.015),
        (5.94, 0.644, 0.284, 0.0),
        (6.015, 0.535, 0.236, 0),
        (6.07, 0.245, 0.18, 0),
    ],
    pearl,
    n=32,
    sub=1,
)
# Lower the top edge of the jacket at centre front and fit the skin beneath it.
jacket = bpy.data.objects["Jacket • fitted ivory tunic"]
for v in jacket.data.vertices:
    if v.co.z > 5.73 and v.co.y < 0:
        opening = max(0, 1 - abs(v.co.x) / 0.41) * min(1, -v.co.y / 0.125)
        v.co.z -= (v.co.z - 5.70) * opening * 0.92
centered(
    "Face • upper chest",
    [
        (5.65, 0.41, 0.27, -0.015),
        (5.77, 0.54, 0.315, -0.015),
        (5.90, 0.55, 0.238, 0),
        (5.99, 0.465, 0.19, 0),
        (6.075, 0.18, 0.15, 0),
    ],
    skin,
    n=32,
)
for side in (-1, 1):
    vertices = [
        (side * 0.16, -0.137, 6.04),
        (side * 0.30, -0.087, 6.21),
        (side * 0.54, -0.086, 6.10),
        (side * 0.47, -0.236, 5.96),
        (side * 0.25, -0.247, 5.96),
    ]
    collar = mesh("Jacket • standing collar", vertices, [(0, 1, 4), (1, 2, 3), (1, 3, 4)], wine)
    collar.modifiers.new("Turned edge", "SOLIDIFY").thickness = 0.025
for s in (-1, 1):
    lock(
        "Jacket • black side gore",
        [
            (s * 0.466, 0, 4.30, 0.064, 0.22),
            (s * 0.457, 0, 4.47, 0.091, 0.255),
            (s * 0.349, 0, 4.77, 0.071, 0.211),
            (s * 0.386, 0.0, 5.10, 0.07, 0.215),
            (s * 0.49, 0.0, 5.42, 0.11, 0.274),
            (s * 0.529, 0, 5.64, 0.12, 0.262),
            (s * 0.49, 0, 5.84, 0.103, 0.204),
        ],
        black,
    )
    cord(
        "Jacket • braided panel edge",
        [
            (s * 0.38, -0.218, 4.35),
            (s * 0.292, -0.207, 4.78),
            (s * 0.36, -0.251, 5.20),
            (s * 0.474, -0.298, 5.58),
        ],
        0.014,
        gold,
    )
    for z, x, y in [(4.97, 0.224, -0.239), (5.27, 0.276, -0.306), (5.55, 0.32, -0.377)]:
        oval("Jacket • brass button", (s * x, y - 0.015, z), (0.044, 0.025, 0.048), gold)
        oval("Button • inset", (s * x, y - 0.037, z), (0.020, 0.009, 0.024), lightgold)
    # Military lapel folded from the neckline across the upper chest.
    pts = [
        (s * 0.20, -0.15, 6.04),
        (s * 0.51, -0.21, 5.96),
        (s * 0.41, -0.333, 5.80),
        (s * 0.06, -0.409, 5.60),
        (s * 0.285, -0.327, 5.85),
    ]
    mesh("Jacket • folded lapel", pts, [(0, 1, 4), (1, 2, 4), (2, 3, 4)], cloth if s < 0 else pearl)
    cord("Lapel • piping", pts[1:4], 0.014, steel)
centered(
    "Belt • leather waist",
    [(4.61, 0.466, 0.326, 0), (4.63, 0.474, 0.338, 0), (4.76, 0.439, 0.323, 0), (4.79, 0.424, 0.307, 0)],
    black,
)
for s in (-1, 1):
    badge("Belt • split gilt clasp", s * 0.084, -0.334, 4.704, 0.077, 0.104, gold)
for j, m in enumerate([gold, blue, red]):
    oval("Medals • ribbon bar", (0.348 + 0.058 * j, -0.312 + 0.027 * j, 5.796), (0.034, 0.025, 0.036), m)
oval("Medals • suspended disc", (0.420, -0.321, 5.68), (0.070, 0.022, 0.076), gold)
badge("Medals • relief", 0.42, -0.347, 5.68, 0.039, 0.053, lightgold)
for i, m in enumerate([red, pearl, blue]):
    cord(
        "Medals • hanging sash",
        [
            (0.433 + 0.012 * i, -0.30, 5.62),
            (0.60 + 0.012 * i, -0.25, 5.27),
            (0.635 + 0.012 * i, -0.20, 4.96),
            (0.48 + 0.012 * i, -0.235, 4.67),
        ],
        0.014,
        m,
    )

group("05 • Arms and gauntlets")
for s in (-1, 1):

    def limb(name, rows, mat):
        return loft(name, [(s * x, y, z, a, b) for x, y, z, a, b in rows], mat)

    limb(
        "Sleeve • tailored",
        [
            (0.99, -0.02, 5.00, 0.136, 0.133),
            (0.99, -0.02, 5.045, 0.166, 0.145),
            (0.88, 0, 5.43, 0.152, 0.166),
            (0.73, 0, 5.81, 0.219, 0.223),
            (0.617, 0, 5.94, 0.208, 0.216),
            (0.57, 0.02, 5.97, 0.11, 0.14),
        ],
        pearl,
    )
    limb(
        "Shoulder • epaulette",
        [
            (0.70, 0, 5.69, 0.229, 0.211),
            (0.706, 0, 5.76, 0.253, 0.25),
            (0.645, 0, 5.94, 0.237, 0.24),
            (0.60, 0.01, 6.0, 0.16, 0.169),
        ],
        black,
    )
    if s == -1:
        for i in range(9):
            t = pi * (i + 1) / 11
            x = 0.70 + 0.225 * cos(t)
            y = -0.225 * sin(t)
            cord(
                "Shoulder • bullion fringe",
                [
                    (s * x, y, 5.80),
                    (s * (x + 0.055), y - 0.025, 5.60),
                    (s * (x + 0.10), y - 0.015, 5.49 + 0.05 * cos(t)),
                ],
                0.017,
                gold,
            )
    limb(
        "Gauntlet • articulated bracer",
        [
            (1.244, -0.09, 4.33, 0.10, 0.105),
            (1.22, -0.084, 4.43, 0.12, 0.13),
            (1.11, -0.055, 4.74, 0.157, 0.15),
            (1.035, -0.034, 4.96, 0.137, 0.139),
            (1.013, -0.028, 5.055, 0.147, 0.142),
        ],
        black,
    )
    for z, x in [(4.36, 1.239), (4.45, 1.212), (4.87, 1.063)]:
        limb(
            "Gauntlet • binding",
            [(x, -0.073, z, 0.135, 0.144), (x - 0.011, -0.073, z + 0.042, 0.139, 0.145)],
            gold if z != 4.45 else red,
        )
    oval("Glove • palm", (s * 1.266, -0.107, 4.21), (0.12, 0.099, 0.177), black, -s * 0.20)
    for j in range(4):
        x = 1.19 + j * 0.051
        h = 0.14 - 0.022 * abs(j - 1)
        oval("Glove • separated digit", (s * x, -0.12, 4.07 + 0.012 * j), (0.029, 0.047, h), black, -s * 0.14)
        oval(
            "Glove • gilt fingertip",
            (s * (x + 0.013), -0.157, 4.04 - h * 0.45 + 0.012 * j),
            (0.023, 0.023, 0.047),
            gold,
            -s * 0.14,
        )
    oval("Glove • thumb", (s * 1.17, -0.177, 4.19), (0.049, 0.053, 0.107), black, s * 0.34)

group("06 • Shorts, stockings and boots")
centered(
    "Shorts • high hip",
    [
        (4.05, 0.468, 0.315, 0.016),
        (4.17, 0.557, 0.354, 0.016),
        (4.42, 0.535, 0.34, 0),
        (4.48, 0.494, 0.31, 0),
    ],
    black,
)
for s in (-1, 1):

    def leg(name, rows, mat):
        return loft(name, [(s * x, y, z, a, b) for x, y, z, a, b in rows], mat, n=22)

    leg(
        "Shorts • tailored leg",
        [
            (0.294, 0, 3.86, 0.276, 0.298),
            (0.290, 0, 3.89, 0.29, 0.31),
            (0.279, 0.0, 4.15, 0.311, 0.359),
            (0.25, 0, 4.40, 0.277, 0.31),
        ],
        black,
    )
    cord(
        "Shorts • carmine welt",
        [
            (s * 0.24, -0.291, 3.90),
            (s * 0.39, -0.302, 4.056),
            (s * 0.53, -0.219, 4.23),
            (s * 0.535, -0.13, 4.34),
        ],
        0.026,
        wine,
    )
    badge("Shorts • strap slider", s * 0.496, -0.236, 4.215, 0.057, 0.084, gold)
    leg(
        "Stockings • thigh",
        [
            (0.335, 0.01, 2.84, 0.19, 0.191),
            (0.334, 0.012, 3.10, 0.237, 0.241),
            (0.319, 0, 3.52, 0.261, 0.277),
            (0.29, 0.0, 3.98, 0.28, 0.30),
        ],
        meshmat,
    )
    leg(
        "Boots • tall fitted shaft",
        [
            (0.38, 0.035, 0.28, 0.146, 0.162),
            (0.372, 0.038, 0.56, 0.131, 0.147),
            (0.371, 0.045, 0.95, 0.148, 0.171),
            (0.372, 0.055, 1.46, 0.191, 0.218),
            (0.352, 0.06, 1.92, 0.229, 0.254),
            (0.337, 0.053, 2.30, 0.196, 0.206),
            (0.335, 0.021, 2.59, 0.203, 0.207),
            (0.333, 0.01, 2.96, 0.224, 0.232),
            (0.332, 0, 3.25, 0.247, 0.259),
        ],
        black,
    )
    leg(
        "Boots • flared cuff",
        [
            (0.333, 0.01, 2.96, 0.222, 0.235),
            (0.333, 0.01, 3.01, 0.248, 0.252),
            (0.331, 0, 3.22, 0.254, 0.272),
            (0.331, 0, 3.27, 0.251, 0.266),
        ],
        cloth,
    )
    for z, y in [(3.177, -0.261), (3.03, -0.244), (2.72, -0.192)]:
        oval("Boots • round stud", (s * 0.333, y, z), (0.050, 0.024, 0.054), gold)
    for side in (-1, 1):
        cord(
            "Boots • red chevron",
            [
                (s * (0.335 + 0.183 * side), -0.13, 2.73),
                (s * (0.335 + 0.105 * side), -0.199, 2.81),
                (s * 0.335, -0.22, 2.91),
            ],
            0.035,
            red,
        )
    badge("Boots • shin insignia", s * 0.335, -0.215, 2.62, 0.059, 0.226, gold)
    leg(
        "UNVERIFIED_Boots • toe and sole",
        [
            (0.38, -0.115, 0.082, 0.151, 0.335),
            (0.38, -0.12, 0.11, 0.173, 0.36),
            (0.38, -0.12, 0.22, 0.169, 0.34),
            (0.38, -0.061, 0.31, 0.145, 0.237),
            (0.38, 0.019, 0.45, 0.135, 0.166),
        ],
        black,
    )
    oval("UNVERIFIED_Boots • heel", (s * 0.38, 0.132, 0.085), (0.114, 0.098, 0.08), cloth)

# Tiny repeating diamonds, integral with the stocking surface. No transparency sorting.
for side in (-1, 1):
    verts = []
    faces = []
    for row in range(11):
        z = 3.285 + row * 0.053
        t = (z - 3.10) / 0.88
        cx = side * (0.334 + (0.29 - 0.334) * t)
        rx = 0.237 + (0.28 - 0.237) * t
        ry = 0.241 + (0.30 - 0.241) * t
        for col in range(26):
            theta = 2 * pi * (col + 0.5 * (row % 2)) / 26
            start = len(verts)
            for dt, dz in [(0, -0.016), (0.03, 0), (0, 0.016), (-0.03, 0)]:
                verts.append(
                    (
                        cx + (rx + 0.005) * cos(theta + dt),
                        0.008 * (1 - t) + (ry + 0.005) * sin(theta + dt),
                        z + dz,
                    )
                )
            faces.append(tuple(range(start, start + 4)))
    mesh(
        "Stockings • woven dots",
        verts,
        faces,
        material("Smoke thread " + str(side), (0.252, 0.19, 0.195), 0.78),
    )
group("07 • Cape")
# Two physical surfaces with shared rim; length varies across shoulder and folds.
for s in (-1, 1):
    vs = []
    fs = []
    cols = 19
    rows = 13
    for layer in range(2):
        for i in range(rows):
            t = i / (rows - 1)
            for j in range(cols):
                u = j / (cols - 1)
                x = s * (
                    (0.035 + 0.68 * u) * (1 - t)
                    + (0.09 + 1.25 * u + 0.22 * sin(pi * u)) * t
                    + 0.12 * sin(pi * t) * u
                )
                y = (
                    0.29
                    + 0.12 * sin(pi * t)
                    + (0.52 + 0.16 * cos(4 * pi * u)) * t
                    - 0.30 * u**3
                    - 0.15 * u**4 * t
                    + 0.051 * layer
                )
                z = 5.99 - 0.18 * u - (3.62 + 0.29 * cos(2 * pi * u + 0.30 * s) - 0.43 * u) * t
                vs.append((x, y, z))
    k = cols * rows
    for layer in range(2):
        for i in range(rows - 1):
            for j in range(cols - 1):
                a = layer * k + i * cols + j
                q = (a, a + 1, a + cols + 1, a + cols)
                fs.append(q if layer else q[::-1])
    edges = (
        list(range(cols))
        + [i * cols + cols - 1 for i in range(1, rows)]
        + list(range(k - 2, k - cols - 1, -1))
        + [i * cols for i in reversed(range(1, rows - 1))]
    )
    for a, b in zip(edges, edges[1:] + edges[:1]):
        fs.append((a, b, b + k, a + k))
    o = mesh("UNVERIFIED_Cape • lined mantle", vs, fs, red, 1)
    o.data.materials.append(cloth)
    for p in list(o.data.polygons)[(cols - 1) * (rows - 1) :]:
        p.material_index = 1
    outer = [vs[i * cols + cols - 1] for i in range(rows)]
    cord("Cape • bound edge", outer, 0.018, wine)

yoke_v = []
yoke_f = []
for z, rx, ry in [(5.68, 0.54, 0.29), (5.85, 0.68, 0.32), (5.99, 0.57, 0.265), (6.035, 0.26, 0.20)]:
    for i in range(19):
        t = pi * i / 18
        yoke_v.append((rx * cos(t), 0.045 + ry * sin(t), z))
for i in range(3):
    for j in range(18):
        v = i * 19 + j
        yoke_f.append((v, v + 1, v + 20, v + 19))
yoke = mesh("UNVERIFIED_Cape • back yoke", yoke_v, yoke_f, cloth, 1)
yoke.modifiers.new("Lined facing", "SOLIDIFY").thickness = 0.025
for s in (-1, 1):
    for j in range(3):
        u = j / 2
        lock(
            "UNVERIFIED_Hair • nape layer",
            [
                (s * (0.10 + 0.13 * u), 0.35, 7.32, 0.19, 0.17),
                (s * (0.17 + 0.14 * u), 0.39, 7.04, 0.185, 0.15),
                (s * (0.25 + 0.13 * u), 0.36, 6.68, 0.12, 0.11),
                (s * (0.33 + 0.11 * u), 0.31, 6.49 + 0.08 * u, 0.027, 0.028),
            ],
            silver if j == 2 else hair,
        )
group("08 • Weapon | toggle collection")
bpy.ops.object.empty_add(type="PLAIN_AXES", location=(1.27, -0.13, 4.19))
socket = bpy.context.object
socket.name = "WeaponSocket.R"
for c in list(socket.users_collection):
    c.objects.unlink(socket)
current.objects.link(socket)
for name, x, y, z, a, b, h, m in [
    ("Weapon • grip", 1.28, -0.205, 4.15, 0.067, 0.066, 0.29, cloth),
    ("Weapon • ferrule", 1.28, -0.205, 4.43, 0.081, 0.080, 0.07, gold),
    ("Weapon • pommel", 1.28, -0.205, 3.87, 0.061, 0.061, 0.085, gold),
]:
    oval(name, (x, y, z), (a, b, h), m)
for j in range(6):
    z = 3.98 + j * 0.065
    cord(
        "Weapon • spiral grip",
        [(1.225, -0.23, z), (1.28, -0.272, z + 0.028), (1.331, -0.239, z + 0.056)],
        0.012,
        lightgold,
    )
badge("Weapon • spearhead", 1.28, -0.213, 4.64, 0.081, 0.247, gold)
badge("Weapon • enamel", 1.28, -0.266, 4.64, 0.036, 0.161, red)
cord(
    "UNVERIFIED_Weapon • flexible lash",
    [
        (1.28, -0.205, 3.84),
        (1.44, -0.23, 3.12),
        (1.58, -0.13, 2.49),
        (1.83, 0.05, 2.03),
        (2.02, 0.14, 2.14),
        (2.01, 0.17, 2.48),
    ],
    0.013,
    black,
)
for o in list(current.objects):
    if o != socket:
        o.parent = socket
        o.matrix_parent_inverse = socket.matrix_world.inverted()

# Export the character before studio lights, floor and camera are added.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=str(OUT / "gordia-static.glb"),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_texcoords=False,
)
group("09 • Portrait studio (excluded from GLB)")
ground = material("Blue-grey cyclorama", (0.144, 0.160, 0.196), 0.9)
bpy.ops.mesh.primitive_plane_add(size=200)
attach(bpy.context.object, "Studio floor", ground)


def aim(o, target):
    o.rotation_euler = (Vector(target) - o.location).to_track_quat("-Z", "Y").to_euler()


def light(name, pos, power, size, color):
    bpy.ops.object.light_add(type="AREA", location=pos)
    o = bpy.context.object
    o.name = name
    o.data.energy = power
    o.data.shape = "DISK"
    o.data.size = size
    o.data.color = color
    aim(o, (0, 0, 4.6))


light("Warm key", (-4, -6, 10), 700, 5, (1, 0.86, 0.78))
light("Cool fill", (4, -4, 8), 550, 4, (0.78, 0.84, 1))
light("Hair rim", (1, 4, 9), 1050, 4, (1, 0.85, 0.74))
bpy.ops.object.camera_add()
cam = bpy.context.object
scene.camera = cam
cam.data.type = "ORTHO"


def camera(angle):
    t = math.radians(angle)
    cam.location = (13 * sin(t), -13 * cos(t), 5.75)
    cam.data.ortho_scale = 8.8
    aim(cam, (0, 0, 3.94))


camera(0)
# Frame the character when the editable scene is opened in Blender.
bpy.ops.object.select_all(action="DESELECT")
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.region_3d.view_rotation = scene.camera.rotation_euler.to_quaternion()
            space.region_3d.view_distance = 11.5
            space.region_3d.view_location = (0, 0, 3.94)
            space.region_3d.view_perspective = "ORTHO"
            space.shading.color_type = "MATERIAL"
            space.overlay.show_extras = False
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "gordia-static.blend"), compress=True)
for name, angle in [("front", 0), ("three-quarter", 45), ("right", 90), ("back", 180), ("left", -90)]:
    camera(angle)
    scene.render.filepath = str(VIEWS / (name + ".png"))
    bpy.ops.render.render(write_still=True)

cam.location = (1.4, -10, 7.2)
aim(cam, (0, 0, 6.75))
cam.data.ortho_scale = 2.9
scene.render.resolution_x = 580
scene.render.resolution_y = 640
scene.cycles.samples = 32
scene.render.filepath = str(VIEWS / "portrait.png")
bpy.ops.render.render(write_still=True)
