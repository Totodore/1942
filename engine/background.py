from pygame import sprite, image
from engine.engine_constants import *
from os import path

import pygame
import os
import json

class Background(sprite.Sprite):
    def __init__(self, image, new):
        sprite.Sprite.__init__(self)

        self.image = image
        self.image.set_colorkey(BLACK) 
        self.rect=self.image.get_rect()
        if new:
            self.rect.bottom = 10
        else:
            self.rect.top = -300
        self.speedy = SPEED_BACKGROUND

    def update(self):
        old_rect = self.rect.top
        self.rect = self.image.get_rect()
        self.rect.left = 0
        self.rect.top = old_rect + self.speedy

