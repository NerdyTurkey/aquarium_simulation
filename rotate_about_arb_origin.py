# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 08:25:29 2021

@author: jwgti
"""


import pygame as pg
import math

vec = pg.math.Vector2
W, H = 900, 600
FPS = 60



def blit_rotate(surf, img, surf_rot_orig, img_rot_orig, angle):
    """
    Blits image rotated by angle onto surf about arbitrary rotation origin.
    Parameters
    ----------
    surf : pygame surface
        TARGET SURFACE
    img : pygame surface
        IMAGE TO BE ROTATED
    surf_rot_orig : (int, int)
        ROTATATION ORIGIN (CoR) ON surf REL TO surf TOPLEFT
    img_rot_orig : (int, int)
        ROTATATION ORIGIN (CoR) ON img REL TO img TOPLEFT
    angle : float
        angle in degrees to rotate image; positive = anticlockwise.

    Returns
    -------
    rect of blitted area on surf

    """
    # calc the axis aligned bounding box of the rotated image
    w, h = img.get_size()
    box = [vec(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]
    min_box = (
        min(box_rotate, key=lambda p: p[0])[0],
        min(box_rotate, key=lambda p: p[1])[1],
    )
    max_box = (
        max(box_rotate, key=lambda p: p[0])[0],
        max(box_rotate, key=lambda p: p[1])[1],
    )

    # calculate the translation of the pivot
    pivot = vec(img_rot_orig[0], -img_rot_orig[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move = pivot_rotate - pivot

    # calculate the upper left origin of the rotated image
    origin = (
        surf_rot_orig[0] - img_rot_orig[0] + min_box[0] - pivot_move[0],
        surf_rot_orig[1] - img_rot_orig[1] - max_box[1] + pivot_move[1],
    )

    # get a rotated image
    rotated_image = pg.transform.rotate(img, angle)

    # rotate and blit the image
    surf.blit(rotated_image, origin)

    return pg.Rect((*origin, *rotated_image.get_size()))

