# -*- coding: utf8 -*-
__author__ = 'pascal'
__xml_type__ = 'map'


from pyglet.graphics import Batch, OrderedGroup

from tileset import EmptyTile

from math import ceil


class Map(object):
    _width = 0
    _height = 0
    _tile_size = 0
    _layers = 0
    _supertile_size = 0

    _matrix = []
    _supertiles = []
    _groups = []
    _visible_supertiles = []

    _window_x = 0
    _window_y = 0
    _center_x = 0
    _center_y = 0

    _super_x1 = 0
    _super_y1 = 0
    _super_x2 = 0
    _super_y2 = 0

    _xml_type = __xml_type__

    def __init__(self, width, height, layers, tile_size, supertile_size):
        self._width = width
        self._height = height
        self._tile_size = tile_size
        self._layers = layers
        self._supertile_size = supertile_size
        self._create_matrix()
        self._create_supertiles()

        for z in range(0, self._layers):
            self._groups.insert(z, OrderedGroup(z))

    @property
    def window_x(self):
        return self._window_x

    @window_x.setter
    def window_x(self, value):
        self._window_x = value

    @property
    def window_y(self):
        return self._window_y

    @window_y.setter
    def window_y(self, value):
        self._window_y = value

    def set_tile(self, x, y, z, tile):
        tile.set_absolute_position(x * self._tile_size, y * self._tile_size)
        tile.group = self._groups[z]
        tile.batch = self._get_supertile(x, y)
        self._matrix[x][y][z] = tile

    def set_absolute_center(self, x, y):
        if (x, y) == (self._center_x, self._center_y):
            return
        self._center_x, self._center_y = x, y

        x1, y1, x2, y2, offset_x, offset_y = self._get_visible_tiles()
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for z in range(0, self._layers):
                    tile = self._matrix[x][y][z]
                    if tile.is_empty:
                        continue
                    tile.x = tile.pos_x + offset_x
                    tile.y = tile.pos_y + offset_y

        self._set_visible_supertiles(x1, y1, x2, y2)

    def draw(self):
        for supertile in self._visible_supertiles:
            supertile.draw()

    def _create_matrix(self):
        for x in range(0, self._width):
            self._matrix.append([])
            for y in range(0, self._height):
                self._matrix[x].append([])
                for z in range(0, self._layers):
                    tile = EmptyTile()
                    tile.set_absolute_position(x * self._tile_size, y * self._tile_size)
                    self._matrix[x][y].append(tile)

    def _create_supertiles(self):
        for super_x in range(0, self._width / self._supertile_size):
            self._supertiles.append([])
            for super_y in range(0, self._height / self._supertile_size):
                batch = Batch()
                self._supertiles[super_x].append(batch)
                for x in range(super_x * self._supertile_size, (super_x + 1) * self._supertile_size):
                    for y in range(super_y * self._supertile_size, (super_y + 1) * self._supertile_size):
                        for z in range(0, self._layers):
                            self._matrix[x][y][z].batch = batch

    def _get_visible_tiles(self):
        offset_x = (self._window_x / 2) - self._center_x
        offset_y = (self._window_y / 2) - self._center_y

        x1 = -1 * offset_x / self._tile_size
        y1 = -1 * offset_y / self._tile_size
        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0

        x2 = x1 + int(ceil(self.window_x / self._tile_size)) + 1
        y2 = y1 + int(ceil(self.window_y / self._tile_size)) + 1
        if x2 >= self._width:
            x2 = self._width - 1
        if y2 >= self._height:
            y2 = self._height - 1

        return x1, y1, x2, y2, offset_x, offset_y

    def _set_visible_supertiles(self, x1, y1, x2, y2):
        super_x1 = x1 / self._supertile_size
        super_y1 = y1 / self._supertile_size
        super_x2 = x2 / self._supertile_size + 1
        super_y2 = y2 / self._supertile_size + 1

        if (super_x1, super_y1, super_x2, super_y2) == (self._super_x1, self._super_y1, self._super_x2, self._super_y2):
            return self._visible_supertiles
        (self._super_x1, self._super_y1, self._super_x2, self._super_y2) = (super_x1, super_y1, super_x2, super_y2)

        visible_supertiles = []
        for x in range(super_x1, super_x2):
            for y in range(super_y1, super_y2):
                visible_supertiles.append(self._supertiles[x][y])

        self._visible_supertiles = visible_supertiles

    def _get_supertile(self, x, y):
        return self._supertiles[int(x) / self._supertile_size][int(y) / self._supertile_size]


def xml_load(source):
    from lxml import etree
    import tileset
    xml_root = etree.parse(source)
    xml_meta = xml_root.findall('meta')[0]
    xml_include = xml_root.findall('includes')[0]
    xml_map = xml_root.findall('map')[0]
    # meta
    width = int(xml_meta.findall('width')[0].get('value'))
    height = int(xml_meta.findall('height')[0].get('value'))
    layers = int(xml_meta.findall('layers')[0].get('value'))
    tile_size = int(xml_meta.findall('tile_size')[0].get('value'))
    supertile_size = int(xml_meta.findall('supertile_size')[0].get('value'))
    mp = Map(width, height, layers, tile_size, supertile_size)
    # fieldsets
    tilesets = []
    for include in xml_include:
        if include.tag == tileset.__xml_type__:
            tilesets.insert(int(include.get('tileset_id')), tileset.xml_load(include.get('src')))
    # tiles
    for tile_data in xml_map:
        x, y = int(tile_data.get('x')), int(tile_data.get('y'))
        ts = tilesets[int(tile_data.get('tileset_id'))]
        tile_id = int(tile_data.get('tile_id'))
        layer = int(tile_data.get('layer'))
        tile = ts.get_tile_by_id(tile_id)
        mp.set_tile(x, y, layer, tile)

    mp._xml_source = source
    return mp