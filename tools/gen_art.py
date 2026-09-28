#!/usr/bin/env python3
"""Placeholder pixel art for the portrait slice. Paths match SpriteCatalog."""

import json
import math
import os
import random
import struct
import wave

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "art")

INK = (42, 32, 28, 255)
CLEAR = (0, 0, 0, 0)


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as handle:
        return json.load(handle)


def ensure(path):
    os.makedirs(path, exist_ok=True)


def put(img, x, y, color):
    if 0 <= x < img.size[0] and 0 <= y < img.size[1]:
        img.putpixel((x, y), color)


def fill_rect(img, x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            put(img, xx, yy, color)


def ellipse(img, cx, cy, rx, ry, light, mid, shadow, outline=INK):
    rx = max(1, rx)
    ry = max(1, ry)
    for y in range(cy - ry - 2, cy + ry + 3):
        for x in range(cx - rx - 2, cx + rx + 3):
            nx = (x - cx) / rx
            ny = (y - cy) / ry
            d = nx * nx + ny * ny
            if d <= 1.0:
                tone = mid
                if nx + ny < -0.35:
                    tone = light
                elif nx + ny > 0.45:
                    tone = shadow
                put(img, x, y, tone)
            elif d <= 1.35:
                put(img, x, y, outline)


def rect_blob(img, x, y, w, h, fill, outline=INK):
    fill_rect(img, x, y, w, h, fill)
    for xx in range(x, x + w):
        put(img, xx, y, outline)
        put(img, xx, y + h - 1, outline)
    for yy in range(y, y + h):
        put(img, x, yy, outline)
        put(img, x + w - 1, yy, outline)


def disk(img, cx, cy, r, color, outline=None):
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d <= r * r:
                put(img, x, y, color)
            elif outline and d <= (r + 1) * (r + 1):
                put(img, x, y, outline)


def line(img, x0, y0, x1, y1, color, radius=0):
    steps = int(max(abs(x1 - x0), abs(y1 - y0), 1))
    for i in range(steps + 1):
        t = i / steps
        x = int(round(x0 + (x1 - x0) * t))
        y = int(round(y0 + (y1 - y0) * t))
        if radius <= 0:
            put(img, x, y, color)
        else:
            disk(img, x, y, radius, color)


def stroke(img, pts, radius, color):
    for i in range(len(pts) - 1):
        line(img, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, radius)


def gray(v):
    return (v, v, v, 255)


def new_layer(size):
    return Image.new("RGBA", size, CLEAR)


def save(img, *parts):
    path = os.path.join(ART, *parts)
    ensure(os.path.dirname(path))
    img.save(path)


# --- paper doll -----------------------------------------------------------

FRONT = (48, 64)
BACK = (40, 52)
HL, MID, SH = gray(245), gray(200), gray(150)


def head_spec(index):
    specs = [
        (24, 16, 9, 10),
        (24, 16, 8, 11),
        (24, 17, 11, 9),
        (24, 16, 9, 10),
        (24, 18, 7, 8),
        (24, 15, 8, 12),
        (24, 17, 10, 10),
        (24, 15, 8, 11),
    ]
    return specs[index % 8]


def draw_body_front():
    img = new_layer(FRONT)
    ellipse(img, 19, 52, 4, 7, HL, MID, SH)
    ellipse(img, 29, 52, 4, 7, HL, MID, SH)
    ellipse(img, 16, 38, 4, 8, HL, MID, SH)
    ellipse(img, 32, 38, 4, 8, HL, MID, SH)
    ellipse(img, 24, 36, 9, 11, HL, MID, SH)
    ellipse(img, 24, 26, 4, 3, HL, MID, SH)
    return img


def draw_head(index):
    img = new_layer(FRONT)
    cx, cy, rx, ry = head_spec(index)
    ellipse(img, cx, cy, rx, ry, HL, MID, SH)
    return img


def draw_face(index):
    img = new_layer(FRONT)
    cx, cy, rx, ry = head_spec(index)
    eye_y = cy - 1
    spread = 3 if rx < 9 else 4
    skin_shadow = (90, 50, 40, 255)
    white = (250, 248, 244, 255)
    pupil = (32, 26, 24, 255)
    for side in (-1, 1):
        ex = cx + side * spread
        disk(img, ex, eye_y, 2, white, pupil)
        put(img, ex + side, eye_y, pupil)
        put(img, ex, eye_y, pupil)
    mouth = (160, 70, 70, 255)
    if index % 3 == 0:
        line(img, cx - 2, cy + 4, cx + 2, cy + 4, mouth)
    elif index % 3 == 1:
        line(img, cx - 2, cy + 5, cx, cy + 4, mouth)
        line(img, cx, cy + 4, cx + 2, cy + 5, mouth)
    else:
        disk(img, cx, cy + 4, 1, mouth)
    if index == 3:
        glass = (40, 60, 80, 255)
        rect_blob(img, cx - spread - 3, eye_y - 3, 6, 6, (180, 210, 220, 90), glass)
        rect_blob(img, cx + spread - 3, eye_y - 3, 6, 6, (180, 210, 220, 90), glass)
        line(img, cx - spread + 3, eye_y, cx + spread - 3, eye_y, glass)
    if index == 7:
        freckle = (170, 90, 60, 255)
        for dx, dy in ((-3, 2), (-1, 3), (2, 2), (4, 3), (0, 1)):
            put(img, cx + dx, cy + dy, freckle)
    if index == 2:
        # square jaw crease
        line(img, cx - 4, cy + 6, cx + 4, cy + 6, skin_shadow)
    return img


def draw_hair(index):
    img = new_layer(FRONT)
    if index == 0:
        return img
    if index == 1:
        ellipse(img, 24, 11, 10, 6, HL, MID, SH)
    elif index == 2:
        ellipse(img, 22, 12, 11, 7, HL, MID, SH)
        ellipse(img, 14, 18, 3, 5, HL, MID, SH)
    elif index == 3:
        ellipse(img, 24, 12, 11, 7, HL, MID, SH)
        ellipse(img, 12, 28, 4, 12, HL, MID, SH)
        ellipse(img, 36, 28, 4, 12, HL, MID, SH)
    elif index == 4:
        ellipse(img, 24, 12, 10, 6, HL, MID, SH)
        ellipse(img, 34, 30, 3, 10, HL, MID, SH)
    elif index == 5:
        ellipse(img, 24, 16, 12, 10, HL, MID, SH)
        # cut out a face window so the bob frames the face
        ellipse(img, 24, 20, 7, 7, CLEAR, CLEAR, CLEAR, CLEAR)
    elif index == 6:
        ellipse(img, 24, 13, 9, 5, HL, MID, SH)
        for dx in (-8, -4, 0, 4, 8):
            line(img, 24 + dx, 12, 24 + dx + (1 if dx > 0 else -1), 4, MID, 1)
    else:
        ellipse(img, 24, 12, 10, 6, HL, MID, SH)
        line(img, 33, 16, 36, 36, MID, 1)
        disk(img, 36, 38, 2, SH, INK)
    return img


def draw_outfit(class_id):
    img = new_layer(FRONT)
    if class_id == "paladin":
        ellipse(img, 24, 38, 10, 10, HL, MID, SH)
        rect_blob(img, 20, 32, 8, 10, gray(230), INK)
        line(img, 24, 32, 24, 42, gray(120))
    elif class_id == "wizard":
        # robe widening toward the feet
        for y in range(30, 58):
            half = 6 + (y - 30) // 3
            line(img, 24 - half, y, 24 + half, y, MID if y % 5 else SH)
        line(img, 24 - 8, 57, 24 + 8, 57, INK)
        line(img, 16, 30, 14, 58, INK)
        line(img, 32, 30, 34, 58, INK)
    elif class_id == "ranger":
        ellipse(img, 24, 38, 10, 11, HL, MID, SH)
        line(img, 16, 32, 12, 50, SH, 1)
        line(img, 32, 32, 36, 50, SH, 1)
    elif class_id == "cleric":
        for y in range(30, 58):
            half = 7 + (y - 30) // 4
            line(img, 24 - half, y, 24 + half, y, (236, 214, 150, 255) if y % 4 else (196, 154, 64, 255))
        rect_blob(img, 21, 32, 6, 8, (240, 220, 120, 255), INK)
    elif class_id == "rogue":
        ellipse(img, 24, 38, 9, 11, (70, 64, 82, 255), (48, 42, 58, 255), (28, 24, 36, 255))
        line(img, 15, 30, 12, 56, (28, 24, 36, 255), 1)
        line(img, 33, 30, 36, 56, (28, 24, 36, 255), 1)
    elif class_id == "barbarian":
        ellipse(img, 24, 38, 11, 10, (196, 140, 96, 255), (160, 104, 68, 255), (110, 70, 44, 255))
        line(img, 14, 32, 10, 44, (120, 72, 36, 255), 1)
        line(img, 34, 32, 38, 44, (120, 72, 36, 255), 1)
    elif class_id == "druid":
        ellipse(img, 24, 40, 10, 12, (72, 140, 72, 255), (46, 110, 52, 255), (28, 72, 36, 255))
        disk(img, 16, 34, 3, (90, 160, 70, 255), INK)
        disk(img, 32, 36, 3, (70, 130, 60, 255), INK)
    else:
        ellipse(img, 24, 38, 9, 10, HL, MID, SH)
        rect_blob(img, 18, 34, 12, 8, gray(235), INK)
        disk(img, 24, 38, 1, gray(80))
    return img


def draw_hat(class_id):
    img = new_layer(FRONT)
    if class_id == "paladin":
        ellipse(img, 24, 12, 11, 6, HL, MID, SH)
        rect_blob(img, 14, 14, 20, 4, gray(220), INK)
    elif class_id == "wizard":
        for y in range(2, 16):
            half = max(1, (y - 2) // 2)
            line(img, 24 - half, y, 24 + half, y, MID)
        line(img, 16, 16, 32, 16, SH, 1)
        ellipse(img, 24, 17, 10, 2, HL, MID, SH)
    elif class_id == "ranger":
        ellipse(img, 24, 14, 12, 8, HL, MID, SH)
        ellipse(img, 24, 20, 7, 6, CLEAR, CLEAR, CLEAR, CLEAR)
    elif class_id == "cleric":
        ellipse(img, 24, 10, 8, 3, (240, 220, 120, 255), (210, 170, 60, 255), (160, 120, 40, 255))
        disk(img, 24, 6, 2, (255, 236, 160, 255), INK)
    elif class_id == "rogue":
        ellipse(img, 24, 14, 11, 8, (48, 42, 58, 255), (32, 28, 40, 255), (18, 16, 24, 255))
        line(img, 14, 16, 10, 28, (32, 28, 40, 255), 1)
        line(img, 34, 16, 38, 28, (32, 28, 40, 255), 1)
    elif class_id == "barbarian":
        line(img, 16, 12, 12, 4, (90, 70, 50, 255), 1)
        line(img, 32, 12, 36, 4, (90, 70, 50, 255), 1)
        ellipse(img, 24, 14, 8, 4, (120, 72, 36, 255), (90, 54, 28, 255), (60, 36, 18, 255))
    elif class_id == "druid":
        line(img, 16, 14, 8, 6, (90, 60, 30, 255), 1)
        line(img, 32, 14, 40, 6, (90, 60, 30, 255), 1)
        disk(img, 8, 6, 2, (80, 150, 60, 255), INK)
        disk(img, 40, 6, 2, (80, 150, 60, 255), INK)
    else:
        ellipse(img, 24, 12, 10, 4, HL, MID, SH)
        line(img, 30, 10, 36, 4, gray(80), 0)
        disk(img, 36, 4, 1, (220, 60, 60, 255))
    return img


def draw_weapon(class_id):
    img = new_layer(FRONT)
    if class_id == "paladin":
        line(img, 38, 28, 38, 48, (120, 90, 50, 255), 0)
        rect_blob(img, 36, 18, 5, 12, (210, 214, 220, 255), INK)
        rect_blob(img, 34, 28, 9, 3, (90, 70, 40, 255), INK)
    elif class_id == "wizard":
        line(img, 40, 16, 40, 58, (110, 80, 40, 255), 1)
        disk(img, 40, 12, 3, (120, 190, 220, 255), INK)
    elif class_id == "ranger":
        line(img, 10, 24, 10, 50, (92, 64, 36, 255), 0)
        line(img, 8, 28, 12, 46, (40, 40, 40, 255), 0)
        line(img, 12, 28, 8, 46, (40, 40, 40, 255), 0)
    elif class_id == "cleric":
        line(img, 40, 18, 40, 58, (196, 154, 64, 255), 1)
        disk(img, 40, 14, 3, (255, 220, 90, 255), INK)
    elif class_id == "rogue":
        line(img, 8, 30, 14, 46, (180, 186, 196, 255), 0)
        line(img, 40, 28, 34, 44, (180, 186, 196, 255), 0)
    elif class_id == "barbarian":
        line(img, 38, 20, 44, 50, (110, 80, 40, 255), 1)
        rect_blob(img, 34, 16, 10, 8, (170, 176, 184, 255), INK)
    elif class_id == "druid":
        line(img, 40, 16, 36, 58, (90, 60, 30, 255), 1)
        disk(img, 42, 14, 3, (80, 160, 70, 255), INK)
    else:
        ellipse(img, 40, 40, 6, 4, (186, 140, 70, 255), (150, 100, 48, 255), (110, 70, 30, 255), INK)
        line(img, 34, 40, 46, 36, (80, 50, 30, 255), 0)
        line(img, 36, 38, 44, 34, (40, 30, 20, 255), 0)
    return img


def draw_ears():
    img = new_layer(FRONT)
    ellipse(img, 12, 16, 3, 4, HL, MID, SH)
    ellipse(img, 36, 16, 3, 4, HL, MID, SH)
    return img


def draw_beard():
    img = new_layer(FRONT)
    ellipse(img, 24, 24, 6, 5, HL, MID, SH)
    return img


def draw_body_back():
    img = new_layer(BACK)
    ellipse(img, 20, 18, 8, 8, HL, MID, SH)
    ellipse(img, 20, 34, 12, 10, HL, MID, SH)
    rect_blob(img, 8, 40, 24, 8, gray(170), INK)
    return img


def draw_outfit_back(class_id):
    img = new_layer(BACK)
    if class_id == "wizard":
        for y in range(24, 46):
            half = 8 + (y - 24) // 4
            line(img, 20 - half, y, 20 + half, y, MID)
    elif class_id == "ranger":
        ellipse(img, 20, 34, 12, 10, HL, MID, SH)
        line(img, 8, 26, 6, 44, SH, 1)
    elif class_id == "cleric":
        for y in range(24, 46):
            half = 7 + (y - 24) // 5
            line(img, 20 - half, y, 20 + half, y, (220, 196, 130, 255))
    elif class_id == "rogue":
        ellipse(img, 20, 34, 11, 10, (48, 42, 58, 255), (32, 28, 40, 255), (18, 16, 24, 255))
    elif class_id == "barbarian":
        ellipse(img, 20, 34, 12, 9, (160, 104, 68, 255), (120, 72, 36, 255), (80, 48, 24, 255))
    elif class_id == "druid":
        ellipse(img, 20, 34, 12, 10, (46, 110, 52, 255), (28, 72, 36, 255), (18, 48, 24, 255))
    else:
        ellipse(img, 20, 34, 11, 9, HL, MID, SH)
    return img


def draw_hat_back(class_id):
    img = new_layer(BACK)
    if class_id == "paladin":
        ellipse(img, 20, 12, 9, 5, HL, MID, SH)
    elif class_id == "wizard":
        for y in range(2, 14):
            half = max(1, (y - 2) // 2)
            line(img, 20 - half, y, 20 + half, y, MID)
        ellipse(img, 20, 14, 8, 2, HL, MID, SH)
    elif class_id == "ranger":
        ellipse(img, 20, 14, 10, 8, HL, MID, SH)
    elif class_id == "cleric":
        ellipse(img, 20, 10, 7, 2, (240, 220, 120, 255), (210, 170, 60, 255), (160, 120, 40, 255))
    elif class_id == "rogue":
        ellipse(img, 20, 14, 9, 6, (32, 28, 40, 255), (18, 16, 24, 255), (10, 8, 14, 255))
    elif class_id == "barbarian":
        line(img, 12, 12, 8, 6, (90, 70, 50, 255), 1)
        line(img, 28, 12, 32, 6, (90, 70, 50, 255), 1)
    elif class_id == "druid":
        line(img, 12, 12, 6, 6, (90, 60, 30, 255), 1)
        line(img, 28, 12, 34, 6, (90, 60, 30, 255), 1)
    else:
        ellipse(img, 20, 12, 8, 3, HL, MID, SH)
    return img


def draw_hair_back(index):
    img = new_layer(BACK)
    if index == 0:
        return img
    ellipse(img, 20, 14, 9, 7, HL, MID, SH)
    if index in (3, 5):
        ellipse(img, 10, 28, 3, 8, HL, MID, SH)
        ellipse(img, 30, 28, 3, 8, HL, MID, SH)
    if index == 4:
        ellipse(img, 30, 26, 3, 8, HL, MID, SH)
    if index == 6:
        for dx in (-6, -2, 2, 6):
            line(img, 20 + dx, 10, 20 + dx, 4, MID)
    return img


def draw_weapon_back(class_id):
    img = new_layer(BACK)
    if class_id == "paladin":
        rect_blob(img, 30, 16, 4, 12, (200, 206, 214, 255), INK)
    elif class_id == "wizard":
        line(img, 32, 14, 32, 46, (110, 80, 40, 255), 1)
    elif class_id == "ranger":
        line(img, 6, 18, 6, 40, (92, 64, 36, 255))
    elif class_id == "cleric":
        line(img, 32, 14, 32, 44, (196, 154, 64, 255), 1)
    elif class_id == "rogue":
        line(img, 6, 24, 12, 36, (180, 186, 196, 255))
    elif class_id == "barbarian":
        line(img, 30, 16, 36, 40, (110, 80, 40, 255), 1)
    elif class_id == "druid":
        line(img, 32, 14, 28, 44, (90, 60, 30, 255), 1)
    else:
        ellipse(img, 32, 36, 5, 3, (186, 140, 70, 255), (150, 100, 48, 255), (110, 70, 30, 255), INK)
    return img


def draw_ears_back():
    img = new_layer(BACK)
    ellipse(img, 10, 16, 2, 3, HL, MID, SH)
    ellipse(img, 30, 16, 2, 3, HL, MID, SH)
    return img


def draw_beard_back():
    img = new_layer(BACK)
    ellipse(img, 20, 22, 4, 2, HL, MID, SH)
    return img


def build_dolls():
    save(draw_body_front(), "doll", "front", "body.png")
    save(draw_ears(), "doll", "front", "ears.png")
    save(draw_beard(), "doll", "front", "beard.png")
    for i in range(8):
        save(draw_head(i), "doll", "front", "head_%d.png" % i)
        save(draw_face(i), "doll", "front", "face_%d.png" % i)
        save(draw_hair(i), "doll", "front", "hair_%d.png" % i)
        save(draw_hair_back(i), "doll", "back", "hair_%d.png" % i)
    for class_id in ("paladin", "wizard", "ranger", "bard", "cleric", "rogue", "barbarian", "druid"):
        save(draw_outfit(class_id), "doll", "front", "outfit_%s.png" % class_id)
        save(draw_hat(class_id), "doll", "front", "hat_%s.png" % class_id)
        save(draw_weapon(class_id), "doll", "front", "weapon_%s.png" % class_id)
        save(draw_outfit_back(class_id), "doll", "back", "outfit_%s.png" % class_id)
        save(draw_hat_back(class_id), "doll", "back", "hat_%s.png" % class_id)
        save(draw_weapon_back(class_id), "doll", "back", "weapon_%s.png" % class_id)
    save(draw_body_back(), "doll", "back", "body.png")
    save(draw_ears_back(), "doll", "back", "ears.png")
    save(draw_beard_back(), "doll", "back", "beard.png")


# --- monsters -------------------------------------------------------------

FRAME = 48


def monster_base(kind, attack=False):
    img = Image.new("RGBA", (FRAME, FRAME), CLEAR)
    shift = 3 if attack else 0
    cy = 28 + shift

    def blob(cx, cyy, rx, ry, fill, edge):
        ellipse(img, cx, cyy, rx, ry, tuple(min(255, c + 30) for c in fill) + (255,), fill + (255,), tuple(max(0, c - 30) for c in fill) + (255,), edge)

    if kind == "puddleblob":
        blob(24, cy, 14, 10, (60, 130, 210), INK)
        disk(img, 18, cy - 2, 2, (250, 250, 255, 255))
        disk(img, 28, cy - 2, 2, (250, 250, 255, 255))
        put(img, 18, cy - 2, (20, 30, 50, 255))
        put(img, 28, cy - 2, (20, 30, 50, 255))
        line(img, 20, cy + 3, 27, cy + 3, (20, 50, 80, 255))
    elif kind == "thicket_imp":
        blob(24, cy, 8, 9, (70, 150, 60), INK)
        ellipse(img, 14, cy - 6, 4, 3, gray(180), (70, 150, 60, 255), (40, 90, 30, 255), INK)
        ellipse(img, 34, cy - 6, 4, 3, gray(180), (70, 150, 60, 255), (40, 90, 30, 255), INK)
        disk(img, 21, cy - 2, 1, (250, 240, 200, 255))
        disk(img, 27, cy - 2, 1, (250, 240, 200, 255))
        line(img, 36, cy - 8 - shift, 42, cy + 8, (110, 80, 40, 255), 1)
    elif kind == "cinder_mite":
        blob(24, cy, 10, 8, (210, 90, 40), INK)
        ellipse(img, 14, cy - 4, 6, 3, (255, 180, 80, 255), (220, 120, 40, 255), (160, 60, 20, 255), INK)
        ellipse(img, 34, cy - 4, 6, 3, (255, 180, 80, 255), (220, 120, 40, 255), (160, 60, 20, 255), INK)
        line(img, 20, cy - 10, 18, cy - 16, (40, 30, 20, 255))
        line(img, 28, cy - 10, 30, cy - 16, (40, 30, 20, 255))
        disk(img, 18, cy - 16, 1, (255, 220, 80, 255))
        disk(img, 30, cy - 16, 1, (255, 220, 80, 255))
    elif kind == "briar_hound":
        blob(22, cy, 12, 7, (140, 90, 50), INK)
        ellipse(img, 34, cy - 2, 5, 4, (170, 120, 70, 255), (140, 90, 50, 255), (100, 60, 30, 255), INK)
        disk(img, 36, cy - 3, 1, (30, 20, 10, 255))
        line(img, 12, cy - 6, 8, cy - 12, (90, 50, 30, 255))
        for fx in (12, 18, 28, 32):
            line(img, fx, cy + 6, fx, cy + 12, (100, 60, 30, 255))
    elif kind == "lantern_wisp":
        blob(24, cy - 2, 8, 10, (255, 210, 80), INK)
        disk(img, 24, cy - 2, 3, (255, 250, 210, 255))
        disk(img, 21, cy - 4, 1, (40, 30, 20, 255))
        disk(img, 27, cy - 4, 1, (40, 30, 20, 255))
    elif kind == "marshlurker":
        blob(24, cy, 16, 10, (50, 110, 70), INK)
        disk(img, 16, cy - 2, 3, (230, 220, 80, 255), INK)
        disk(img, 30, cy - 2, 3, (230, 220, 80, 255), INK)
        put(img, 16, cy - 2, (20, 30, 10, 255))
        put(img, 30, cy - 2, (20, 30, 10, 255))
    elif kind == "cave_howler":
        ellipse(img, 12, cy, 10, 4, (120, 80, 170, 255), (90, 50, 140, 255), (50, 30, 90, 255), INK)
        ellipse(img, 36, cy, 10, 4, (120, 80, 170, 255), (90, 50, 140, 255), (50, 30, 90, 255), INK)
        blob(24, cy, 6, 7, (70, 40, 110), INK)
        disk(img, 22, cy - 1, 1, (255, 80, 80, 255))
        disk(img, 26, cy - 1, 1, (255, 80, 80, 255))
    else:
        blob(24, cy + 4, 14, 8, (130, 130, 136), INK)
        blob(24, cy - 6, 8, 7, (160, 160, 168), INK)
        disk(img, 21, cy - 8, 1, (40, 40, 40, 255))
        disk(img, 27, cy - 8, 1, (40, 40, 40, 255))
        rect_blob(img, 10, cy + 2, 6, 6, (100, 100, 108, 255), INK)
        rect_blob(img, 32, cy + 2, 6, 6, (100, 100, 108, 255), INK)
    return img


def build_monsters():
    monsters = load("monsters.json")
    for monster in monsters:
        frames = [monster_base(monster["id"], attack=False), monster_base(monster["id"], attack=False)]
        # idle bob
        bob = Image.new("RGBA", (FRAME, FRAME), CLEAR)
        bob.paste(frames[0], (0, -1), frames[0])
        frames[1] = bob
        frames.append(monster_base(monster["id"], attack=True))
        extra = monster_base(monster["id"], attack=True)
        nudged = Image.new("RGBA", (FRAME, FRAME), CLEAR)
        nudged.paste(extra, (0, 1), extra)
        frames.append(nudged)
        sheet = Image.new("RGBA", (FRAME * 4, FRAME), CLEAR)
        for i, frame in enumerate(frames):
            sheet.paste(frame, (i * FRAME, 0), frame)
        save(sheet, "monsters", "%s.png" % monster["id"])


# --- scenery --------------------------------------------------------------

def build_table(layout):
    rect = layout["portrait"]["combat"]["table"]
    w, h = int(rect[2]), int(rect[3])
    img = Image.new("RGBA", (w, h), CLEAR)
    top = (146, 96, 58, 255)
    edge = (96, 60, 36, 255)
    dark = (70, 42, 26, 255)
    fill_rect(img, 8, 6, w - 16, h - 16, top)
    fill_rect(img, 4, h // 2, w - 8, h // 2 - 2, edge)
    for x in range(8, w - 8, 18):
        line(img, x, 6, x, h // 2, (120, 78, 46, 255))
    rect_blob(img, 2, 2, w - 4, h - 4, (0, 0, 0, 0), dark)
    # screen and papers
    rect_blob(img, w // 2 - 18, 8, 28, 16, (196, 168, 120, 255), INK)
    disk(img, w // 2 - 4, 16, 4, (70, 50, 36, 255))
    rect_blob(img, w // 2 + 16, 18, 22, 12, (230, 214, 180, 255), INK)
    disk(img, w // 2 + 46, 22, 4, (70, 110, 190, 255), INK)
    disk(img, w // 2 + 56, 28, 3, (180, 50, 50, 255), INK)
    save(img, "ui", "table.png")


def build_gm():
    img = new_layer((72, 80))
    # olive coat, original GM, facing the camera
    ellipse(img, 36, 62, 18, 14, (70, 110, 70, 255), (48, 86, 52, 255), (30, 58, 36, 255), INK)
    ellipse(img, 22, 58, 6, 8, (70, 110, 70, 255), (48, 86, 52, 255), (30, 58, 36, 255), INK)
    ellipse(img, 50, 58, 6, 8, (70, 110, 70, 255), (48, 86, 52, 255), (30, 58, 36, 255), INK)
    ellipse(img, 36, 28, 12, 13, (236, 196, 160, 255), (214, 164, 128, 255), (170, 120, 90, 255), INK)
    ellipse(img, 36, 18, 13, 8, (120, 64, 36, 255), (90, 48, 28, 255), (60, 32, 20, 255), INK)
    ellipse(img, 36, 36, 8, 5, (90, 50, 32, 255), (70, 40, 26, 255), (50, 28, 18, 255), INK)
    disk(img, 31, 28, 1, (40, 30, 20, 255))
    disk(img, 41, 28, 1, (40, 30, 20, 255))
    # glasses
    rect_blob(img, 26, 24, 8, 6, (180, 210, 220, 70), (40, 50, 60, 255))
    rect_blob(img, 38, 24, 8, 6, (180, 210, 220, 70), (40, 50, 60, 255))
    save(img, "ui", "gm.png")


def scenery(kind, layout):
    w, h = 270, 480
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    table_y = int(layout["portrait"]["combat"]["table"][1])
    sky = {
        "meadow": (126, 196, 232),
        "town": (126, 196, 232),
        "cave": (70, 90, 110),
        "coast": (120, 190, 220),
        "keep": (110, 160, 196),
    }[kind]
    grass = {
        "meadow": (96, 168, 64),
        "town": (96, 168, 64),
        "cave": (62, 90, 58),
        "coast": (88, 160, 70),
        "keep": (78, 130, 62),
    }[kind]
    draw.rectangle([0, 0, w, table_y], fill=sky)
    # clouds
    if kind != "cave":
        for cx, cy, rw in ((40, 28, 18), (120, 18, 22), (200, 34, 16)):
            draw.ellipse([cx - rw, cy - 6, cx + rw, cy + 6], fill=(236, 244, 248))
    draw.rectangle([0, table_y - 28, w, table_y], fill=grass)
    rng = random.Random(kind)
    for _ in range(80):
        x = rng.randrange(0, w)
        y = rng.randrange(table_y - 26, table_y)
        img.putpixel((x, y), (70, 130, 48, 255) if rng.random() < 0.5 else (150, 190, 80, 255))
    # trees at the sides
    def tree(tx, ty, scale=1):
        disk(img, tx, ty, int(14 * scale), (46, 120, 48, 255), (24, 70, 28, 255))
        disk(img, tx - 6, ty + 2, int(8 * scale), (60, 140, 54, 255))
        rect_blob(img, tx - 2, ty + 8, 4, 12, (110, 74, 42, 255), INK)

    if kind == "meadow":
        tree(18, table_y - 50)
        tree(250, table_y - 46, 0.8)
        tree(28, table_y - 30, 0.6)
    elif kind == "town":
        rect_blob(img, 16, table_y - 58, 28, 24, (186, 150, 110, 255), INK)
        line(img, 14, table_y - 58, 30, table_y - 74, (160, 64, 48, 255), 0)
        line(img, 46, table_y - 58, 30, table_y - 74, (160, 64, 48, 255), 0)
        rect_blob(img, 210, table_y - 50, 22, 18, (170, 130, 90, 255), INK)
        tree(250, table_y - 40, 0.7)
    elif kind == "cave":
        disk(img, 40, table_y - 36, 28, (90, 96, 104, 255), (40, 42, 48, 255))
        disk(img, 210, table_y - 30, 34, (80, 84, 92, 255), (40, 42, 48, 255))
        disk(img, 40, table_y - 30, 10, (16, 16, 20, 255))
    elif kind == "coast":
        draw.rectangle([150, table_y - 40, w, table_y], fill=(48, 120, 190))
        draw.rectangle([160, table_y - 36, w, table_y - 28], fill=(220, 200, 150))
        rect_blob(img, 200, table_y - 70, 10, 32, (230, 230, 234, 255), INK)
        draw.polygon([(196, table_y - 70), (214, table_y - 70), (205, table_y - 86)], fill=(180, 48, 48))
    else:
        rect_blob(img, 80, table_y - 64, 110, 36, (120, 124, 130, 255), INK)
        rect_blob(img, 90, table_y - 80, 16, 20, (100, 104, 110, 255), INK)
        rect_blob(img, 164, table_y - 80, 16, 20, (100, 104, 110, 255), INK)
    # floor under the table
    floor = (92, 64, 40, 255)
    draw.rectangle([0, table_y, w, h], fill=floor)
    for y in range(table_y, h, 6):
        draw.line([(0, y), (w, y)], fill=(70, 46, 28))
    return img


def build_backgrounds(layout):
    for kind in ("meadow", "town", "cave", "coast", "keep"):
        save(scenery(kind, layout), "bg", "%s.png" % kind)


def build_map(layout, region):
    content = layout["portrait"]["map"]["content"]
    w, h = int(content[0]), int(content[1])
    img = Image.new("RGBA", (w, h), (88, 168, 72, 255))
    rng = random.Random(7)
    for y in range(h):
        for x in range(0, w, 3):
            if rng.random() < 0.15:
                shade = (70, 140, 56, 255) if rng.random() < 0.5 else (120, 186, 78, 255)
                put(img, x + rng.randrange(0, 3), y, shade)
    # mountains
    draw = ImageDraw.Draw(img)
    draw.polygon([(0, 120), (40, 20), (90, 100), (130, 10), (180, 90), (230, 16), (250, 110)], fill=(150, 156, 162))
    draw.polygon([(20, 120), (70, 40), (120, 120)], fill=(120, 126, 132))
    # sea and beach at the bottom right
    draw.polygon([(80, 640), (250, 600), (250, 760), (40, 760)], fill=(46, 116, 186))
    draw.polygon([(70, 650), (200, 620), (160, 700), (50, 720)], fill=(214, 190, 130))
    # river
    stroke(img, [(200, 80), (210, 200), (190, 360), (150, 520), (190, 640)], 4, (58, 130, 196, 255))
    # roads
    for edge in region["edges"]:
        stroke(img, edge["points"], 5, (176, 140, 90, 255))
        stroke(img, edge["points"], 3, (196, 164, 112, 255))

    def building(icon, x, y):
        if icon == "house":
            rect_blob(img, x - 12, y - 8, 24, 16, (186, 140, 96, 255), INK)
            draw.polygon([(x - 16, y - 8), (x, y - 22), (x + 16, y - 8)], fill=(168, 64, 48))
            rect_blob(img, x - 3, y, 6, 8, (90, 60, 40, 255), INK)
        elif icon == "windmill":
            rect_blob(img, x - 6, y - 8, 12, 18, (150, 140, 120, 255), INK)
            line(img, x - 14, y - 10, x + 14, y - 18, (236, 236, 236, 255), 1)
            line(img, x - 14, y - 18, x + 14, y - 10, (236, 236, 236, 255), 1)
        elif icon == "castle":
            rect_blob(img, x - 16, y - 10, 32, 20, (140, 144, 150, 255), INK)
            rect_blob(img, x - 16, y - 18, 8, 10, (120, 124, 130, 255), INK)
            rect_blob(img, x + 8, y - 18, 8, 10, (120, 124, 130, 255), INK)
            rect_blob(img, x - 4, y - 2, 8, 12, (50, 46, 42, 255), INK)
        elif icon == "cave":
            disk(img, x, y, 16, (120, 124, 130, 255), (50, 52, 56, 255))
            disk(img, x, y + 2, 7, (20, 18, 22, 255))
        elif icon == "lighthouse":
            rect_blob(img, x - 5, y - 16, 10, 24, (236, 236, 240, 255), INK)
            draw.polygon([(x - 8, y - 16), (x + 8, y - 16), (x, y - 28)], fill=(180, 48, 48))
            disk(img, x, y - 12, 2, (255, 220, 80, 255))
        else:
            line(img, x, y - 12, x, y + 8, (110, 74, 42, 255), 1)
            rect_blob(img, x - 10, y - 8, 12, 6, (196, 164, 96, 255), INK)
            rect_blob(img, x - 2, y - 2, 12, 6, (176, 140, 80, 255), INK)

    # trees avoiding nodes and roads
    nodes = [(p["x"], p["y"]) for p in region["places"]]

    def far_from_roads(x, y):
        for edge in region["edges"]:
            pts = edge["points"]
            for i in range(len(pts) - 1):
                x0, y0 = pts[i]
                x1, y1 = pts[i + 1]
                # distance to segment, coarse
                for t in range(0, 11):
                    px = x0 + (x1 - x0) * t / 10
                    py = y0 + (y1 - y0) * t / 10
                    if (x - px) ** 2 + (y - py) ** 2 < 16 ** 2:
                        return False
        for nx, ny in nodes:
            if (x - nx) ** 2 + (y - ny) ** 2 < 28 ** 2:
                return False
        return True

    planted = 0
    attempts = 0
    while planted < 46 and attempts < 800:
        attempts += 1
        x = rng.randrange(8, w - 8)
        y = rng.randrange(130, h - 30)
        if not far_from_roads(x, y):
            continue
        disk(img, x, y, rng.choice((6, 7, 8)), (42, 120, 46, 255), (20, 70, 28, 255))
        rect_blob(img, x - 1, y + 4, 3, 6, (100, 70, 40, 255), INK)
        planted += 1
    for place in region["places"]:
        disk(img, place["x"], place["y"] + 8, 12, (186, 150, 96, 255))
        building(place["icon"], place["x"], place["y"])
    save(img, "map", "greenmere.png")


# --- ui bits --------------------------------------------------------------

def icon_sword():
    img = new_layer((16, 16))
    line(img, 3, 13, 12, 4, (210, 214, 220, 255))
    line(img, 4, 12, 11, 5, (230, 232, 236, 255))
    line(img, 2, 12, 6, 14, (120, 80, 40, 255))
    return img


def icon_star():
    img = new_layer((16, 16))
    draw = ImageDraw.Draw(img)
    cx, cy, r = 8, 8, 6
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else 3
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=(240, 200, 70, 255), outline=(80, 50, 20, 255))
    return img


def icon_potion():
    img = new_layer((16, 16))
    rect_blob(img, 6, 2, 4, 3, (180, 200, 210, 255), INK)
    ellipse(img, 8, 10, 5, 4, (120, 210, 170, 255), (60, 170, 120, 255), (30, 110, 80, 255), INK)
    return img


def icon_shield():
    img = new_layer((16, 16))
    draw = ImageDraw.Draw(img)
    draw.polygon([(3, 2), (13, 2), (13, 8), (8, 14), (3, 8)], fill=(70, 120, 190, 255), outline=(30, 40, 60, 255))
    return img


def icon_boot():
    img = new_layer((16, 16))
    rect_blob(img, 4, 2, 6, 7, (140, 90, 50, 255), INK)
    rect_blob(img, 4, 8, 10, 5, (120, 74, 40, 255), INK)
    return img


def icon_check():
    img = new_layer((16, 16))
    line(img, 3, 8, 7, 12, (240, 250, 240, 255), 1)
    line(img, 7, 12, 13, 3, (240, 250, 240, 255), 1)
    return img


def icon_die():
    img = new_layer((16, 16))
    rect_blob(img, 2, 2, 12, 12, (244, 244, 246, 255), INK)
    for dx, dy in ((5, 5), (10, 5), (5, 10), (10, 10), (7, 7)):
        put(img, dx, dy, INK)
    return img


def icon_arrow():
    img = new_layer((12, 12))
    draw = ImageDraw.Draw(img)
    draw.polygon([(6, 1), (11, 10), (1, 10)], fill=(255, 210, 60, 255), outline=(80, 50, 10, 255))
    return img


def icon_bang():
    img = new_layer((16, 16))
    draw = ImageDraw.Draw(img)
    draw.polygon([(8, 0), (10, 6), (16, 6), (11, 10), (13, 16), (8, 12), (3, 16), (5, 10), (0, 6), (6, 6)], fill=(220, 50, 40, 255))
    return img


def build_ui():
    save(icon_sword(), "ui", "icon_attack.png")
    save(icon_star(), "ui", "icon_skill.png")
    save(icon_potion(), "ui", "icon_item.png")
    save(icon_shield(), "ui", "icon_cover.png")
    save(icon_boot(), "ui", "icon_run.png")
    save(icon_check(), "ui", "icon_check.png")
    save(icon_die(), "ui", "icon_die.png")
    save(icon_arrow(), "ui", "arrow.png")
    save(icon_bang(), "ui", "bang.png")
    # nine patches
    def patch(fill, border, hi):
        img = Image.new("RGBA", (16, 16), border)
        fill_rect(img, 3, 3, 10, 10, fill)
        fill_rect(img, 3, 3, 10, 1, hi)
        return img

    save(patch((214, 176, 110, 255), (70, 46, 28, 255), (236, 210, 150, 255)), "ui", "btn_tan.png")
    save(patch((170, 130, 74, 255), (50, 32, 18, 255), (196, 160, 100, 255)), "ui", "btn_tan_down.png")
    save(patch((232, 214, 176, 255), (90, 64, 40, 255), (250, 240, 214, 255)), "ui", "panel_tan.png")
    save(patch((48, 36, 28, 255), (20, 14, 10, 255), (80, 60, 44, 255)), "ui", "panel_dark.png")
    # die
    die = Image.new("RGBA", (16, 16), CLEAR)
    rect_blob(die, 1, 1, 14, 14, (244, 244, 248, 255), INK)
    save(die, "ui", "die.png")
    bad = Image.new("RGBA", (16, 16), CLEAR)
    rect_blob(bad, 1, 1, 14, 14, (150, 150, 154, 255), INK)
    save(bad, "ui", "die_fail.png")
    spins = Image.new("RGBA", (64, 16), CLEAR)
    for i in range(4):
        frame = Image.new("RGBA", (16, 16), CLEAR)
        rect_blob(frame, 1, 1, 14, 14, (230, 230, 236, 255), INK)
        for k in range(3 + i):
            put(frame, 3 + ((i * 3 + k * 5) % 10), 3 + ((k * 4 + i) % 10), INK)
        spins.paste(frame, (i * 16, 0), frame)
    save(spins, "ui", "die_spin.png")
    # horse pawn
    horse = new_layer((28, 24))
    ellipse(horse, 14, 14, 8, 5, (150, 96, 48, 255), (120, 74, 36, 255), (80, 48, 24, 255), INK)
    ellipse(horse, 22, 10, 4, 3, (150, 96, 48, 255), (120, 74, 36, 255), (80, 48, 24, 255), INK)
    line(horse, 8, 16, 6, 22, (90, 56, 28, 255))
    line(horse, 18, 16, 20, 22, (90, 56, 28, 255))
    ellipse(horse, 16, 8, 3, 3, (230, 200, 160, 255), (200, 160, 120, 255), (150, 110, 80, 255), INK)
    save(horse, "ui", "pawn.png")
    chicken = new_layer((16, 16))
    ellipse(chicken, 8, 9, 5, 4, (255, 220, 80, 255), (240, 180, 40, 255), (190, 120, 20, 255), INK)
    disk(chicken, 12, 7, 2, (255, 230, 120, 255), INK)
    put(chicken, 13, 7, (20, 20, 20, 255))
    line(chicken, 14, 8, 16, 9, (220, 80, 40, 255))
    save(chicken, "ui", "chicken.png")
    # app icon: shield and quill
    icon = Image.new("RGBA", (128, 128), (48, 86, 52, 255))
    draw = ImageDraw.Draw(icon)
    draw.rounded_rectangle([8, 8, 120, 120], 12, fill=(214, 176, 110), outline=(50, 32, 18), width=4)
    draw.polygon([(40, 28), (88, 28), (88, 64), (64, 96), (40, 64)], fill=(48, 96, 160), outline=(20, 30, 50))
    line(icon, 78, 78, 104, 40, (40, 30, 20, 255), 1)
    save(icon, "icon.png")


def tone(path, freq, dur, volume=0.25, shape="square"):
    sample_rate = 22050
    count = int(sample_rate * dur)
    frames = bytearray()
    for i in range(count):
        t = i / sample_rate
        env = min(1.0, i / 80.0, (count - i) / 200.0)
        if shape == "square":
            sample = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            sample = math.sin(2 * math.pi * freq * t)
        frames += struct.pack("<h", int(sample * volume * env * 32767))
    ensure(os.path.dirname(path))
    with wave.open(path, "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(frames)


def build_sfx():
    base = os.path.join(ART, "sfx")
    tone(os.path.join(base, "tap.wav"), 660, 0.05, 0.2)
    tone(os.path.join(base, "hit.wav"), 180, 0.08, 0.3)
    tone(os.path.join(base, "dice.wav"), 520, 0.12, 0.2)
    tone(os.path.join(base, "good.wav"), 880, 0.12, 0.22, "sine")
    tone(os.path.join(base, "bad.wav"), 140, 0.16, 0.25)
    tone(os.path.join(base, "heal.wav"), 740, 0.14, 0.2, "sine")
    tone(os.path.join(base, "ambush.wav"), 220, 0.2, 0.3)
    tone(os.path.join(base, "victory.wav"), 660, 0.28, 0.22, "sine")
    tone(os.path.join(base, "chicken.wav"), 980, 0.1, 0.18)
    tone(os.path.join(base, "level.wav"), 520, 0.22, 0.22, "sine")


def main():
    layout = load("layout.json")
    region = load("region.json")
    build_dolls()
    build_monsters()
    build_table(layout)
    build_gm()
    build_backgrounds(layout)
    build_map(layout, region)
    build_ui()
    build_sfx()
    print("art generated")


if __name__ == "__main__":
    main()
