import os
from PIL import Image, ImageDraw, ImageFont  # , ImageFilter
from datetime import datetime

import textwrap



def create_texture_image(dir_path):
    output_image = os.path.join(dir_path, f"texture_####.png")
    cmd = f'python  create_texture.py -o {output_image}'
    print(cmd)
    os.system(cmd)

    try:
        output_image = os.path.join(dir_path, f"texture_0001.png")
        assert os.path.exists(output_image)
        return output_image
    except Exception as e:
        print(str(e))

    return None


def fit_text_in_shape(
    image,
    x, y,
    w, h,
    text,
    text_color=(255, 255, 255),
    font_file="input/fonts/bauhaus/BauhausRegular.ttf"):


    print(f"fit_text_in_shape: {text}")

    width = w
    height = h
    font_ttf = font_file
    textarea_size = (int(width * .9), int(height * .8))

    pad = (int(width * .05), int(height * .1))
    char_step = 1
    font_step = 1

    line_max_chars = 200
    line_min_chars = 5

    nb_chars = line_max_chars

    draw = ImageDraw.Draw(image)

    smallest_font_size = 5
    largest_front_size = 600
    font_size = smallest_font_size
    font = ImageFont.truetype(font_ttf, font_size)

    #	for f in range(smallest_font_size, largest_front_size, font_step):
    fit_vertically = True
    fit_horizontally = True
    tmp = 0
    tmp_f = -1

    while True:
        tmp = tmp + 1

        f = int((smallest_font_size + largest_front_size) / 2)
        if f == tmp_f:
            font = ImageFont.truetype(font_ttf, f - 2)
            break
        tmp_f = f

        # print('>>current font size:', f)
        font_size = f
        font = ImageFont.truetype(font_ttf, font_size)
        text_size = (-1, -1)
        lines = []

        for nb_chars in range(line_min_chars, line_max_chars, char_step):
            wrapper = textwrap.TextWrapper(break_long_words=False, width=int(nb_chars))
            lines = wrapper.wrap(text)

            # Fit vertically ?
            fit_vertically = True
            if len(lines) < 1:
                continue
            text_size = draw.textsize(lines[0], font=font)
            if text_size[1] * len(lines) > textarea_size[1]:
                fit_vertically = False
                continue  # does not fit

            # Fit horizontally ?
            fit_horizontally = True
            for l in lines:
                l = str(' ' + l + ' ')  # adding whitespace so letters don't get chopped
                text_size = draw.textsize(l, font=font)
                if text_size[0] > textarea_size[0]:
                    fit_horizontally = False
                    continue  # does not fit

            if fit_vertically and fit_vertically:
                break

        if fit_horizontally and fit_vertically:
            smallest_font_size = f
        else:
            largest_front_size = f

        if tmp == 1000:
            break

    wrapper = textwrap.TextWrapper(break_long_words=False, width=int(nb_chars))
    lines = wrapper.wrap(text)
    lines.append(" ")

    # get total text height
    total_h = 0
    for line in lines:
        text_size = draw.textsize(line, font=font)
        total_h += text_size[1]

  # get vertical padding
    current_h = (height - total_h) / 2

    for line in lines[:-1]:
        line = str(' ' + line + ' ')  # adding whitespace so letters don't get chopped
        text_size = draw.textsize(line, font=font)

        tx = x + (width - text_size[0]) / 2
        ty = y + current_h
        draw.text((tx - 2, ty - 2), line, font=font, fill='black')
        draw.text((tx + 2, ty - 2), line, font=font, fill='black')
        draw.text((tx - 2, ty + 2), line, font=font, fill='black')
        draw.text((tx + 2, ty + 2), line, font=font, fill='black')

        draw.text((tx, ty), line, font=font, fill=text_color)
        current_h += text_size[1]