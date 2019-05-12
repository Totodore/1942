import pygame
from os import path
from engine.engine_constants import *

"""
Classe gérant chaque balle
Arguments: x,y : position, image : image de la balle, ammo : specs, angle : angle de déplacement de la balle
"""
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image, ammo, angle):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = image
        self.angle = angle            

        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = ammo["vitesse"]
        self.strength = ammo["degats"]

    """
    Fonction de mise à jour de la position
    """
    def update(self):
        #si l'angle est inversé on inverse l'ajout en y
        if self.angle == 180:
            self.rect.y += AMMO_SPEED_FACTOR*(self.speedy/100)
            #si ca part en dehors de l'écran on enlève
            if self.rect.top > HEIGHT:
                self.kill()
        else:
            #si ca part en dehors de l'écran on enlève
            self.rect.y -= self.speedy
            if self.rect.bottom < 0:
                self.kill()
