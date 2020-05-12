#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from MyQR.mylibs import theqrmodule
from PIL import Image, ImageDraw, ImageOps, ImageEnhance, ImageFilter
from MyQR.mylibs.constant import alig_location


def combine(ver, qr_code, scale, color, image):
    qr = qr_code
    ul = 4 * scale

    if ver > 1:
        aligs = []
        aloc = alig_location[ver - 2]
        for a in range(len(aloc)):
            for b in range(len(aloc)):
                if not ((a == b == 0) or (a == len(aloc) - 1 and b == 0) or (a == 0 and b == len(aloc) - 1)):
                    for i in range((aloc[a] + 2), (aloc[a] + 7)):
                        for j in range((aloc[b] + 2), (aloc[b] + 7)):
                            aligs.append((i, j))

    draw = ImageDraw.Draw(qr)

    # Draw orthogonal lines
    color_flag = True
    for d in range(21 + (ver - 1) * 4 - 8 * 2):
        # Horizontal
        draw.rectangle([
            ul * (8 + d),
            ul * 6,
            ul * (9 + d),
            ul * 7 - 1
        ], color if color_flag else 'white')

        # Vertical
        draw.rectangle([
            ul * 6,
            ul * (8 + d),
            ul * 7 - 1,
            ul * (9 + d)
        ], color if color_flag else 'white')
        color_flag = not color_flag

    # Draw aligs markers
    for chunk in chunks(aligs, 25):
        coordinates = chunk[0]
        draw.rectangle([
            ul * coordinates[0] - ul * 4,
            ul * coordinates[1] - ul * 4,
            ul * (coordinates[0] + 5) - ul * 4 - 1,
            ul * (coordinates[1] + 5) - ul * 4 - 1
        ], color)

        draw.rectangle([
            ul * (coordinates[0] + 1) - ul * 4,
            ul * (coordinates[1] + 1) - ul * 4,
            ul * (coordinates[0] + 4) - ul * 4 - 1,
            ul * (coordinates[1] + 4) - ul * 4 - 1
        ], (255, 255, 255))

        draw.rectangle([
            ul * (coordinates[0] + 2) - ul * 4,
            ul * (coordinates[1] + 2) - ul * 4,
            ul * (coordinates[0] + 3) - ul * 4 - 1,
            ul * (coordinates[1] + 3) - ul * 4 - 1,
        ], color)

    # Draw corners markers
    x_end = qr.size[0] - 1
    y_end = qr.size[1] - 1

    draw.rectangle([0, 0, ul * 8 - 1, ul * 8 - 1], 'white')
    draw.rectangle([x_end - ul * 8 + 1, 0 - ul, x_end + ul, ul * 8], 'white')
    draw.rectangle([0, y_end - ul * 8 + 1, ul * 8 - 1, y_end + ul], 'white')

    draw.rectangle([0, 0, ul * 7 - 1, ul * 7 - 1], color)
    draw.rectangle([x_end - ul * 7 + 1, 0, x_end, ul * 7 - 1], color)
    draw.rectangle([0, y_end - ul * 7 + 1, ul * 7 - 1, y_end], color)

    draw.rectangle([ul, ul, ul * 6 - 1, ul * 6 - 1], 'white')
    draw.rectangle([x_end - ul * 6 + 1, ul, x_end - ul, ul * 6 - 1], 'white')
    draw.rectangle([ul, y_end - ul * 6 + 1, ul * 6 - 1, y_end - ul], 'white')

    draw.rectangle([ul * 2, ul * 2, ul * 5 - 1, ul * 5 - 1], color)
    draw.rectangle([x_end - ul * 5 + 1, ul * 2, x_end - ul * 2, ul * 5 - 1], color)
    draw.rectangle([ul * 2, y_end - ul * 5 + 1, ul * 5 - 1, y_end - ul * 2], color)

    qr = ImageOps.expand(qr.crop(qr.getbbox()), border=ul, fill=255)
    draw = ImageDraw.Draw(qr)

    draw.rectangle([0, 0, ul * 9 - 1, ul - 1], 'white')
    draw.rectangle([x_end - ul * 7 + 1, 0, x_end + ul * 2, ul - 1], 'white')
    draw.rectangle([0, y_end + ul + 1, ul * 9 - 1, y_end + ul * 2], 'white')

    draw.rectangle([0, 0, ul - 1, ul * 9 - 1], 'white')
    draw.rectangle([x_end + ul + 1, 0, x_end + ul * 2, ul * 9], 'white')
    draw.rectangle([0, y_end - ul * 7 + 1, ul - 1, y_end + ul * 2], 'white')

    qr = ImageOps.expand(qr.crop(qr.getbbox()), border=ul, fill=255)

    if image is not None:
        width, height = image.size
        size = min(width, height)
        box = ((width - size) / 2, (height - size) / 2, (width + size) / 2, (height + size) / 2)
        image = image.crop(box)
        image = image.resize(qr.size, Image.ANTIALIAS).convert('RGBA')
        image.paste(qr.copy(), (0, 0), qr.copy())
        qr = image
    return qr


def chunks(lst, n):
    arr = []
    for i in range(0, len(lst), n):
        arr.append(lst[i:i + n])
    return arr


def run(words: str, version: object = 1, level: object = 'H', scale: int = 1,
        color: object = (0, 0, 0), image: object = None) -> object:
    supported_chars = r"0123456789" \
                      r"ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                      r"abcdefghijklmnopqrstuvwxyz" \
                      r" ··,.:;+-*/\~!@#$%^&`'=<>[]()?_{}| "  # \
    # r"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ" \
    # r"абвгдеёжзийклмнопрстуфхцчшщъыьэюя" \
    # check every parameter
    if not isinstance(words, str) or any(i not in supported_chars for i in words):
        raise ValueError('Wrong words! Make sure the characters are supported!')
    if not isinstance(version, int) or version not in range(1, 41):
        raise ValueError('Wrong version! Please choose a int-type value from 1 to 40!')
    if not isinstance(level, str) or len(level) > 1 or level not in 'LMQH':
        raise ValueError("Wrong level! Please choose a string-type level from {'L','M','Q','H'}!")
    if not isinstance(scale, int) or scale not in range(1, 16):
        raise ValueError('Wrong scale! Please choose a string-type level from 1 to 16!')
    if not isinstance(color, tuple) or len(color) != 3 or len([c for c in color if c in range(0, 256)]) != len(color):
        raise ValueError('Wrong color! Color must be a tuple which every item is in range from 0 to 255')

    try:
        ver, qr_code = theqrmodule.get_qrcode(version, level, words, scale, color)
        qr = combine(ver, qr_code, scale, color, image)
        return qr

    except:
        raise
