import pygame as pg
W, H = 900, 600
pg.init()
screen = pg.display.set_mode((W,H))

def get_outline_image(img, colour="white", linewidth=5, sf=1.4):
    mask = pg.mask.from_surface(img)
    outline = mask.outline()
    dw, dh = 2 * linewidth, 2*linewidth
    outline = [(dw//2 + p[0], dh//2 + p[1]) for p in outline]
    outline_img = pg.Surface(img.get_rect().inflate(dw, dh).size, pg.SRCALPHA)
    pg.draw.polygon(outline_img, colour, outline, linewidth)
    return pg.transform.rotozoom(outline_img, 0, sf)


def main():
    image_w, image_h = 100, 100
    r = 50
    img = pg.Surface((image_w, image_h), pg.SRCALPHA)
    pg.draw.circle(img, "red", (image_w//2, image_h//2), r)
    img_rect = img.get_rect(center=(W//2, H//2))

    outline_img = get_outline_image(img)
    outline_rect = outline_img.get_rect(center=(W//2, H//2))

    screen.fill("black")
    screen.blit(outline_img, outline_rect)
    screen.blit(img, img_rect)
    pg.display.flip()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return


if __name__=="__main__":
    main()
    pg.quit()
