# -*- coding: utf8 -*-
__author__ = 'pascal'


from pyglet.graphics import Batch

from tileset import EmptyTile


class Map(object):
    tileset     = None
    height      = 0
    width       = 0
    px_height   = 0
    px_width    = 0

    _matrix = []
    _batch = None
    _pos_x = 0
    _pos_y = 0
    _window_x = 0
    _window_y = 0

    _prev_start_x = None
    _prev_start_y = None
    _prev_end_x = None
    _prev_end_y = None

    def __init__(self, tileset, width=10, height=10):
        self._batch = Batch()
        self.tileset = tileset
        self.width = width
        self.height = height
        self.px_height = height * self.tileset.tile_size
        self.px_width = width * self.tileset.tile_size
        for x in range(0, self.width):
            self._matrix.append([])
            for y in range(0, self.height):
                # debug #
                tile = self.tileset.get_default_tile()
                # debug #
                tile.set_absolute_position(x * self.tileset.tile_size, y * self.tileset.tile_size)
                self._matrix[x].append(tile)

    def update(self, window_x, window_y, pos_x, pos_y):
        if (window_x, window_y, pos_x, pos_y) == (self._window_x, self._window_y, self._pos_x, self._pos_y):
            return
        self._window_x, self._window_y, self._pos_x, self._pos_y = window_x, window_y, pos_x, pos_y
        offset_x = (window_x / 2) - pos_x
        offset_y = (window_y / 2) - pos_y
        start_x = -1 * offset_x / self.tileset.tile_size
        start_y = -1 * offset_y / self.tileset.tile_size
        if start_x < 0:
            start_x = 0
        if start_y < 0:
            start_y = 0
        end_x = start_x + (window_x / self.tileset.tile_size) + 1
        end_y = start_y + (window_y / self.tileset.tile_size) + 1
        if end_x > self.width - 1:
            end_x = self.width - 1
        if end_y > self.height - 1:
            end_y = self.height - 1
        if not self._prev_start_x or not self._prev_start_y or not self._prev_end_x or not self._prev_end_y:
            self._prev_start_x, self._prev_start_y = start_x, start_y
            self._prev_end_x, self._prev_end_y = end_x, end_y
        for x in range(min(start_x, self._prev_start_x), max(end_x, self._prev_end_x)):
            for y in range(min(start_y, self._prev_start_y), max(end_x, self._prev_end_y)):
                if not start_x <= x <= end_x or not start_y <= y <= end_y:
                    self._matrix[x][y].batch = None
                    continue
                tile = self._matrix[x][y]
                tile.x = tile.pos_x + offset_x
                tile.y = tile.pos_y + offset_y
                tile.batch = self._batch
        self._prev_start_x, self._prev_start_y = start_x, start_y
        self._prev_end_x, self._prev_end_y = end_x, end_y

    def draw(self):
        self._batch.draw()
