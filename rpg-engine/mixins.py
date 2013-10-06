# -*- coding: utf8 -*-
__author__ = 'pascal'


class PositionMixin(object):
    _pos_x = 0
    _pos_y = 0

    @property
    def pos_x(self):
        return self._pos_x

    @pos_x.setter
    def pos_x(self, value):
        self._pos_x = value

    @property
    def pos_y(self):
        return self._pos_y

    @pos_y.setter
    def pos_y(self, value):
        self._pos_y = value

    def set_absolute_position(self, x, y):
        self.pos_x, self.pos_y = x, y

    def get_absolute_position(self):
        return self.pos_x, self.pos_y