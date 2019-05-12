import pygame
import random
import json
import os
import math
from colour import Color
from engine.engine_constants import *
from engine.bullet import Bullet
from os import path
from pygame import sprite, image, transform, time, draw, Rect, mixer

global player_id
mob_data_d = []
player_id = 0

"""
    Chargement de toutes les images nécessaires à l'apparition aléatoire des ennemies
    retourne un tuple avec le json et les images ennemies
"""
def load(player_id_):
    ennemies_images = []
    player_id = player_id_
    #on récupère le fichier json des avions
    mob_data = json.load(open(SPEC_DIR, "r"))["body"]
    del mob_data[player_id] #on supprime l'avion du joueur dans celui-ci pour pas qu'il apparaisse dans les ennemies
    #pour chaque avion
    for plane in mob_data:
        colors = []
        #pour chaque couleur
        for folder in os.listdir(plane["image"]):
            #pour chaque images
            imgs = []
            for file in os.listdir(path.join(plane["image"], folder)):
                #on charge et on transforme chaque image et on l'ajoute à l'array colors
                img = image.load(path.join(plane["image"], folder, file)).convert_alpha()
                img = transform.scale(img, (75, 50))
                img = transform.rotate(img, 180)
                imgs.append(img)
            colors.append(imgs)

        ennemies_images.append(colors)
    return (mob_data, ennemies_images)   

"""
Classe représentant les ennemis
arguments: liste des sprites de balles, liste de tous les sprites, tuple retourné par la fonction ci-dessus, objet fenêtre de pygame
"""
class Mob(sprite.Sprite):
    def __init__(self, bullets, all_sprites, mob_data, screen):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.last_gif = 0
        self.image_index = 0
        self.last_shot = 0

        self.mob_data = mob_data[0]
        self.ennemies_images = mob_data[1]
        self.all_sprites = all_sprites
        self.bullets = bullets

        #on récupère aléatoirement un avion et une couleure depuis la banque d'images d'avion fournie
        self.plane_index = random.randint(0, len(self.ennemies_images) - 1)
        self.color_index = random.randint(0, len(self.ennemies_images[self.plane_index]) -1)

        #on récupère les animations et les stats
        self.group_image = self.ennemies_images[self.plane_index][self.color_index]
        self.speed = self.mob_data[self.plane_index]["vitesse"]
        self.ammo = self.mob_data[self.plane_index]["munitions"][0]
        self.shoot_delay = self.ammo["frequence_de_tir"]
        self.max_life = self.mob_data[self.plane_index]["vie"]
        self.actual_life = self.max_life
        self.random_shoot = self.mob_data[self.plane_index]["random_shoot"]

        #on récupère l'image de munitions et on la transforme
        self.ammo_image = image.load(self.ammo["image"]).convert_alpha()
        self.ammo_image = transform.rotate(self.ammo_image, 180)
        size = (int(self.ammo_image.get_width()/4), int(self.ammo_image.get_height()/4))
        self.ammo_image = transform.scale(self.ammo_image, size)
        self.image = self.group_image[0]
        #on génère une position et une direction aléatoire
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.dir = (random.randrange(-5, 5), random.randrange(0, 10))
        self.rect_life = self.rect.copy()
        self.rect_life.top -= 10
        self.rect_life_inner = self.rect.copy()

        #on génère 100 nuances de couleures 
        self.color_scale = list(Color("red").range_to(Color("green"), 100))
        #on récupère la première que l'on converti du format (1, 1, 1) à (250, 250, 250)
        rgb_color = self.color_scale[99].rgb
        self.actual_color = (int(rgb_color[0]*250), int(rgb_color[1]*250), int(rgb_color[2]*250))

        # self.channel = mixer.find_channel()
        # self.channel.set_volume(BULLET_SOUND_ENNEMY)
        # self.sound = mixer.Sound(self.ammo["sound"])

    """
        Méthode de mise à jour de l'objet, changement des positions, des couleures et animation des ennemies
    """
    def update(self):
        now = time.get_ticks()
        #on change l'image de l'avion si le délai est écoulé pour avoir une animation
        if now - self.last_gif > GIF_SPEED:
            self.last_gif = now
            self.image_index += 1
            if self.image_index > len(self.group_image) -1:
                self.image_index = 0
        #on récupère l'image en fonction de l'index d'animation
        self.image = self.group_image[self.image_index]
        self.image.set_colorkey(BLACK)

        #on change la position en fonction du vecteur aléatoirement créé
        self.coords = (self.rect.x, self.rect.y)
        self.rect = self.image.get_rect()
        self.rect.x = self.coords[0]
        self.rect.y = self.coords[1]
        self.rect.x += self.dir[0]
        self.rect.y += self.dir[1]
        
        #on génère des rectangles de couleur pour afficher la barre de vie
        #un rectangle noir autour pour les bordures et un rectangle de couleure à l'intérieur
        self.rect_life = self.rect.copy()
        self.rect_life.width = self.rect.width
        self.rect_life.height = 10
        self.rect_life.center = self.rect.center
        self.rect_life.top -= 10
        self.rect_life_inner = self.rect_life.copy()
        self.rect_life_inner.x += 1
        self.rect_life_inner.y += 1

        #on récupère le ratio de vie et on change la barre de vie en conséquence
        life_ratio = self.actual_life/self.max_life
        self.rect_life_inner.width = int(life_ratio*(self.rect_life.width-2))
        self.rect_life_inner.height -= 2 

        #on tire aléatoirement
        shoot = random.randint(0,self.random_shoot)
        if shoot == 3:
            self.shoot()

    """
    Méthode pour tirer si seulement le delai de tir est écoulé
    """
    def shoot(self):
        now = time.get_ticks()
        if now - self.last_shot > self.shoot_delay: 
            self.last_shot = now
            self.bullet = Bullet(self.rect.centerx, self.rect.bottom + 10, self.ammo_image, self.ammo, 180)
            self.all_sprites.add(self.bullet)
            self.bullets.add(self.bullet)
            # if self.channel.get_busy():
                # self.channel.stop()
            # self.channel.play(self.sound)

    """
    Méthode appelée lorsque l'ennemie se prend une balle
    Retourne True si le mob est mort sinon retourne false et change la couleure actuel
    """
    def shot(self, strength):
        self.actual_life -= strength
        #si il y a encore de la vie
        if self.actual_life > 0:
            life_ratio = self.actual_life/self.max_life
            life_ratio = int(life_ratio*100)
            rgb_color = self.color_scale[life_ratio].rgb
            self.actual_color = (int(rgb_color[0]*250), int(rgb_color[1]*250), int(rgb_color[2]*250))
            return False
        else:
            return True
