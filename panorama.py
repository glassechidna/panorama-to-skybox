#!/usr/bin/env python
from enum import Enum, auto
from math import pi, atan2, hypot, floor

class CubeFace(Enum):
    Back = auto()
    Left = auto()
    Front = auto()
    Right = auto()
    Top = auto()
    Bottom = auto()

def _face_pixel_to_cube_point(x, y, face, face_size):
    """
    Converts a face pixel location to an (x, y, z) coordinate on 2x2x2 cube centered at (0, 0, 0).
    :param i : int
    :param j : int
    :param face : CubeFace
    :return (float, float, float)
    """
    a = 2.0 * float(x) / face_size
    b = 2.0 * float(y) / face_size

    if face == CubeFace.Back:
        return (-1.0, 1.0 * (1.0 - a), 1.0 - b)
    elif face == CubeFace.Left:
        return (1.0 * (a - 1.0), -1.0, 1.0 - b)
    elif face == CubeFace.Front:
        return (1.0, 1.0 * (a - 1.0), 1.0 - b)
    elif face == CubeFace.Right:
        return (1.0 * (1.0 - a), 1.0, 1.0 - b)
    elif face == CubeFace.Top:
        return (1.0 * (b - 1.0), 1.0 * (a - 1.0), 1.0)
    else: # face == CubeFace.Bottom:
        return (1.0 * (1.0 - b), 1.0 * (a - 1.0), -1.0)

def _wrap_panorama_coordinates(x, y, bounds):
    """
    Wraps (x, y) coordinates to bounds in a way that makes sense for panorama pixel coordinates.
    :param x: int
    :param y: int
    :param bounds: (int, int)
    :return: (int, int)
    """
    if y > bounds[1] - 1 or y < 0:
        return ((x + int(bounds[0] / 2)) % bounds[0], max(0, min(y, bounds[1] - 1)))
    return (x % bounds[0], y)

def populate_face(panorama_image, face_image, face):
    """
    Populates output face_image with the skybox image for face from input panorama_image.
    :param panorama_image: Pillow.Image
    :param face_image: Pillow.Image
    :param face: CubeFace
    """
    panorama_dimensions = panorama_image.size
    panorama_pixels = panorama_image.load()

    face_size = face_image.size[0]
    face_pixels = face_image.load()

    for cube_x in range(face_size):
        for cube_y in range(face_size):
            (x, y, z) = _face_pixel_to_cube_point(cube_x, cube_y, face, face_size)

            theta = atan2(y, x)
            r = hypot(x, y)
            phi = atan2(z, r)

            x = 0.5 * panorama_dimensions[0] * (theta + pi) / pi
            y = 0.5 * panorama_dimensions[0] * (0.5 * pi - phi) / pi

            x_before = floor(x)
            y_before = floor(y)

            x_after = x_before + 1
            y_after = y_before + 1

            frac_x = x - x_before
            frac_y = y - y_before

            a = panorama_pixels[_wrap_panorama_coordinates(x_before, y_before, panorama_dimensions)]
            b = panorama_pixels[_wrap_panorama_coordinates(x_after, y_before, panorama_dimensions)]
            c = panorama_pixels[_wrap_panorama_coordinates(x_before, y_after, panorama_dimensions)]
            d = panorama_pixels[_wrap_panorama_coordinates(x_after, y_after, panorama_dimensions)]

            # Bilinear interpolation between four surrounding points
            (r, g, b) = (
                a[0] * (1 - frac_x) * (1 - frac_y) + b[0] * (frac_x) * (1 - frac_y) + c[0] * (1 - frac_x) * frac_y + d[0] * frac_x * frac_y,
                a[1] * (1 - frac_x) * (1 - frac_y) + b[1] * (frac_x) * (1 - frac_y) + c[1] * (1 - frac_x) * frac_y + d[1] * frac_x * frac_y,
                a[2] * (1 - frac_x) * (1 - frac_y) + b[2] * (frac_x) * (1 - frac_y) + c[2] * (1 - frac_x) * frac_y + d[2] * frac_x * frac_y
            )

            face_pixels[cube_x, cube_y] = (int(round(r)), int(round(g)), int(round(b)))
