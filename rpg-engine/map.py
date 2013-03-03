# -*- coding: utf8 -*-
__author__ = 'pascal'
__xml_type__ = 'map'


from pyglet.graphics import Batch, OrderedGroup

from tileset import EmptyTile

from math import ceil


class Map(object):
    tile_size   = 0
    width       = 0
    height      = 0
    px_height   = 0
    px_width    = 0
    layers      = 0

    _matrix     = []
    _batch      = None
    _groups     = []
    _pos_x      = 0
    _pos_y      = 0
    _window_x   = 0
    _window_y   = 0

    _prev_start_x   = None
    _prev_start_y   = None
    _prev_end_x     = None
    _prev_end_y     = None

    _xml_type   = __xml_type__
    _xml_source = ''

    def __init__(self, tile_size, width, height, layers):
        self._batch = Batch()
        self.tile_size = tile_size
        self.width = width
        self.height = height
        self.px_height = height * self.tile_size
        self.px_width = width * self.tile_size
        self.layers = layers
        for z in range(0, layers):
            self._groups.insert(z, OrderedGroup(z))
        for x in range(0, self.width):
            self._matrix.append([])
            for y in range(0, self.height):
                self._matrix[x].append([])
                for z in range(0, self.layers):
                    tile = EmptyTile()
                    tile.set_absolute_position(x * self.tile_size, y * self.tile_size)
                    self._matrix[x][y].append(tile)

    def set_tile(self, x, y, tile_list):
        for i, tile in enumerate(tile_list):
            self.set_tile_layer(x, y, i, tile)

    def get_tile(self, x, y):
        return self._matrix[x][y]

    def set_tile_layer(self, x, y, z, tile):
        tile.set_absolute_position(x * self.tile_size, y * self.tile_size)
        tile.group = self._groups[z]
        self._matrix[x][y][z] = tile

    def get_tile_layer(self, x, y, z):
        return self._matrix[x][y][z]

    def update(self, window_x, window_y, pos_x, pos_y):
        if (window_x, window_y, pos_x, pos_y) == (self._window_x, self._window_y, self._pos_x, self._pos_y):
            return
        self._window_x, self._window_y, self._pos_x, self._pos_y = window_x, window_y, pos_x, pos_y
        offset_x = (window_x / 2) - pos_x
        offset_y = (window_y / 2) - pos_y
        start_x = -1 * offset_x / self.tile_size
        start_y = -1 * offset_y / self.tile_size
        if start_x < 0:
            start_x = 0
        if start_y < 0:
            start_y = 0
        end_x = start_x + int(ceil(window_x / self.tile_size)) + 1
        end_y = start_y + int(ceil(window_y / self.tile_size)) + 1
        if end_x >= self.width:
            end_x = self.width - 1
        if end_y >= self.height:
            end_y = self.height - 1
        if not self._prev_start_x or not self._prev_start_y or not self._prev_end_x or not self._prev_end_y:
            self._prev_start_x, self._prev_start_y = start_x, start_y
            self._prev_end_x, self._prev_end_y = end_x, end_y
        for x in range(min(start_x, self._prev_start_x), max(end_x, self._prev_end_x) + 1):
            for y in range(min(start_y, self._prev_start_y), max(end_y, self._prev_end_y) + 1):
                for z in range(0, self.layers):
                    tile = self._matrix[x][y][z]
                    if tile.is_empty:
                        continue
                    if not start_x <= x <= end_x or not start_y <= y <= end_y:
                        tile.batch = None
                        continue
                    tile.x = tile.pos_x + offset_x
                    tile.y = tile.pos_y + offset_y
                    tile.batch = self._batch
        self._prev_start_x, self._prev_start_y = start_x, start_y
        self._prev_end_x, self._prev_end_y = end_x, end_y

    def draw(self):
        self._batch.draw()

    def xml_export(self, destination):
        from lxml import etree
        import tileset
        xml_root = etree.Element('root', type=self._xml_type)
        xml_meta = etree.SubElement(xml_root, 'meta')
        xml_include = etree.SubElement(xml_root, 'includes')
        xml_map = etree.SubElement(xml_root, 'map')
        # meta
        etree.SubElement(xml_meta, 'tile_size', value=str(self.tile_size))
        etree.SubElement(xml_meta, 'width', value=str(self.width))
        etree.SubElement(xml_meta, 'height', value=str(self.height))
        # map
        tilesets = []
        for x, column in enumerate(self._matrix):
            for y, tile in enumerate(column):
                if tile.is_empty:
                    continue
                if tile.tileset not in tilesets:
                    tilesets.append(tile.tileset)
                tileset_id = tilesets.index(tile.tileset)
                etree.SubElement(xml_map, 'tile', x=str(x), y=str(y),
                                 tileset_id=str(tileset_id), tile_id=str(tile.tile_id))
        # includes
        for i, ts in enumerate(tilesets):
            etree.SubElement(xml_include, tileset.__xml_type__, src=ts._xml_source.__str__(), tileset_id=str(i))

        destination.write(etree.tostring(xml_root, pretty_print=True))


def xml_load(source):
    from lxml import etree
    import tileset
    xml_root = etree.parse(source)
    xml_meta = xml_root.findall('meta')[0]
    xml_include = xml_root.findall('includes')[0]
    xml_map = xml_root.findall('map')[0]
    # meta
    tile_size = int(xml_meta.findall('tile_size')[0].get('value'))
    width = int(xml_meta.findall('width')[0].get('value'))
    height = int(xml_meta.findall('height')[0].get('value'))
    layers = int(xml_meta.findall('layers')[0].get('value'))
    mp = Map(tile_size, width, height, layers)
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
        mp.set_tile_layer(x, y, layer, tile)

    mp._xml_source = source
    return mp