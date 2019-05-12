import pygame
import random
import os
#import du moteur de jeu et des fonctions menu
from menu.draw_letter import draw_letter
from menu.draw_select import draw_select
from menu.draw_arcade import Arcade_Interface
from engine.interface import EngineInterface

from os import path
from constants import *

global screen, actual_level

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
    menu = True
    continue_game = True
    fonds= []
    index = 1
    #on charge les deux fonds correspondant au menu start
    for file in os.listdir(START_DIR):
        img = pygame.image.load(path.join(START_DIR, file))
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        fonds.append(img)
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
                        
                    #si on a selectionné le mode Campagne
                    else:
                        #si il n'y a pas de save on affiche la lettre d'introduction
                        if get_save() == -1:
                            if draw_menu_letter(-1) == pygame.QUIT:
                                menu = False
                                continue_game = False
                                break
                        #on affiche le menu de selection des niveaux
                        selector = draw_select(screen, get_save())
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
                            pygame.mixer.fadeout(200)
                            if response == pygame.QUIT:
                                menu = False
                                continue_game = False
                                break
                            #si le jeu renvoie "succeed" alors la mission est réussie on affiche la lettre de réussite et on met à jour la save
                            elif isinstance(response, str):
                                if response == "succeed":
                                    set_save(selector+1)
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
        #on affiche le fond
        screen.blit(fonds[index], (0,0))
        pygame.mixer.fadeout(200)
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
Fonction de récupèration de la sauvegarde
"""
def get_save():
    save_file = None
    #si ya pas de fichier lance la création d'un fichier de sauvegarde et on retourne -1
    try:
        save_file = open("./save/save.txt", "r")        
    except FileNotFoundError:
        set_save(0)
        return -1
    line = save_file.readline()
    if len(line) != 1: #si le contenus du fichier save est différent de un caractère on créer save et on retourne -1
        set_save(0)
        return -1
    #sinon on retourne l'index de la save
    return line

"""
Fonction de création ou de changement de la save
"""
def set_save(level):
    #on supprime l'ancienne save
    os.remove("./save/save.txt")
    #on créé une nouvelle
    save_file = open("./save/save.txt", "x")
    #on écrit le dernier niveau disponible dedans
    save_file.write(str(level))
    save_file.close()

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
