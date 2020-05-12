# -*- coding: utf-8 -*-

from MyQR.mylibs import data, ECC, structure, matrix, draw


def get_qrcode(ver: object, ecl: object, string: str, scale: int, color: tuple) -> object:
    # Data Coding
    ver, data_codewords = data.encode(ver, ecl, string)

    # Error Correction Coding
    ecc = ECC.encode(ver, ecl, data_codewords)

    # Structure final bits
    final_bits = structure.structure_final_bits(ver, ecl, data_codewords, ecc)

    # Get the QR Matrix
    qrmatrix = matrix.get_qrmatrix(ver, ecl, final_bits)

    # Draw the picture and Save it, then return the real ver and the absolute name
    return ver, draw.draw_qrcode(qrmatrix, scale, color)
