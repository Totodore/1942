import os
import pygame
from os import path
from pygame import sprite, image, time, mask
from random import randint
from engine.engine_constants import *

class Cloud(sprite.Sprite):
    def __init__(self, clouds_path, cloud_delay):
        sprite.Sprite.__init__(self)
        files = os.listdir(clouds_path)
        self.cloud_group = []
        self.last_cloud = time.get_ticks()
        for file in files:
            img = image.load(path.join(clouds_path, file)).convert_alpha()
            self.cloud_group.append(img)
        self.image = self.cloud_group[randint(0, len(self.cloud_group)-1)]
        # get the mask for the maskcollide method otherwise the mask will be generated on time (performance issues)
        self.rect = self.image.get_rect()
        self.rect.centerx = randint(10, WIDTH-10)
        self.rect.bottom = 0
        self.speedy = SPEED_BACKGROUND
        self.cloud_delay = cloud_delay
        self.stack = 0


    def update(self):
        now = pygame.time.get_ticks()
        self.rect.top += self.speedy
        if now - self.last_cloud > self.cloud_delay:
            self.last_cloud = now
            cloud_index = randint(0, len(self.cloud_group)-1)
            x = randint(10, WIDTH-10)
            self.image = self.cloud_group[cloud_index]
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.bottom = 0
            self.stack = randint(0, 3)

            #on soustrait la hauteur du jeu pour que le nuage apparraisse avant qu'on le voit


