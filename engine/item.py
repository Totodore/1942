from pygame import image, sprite, time, transform, mask
from engine.engine_constants import *
from random import randint
from os import path
import os

"""
Classe de gestion des items dans le jeu
Pour l'instant seulement les caisses de munitions
Arguments: image: image de l'item
"""
class Item(sprite.Sprite):
    def __init__(self, image):
        sprite.Sprite.__init__(self)
        self.image = image
        #On récupère le mask pour la méthode mask_collide
        self.mask = mask.from_surface(self.image)

        #on place la boite aléatoirement
        self.rect = self.image.get_rect()
        self.rect.centerx = randint(10, WIDTH-10)
        self.rect.bottom = 0
        self.speedy = SPEED_BACKGROUND
        self.dead = False

    #on la fait bouger avec l'arriere plan
    def update(self):
        self.rect.top += self.speedy
    