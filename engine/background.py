from pygame import sprite, image
from engine.engine_constants import *
from os import path

import pygame
import os
import json

"""
Classe de gestion des fonds
Arguments: image du background, new : si c'est le premier fond ou pas
"""
class Background(sprite.Sprite):
    def __init__(self, image, new):
        sprite.Sprite.__init__(self)

        self.image = image
        self.image.set_colorkey(BLACK) 
        self.rect=self.image.get_rect()
        #si c'est le premier on le position différemment
        if new:
            self.rect.bottom = 10
        else:
            self.rect.top = -300
        self.speedy = SPEED_BACKGROUND

    """
    Méthode de mise à jour de la postion du fond
    """
    def update(self):
        #on déplace verticalement le fond
        old_rect = self.rect.top
        self.rect = self.image.get_rect()
        self.rect.left = 0
        self.rect.top = old_rect + self.speedy

