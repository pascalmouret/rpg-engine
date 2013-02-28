# -*- coding: utf8 -*-
__author__ = 'pascal'
__xml_type__ = 'tileset'

from pyglet.image import ImageGrid, TextureGrid
from pyglet.image import load as load_image
from pyglet.sprite import Sprite

from mixins import PositionMixin


class BaseTile(PositionMixin):
    is_empty = False


class EmptyTile(BaseTile):
    is_empty = True

    def draw(self):
        pass


class Tile(Sprite, BaseTile):
    _tileset = None
    _tile_id = None

    def __init__(self, tileset, tile_id, image):
        self._tileset = tileset
        self._tile_id = tile_id
        super(Tile, self).__init__(image)

    @property
    def tileset(self):
        return self._tileset

    @property
    def tile_id(self):
        return self._tile_id


class TileSet(object):
    _tile_size = 0

    _img_src = ''
    _width = 0
    _height = 0

    _xml_type = 'tileset'
    _xml_source = __xml_type__

    def __init__(self, filepath, width, height):
        self._img_src = filepath
        self._height = height
        self._width = width
        self._grid = TextureGrid(ImageGrid(load_image(self._img_src), self._height, self._width))
        if self._grid[0].width != self._grid[0].height:
            raise Exception('Tiles must be quadratic!')
        self._tile_size = self._grid[0].width

    def get_default_tile(self):
        return Tile(self, 91, self._grid[91])

    def get_tile_by_id(self, tile_id):
        return Tile(self, tile_id, self._grid[tile_id])

    @property
    def tile_size(self):
        return self._tile_size

    def export(self, destination):
        from lxml import etree
        # structure
        xml_root = etree.Element('root', type=self._xml_type)
        xml_meta = etree.SubElement(xml_root, 'meta')
        # fill up meta
        etree.SubElement(xml_meta, 'image', src=self._img_src)
        etree.SubElement(xml_meta, 'width', value=str(self._width))
        etree.SubElement(xml_meta, 'height', value=str(self._height))
        # write to file-like object
        destination.write(etree.tostring(xml_root, pretty_print=True))


def load(source):
    from lxml import etree
    xml_root = etree.parse(source)
    xml_meta = xml_root.findall('meta')[0]
    # get meta
    src = xml_meta.findall('image')[0].get('src')
    width = xml_meta.findall('width')[0].get('value')
    height = xml_meta.findall('height')[0].get('value')
    # finalize
    tileset = TileSet(src, int(width), int(height))
    tileset._xml_source = source
    return tileset