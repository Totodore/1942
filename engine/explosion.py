import os
from os import path
from engine.engine_constants import *
from pygame import image, transform, time, sprite

"""
Fonction de chargement des deux explosinos différentes
"""
def load_expl():
    normal_expl = []
    ammo_expl = []
    for file in os.listdir(EXPLOSION_DIR):
        img = image.load(path.join(EXPLOSION_DIR, file)).convert_alpha()
        img = transform.scale(img, (75, 75))
        normal_expl.append(img)
    files = os.listdir(AMMO_DIR)
    files.sort()
    for file in files:
        img = image.load(path.join(AMMO_DIR, file)).convert_alpha()
        img = transform.scale(img, (65, 65))
        ammo_expl.append(img)

    return normal_expl, ammo_expl

"""
Classe affichant les explosions
Arguments: center: position de l'explosion, images: liste d'images de l'explosion
"""
class Explosion(sprite.Sprite):
    def __init__(self, center, images):
        sprite.Sprite.__init__(self)
        self.images_cluster = images        
        
        #récupèration et positionnement des images
        self.image = self.images_cluster[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame_index = 0
        self.last_update = time.get_ticks()
        self.frame_rate = 20

    """
    Méthode appelée pour mettre à jour l'animation et la position de l'explosion
    """
    def update(self):
        now = time.get_ticks()
        #si on a dépassé le délai d'animation
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_index += 1
            #si on atteint la fin de l'animation on stop tout
            if self.frame_index == len(self.images_cluster):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.images_cluster[self.frame_index]
                self.rect = self.image.get_rect()
                self.rect.center = center
