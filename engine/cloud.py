import os
import pygame
from os import path
from pygame import sprite, image, time, mask
from random import randint
from engine.engine_constants import *

"""
Classe gérant l'apparition des nuages,
Arguments: chemin vers les nuages, delai d'apparition des nuages
"""
class Cloud(sprite.Sprite):
    def __init__(self, clouds_path, cloud_delay):
        sprite.Sprite.__init__(self)
        files = os.listdir(clouds_path)
        self.cloud_group = []
        self.last_cloud = time.get_ticks()
        for file in files:
            img = image.load(path.join(clouds_path, file)).convert_alpha()
            self.cloud_group.append(img)
        #on récupère un nuage aléatoirement et on le positionne aléatoirement
        self.image = self.cloud_group[randint(0, len(self.cloud_group)-1)]
        self.rect = self.image.get_rect()
        self.rect.centerx = randint(10, WIDTH-10)
        self.rect.bottom = 0
        self.speedy = SPEED_BACKGROUND
        self.cloud_delay = cloud_delay
        self.stack = 0

    """
    Fonction de mise à jour de la position des nuages
    """
    def update(self):
        now = pygame.time.get_ticks()
        #on fait déplacer le nuages aussi vite que la fond
        self.rect.top += self.speedy
        #si on atteint le délai de spawn
        if now - self.last_cloud > self.cloud_delay:
            #on change l'image et la position ainsi que la stack
            self.last_cloud = now
            cloud_index = randint(0, len(self.cloud_group)-1)
            x = randint(10, WIDTH-10)
            self.image = self.cloud_group[cloud_index]
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.bottom = 0
            self.stack = randint(0, 3)