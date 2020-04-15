#! /usr/bin/python

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import random

from src.scene import Scene
from src.linalg import Vector

seed = 137
def rgen():
    global seed
    seed = (12737 * seed + 37) % 256
    return seed


class Window(Gtk.Window):
    def __init__(self, w, h):
        super().__init__()

        self.connect('destroy', Gtk.main_quit)
        self.set_default_size(w, h)

        drawingarea = Gtk.DrawingArea()
        drawingarea.set_can_focus(True)
        drawingarea.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        drawingarea.connect('draw', self.on_draw)
        drawingarea.connect('key-press-event', self.on_key_press)
        self.add(drawingarea)
        self.drawingarea = drawingarea

        self.center = (w//2, h//2)
        self.scene = Scene(120)


    def __fill_triangle(self, ctx, v1, v2, v3, color):
        # http://www.sunshine2k.de/coding/java/TriangleRasterization/TriangleRasterization.html
        v1, v2, v3 = sorted([v1, v2, v3], key=lambda v: v.y)
        if v2.y == v3.y:
            self.__fill_bottom_flat_triangle(ctx, v1, v2, v3, color)
        elif v1.y == v2.y:
            self.__fill_top_flat_triangle(ctx, v1, v2, v3, color)
        else:
            v = Vector([
                v1.x + (v3.x - v1.x) * (v2.y - v1.y) // (v3.y - v1.y),
                v2.y,
                0,
            ])
            self.__fill_bottom_flat_triangle(ctx, v1, v2, v, color)
            self.__fill_top_flat_triangle(ctx, v2, v, v3, color)


    def __fill_bottom_flat_triangle(self, ctx, v1, v2, v3, color):
        scanlineY = v1.y
        while scanlineY <= v2.y:
            x1 = v1.x + (scanlineY - v1.y) * (v2.x - v1.x) // (v2.y - v1.y)
            x2 = v1.x + (scanlineY - v1.y) * (v3.x - v1.x) // (v3.y - v1.y)
            scanlineY += 1
            self.__draw_line(ctx, x1, x2, scanlineY, color)


    def __fill_top_flat_triangle(self, ctx, v1, v2, v3, color):
        scanlineY = v3.y
        while scanlineY > v1.y:
            x1 = v3.x - (v3.y - scanlineY) * (v3.x - v1.x) // (v3.y - v1.y)
            x2 = v3.x - (v3.y - scanlineY) * (v3.x - v2.x) // (v3.y - v2.y)
            scanlineY -= 1
            self.__draw_line(ctx, x1, x2, scanlineY, color)


    def __draw_line(self, ctx, x1, x2, y, color):
        if x2 < x1:
            x1, x2 = x2, x1

        while x1 < x2:
            # https://en.wikipedia.org/wiki/Dither
            if color * 300 >= rgen():
                ctx.set_source_rgb(0, 0, 0)
            else:
                ctx.set_source_rgb(1, 1, 1)
            ctx.rectangle(x1 + self.center[0], -y + self.center[1], 1, 1)
            ctx.fill()
            x1 += 1


    def on_draw(self, _, ctx):
        ctx.save()
        ctx.set_line_width(1)

        ctx.set_source_rgb(1, 1, 1)
        ctx.new_path()
        ctx.move_to(0, 0)
        ctx.line_to(512, 0)
        ctx.line_to(512, 256)
        ctx.line_to(0, 256)
        ctx.close_path()
        ctx.fill()

        for v1, v2, v3, cl in self.scene.iter_facets():
            self.__fill_triangle(ctx, v1, v2, v3, cl)
            ctx.set_source_rgb(0, 0, 0)
            ctx.new_path()
            ctx.move_to(v1.x+self.center[0], -v1.y+self.center[1])
            ctx.line_to(v2.x+self.center[0], -v2.y+self.center[1])
            ctx.line_to(v3.x+self.center[0], -v3.y+self.center[1])
            ctx.close_path()
            ctx.stroke()

        ctx.restore()


    def on_key_press(self, _, e):
        if e.keyval == Gdk.KEY_Up:
            self.scene.rotate_x(-1)
        elif e.keyval == Gdk.KEY_Down:
            self.scene.rotate_x(1)
        elif e.keyval == Gdk.KEY_Left:
            self.scene.rotate_y(1)
        elif e.keyval == Gdk.KEY_Right:
            self.scene.rotate_y(-1)

        self.drawingarea.queue_draw()


def main():
    win = Window(512, 256)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
