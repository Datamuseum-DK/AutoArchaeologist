#/usr/bin/env python3

''' Produce the AutoArchaeologist logo SVG '''

import cairo

WIDTH = 200
HEIGHT = 80

def ctext(ctx, txt):
    ''' Center text '''
    a = ctx.text_extents(txt)
    ctx.rel_move_to(-a.x_advance // 2, 0)
    ctx.show_text(txt)

def main():
    ''' main function '''

    surface = cairo.SVGSurface(
        "aa_logo.svg",
        WIDTH, HEIGHT,
    )
    ctx = cairo.Context(surface)

    if True:
        ctx.save()
        ctx.set_source_rgb(.9,.9,.9)
        ctx.move_to(0,0)
        ctx.line_to(WIDTH,0)
        ctx.line_to(WIDTH,HEIGHT)
        ctx.line_to(0,HEIGHT)
        ctx.close_path()
        ctx.fill()
        ctx.restore()

    font = "OpenDinSchriftenEngshrift"
    font = "Alte DIN 1451 Mittelschrift gepraegt"
    ctx.select_font_face(font,
                     cairo.FONT_SLANT_NORMAL,
                     cairo.FONT_WEIGHT_NORMAL)

    ctx.save()

    ctx.save()
    ctx.set_source_rgb(.2,.4,.2)
    ctx.move_to(WIDTH//2, 4/12 * HEIGHT)
    ctx.set_font_size(24)
    ctext(ctx, "AutoArchaeologist")
    ctx.restore()

    ctx.move_to(WIDTH//2, 7/12 * HEIGHT)
    ctx.set_font_size(12)
    ctext(ctx, "by")

    ctx.move_to(WIDTH//2, 10/12 * HEIGHT)
    ctx.set_font_size(14)
    ctext(ctx, "Datamuseum.dk")

    ctx.restore()

if __name__ == "__main__":
    main()
