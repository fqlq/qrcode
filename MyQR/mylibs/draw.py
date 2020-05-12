# -*- coding: utf-8 -*-

from PIL import Image


def draw_qrcode(qrmatrix, qrscale, qrcolor):
    unit_len = 4 * qrscale
    x = y = 0
    pic = Image.new('RGBA', [len(qrmatrix) * unit_len] * 2, 0)

    for line in qrmatrix:
        for module in line:
            if module:
                draw_a_color_unit(pic, x, y, int(unit_len / 3), int(unit_len / 3), qrcolor)
            else:
                draw_a_color_unit(pic, x, y, int(unit_len / 3), int(unit_len / 3), (255, 255, 255))
            x += unit_len
        x, y = 0, y + unit_len
    return pic


def draw_a_color_unit(p, x, y, ul, pd, color):
    for i in range(ul):
        for j in range(ul):
            p.putpixel((x + i + pd, y + j + pd), color)
