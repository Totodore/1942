import pygame
import json
import os
import math
import PIL
from os import path
from pygame import sprite, image, transform, mask, font, time
from engine.bullet import Bullet
from engine.engine_constants import *

"""
Classe de gestion de l'ATH, les informations affichées à l'écran
Arguments: player: player objet, surface : objet fenetre
"""
class ATH(sprite.Sprite):
    def __init__(self, player, surface):
        sprite.Sprite.__init__(self)

        #on recp les specs et on charge l'image
        self.surface = surface
        self.ammo_data = player.ammo
        self.ammo_number = player.ammo_number
        self.player = player
        self.image = image.load(path.join(ATH_DIR, "ath.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
        self.score = 0
        self.grow_q = (530, 540)
        self.grow_q_delay = 40
        self.q_top = self.grow_q[0]
        self.grow_q_forward = True
        self.last_grow = 0
        self.ammo_image = []

    """
    Méthode de calcul du score en fonction du nombre de tués et du temps écoulé    
    """
    def process_score(self, killed, time):
        killed *= 100
        time = int(time/100)
        return killed + time

    """
    Méthode d'affichage du texte
    Arguments : text : string, size : taille d'écriture, x,y : position, right : si c'est aligné à droite ou pas
    """
    def __draw_text(self, text, size, x, y, right, font_name=None):
        if font_name:
            font_t = font.Font(font.get_default_font(), size)
        else:
            font_t = font.Font(path.join(FONT_DIR, "ath.ttf"), size)
        text_surface = font_t.render(text, True, (227, 180, 77))
        text_rect = text_surface.get_rect()
        if right:
            text_rect.topright = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.surface.blit(text_surface, text_rect)

    """
    Méthode de mise à jour de la position et du contenu de l'ATH
    Arguments : killed : nombre d'avions tués, time_d : temps écoulé depuis le début de la partie
    """
    def update_ath(self, killed, time_d):
        now = time.get_ticks()
        if now - self.last_grow > self.grow_q_delay:
            self.last_grow = now
            if self.grow_q_forward: self.q_top += 1
            else: self.q_top -=1
            
            if self.q_top < self.grow_q[0] and not self.grow_q_forward:
                self.grow_q_forward = True
            elif self.q_top > self.grow_q[1] and self.grow_q_forward:
                self.grow_q_forward = False

        #on affiche le nombre de tués le score
        self.__draw_text(str(killed), 40, 40, 110, right=False)
        self.score = self.process_score(killed, time_d)
        self.__draw_text(str(self.score), 40, 40, 48, right=False)
        #on positionne les munitions
        rect = self.player.ammo_image[self.player.ammo_index].get_rect()
        rect.center = (975, 542)
        new_ammo = self.player.ammo_index + 1
        if new_ammo >= len(self.player.ammo_image):
            new_ammo = 0
        rect_new = self.player.ammo_image[new_ammo].get_rect()
        rect_new.center = (840, 552) 
        #on affiche toutes ces informations
        self.surface.blit(self.player.ammo_image[new_ammo], rect_new)
        self.surface.blit(self.player.ammo_image[self.player.ammo_index], rect)
        self.__draw_text(str(self.player.ammo_number[self.player.ammo_index]), 40, 960, 522, right=True)
        self.__draw_text("Q", 40, 805, self.q_top, right=False, font_name=True)
