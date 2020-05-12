from MyQR.mylibs import data, ECC, structure, matrix
from MyQR.mylibs.draw import draw_a_color_unit
from PIL import Image, ImageOps, ImageDraw, ImageFilter


def generate(text: str, version: int = 1, level: str = 'H', scale: int = 1,
             color: tuple = (0, 0, 0), image: object = None,
             imagesize: tuple = (10, 10), gold: object = None) -> object:
    # Data Coding
    version, data_codewords = data.encode(version, level, text)

    # Error Correction Coding
    ecc = ECC.encode(version, level, data_codewords)

    # Structure final bits
    final_bits = structure.structure_final_bits(version, level, data_codewords, ecc)

    # Get the QR Matrix
    qrmatrix = matrix.get_qrmatrix(version, level, final_bits)

    unit_len = 4 * scale
    x = y = 0
    qr = Image.new('RGBA', [len(qrmatrix) * unit_len] * 2, 0)

    # Gold source
    if gold == 'tile':
        tile = Image.open('gold-dark.jpg')
        tile = tile.resize(qr.size, Image.ANTIALIAS).convert('RGBA')

    for line in qrmatrix:
        for module in line:
            if module:
                if gold == 'tile':
                    for i in range(unit_len):
                        for j in range(unit_len):
                            coordinate = a, b = x + i, y + j
                            pixelcolor = tile.getpixel(coordinate)
                            qr.putpixel((x + i, y + j), pixelcolor)
                else:
                    draw_a_color_unit(qr, x, y, unit_len, 0, color)
            else:
                draw_a_color_unit(qr, x, y, unit_len, 0, (255, 255, 255, 0))
            x += unit_len
        x, y = 0, y + unit_len

    padding = 2 * unit_len

    if image is not None:
        width, height = image.size
        size = min(width, height)
        box = ((width - size) / 2, (height - size) / 2, (width + size) / 2, (height + size) / 2)
        image = image.crop(box)
        image = image.resize((
            imagesize[0] - 2 * padding,
            imagesize[1] - 2 * padding
        ), Image.ANTIALIAS).convert('RGBA')

        # Draw background placeholder
        draw = ImageDraw.Draw(qr)
        draw.rectangle([
            int((qr.size[0] - image.size[0] - padding) / 2),
            int((qr.size[1] - image.size[1] - padding) / 2),
            int((qr.size[0] + image.size[0] + padding) / 2),
            int((qr.size[1] + image.size[1] + padding) / 2)
        ], (255, 255, 255, 0))

        # corner = Image.new('RGBA', (16 * 4, 16 * 4), (255, 255, 255, 255))
        # corner_draw = ImageDraw.ImageDraw(corner)
        # corner_draw.pieslice((-64, -64, 64, 64), 0, 340, fill=(255, 255, 255, 0))
        # corner = corner.resize((
        #     int(padding / 2),
        #     int(padding / 2)
        # ), Image.ANTIALIAS)
        # image.paste(corner.copy(), (
        #     image.size[0] - int(padding / 2),
        #     image.size[1] - int(padding / 2)
        # ), corner.copy())

        # image.paste(corner.rotate(90).copy(), (
        #     image.size[0] - int(padding / 2),
        #     -1
        # ), corner.rotate(90).copy())

        # image.paste(corner.rotate(180).copy(), (
        #     0,
        #     0
        # ), corner.rotate(180).copy())
        #
        # image.paste(corner.rotate(-90).copy(), (
        #     -1,
        #     image.size[1] - int(padding / 2)
        # ), corner.rotate(-90).copy())

        mask = Image.open('mask.png')
        mask = mask.resize(image.size, Image.ANTIALIAS).convert('L')

        image.putalpha(mask)

        image = ImageOps.expand(image.crop(image.getbbox()), border=padding, fill=(255, 255, 255, 0))
        qr.paste(image.copy(), (
            int((qr.size[0] - image.size[0]) / 2),
            int((qr.size[1] - image.size[1]) / 2)
        ), image.copy())
    qr = ImageOps.expand(qr.crop(qr.getbbox()), border=unit_len * 2, fill=(255, 255, 255, 0))

    if gold == 'background':
        bg = Image.open('gold-light.jpg')
        bg = bg.resize(qr.size, Image.ANTIALIAS).convert('RGBA')
        qr = Image.composite(qr, bg, qr)

    return qr
