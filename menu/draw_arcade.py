from constants import *
from pygame import transform, sprite, image, time, font, mixer, rect, draw, time
from os import path
from menu.draw_score import Score_Interface
import pygame
import json
import os


"""
Classe gérant l'interface et le menu Arcade
"""
class Arcade_Interface:
    def __init__(self, screen):
        self.display = True
        self.screen = screen
        self.clock = time.Clock()

        #Chargement du JSON et de toutes les images
        self.json_planes = json.load(open(path.join(DATA_DIR, "player.json")))["body"]
        self.background = image.load(path.join(ARCADE_DIR, "arcade_background.png")).convert_alpha()
        self.carte = image.load(path.join(ARCADE_DIR, "arcade_map.png")).convert_alpha()
        self.frame = image.load(path.join(ARCADE_DIR, "frame_arcade.png")).convert_alpha()
        self.score_btn = image.load(path.join(SCORE_DIR, "btn_score.png")).convert_alpha()

        #redimmensionnement des images
        self.carte = transform.scale(self.carte, (310, 500))
        self.frame = transform.scale(self.frame, (330, 520))

        #on positionne le cadre de selection
        self.frame_rect = self.frame.get_rect()
        self.frame_rect.y = int((HEIGHT-self.carte.get_height())/2)-10
        self.frame_rect.x = 10

        #Variable d'animation de lettres
        self.grow_s = (0, 5)
        self.grow_s_delay = 50
        self.s_top = self.grow_s[0]
        self.grow_s_forward = True
        self.last_grow = 0
        #chargement et positionnement des flèches
        self.last_anim = 0
        self.arrow_l = image.load(path.join(ARCADE_DIR, "arrow_left.png")).convert_alpha()
        self.arrow_r = image.load(path.join(ARCADE_DIR, "arrow_right.png")).convert_alpha()
        self.arrow_up = image.load(path.join(ARCADE_DIR, "arrow_up.png")).convert_alpha()
        self.arrow_down = image.load(path.join(ARCADE_DIR, "arrow_down.png")).convert_alpha()
        self.arrow_l_left = 100
        self.arrow_r_left = WIDTH-100
        self.arrow_up_top = 80
        self.arrow_down_top = HEIGHT-80
        self.forward = True

        #on affiche les flèches informatives
        self.arrow_r_rect = self.arrow_r.get_rect()
        self.arrow_r_rect.center = (WIDTH-40, int(HEIGHT/2))
        self.arrow_l_rect = self.arrow_l.get_rect()
        self.arrow_l_rect.center = (40, int(HEIGHT/2))
        self.arrow_up_rect = self.arrow_up.get_rect()
        self.arrow_up_rect.center = (self.frame_rect.centerx, 80)
        self.arrow_down_rect = self.arrow_down.get_rect()
        self.arrow_down_rect.center = (self.frame_rect.centerx, HEIGHT-80)

        #chargement de la police d'écriture
        self.write_font = font.Font("ath.ttf", 30)

        #initialisation des variables
        #self.posx: selection des avions avec fleches latérales
        #self.posy: selection des couleurs avec fleches haut/bas
        self.img_planes = ([],[])
        self.posx = 0
        self.posy = 0
        self.display_frame = True
        self.last_flash = 0

        #pour chaque avion
        for plane in self.json_planes:
            color_planes = []
            #pour chaque couleur d'avion on charge l'image et on la met dans une array
            colors = os.listdir(plane["image"])
            colors.sort()
            for color in colors:
                img = image.load(path.join(plane["image"], color, "1.png")).convert_alpha()
                img = transform.scale(img, (int(img.get_width()/1.5), int(img.get_height()/1.5)))
                color_planes.append(img)
            ammo_planes = []
            #pour chaque munitions on charge l'image et on met le tout en parallele avec les 
            #couleurs dans l'array des avions
            for ammo in plane["munitions"]:
                img = image.load(ammo["image"]).convert_alpha()
                img = transform.scale(img, (int(img.get_width()/3), int(img.get_height()/3)))
                ammo_planes.append(img)
            self.img_planes[0].append(color_planes)
            self.img_planes[1].append(ammo_planes)

    """
    Méthode de gestion des evenements 
    """
    def event_handler(self):
        #on récupère les evenements
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                #touches latérale on change l'avion et on remet la couleur à la première
                if event.key == pygame.K_LEFT:
                    self.posx -= 1
                    self.posy = 0
                    if self.posx < 0:
                        self.posx = 0
                elif event.key == pygame.K_RIGHT:
                    self.posx += 1
                    self.posy = 0
                    if self.posx > len(self.img_planes[0])-1:
                        self.posx = len(self.img_planes[0])-1
                #touches haut et bas on change la couleure
                elif event.key == pygame.K_UP:
                    self.posy += 1
                    if self.posy > len(self.img_planes[0][self.posx])-1:
                        self.posy = len(self.img_planes[0][self.posx])-1
                elif event.key == pygame.K_DOWN:
                    self.posy -= 1
                    if self.posy < 0:
                        self.posy = 0
                #Touche S on affiche les scores
                elif event.key == pygame.K_s:
                    event = Score_Interface(self.screen).draw_score()
                    if event == pygame.QUIT:
                        return pygame.QUIT
                #appuis sur entrer : on retourne l'avion et la couleure
                elif event.key == pygame.K_RETURN:
                    return (self.posx, self.posy)
                elif event.key == pygame.K_ESCAPE:
                    self.display = False
                    break
            if self.getBasicEvent(event):
                self.display = False
                return pygame.QUIT

    """
    Méthode de gestion de l'affichage des avions
    """
    def planes_handler(self):
        #pour chaque avions
        i = 0
        for img in self.img_planes[0]:
            #on set des coordonnées 20: marge de gauche,
            #on ajoute le nombre de pixels par carte avion pour avoir un affichage en ligne
            #on soustrait par le nombre pixel correspondant a la position pour avoir un défilement
            x = 20 + ((self.carte.get_width()+10)*i) - ((self.carte.get_width()+10)*self.posx)
            y = int((HEIGHT-self.carte.get_height())/2)
            carte_rect = self.carte.get_rect()
            carte_rect.x = x
            carte_rect.y = y

            #si l'avion est celui sur le curseur on récup la couleur correspondant à posy
            #sinon on prend la première couleur
            if i == self.posx:
                plane = img[self.posy]
            else:
                plane = img[0]

            #on positionne l'avion
            plane_rect = plane.get_rect()
            plane_rect.centerx = int(carte_rect.width/2) + x
            plane_rect.centery = int(carte_rect.height/4) + 20

            #on écrit toutes les stats
            text_life_surface = self.write_font.render(str(self.json_planes[i]["vie"]), True, BLACK)
            text_life_rect = text_life_surface.get_rect()
            text_life_rect.top = 250
            text_life_rect.left = 100 + carte_rect.left

            text_speed_surface = self.write_font.render(str(self.json_planes[i]["vitesse"]), True, BLACK)
            text_speed_rect = text_life_surface.get_rect()
            text_speed_rect.top = 310
            text_speed_rect.left = 100 +carte_rect.left        

            text_title_surface = self.write_font.render(self.json_planes[i]["nom"], True, BLACK)
            text_title_rect = text_title_surface.get_rect()
            text_title_rect.top = 200
            text_title_rect.centerx = carte_rect.centerx  

            #on affiche tout sauf les munitions
            self.screen.blit(self.carte, carte_rect)
            self.screen.blit(plane, plane_rect)
            self.screen.blit(text_life_surface, text_life_rect)
            self.screen.blit(text_speed_surface, text_speed_rect)
            self.screen.blit(text_title_surface, text_title_rect)

            #pour chaque munition par avion
            k = 0
            for ammo in self.json_planes[i]["munitions"]:
                #on récup l'image et on la positionne
                ammo_surface = self.img_planes[1][i][k]
                ammo_rect = ammo_surface.get_rect()
                ammo_rect.top = 370
                ammo_rect.centerx = 116 + carte_rect.left + k*100
                #on écrit le nombre de munitions de base
                text_ammo_surface = self.write_font.render(str(ammo["base_munitions"]), True, BLACK)
                text_ammo_rect = text_ammo_surface.get_rect()
                text_ammo_rect.top = ammo_rect.bottom
                text_ammo_rect.centerx = ammo_rect.centerx
                #on créé un petit rectangle autour de "chaque" munition
                rect = ammo_rect.copy()
                rect.height += text_ammo_rect.height + 7
                rect.width = text_ammo_rect.width + 10
                rect.top -= 5
                rect.centerx = text_ammo_rect.centerx
                #on affiche tout ca
                self.screen.blit(ammo_surface, ammo_rect)
                self.screen.blit(text_ammo_surface, text_ammo_rect)
                draw.rect(self.screen, BLACK, rect, 1)
                k += 1
            i += 1

    """
    Méthode de gestion de l'affichage des flèches
    """
    def arrow_handler(self):
        #si les flèches doivent avancer on change les positions en fonction
        if self.forward == True:
            self.arrow_r_rect.left += 1
            self.arrow_l_rect.left -= 1
            self.arrow_up_rect.top -= 1
            self.arrow_down_rect.top += 1
            #si la position de la fleches dépasse un maximum on la fait reculer
            if self.arrow_r_rect.left > self.arrow_r_left + ARROW_MOVE:
                self.forward = False
        #si les fleches doivent reculer on change les positions en fonction
        else:
            self.arrow_r_rect.left -= 1
            self.arrow_l_rect.left += 1
            self.arrow_up_rect.top += 1
            self.arrow_down_rect.top -= 1
            #si la position de la fleche depasse sa position initiale on la fait a nouveau avancer
            if self.arrow_r_rect.left <= self.arrow_r_left:
                self.forward = True

    def s_anim_handler(self):
        if self.grow_s_forward: self.s_top += 1
        else: self.s_top -=1
        
        if self.s_top < self.grow_s[0] and not self.grow_s_forward:
            self.grow_s_forward = True
        elif self.s_top > self.grow_s[1] and self.grow_s_forward:
            self.grow_s_forward = False
    """
    Méthode d'affichage du menu Arcade
    """
    def draw_arcade(self):
        while self.display:
            tick = self.clock.tick(FPS) 
            self.now = time.get_ticks()
            #posx : position des fiches avions
            #posy : position des couleurs d'avions dans les fiches
            #si il ya a un event retourné alors on le retourne a nouveau
            event = self.event_handler()
            if event != None:
                return event

            #on affiche l'arriere plan
            self.screen.blit(self.background, (0, 0))

            #on gère et on affiche tous les cartes et avions
            self.planes_handler()     

            #on fait clignoter le cadre
            if self.now - self.last_flash > FLASH_DELAY:
                self.last_flash = self.now
                if self.display_frame:
                    self.display_frame = False
                else:
                    self.display_frame = True
            if self.display_frame:
                self.screen.blit(self.frame, self.frame_rect)

            #on fait bouger les fleches avec un certain délai pour pas que ca aille trop vite
            if self.now - self.last_anim > ARROW_DELAY:
                self.last_anim = self.now
                self.arrow_handler()
            #On fait bouger les lettres avec un certain delai pareil que les fleches
            if self.now - self.last_grow > self.grow_s_delay:
                self.last_grow = self.now
                self.s_anim_handler()

            #on affiche les fleches
            if self.posx != 0:
                self.screen.blit(self.arrow_l, self.arrow_l_rect)   
            if self.posx != len(self.img_planes[0])-1:
                self.screen.blit(self.arrow_r, self.arrow_r_rect)
            if self.posy != 0:
                self.screen.blit(self.arrow_down, self.arrow_down_rect)
            if self.posy != len(self.img_planes[0][self.posx])-1:
                self.screen.blit(self.arrow_up, self.arrow_up_rect)
            
            #On affiche le bouton score
            self.screen.blit(self.score_btn, (0, 0))
            caption = self.write_font.render("S", True, WHITE)
            self.screen.blit(caption, (125, self.s_top))
            pygame.display.flip()

    def getBasicEvent(self, event):
        if event.type == pygame.QUIT:                
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F4:
                return True

