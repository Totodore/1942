import pygame
from os import path
from engine.engine_constants import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image, ammo, angle):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.angle = angle            
        # get the mask for the maskcollide method otherwise the mask will be generated on time (performance issues)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = ammo["vitesse"]
        self.strength = ammo["degats"]

    def update(self):
        # le tuer si il va en haut de l'écran
        if self.angle == 180:
            self.rect.y += AMMO_SPEED_FACTOR*(self.speedy/100)
            if self.rect.top > HEIGHT:
                self.kill()
        else:
            self.rect.y -= self.speedy
            if self.rect.bottom < 0:
                self.kill()
