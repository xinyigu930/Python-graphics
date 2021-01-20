from graphics import Canvas

"""
File: extension.py
------------------
This program animates a setting sun at the seaside. 
Besides sun and sea, it also draws two floating clouds, 
and shows a crescent moon and a line of text saying "Good night!" 
after the sun dips below the horizon.
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
    sky = canvas.set_canvas_background_color('deep sky blue')
    sea_y = CANVAS_HEIGHT * (3 / 4)
    sea = canvas.create_rectangle(0, sea_y, CANVAS_WIDTH, CANVAS_HEIGHT, fill='turquoise4', outline='turquoise4')
    # Create wavy effect of the sea.
    for i in range(0, 1000, 60):
        canvas.create_oval(i, sea_y - 15, i + 60, sea_y + 15, tags='wave', fill='turquoise4', outline='turquoise4')
    # Create two clouds.
    canvas.create_oval(90, 40, 140, 80, tags='cloud1', fill='light cyan', outline='light cyan')
    canvas.create_oval(120, 30, 180, 90, tags='cloud1', fill='light cyan', outline='light cyan')
    canvas.create_oval(160, 40, 210, 80, tags='cloud1', fill='light cyan', outline='light cyan')
    canvas.create_oval(490, 30, 545, 65, tags='cloud2', fill='light cyan', outline='light cyan')
    canvas.create_oval(460, 30, 515, 65, tags='cloud2', fill='light cyan', outline='light cyan')
    canvas.create_oval(475, 55, 530, 90, tags='cloud2', fill='light cyan', outline='light cyan')
    canvas.create_oval(445, 55, 500, 90, tags='cloud2', fill='light cyan', outline='light cyan')
    # Create the setting sun.
    x0 = (CANVAS_WIDTH - SUN_SIZE) / 2
    y0 = 0
    x1 = (CANVAS_WIDTH + SUN_SIZE) / 2
    y1 = y0 + SUN_SIZE
    sun = canvas.create_oval(x0, y0, x1, y1, fill='yellow', outline='yellow')

    while not is_off_screen(canvas, sun):
        canvas.move(sun, 0, 0.8)
        canvas.move('cloud1', 0.1, 0)
        canvas.move('cloud2', 0.1, 0)
        canvas.move('wave', -0.5, 0)
        canvas.update()
        time.sleep(1 / 100)
        y0 = canvas.get_top_y(sun)
        canvas.set_fill_color(sun, get_sun_color(y0))
        canvas.set_outline_color(sun, get_sun_color(y0))
    canvas.set_canvas_background_color('midnight blue')
    canvas.create_text(200, 130, anchor='w', font=('Garamond', '36'), fill='gold', text='Good Night!')
    # After the sunset, a crescent moon appears with a text wishing "Good night!"
    canvas.create_oval(25, 25, 75, 75, fill='goldenrod1', outline='goldenrod1')
    canvas.create_oval(40, 15, 110, 80, fill='midnight blue', outline='midnight blue')

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
