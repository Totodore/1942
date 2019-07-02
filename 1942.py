import pygame
import random
import os
#import du moteur de jeu et des fonctions menu
from menu.draw_letter import draw_letter
from menu.draw_select import draw_select
from menu.draw_score import Score_Interface
from menu.draw_arcade import Arcade_Interface
from menu.draw_score import Score_Interface
from menu.save_handler import set_save_campain, get_save_campain
from engine.interface import EngineInterface

from os import path
from constants import *

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
Fonction d'affichage du menu start
"""
def draw_menu_start():
    global arrow_l, forward, arrow_r, arrow_r_left, arrow_r_rect, arrow_l_rect
    menu = True
    continue_game = True
    fonds= []
    index = 1
    #on charge les deux fonds correspondant au menu start
    for file in os.listdir(START_DIR):
        img = pygame.image.load(path.join(START_DIR, file))
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        fonds.append(img)

    #chargement et positionnement des flèches
    last_anim = 0
    arrow_l = pygame.image.load(path.join(ARCADE_DIR, "arrow_left.png")).convert_alpha()
    arrow_r = pygame.image.load(path.join(ARCADE_DIR, "arrow_right.png")).convert_alpha()
    arrow_l_left = 100
    arrow_r_left = WIDTH-100
    forward = True

    #on affiche les flèches informatives
    arrow_r_rect = arrow_r.get_rect()
    arrow_r_rect.center = (WIDTH-40, int(HEIGHT/2))
    arrow_l_rect = arrow_l.get_rect()
    arrow_l_rect.center = (40, int(HEIGHT/2))

    Score_Interface(screen, (200, 200)).draw_score();
    #boucle de jeu
    while menu:
        #on récupère les evenements
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                #si on appuis sur espace ou entrer
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    #si on a selectionné le mode Arcade
                    if index == 0:
                        #on affiche le menu de selection des avions
                        #peut retourner l'id de l'avion et l'id de la couleure ou l'evenement QUIT
                        selector = draw_menu_plane()
                        if selector == pygame.QUIT:
                            menu = False
                            continue_game = False
                        #si c'est bien deux index contenus dans un tuple qui sont retournés
                        if isinstance(selector, tuple):
                            #on lance le jeu
                            #-1 pour le niveau arcade
                            newGame = EngineInterface(screen, -1, selector[0], selector[1])
                            response = newGame.draw_game()
                            if response == pygame.QUIT:
                                menu = False
                                continue_game = False
                            elif isinstance(response, tuple):
                                score_interface = Score_Interface(screen, response) 
                                response_score = score_interface.draw_score()
                                if response_score == pygame.QUIT:
                                    menu = False
                                    continue_game = False
                        
                    #si on a selectionné le mode Campagne
                    else:
                        #si il n'y a pas de save on affiche la lettre d'introduction
                        if get_save_campain() == -1:
                            if draw_menu_letter(-1) == pygame.QUIT:
                                menu = False
                                continue_game = False
                                break
                        #on affiche le menu de selection des niveaux
                        selector = draw_select(screen, get_save_campain())
                        if selector == pygame.QUIT:
                            menu = False
                            continue_game = False
                        #si il renvoie un entier alors on génère le jeu avec le niveau correspondant en argument
                        #on prend le 3em avion et la première couleure
                        elif isinstance(selector, int) and selector < 6:
                            newGame = EngineInterface(screen, selector, 3, 0)
                            #Si ya une lettre a afficher avant on l'affiche
                            if newGame.text_before == True and len(newGame.text) > 2:
                                if draw_menu_letter(selector) == pygame.QUIT:
                                    menu = False
                                    continue_game = False
                                    break
                            #on lance le jeu
                            response = newGame.draw_game()
                            #à la fin du jeu on coupe les sons de celui-ci
                            if response == pygame.QUIT:
                                menu = False
                                continue_game = False
                                break
                            #si le jeu renvoie "succeed" alors la mission est réussie on affiche la lettre de réussite et on met à jour la save
                            elif isinstance(response, str):
                                if response == "succeed":
                                    set_save_campain(selector+1)
                                    if draw_menu_letter(selector, "win") == pygame.QUIT:
                                        menu = False
                                        continue_game = False
                                        break
                                #si le jeu renvoie "lost" alors la mission est ratée et on affiche la lettre de perte
                                elif response == "lost":    
                                    if draw_menu_letter(selector, "lost") == pygame.QUIT:
                                        menu = False
                                        continue_game = False
                                        break
                                #sinon on affiche la lettre écrite par les soins de Stanislav...
                                else:
                                    if draw_menu_letter(selector) == pygame.QUIT:
                                        menu = False
                                        continue_game = False
                                        break
                #changement entre les modes arcades et campagne
                if event.key == pygame.K_RIGHT:
                    index += 1
                    if index > 1:
                        index = 0
                if event.key == pygame.K_LEFT:
                    index -= 1
                    if index < 0:
                        index = 1
                #on ferme si on appuis sur echape
                if event.key == pygame.K_ESCAPE:
                    menu = False
                    continue_game = False
            if getBasicEvent(event):
                menu = False
                continue_game = False 
        now = pygame.time.get_ticks()
        if now - last_anim > ARROW_DELAY:
            last_update = now
            forward = arrow_handler(forward)    
        #on affiche le fond
        screen.blit(fonds[index], (0,0))
        if index == 0:
            screen.blit(arrow_r, arrow_r_rect)
        else:
            screen.blit(arrow_l, arrow_l_rect)
        pygame.mixer.music.stop()
        pygame.mixer.stop()
        pygame.display.flip()
    return continue_game


"""
Fonction de lancement de l'affichage de lettres
arguments: index: index du texte, end: si c'est lorsqu'on a perdu ou gagné, peut prendre deux valeurs : win ou lost
"""
def draw_menu_letter(index, end=None):
    response = 0
    #On affiche les lettres tant que la fonction ne renvoie pas l'évenement quitter ou que le texte est fini
    while isinstance(response, int): 
        #on affiche les lettres de manière récursive tant que le texte n'est pas fini
        #arguments : screen: objet fenetre, index : id du texte, response : position dans le texte 
        response = draw_letter(screen, index, response, end)
        if response == pygame.QUIT:
            return pygame.QUIT

"""
Fonction de lancement du menu de selection des avions
"""
def draw_menu_plane():
    #On instancie la classe Arcade_interface
    response = 0
    arcadeInterface = Arcade_Interface(screen)
    response = arcadeInterface.draw_arcade()
    return response

#-1: premier lancement du jeu affichage de la lettre d'intro
#sinon index du dernier niveau disponible


"""
Fonction de gestion des flêches d'affichage
Retourne la variable forward : direction des fleches
"""
def arrow_handler(forward):
    #si les flèches doivent avancer on change les positions en fonction
    if forward == True:
        arrow_r_rect.left += 1
        arrow_l_rect.left -= 1
        #si la position de la fleches dépasse un maximum on la fait reculer
        if arrow_r_rect.left > arrow_r_left + ARROW_MOVE:
            return False
        else: return True
    #si les fleches doivent reculer on change les positions en fonction
    else:
        arrow_r_rect.left -= 1
        arrow_l_rect.left += 1
        #si la position de la fleche depasse sa position initiale on la fait a nouveau avancer
        if arrow_r_rect.left <= arrow_r_left:
            return True
        else: return False

#on initialise le gestionnaire de son de pygame ainsi que pygame
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
#on créer 48 channels de son pour en avoir suffisament
pygame.mixer.set_num_channels(48)
#on créer la fenetre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("1942")

# Boucle principale
CONTINUE = True
while CONTINUE:
    CONTINUE = draw_menu_start()
pygame.quit()
