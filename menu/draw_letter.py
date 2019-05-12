from constants import *
from pygame import transform, sprite, image, time, font, mixer
from os import path
import pygame
import json

def getBasicEvent(event):
    if event.type == pygame.QUIT:                
        return True
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F4:
            return True

#Affichage du scénario index: numéro de la lettre, pos: position du dernier arret si plusieurs pages
#retourne la position dans le texte si jamais il n'est pas fini d'écrire
#peut aussi retourner QUIT pour fermer le jeu
#end : win or lost 
def draw_letter(surface, index, pos, end):
    sound = mixer.music.load(path.join(SOUND_DIR, "typewriter.mp3"))
    img = image.load(path.join(MENU_DIR, "fond_lettre.png")).convert_alpha()
    img = transform.scale(img, (1000, 600))
    
    run = True
    clock = time.Clock()
    write_font = font.Font(path.join(FONT_DIR, "letter_font.ttf"), 16)

    #récupération du text
    if index >= 0:
        if end == "win":
            text = json.load(open(path.join(DATA_DIR, "levels.json")))["win"]
        elif end == "lost":
            text= json.load(open(path.join(DATA_DIR, "levels.json")))["lost"]
        else:
            text = json.load(open(path.join(DATA_DIR, "levels.json")))["levels"][index]["description"]
    else:
        text = json.load(open(path.join(DATA_DIR, "first_letter.json")))["text"]
    #delay de l'écriture et du son et du clignotement
    last_write = 0
    last_sound = 0
    last_flash = 0
    display_flash = True
    first_coords = (375, 110)
    #index des lignes de texte et des lettres
    letter_index = pos
    line_index = 0
    #indique la création d'une nouvelle ligne
    new_line = False
    #indique qu'il faut continuer à écrire le texte
    run_text = True
    #tableau de toutes les lignes
    text_lines = [""]
    mixer.music.play(0)

    text_info = write_font.render("Pour continuer pressez entrer...", True, BLACK)
    text_info_rect = text_info.get_rect()
    text_info_rect.topleft = (375, 500)
    while run:
        tick = clock.tick(FPS) 
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not run_text:
                        run = False
                        if len(text) > letter_index:
                            return letter_index
            if getBasicEvent(event):
                run = False
                return pygame.QUIT

        now = time.get_ticks()
        #affichage du texte lettre par lettre
        if now - last_write > WRITE_TIME and run_text: 
            last_write = now
            #si nouvelle ligne on l'ajoute 
            if text[letter_index] == "\n":
                new_line = True
            if new_line:
                #si jamais on saute une ligne au niveau d'un mot
                if text[letter_index] != " ":
                    i = letter_index
                    j = 0
                    letter = ""
                    word = ""
                    #on récupère le mot qui est coupé
                    while letter != " ":
                        letter = text[i]
                        word = letter + word
                        i -= 1
                        j += 1
                    #on le supprime de la dernière ligne
                    text_lines[-1] = text_lines[-1][:-j+1]
                    #et on le réinjecte sur la ligne d'après
                    text_lines.append(word)
                else:
                    text_lines.append(text[letter_index])
                line_index += 1
                new_line = False
                if line_index >= 15:
                    run_text = False
            else: #sinon on ajoute la lettre a la ligne actuelle
                text_lines[-1] += text[letter_index]
            letter_index += 1
            #si le texte est fini on arrete de l'écrire et on coupe la musique
            if letter_index > len(text) - 1:
                run_text = False
            if not run_text:
                mixer.music.fadeout(400)
        
        #quand le bruitage fini on le relance tant que le texte s'écrit
        if now - last_sound > TYPEWRITER_LEN and run_text:
            last_sound = now
            mixer.music.play(0)

        #on affiche le fond
        # if index >= 0:
        surface.blit(img, (0, 0))
        # else:
        #     surface.fill(BLACK)
        i = 0
        #pour chaque ligne on l'affiche avec les bonnes coordonées
        for text_line in text_lines:
            text_surface = write_font.render(text_line, True, BLACK)
            text_rect = text_surface.get_rect()
            text_rect.top = first_coords[1] + 25*i
            if i > 2:
                text_rect.left = first_coords[0] - 50
            else:
                text_rect.left = first_coords[0]
            surface.blit(text_surface, text_rect)
            #si ca commence à déborder on demande une nouvelle ligne la prochaine boucle
            if text_line == text_lines[-1]: 
                if text_rect.right > 700:
                    new_line = True
            i += 1
        if not run_text:
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