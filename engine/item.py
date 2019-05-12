from pygame import image, sprite, time, transform, mask
from engine.engine_constants import *
from random import randint
from os import path
import os

class Item(sprite.Sprite):
    def __init__(self, image):
        sprite.Sprite.__init__(self)
        self.image = image
        self.index = 0
        # get the mask for the maskcollide method otherwise the mask will be generated on time (performance issues)
        self.mask = mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = randint(10, WIDTH-10)
        self.rect.bottom = 0
        self.speedy = SPEED_BACKGROUND
        self.dead = False

    def update(self):
        self.rect.top += self.speedy
    
    def collided(self):
        del self