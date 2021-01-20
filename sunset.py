"""
File: sunset.py
----------------
Stanford CS106A Sunset Project
This program creates an animation of a setting sun. The sun changes its color from yellow
to orange to red as it gradually goes downs.
"""

import tkinter
import time
from graphics import Canvas

CANVAS_WIDTH = 600  # Width of drawing canvas in pixels
CANVAS_HEIGHT = 300  # Height of drawing canvas in pixels
SUN_SIZE = 70  # Width and height of the sun oval

# The sun turns orange when the middle of the sun passes this y location
ORANGE_Y = CANVAS_HEIGHT * (1 / 3)
# The sun turns red when the middle of the sun passes this y location
RED_Y = CANVAS_HEIGHT * (2 / 3)


def main():
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT, 'Sunset')
    sky = canvas.set_canvas_background_color('blue')
    x0 = (CANVAS_WIDTH - SUN_SIZE) / 2
    y0 = 0
    x1 = (CANVAS_WIDTH + SUN_SIZE) / 2
    y1 = y0 + SUN_SIZE
    cir = canvas.create_oval(x0, y0, x1, y1, fill='yellow')
    while not is_off_screen(canvas, cir):
        canvas.move(cir, 0, 1)
        canvas.update()
        time.sleep(1 / 40)
        y0 = canvas.get_top_y(cir)
        canvas.set_fill_color(cir, get_sun_color(y0))
    print("animation complete")
    canvas.mainloop()


def is_off_screen(canvas, cir):
    top_y = canvas.get_top_y(cir)
    return top_y >= CANVAS_HEIGHT


def get_sun_color(top_y):
    if top_y > RED_Y - SUN_SIZE / 2:
        clr = 'red'
    elif top_y > ORANGE_Y - SUN_SIZE / 2:
        clr = 'orange'
    else:
        clr = 'yellow'
    return clr



if __name__ == '__main__':
    main()
