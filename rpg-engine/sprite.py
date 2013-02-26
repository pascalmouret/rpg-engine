# -*- coding: utf8 -*-
__author__ = 'pascal'

from pyglet.sprite import Sprite


class MovingSprite(Sprite):
    speed = 0

    _dest_x = 0
    _dest_y = 0

    def __init__(self, *args, **kwargs):
        super(Sprite, self).__init__(*args, **kwargs)
        self.image.anchor_x = self.image.height / 2
        self.image.anchor_y = self.image.width / 2

    @property
    def moving(self):
        if self.x != self._dest_x or self.y != self._dest_y:
            return True
        return False

    def set_position(self, x, y):
        super(MovingSprite, self).set_position(x, y)
        self._dest_x = self.x
        self._dest_y = self.y

    def move_absolute(self, x=0, y=0):
        self._dest_x = x
        self._dest_y = y

    def move_delta(self, dx=0, dy=0):
        self._dest_x = self.x + dx
        self._dest_y = self.y + dy

    def _deltas(self):
        # TODO: can this be done more elegant?
        offset_x = abs(float(self._dest_x - self.x))
        offset_y = abs(float(self._dest_y - self.y))
        # if there is only one axis it's simple
        if offset_x == 0:
            dx, dy = self.speed, 0
        if offset_y == 0:
            dx, dy = 0, self.speed
        else:
            # distribute the speed
            ratio = (offset_x / offset_y)
            dx = round((float(self.speed) / (ratio + 1.)) * ratio)
            dy = round(self.speed - dx)
        # is the delta bigger than the offset?
        if offset_x - dx <= 0:
            dx -= abs(offset_x - dx)
        if offset_y - dy <= 0:
            dy -= abs(offset_y - dy)
        # is the delta positive or negative?
        if self._dest_x < self.x:
            dx = -dx
        if self._dest_y < self.y:
            dy = -dy
        return int(dx), int(dy)

    def update(self):
        if self.moving:
            dx, dy = self._deltas()
            self.x += dx
            self.y += dy
