import pygame
import json
import os
import math
import PIL

from colour import Color
from os import path
from pygame import sprite, image, transform, mask, Rect, mixer
from engine.bullet import Bullet
from engine.engine_constants import *



"""
Classe représentant le joueur
arguments: liste des sprites de balles, liste de tous les sprites, id de l'avion à charger, id de la couleure à charger
"""
class Player(sprite.Sprite):
    def __init__(self, bullets, all_sprites, plane_id, color_id):
        sprite.Sprite.__init__(self)

        #on charge toutes l'avion et ses specs
        self.__load(plane_id, color_id)

        self.speedx = 0
        self.speedy = 0
        self.last_shot = pygame.time.get_ticks()
        self.all_sprites = all_sprites
        self.bullets = bullets
        self.index = 0
        self.oldMove = None
        self.image = self.group_image[self.index]
        self.image.set_colorkey(BLACK) 
        self.rect=self.image.get_rect()
        self.rect.centerx= WIDTH / 2
        self.rect.bottom = HEIGHT -10
        self.last_gif = 0

    """
        Analyse du fichier de data JSON avec les specs des avions
        chargement des images de l'avion
        arguments: plane_id: id de l'avion a charger, color_id: id de la couleure à charger
    """
    def __load(self, plane_id, color_id):
        self.group_image = []
        self.ammo_image = []
        self.ammo_number = []
        self.ammo_sounds = []
        self.ammo_index = 0
        #on ouvre le fichier de specs json et on récupère le dossier des animations de l'avion 
        data = json.load(open(SPEC_DIR, "r"))["body"]
        path_image = path.join(data[plane_id]["image"], str(color_id))

        #on charge des specs...
        self.speed = data[plane_id]["vitesse"]
        self.ammo = data[plane_id]["munitions"]
        self.shoot_delay = self.ammo[0]["frequence_de_tir"]
        self.max_life = data[plane_id]["vie"]
        self.actual_life = self.max_life

        #on paramètre le rectangle d'affichage de la vie avec un rect extérieur pour la bordure noir
        #et un intérieur de couleur pour l'affichage de la vie
        self.rect_life = Rect(0 + int(WIDTH*(1/4)), HEIGHT-10, WIDTH-int(WIDTH*(1/2)), 10)
        self.rect_life_inner = self.rect_life.copy()
        self.rect_life_inner.left += 1
        self.rect_life_inner.top += 1
        self.rect_life_inner.width -= 2
        self.rect_life_inner.height -= 2

        #on génère 100 nuances de couleures entre rouge et vert
        self.color_scale = list(Color("red").range_to(Color("green"), 100))
        #on récupère la première que l'on converti du format (1, 1, 1) à (250, 250, 250)
        rgb_color = self.color_scale[99].rgb
        self.actual_color = (int(rgb_color[0]*250), int(rgb_color[1]*250), int(rgb_color[2]*250))

        #on réserve de channels de son pour le son de l'avion et celui de ses munitions
        mixer.set_reserved(PLAYER_CHANNEL)
        mixer.set_reserved(AMMO_CHANNEL)
        #on les récupères, on change leur volume et on lance le son de l'avion à l'infini
        self.ammo_channel = mixer.Channel(AMMO_CHANNEL)
        self.ammo_channel.set_volume(BULLET_SOUND_PLAYER)
        self.sound_channel = mixer.Channel(PLAYER_CHANNEL)
        self.sound_channel.set_volume(SOUND_PLAYER)
        self.sound_channel.play(mixer.Sound(data[plane_id]["sound"]), -1)

        #pour chaque images d'animations de l'avion on les charge, on les transforme et on les ajoute à l'array finale
        for file in os.listdir(path_image):
            img = image.load(path.join(path_image, file)).convert_alpha()
            img = transform.scale(img, (100, 75))
            self.group_image.append(img)
        #idem pour chaque munition avec les trois array representant les images, le nombre de munitions et les sons par munitions
        for file in self.ammo:
            img = image.load(path.join(file["image"])).convert_alpha()
            size = (int(img.get_width()/3), int(img.get_height()/3))
            img = transform.scale(img, size)
            img.set_colorkey(BLACK)
            self.ammo_image.append(img)
            self.ammo_number.append(file["base_munitions"])
            self.ammo_sounds.append(mixer.Sound(file["sound"]))

    """
    Méthode de changement de munition
    """
    def swap_ammo(self):
        #on augment l'index de 1, si celui ci dépasse la taille de l'array il repasse à 0, on change le délai de tire
        self.ammo_index += 1
        if self.ammo_index >= len(self.ammo_image):
            self.ammo_index = 0
        self.shoot_delay = self.ammo[self.ammo_index]["frequence_de_tir"]

    """
    Méthode de mise à jour de la position du joueur, de son animation et de sa vie
    """
    def update(self):
        now = pygame.time.get_ticks()
        #on récupères les evenements clavier
        keystate = pygame.key.get_pressed()

        #on anim les images du joueur en changeant l'index 
        if now - self.last_gif > GIF_SPEED:
            self.last_gif = now
            self.index += 1
            if self.index >= len(self.group_image):
                self.index = 0
        #on change l'image et sa position
        self.image = self.group_image[self.index]
        self.image.set_colorkey(BLACK)
        self.coord = (self.rect.centerx, self.rect.bottom) 
        self.rect=self.image.get_rect()
        self.rect.centerx= self.coord[0]
        self.rect.bottom = self.coord[1]

        #on récupère le ratio de vie et on change la taille de la barre de vie en conséquence
        life_ratio = self.actual_life/self.max_life
        self.rect_life_inner.width = int(life_ratio*(self.rect_life.width-2))

        #système de déplacement avec accéleration, si on appuie sur une touche en continue
        #on additionne la vitesse avec la précédente
        #sinon on la met à une valeur fixe
        #fonctionne seulement pour l'axe Y
        if keystate[pygame.K_LEFT]:
            self.speedx = -SPEED_FACTOR_X*(self.speed/100)    
            self.oldMove = None
        elif keystate[pygame.K_RIGHT]:
            self.speedx = SPEED_FACTOR_X*(self.speed/100)
            self.oldMove = None      
        elif keystate[pygame.K_UP]:
            if self.oldMove == "u":
                self.speedy += -SPEED_FACTOR_Y*(self.speed/100)
            else:
                self.speedy = -SPEED_FACTOR_Y*(self.speed/100)
                self.oldMove = "u"
        elif keystate[pygame.K_DOWN]:
            if self.oldMove == "d":
                self.speedy += SPEED_FACTOR_Y*(self.speed/100)
            else:
                self.speedy = SPEED_FACTOR_Y*(self.speed/100)
                self.oldMove = "d"
        else:
            self.oldMove = None
            self.speedx = 0
            self.speedy = 0
        #si on appuis sur espace alors on tire
        if keystate[pygame.K_SPACE]:
            self.shoot()   
            
        #on fait bouger l'avion en fonction des actions du joueur
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        #on garde le joueur dans la fenêtre de jeu
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT: 
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0
    
    """
    Méthode appelée lorsque le joueur souhaite tirer
    """
    def shoot(self):
        now = pygame.time.get_ticks()
        #vérifier que l'intervalle de temps soit assez grand pour tirer à nouveau et qu'il y ait des munitions
        if now - self.last_shot > self.shoot_delay and self.ammo_number[self.ammo_index] > 0: 
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top, self.ammo_image[self.ammo_index], self.ammo[self.ammo_index], 0)
            self.all_sprites.add(bullet)
            #si le channel des munitions est occupé alors on l'arrete
            if self.ammo_channel.get_busy():
                self.ammo_channel.stop()
            #on joue le son de la balle
            self.ammo_channel.play(self.ammo_sounds[self.ammo_index])
            #on ajoute la balle au groupe de sprites général
            self.bullets.add(bullet)
            #on fait baisse la réserve de balles
            self.ammo_number[self.ammo_index] -= 1

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
            self.actual_color = (
                int(rgb_color[0]*250), int(rgb_color[1]*250), int(rgb_color[2]*250))
            return False
        else:
            return True
    
    """
    Méthode appelée lorsque le joueur ouvre une boite de munitions
    On ajoute un certain nombre de munition passé en argument de la méthode à l'avion 
    """
    def add_ammo(self, number):
        self.ammo_number[self.ammo_index] += number
            
 
