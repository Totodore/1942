from engine.background import Background
from engine.bullet import Bullet
from engine.cloud import Cloud
from engine.explosion import Explosion, load_expl
from engine.item import Item
from engine.mob import Mob
from engine.player import Player
from engine.ath import ATH
from engine.engine_constants import *

from pygame import * 
from random import randint
from os import path
from threading import Thread

import pygame
import os
import json
import engine.mob

"""
Classe centrale d'affichage du jeu
Arguments: screen: objet fenetre, level: index du niveau, player: index de l'avion, color: index de la couleure
"""
class EngineInterface:
    def __init__(self, screen, level, player, color):
        #création de variables et chargement des specs
        self.player = player
        self.color = color
        self.font_name = font.match_font('arial')
        self.screen = screen
        self.clock = time.Clock()
        self.__load(level, player, color)

        #Channels réservées pour les explosions
        pygame.mixer.set_reserved(EXPLOSION_CHANNEL[0])
        pygame.mixer.set_reserved(EXPLOSION_CHANNEL[1])
        pygame.mixer.set_reserved(EXPLOSION_CHANNEL[2])
        self.channels = []
        self.channels.append(pygame.mixer.Channel(EXPLOSION_CHANNEL[0]))
        self.channels.append(pygame.mixer.Channel(EXPLOSION_CHANNEL[1]))
        self.channels.append(pygame.mixer.Channel(EXPLOSION_CHANNEL[2]))

    """
    Méthode de chargement des specs, des images et des sons
    Arguments: level: index du niveau, player: index de l'avion, color: index de la couleure
    """
    def __load(self, level, player, color):
        #si c'est un niveau arcade on charge les specs Aracade
        if level == -1:
            level_data = json.load(open(ARCADE_DIR, "r"))
            self.level_specs = level_data
        #sinon on charge les specs correspondantes au niveau
        else:
            level_data = json.load(open(LEVEL_DIR, "r"))
            self.level_specs = level_data["levels"][level]   
        
        #chargement des specs du niveau
        self.clouds_path = level_data["clouds"] 
        self.bg_images = []
        self.cloud_delay = self.level_specs["cloud_delay"]
        self.item_delay = self.level_specs["ammo_delay"]
        self.ammo_size = self.level_specs["ammo_size"]
        self.max_score = self.level_specs["score_max"]
        self.spawn_delay = self.level_specs["ennemy_delay"]
        self.text = self.level_specs["description"]
        self.text_before = self.level_specs["before"]
        self.wave_size = self.level_specs["wave_size"]
        self.explosion_sound = []
        #on charges les explosions
        self.expls = load_expl()
        self.last_item = 0
        #on recupère les fonds
        map_path = self.level_specs["map_path"]
        map_path = path.join(path.dirname(__file__), map_path)
        files = os.listdir(map_path)
        #pour chaque fond on le charge et on l'ajoute à une array
        for file in files:
            img = image.load(path.join(map_path, file)).convert_alpha()
            self.bg_images.append(img)
        #pour chaque son on le charge et on l'ajoute à une array
        for file in os.listdir(path.join(SOUND_DIR, "explosions")):
            sound = mixer.Sound(bytes(path.join(SOUND_DIR, "explosions", file), "utf-8"))
            self.explosion_sound.append(sound)
            
    """
    Méthode d'affichage du jeu
    """
    def draw_game(self):
        #initialisation de variables
        self.last_spawn = pygame.time.get_ticks()
        self.last_gif = 0
        self.plane_kill = 0
        self.all_sprites = sprite.Group()
        self.mobs = sprite.Group()
        self.bullets = sprite.Group()
        self.mob_bullets = sprite.Group()
        self.backgrounds = []
        #on ajoute le premier fond a la liste des fonds actifs
        self.backgrounds.append(Background(self.bg_images[0], False))
        self.map_index = 0
        self.image_index = 0
        #on charge le joeur
        self.player = Player(self.bullets, self.all_sprites, self.player, self.color)
        #on charge tous les ennemies
        self.mob_data = engine.mob.load(3)
        #on charge les nuages, la première boite de munitions et l'ATH
        self.cloud = Cloud(self.clouds_path, self.cloud_delay)
        self.ammo = Item(self.expls[1][0])
        self.ath = ATH(self.player, self.screen)

        #on ajoute tout ca au groupe de sprites principal
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.cloud)
        self.all_sprites.add(self.ammo)
        self.all_sprites.add(self.ath)
        self.stack = 0
        self.sound = []

        #on génère une première vague d'ennemis
        for i in range(self.wave_size):
            m = Mob(self.mob_bullets, self.all_sprites, self.mob_data, self.screen)
            self.all_sprites.add(m)
            self.mobs.add(m)
        self.start_time = time.get_ticks() 
        #on retourne la méthode run_game()
        return self.__run_game()

    """
    Méthode du lancement de bruits d'explosions
    """
    def __kill_sound(self):
        isnotbusy = False
        #on récup un channel qui n'est pas occupé parmis les trois réservés
        for channel in self.channels:
            if channel.get_busy:
                isnotbusy = channel

        #si il n'y en a aucun on vide le premier
        if not isnotbusy:
            channel = self.channels[0]
        else:
            channel = isnotbusy
        #on récupère un bruit d'explosion aléatoirement et on le joue
        channel.set_volume(EXPLOSION_SOUND)
        sound = self.explosion_sound[randint(0, len(self.explosion_sound)-1)]
        channel.play(sound)

    """
    Méthode de gestion des arrières-plans
    """
    def __bg_handler(self):
        #on récupère la position du dernier fond
        y = self.backgrounds[-1].rect.y
        if y > 0: #si elle sort de l'écran on créer une nouvelle image 
            self.map_index += 1
            #on change de map
            if self.map_index > 2:
                self.map_index = 0
                self.image_index += 1
                #si on arrive au bout de la liste d'image on repart à 0
                if self.image_index > len(self.bg_images) -1:
                    self.image_index = 0
            self.backgrounds.append(Background(self.bg_images[self.image_index], True))
            #on supprimer les fonds qui ne sont plus affichés
            #il n'y a jamais plus de deux fonds actifs
            if len(self.backgrounds) > 2:
                del self.backgrounds[0]

    """
    Méthode de gestion des collisions
    """
    def __collide_handler(self):
        #vérifier si le player rencontre un nuage
        cloud_hit = sprite.collide_mask(self.player, self.cloud)
        bullet_cloud_hit = True
        #vérifier si le player rencontre une caise de munitions
        hit = sprite.collide_mask(self.player, self.ammo)
        if hit:
            #on fait bouger la caisse en dehors de l'écran et on lance une explosions
            expl = Explosion(self.ammo.rect.center, self.expls[1])
            self.all_sprites.add(expl)
            self.ammo.rect.top = HEIGHT + 200
            self.player.add_ammo(self.ammo_size)

        #vérifier si bullet rencontre un mob
        hits = pygame.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            #on lance la méthode shot si elle renvoie true alors le mob est mort
            if hit.shot(self.player.ammo[self.player.ammo_index]["degats"]):
                #on joue alors un bruit d'explosion
                hit.kill()
                self.__kill_sound()
                self.plane_kill += 1
                expl = Explosion(hit.rect.center, self.expls[0])
                self.all_sprites.add(expl)
                #on en créer un nouveau
                m = Mob(self.mob_bullets, self.all_sprites, self.mob_data, self.screen)
                self.all_sprites.add(m)
                self.mobs.add(m)

        #vérifier si un mob rencontre le joueur
        hits = sprite.spritecollide(self.player, self.mobs, False, sprite.collide_mask)
        if hits: ##si ca touche
            #si c'est dans un nuage et qu'ils sont a la meme hauteur
            if cloud_hit and self.stack < 2:   
                self.running = False
                return "lost"
            #si c'est dans un nuage et qu'ils sont a des hauteurs différentes
            elif cloud_hit and self.stack >= 2: 
                return
            else:
                self.running = False   #si ils ne sont pas dans un nuage
                return "lost"

        #vérifier si une munition ennemie rencontre le joueur
        hits = sprite.spritecollide(self.player, self.mob_bullets, True, sprite.collide_mask)
        if hits:
            for hit in hits:
                #si c'est dans un nuage et qu'ils sont a la meme hauteur 
                if bullet_cloud_hit and self.stack < 2:                  
                    if self.player.shot(hit.strength):
                        self.running = False
                        return "lost"
                #si c'est dans un nuage et qu'ils sont a des hauteurs différentes
                elif bullet_cloud_hit and self.stack >= 2:
                    return
                else:
                    self.running = False   #si ils ne sont pas dans un nuage
                    return

    """
    Méthode de lancement du jeu
    """
    def __run_game(self):
        self.running = True
        while self.running:
            # la boucle tourne à la même vitesse
            self.clock.tick(FPS)
            # on récup les evenements
            for event in pygame.event.get():
                # vérifier si on ferme la fenêtre
                if event.type == pygame.QUIT:
                    self.running = False
                    return pygame.QUIT
                #si on appuis sur q on change de munition
                if event.type == KEYUP:
                    if event.key == K_q:
                        self.player.swap_ammo()
                    #si on appuis sur echape on ferme la partie
                    elif event.key == K_ESCAPE:
                        running = False
                        return
            now = time.get_ticks()
            #on fait spawn des ennemis regulierement
            if now - self.last_spawn > self.spawn_delay:
                self.last_spawn = now
                for i in range(0, self.wave_size):
                    m = Mob(self.mob_bullets, self.all_sprites, self.mob_data, self.screen)
                    self.all_sprites.add(m)
                    self.mobs.add(m)     

            #on fait spawn les caisses de munitions regulierement
            if now - self.last_item > self.item_delay:
                self.last_item = now
                self.ammo = Item(self.expls[1][0])

            #on met tout à jour
            #self.stack représente la façon dont est empilé chaque sprite
            self.stack = self.cloud.stack
            self.__bg_handler()
            self.all_sprites.update()
            self.ammo.update()
            lost = self.__collide_handler()
            for background in self.backgrounds:
                background.update()
            # Draw / render
            self.screen.fill(BLACK)
            for background in self.backgrounds:
                self.screen.blit(background.image, background.rect)

            
            #stack=0 / avion et ennemis au dessus des nuages
            #stack=1 / avion et ennemis en dessous des nuages
            #stack=2 / avion en dessous des nuages et ennemis au dessus
            #stack=3 / avion au dessus des nuages et ennemis en dessous
            if self.stack == 0:
                self.screen.blit(self.cloud.image, self.cloud.rect)
                self.all_sprites.draw(self.screen)
                for mob in self.mobs:
                    draw.rect(self.screen, BLACK, mob.rect_life, 1)
                    draw.rect(self.screen, mob.actual_color, mob.rect_life_inner)
                self.screen.blit(self.player.image, self.player.rect)
                self.screen.blit(self.ammo.image, self.ammo.rect)
            elif self.stack == 1:
                self.screen.blit(self.player.image, self.player.rect)
                self.all_sprites.draw(self.screen)
                for mob in self.mobs:
                    draw.rect(self.screen, BLACK, mob.rect_life, 1)
                    draw.rect(self.screen, mob.actual_color, mob.rect_life_inner)
                    self.screen.blit(self.ammo.image, self.ammo.rect)
                self.screen.blit(self.cloud.image, self.cloud.rect)
            elif self.stack == 2:
                self.screen.blit(self.player.image, self.player.rect)
                self.screen.blit(self.ammo.image, self.ammo.rect)
                self.screen.blit(self.cloud.image, self.cloud.rect)
                self.all_sprites.draw(self.screen)
                for mob in self.mobs:
                    draw.rect(self.screen, BLACK, mob.rect_life, 1)
                    draw.rect(self.screen, mob.actual_color, mob.rect_life_inner)
            elif self.stack == 3:
                self.all_sprites.draw(self.screen)
                for mob in self.mobs:
                    draw.rect(self.screen, BLACK, mob.rect_life, 1)
                    draw.rect(self.screen, mob.actual_color, mob.rect_life_inner)
                self.screen.blit(self.cloud.image, self.cloud.rect)
                self.screen.blit(self.ammo.image, self.ammo.rect)
                self.screen.blit(self.player.image, self.player.rect)

            #on affiche l'ath
            self.screen.blit(self.ath.image, self.ath.rect)
            #on affiche la barre de vie
            draw.rect(self.screen, BLACK, self.player.rect_life, 1)
            draw.rect(self.screen, self.player.actual_color, self.player.rect_life_inner)
            #on update l'ath en donnant comme argument le temps ecoulé et le nombre d'avions tués
            self.time = time.get_ticks() - self.start_time
            self.ath.update_ath(self.plane_kill, self.time)
            #si il y a un score max et que celui ci est dépassé alors renvoie gagné
            if self.ath.score > self.max_score and self.max_score > 0:
                if self.text_before == False:
                    return self.text
                else:
                    return "succeed"
            #si on a perdu la méthode renvoie perdu
            if lost and lost == "lost":
                return "lost"
            pygame.display.flip()
