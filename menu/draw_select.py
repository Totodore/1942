from constants import *
from pygame import transform, sprite, image, time, font, mixer, surface
from os import path
import pygame
import json
import os

"""
Fonction qui récupère les évenements correspondant à la fermeture du jeu
"""
def getBasicEvent(event):
    if event.type == pygame.QUIT:                
        return True
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F4:
            return True


"""
Fonction qui transforme l'index du curseur (i, j) en index de niveau
"""
def get_level_from_index(index):
    if index[1] == 1:
        return index[0] + 3
    else:
        return index[0]

"""
Fonction d'affichage du menu de selection des niveaux
"""
def draw_select(screen, level_save):
    #chargement du JSON des niveaux
    json_menu = json.load(open(path.join(DATA_DIR, "levels.json")))["levels"]
    filter_ = surface.Surface((262, 163))
    display = True
    display_flash = False
    last_flash = 0
    thumbs = []
    level_save = int(level_save)
    #pour chaque niveau on charge la miniature
    for level in json_menu:
        img = image.load(path.join(THUMB_DIR, level["img_name"])).convert_alpha()
        img = transform.scale(img, (262, 163))
        thumbs.append(img)
    #on charge le font, le selecteur, et le cadenas
    img = image.load(path.join(MENU_DIR, "level_select/select_level.png")).convert_alpha()
    selector = image.load(path.join(MENU_DIR, "level_select/frame_select.png")).convert_alpha()
    cadenas = image.load(path.join(MENU_DIR, "level_select/cadenas.png")).convert_alpha()
    i = 0
    j = 0
    while display:
        now = time.get_ticks()
        rect_selector = selector.get_rect()
        #système de déplacement du curseur avec des coordonnées i,j
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    i -= 1
                    if i < 0:
                        i = 2
                elif event.key == pygame.K_RIGHT:
                    i += 1
                    if i > 2:
                        i = 0
                elif event.key == pygame.K_UP:
                    j -= 1
                    if j < 0:
                        j = 1
                elif event.key == pygame.K_DOWN:
                    j += 1
                    if j > 1:
                        j = 0
                #si on  appuis sur entrer on récupère le niveau depuis les coordonnées curseur et on retourne ce numéro de niveau
                elif event.key == pygame.K_RETURN:
                    level = get_level_from_index((i, j))
                    if level <= level_save:
                        display = False
                        return level
                elif event.key == pygame.K_ESCAPE:
                    display = False
                    return
            if getBasicEvent(event):
                run = False
                return pygame.QUIT
        #on positionne le curseur en fonction de i et j
        rect_selector.left = 47 + 310*i
        rect_selector.top = 140 + 208*j
        screen.blit(img, (0, 0))
        index = 0
        line = 0
        k = 0
        #pour chaque miniature
        for thumb in thumbs:
            rect = thumb.get_rect()
            rect.left = 63 + 307*index
            rect.top = 153 + 208*line
            filter_ = pygame.Surface((262, 163), pygame.SRCALPHA)
            filter_.fill((150, 150, 150, 128))
            screen.blit(thumb, rect)
            if k > level_save:
                rect_cad = cadenas.get_rect()
                rect_cad.left = 255 + 307*index
                rect_cad.top = 220 + 208*line
                screen.blit(filter_, rect)
                screen.blit(cadenas, rect_cad)
            index += 1
            if index > 2:
                index = 0
                line += 1
            k += 1
        #on fait clignoter le selecteur
        if now - last_flash > FLASH_DELAY:
            last_flash = now
            if display_flash:
                display_flash = False
            else:
                display_flash = True
                
        #on l'affiche
        if display_flash:
            screen.blit(selector, rect_selector)
        pygame.display.flip()
