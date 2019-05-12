import pygame
import json
import os
import math
import PIL
from os import path
from pygame import sprite, image, transform, mask, font
from engine.bullet import Bullet
from engine.engine_constants import *

class ATH(sprite.Sprite):
    def __init__(self, player, surface):
        sprite.Sprite.__init__(self)
        self.surface = surface
        self.ammo_data = player.ammo
        self.ammo_number = player.ammo_number
        self.player = player
        self.image = image.load(path.join(ATH_DIR, "ath.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
        self.score = 0

        self.ammo_image = []
        # for file in os.listdir(path.join(BULLET_DIR,))
    
    def process_score(self, killed, time):
        killed *= 100
        time = int(time/100)
        return killed + time

    def __draw_text(self, text, size, x, y, right):
        font_t = font.Font(path.join(FONT_DIR, "ath.ttf"), size)
        text_surface = font_t.render(text, True, (227, 180, 77))
        text_rect = text_surface.get_rect()
        if right:
            text_rect.topright = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.surface.blit(text_surface, text_rect)

    def update_ath(self, killed, time):
        self.__draw_text(str(killed), 40, 40, 110, right=False)
        self.score = self.process_score(killed, time)
        self.__draw_text(str(self.score), 40, 40, 48, right=False)
        rect = self.player.ammo_image[self.player.ammo_index].get_rect()
        rect.center = (975, 542)
        new_ammo = self.player.ammo_index + 1
        if new_ammo >= len(self.player.ammo_image):
            new_ammo = 0
        rect_new = self.player.ammo_image[new_ammo].get_rect()
        rect_new.center = (840, 552) 
        self.surface.blit(self.player.ammo_image[new_ammo], rect_new)
        self.surface.blit(self.player.ammo_image[self.player.ammo_index], rect)
        self.__draw_text(str(self.player.ammo_number[self.player.ammo_index]), 40, 960, 522, right=True)
