# -*- coding: utf8 -*-
__author__ = 'pascal'


class PositionMixin(object):
    pos_x = 0
    pos_y = 0

    def set_absolute_position(self, x, y):
        self.pos_x, self.pos_y = x, y

    def get_absolute_position(self):
        return self.pos_x, self.pos_y