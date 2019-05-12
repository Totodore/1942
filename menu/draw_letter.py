from constants import *
from pygame import transform, sprite, image, time, font, mixer
from os import path
import pygame
import json

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
Affichage du scénario 
index: numéro de la lettre, pos: position du dernier arret si plusieurs pages
end : win or lost, si jamais on écris la lettre lorsqu'on a perdu ou gagné
retourne la position dans le texte si il n'y a plus la place dans la lettre pour écrire
peut aussi retourner QUIT pour fermer le jeu
"""
def draw_letter(surface, index, pos, end):
    #on charge le son  et le fond
    sound = mixer.Sound(bytes(path.join(SOUND_DIR, "typewriter.wav"), 'UTF-8'))
    mixer.music.load(path.join(SOUND_DIR, "letter_music.wav"))
    img = image.load(path.join(MENU_DIR, "fond_lettre.png")).convert_alpha()
    img = transform.scale(img, (1000, 600))
    letter_img = image.load(path.join(MENU_DIR, "lettre.png")).convert_alpha()
    letter_img = transform.scale(letter_img, (440, 430))
    
    run = True
    clock = time.Clock()
    write_font = font.Font(path.join(FONT_DIR, "letter_font.ttf"), 16)

    if index >= 0:
        #si on a perdu ou gagné on recup le texte
        if end == "win":
            text = json.load(open(path.join(DATA_DIR, "levels.json")))["win"]
        elif end == "lost":
            text= json.load(open(path.join(DATA_DIR, "levels.json")))["lost"]
        #si ya un index on charge la lettre correspondante
        else:
            text = json.load(open(path.join(DATA_DIR, "levels.json")))["levels"][index]["description"]
    #si index < 0 cela veut dire que c'est la lettre d'introduction
    else:
        text = json.load(open(path.join(DATA_DIR, "first_letter.json")))["text"]
    text.encode(encoding='UTF-8')
    #delay de l'écriture et du son et du clignotement
    last_write = 0
    last_sound = 0
    last_flash = 0
    display_flash = True
    first_coords = (365, 110)
    #index des lignes de texte et des lettres
    letter_index = pos
    line_index = 0
    #indique la création d'une nouvelle ligne
    new_line = False
    #indique qu'il faut continuer à écrire le texte
    run_text = True
    #tableau de toutes les lignes
    text_lines = [""]
    sound.play(-1)
    mixer.music.play(-1)

    #petite ligne en bas de la feuille
    text_info = write_font.render("Pour continuer pressez entrer...", True, BLACK)
    text_info_rect = text_info.get_rect()
    text_info_rect.topleft = (375, 500)

    while run:
        tick = clock.tick(FPS) 
        #on get les evenements
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                #si on appuis sur entrer et que le texte est fini d'écrire
                if event.key == pygame.K_RETURN and not run_text:
                    run = False
                    #si la lettre n'est pas finie mais que ya plus de place on renvoie
                    #la position de la ou on s'est arrété dans le texte
                    if len(text) > letter_index:
                        return letter_index
            if getBasicEvent(event):
                run = False
                return pygame.QUIT

        now = time.get_ticks()

        #affichage du texte lettre par lettre avec un delay
        if now - last_write > WRITE_TIME and run_text: 
            last_write = now
            #si nouvelle ligne on l'ajoute 
            if text[letter_index] == "\n":
                new_line = True
            if new_line:
                #si jamais on saute une ligne au niveau d'un mot
                if text[letter_index] != " ":
                    #représente la positon du curseur depuis l'endroit de la césure
                    i = letter_index
                    #représente la taille du mot tronqué
                    j = 0
                    letter = ""
                    word = ""
                    #on remonte lettre par lettre dans la dernière ligne tant qu'il n'y a pas d'espaces
                    #on récupère ainsi le mot
                    while letter != " ":
                        letter = text[i]
                        word = letter + word
                        i -= 1
                        j += 1
                    #on le supprime de la dernière ligne
                    text_lines[-1] = text_lines[-1][:-j+1]
                    #et on le réinjecte sur la ligne d'après
                    text_lines.append(word)
                else: #si on saute pas de ligne au niveau d'un mot on ajoute juste une nouvelle ligne
                    text_lines.append(text[letter_index])
                #on augmente l'index des lignes
                line_index += 1
                new_line = False
                #si on arrive à la 15em ligne on arrete d'écrire
                if line_index >= 15:
                    run_text = False
            else: #sinon on saute pas de ligne on ajoute la lettre à la ligne actuelle
                text_lines[-1] += text[letter_index]
            #on augment l'index des lettres
            letter_index += 1
            #si le texte est fini on arrete de l'écrire et on coupe la musique
            if letter_index > len(text) - 1:
                run_text = False
                sound.fadeout(400)

        #on affiche le fond
        surface.blit(img, (0, 0))
        surface.blit(letter_img, (280, 105))
        i = 0
        #pour chaque ligne on l'affiche avec les bonnes coordonées
        for text_line in text_lines:
            #on créer une surface et un rect que l'on positionne en fct de l'index de la ligne
            text_surface = write_font.render(text_line, True, BLACK)
            text_rect = text_surface.get_rect()
            text_rect.top = first_coords[1] + 25*i
            #a partir de la 3em ligne on arrete d'écrire en retrait
            if i > 2:
                text_rect.left = first_coords[0] - 50
            else:
                text_rect.left = first_coords[0]
            #on affiche chaque ligne
            surface.blit(text_surface, text_rect)
            #si ca commence à déborder on demande une nouvelle ligne la prochaine boucle
            if text_line == text_lines[-1]: 
                if text_rect.right > 700:
                    new_line = True
            i += 1
        
        #si le texte est fini d'écrire
        if not run_text:
            #on fait clignoter le texte en bas de lettre
            if now - last_flash > FLASH_DELAY:
                last_flash = now
                if display_flash:
                    display_flash = False
                else:
                    display_flash = True
            if display_flash:
                surface.blit(text_info, text_info_rect)
        pygame.display.flip()
    return
