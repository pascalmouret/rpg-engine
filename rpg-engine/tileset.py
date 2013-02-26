# -*- coding: utf8 -*-
__author__ = 'pascal'

from pyglet.image import ImageGrid, TextureGrid
from pyglet.sprite import Sprite

from mixins import PositionMixin


class Tile(Sprite, PositionMixin):
    pass


class EmptyTile(Tile):
    def draw(self):
        pass


class TileSet(object):
    tile_size = 0

    def __init__(self, image, high, wide):
        self._grid = ImageGrid(image, high, wide)
        self._grid = TextureGrid(self._grid)
        if self._grid[0].width != self._grid[0].height:
            raise Exception('Tiles must be quadratic!')
        self.tile_size = self._grid[0].width
        self._default_tile = Tile(self._grid[91])

    def get_default_tile(self):
        return Tile(self._grid[91])

    def get_tile_by_id(self, tile_id):
        return Tile(self._grid[tile_id])