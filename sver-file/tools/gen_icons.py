from PIL import Image

PAL = {
    '.': None,
    'K': (15, 23, 42, 255),
    'S': (203, 213, 225, 255),
    'B': (37, 99, 235, 255),
    'W': (241, 245, 249, 255),
    'G': (34, 197, 94, 255),
    'D': (13, 22, 47, 255),
}

ART = [
    "................",
    "..KKKKKKKKKKKK..",
    "..KSSSSSSSSSSK..",
    "..KSSSSKKSSSSK..",
    "..KSSSSKKSSSSK..",
    "..KSSSSKKSSSSK..",
    "..KBBBBBBBBBBK..",
    "..KBBBBBBBBBBK..",
    "..KBWWWWWWWWBK..",
    "..KBWWWWWWWWBK..",
    "..KBWGGGGGGWBK..",
    "..KBWWWWWWWWBK..",
    "..KBWGGGGGGWBK..",
    "..KBWWWWWWWWBK..",
    "..KKKKKKKKKKKK..",
    "................",
]


def render_art(scale=1):
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(ART):
        for x, c in enumerate(row):
            col = PAL[c]
            if col:
                px[x, y] = col
    if scale > 1:
        img = img.resize((16 * scale, 16 * scale), Image.NEAREST)
    return img


def with_bg(size, art_px):
    bg = Image.new('RGBA', (size, size), PAL['D'])
    art_px = art_px.resize((art_px.width, art_px.height), Image.NEAREST)
    off = (size - art_px.width) // 2
    bg.alpha_composite(art_px, (off, off))
    return bg


def write_svg(path):
    rects = []
    for y, row in enumerate(ART):
        for x, c in enumerate(row):
            col = PAL[c]
            if col:
                op = col[3] / 255
                fill = '#%02x%02x%02x' % col[:3]
                rects.append(
                    f'<rect x="{x}" y="{y}" width="1" height="1" fill="{fill}"'
                    + (f' fill-opacity="{op:.2f}"' if op < 1 else '') + '/>')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" '
           'shape-rendering="crispEdges">' + ''.join(rects) + '</svg>')
    with open(path, 'w') as f:
        f.write(svg)


if __name__ == '__main__':
    write_svg('../icons/logo.svg')
    render_art(11).save('preview-full.png')
    with_bg(192, render_art(11)).save('../icons/icon-192.png')
    with_bg(512, render_art(27)).save('../icons/icon-512.png')
    render_art(2).save('preview.png')
    print('icons generated')
