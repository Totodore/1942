from pygame import *
from constants import *
from menu.save_handler import set_save_arcade, get_save_arcade

import pygame

class Score_Interface:
    def __init__(self, screen, stats):
        self.json_data = get_save_arcade()
        self.stats = stats
        self.screen = screen
        self.keep_drawing = False

        """
        Fonction qui détermine si l'on est dans le top 10 ou pas
        """
        #Si il reste encore de la place parmis les 10 meilleurs
        if len(self.json_data) < 10:
            self.add_stats = True
            self.save_score("Patate", False)
        #Si on est parmis les 10 meilleurs
        if len(self.json_data) > 10 and self.json_data[-1]["score"] > self.stats[0]:
            self.save_score("Patate", True)


    """
    Méthode qui sauvegarde le score
    """
    def save_score(self, name, remove_last):
        if remove_last:
            del self.json_data[-1]
        self.json_data.append({
            "name": name,
            "score": self.stats[0],
            "plane_kills": self.stats[1],
        })
        set_save_arcade(self.json_data)

    def event_handler(self):
        #on récupère les evenements
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.keep_drawing = False
            if self.getBasicEvent():
                self.keep_drawing = False
                return pygame.QUIT


    def draw_score(self):
        while self.keep_drawing:
            #si il ya a un event retourné alors on le retourne a nouveau
            event = self.event_handler()
            if event != None:
                return event

            self.screen.blit(Rect(0, 0, 1000, 600), GREEN)

            pygame.display.flip()


    def getBasicEvent(self, event):
        if event.type == pygame.QUIT:                
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F4:
                return True