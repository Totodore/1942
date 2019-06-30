from pygame import image
from constants import *
from menu.save_handler import set_save_arcade, get_save_arcade
from menu.account_handler import set_online_score, get_online_score
import pygame

class Score_Interface:
    """
    stats : tuple [score, plane_kill]
    """
    def __init__(self, screen, stats):
        self.json_data_local = get_save_arcade()
        # self.json_data_online = get_online_score()
        self.stats = stats
        self.screen = screen
        self.keep_drawing = True

        self.bg = image.load(path.join(SCORE_DIR, "scores_background.png")).convert_alpha()
        self.divs = (image.load(path.join(SCORE_DIR, "div_online.png")).convert_alpha(), image.load(path.join(SCORE_DIR, "div_local.png")).convert_alpha())
        self.div_index = 0;
        self.draw_score()

    def getBasicEvent(self, event):
        if event.type == pygame.QUIT:                
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F4:
                return True


    """
    Méthode qui détermine si l'on est dans le top 10 ou pas en mode local et en mode hors ligne
    """
    def check_score(self):
        #Si il reste encore de la place parmis les 10 meilleurs local
        if len(self.json_data_local) < 10:
            self.add_stats = True
            self.save_score("Patate", False)
        #Si on est parmis les 10 meilleurs local
        if len(self.json_data_local) > 10 and self.json_data_local[-1]["score"] > self.stats[0]:
            self.save_score("Patate", True)

        #Si il reste encore de la place parmis les 10 meilleurs online
        if len(self.json_data_online) < 10:
            self.add_stats = True
            self.save_score("Patate", False, online=True)
        #Si on est parmis les 10 meilleurs online
        if len(self.json_data_online) > 10 and self.json_data_online[-1]["score"] > self.stats[0]:
            self.save_score("Patate", True, online=True)
            
    """
    Méthode qui sauvegarde le score
    """
    def save_score(self, name, remove_last, online = False):
        if online: json_data = self.json_data_online
        else: json_data = self.json_data_local

        if remove_last:
            del json_data[-1]
        json_data.append({
            "name": name,
            "score": self.stats[0],
            "plane_kills": self.stats[1],
        })
        set_save_arcade(json_data)

    def event_handler(self):
        #on récupère les evenements
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.keep_drawing = False
                if event.key == pygame.K_RIGHT:
                    self.div_index += 1
                    if self.div_index > 1:
                        self.div_index = 0
                if event.key == pygame.K_LEFT:
                    self.div_index -=1
                    if self.div_index < 0:
                        self.div_index = 1
            if self.getBasicEvent(event):
                self.keep_drawing = False
                return pygame.QUIT


    def draw_score(self):
        while self.keep_drawing:
            #si il ya a un event retourné alors on le retourne a nouveau
            event = self.event_handler()
            if event != None:
                return event

            # self.screen.blit(Rect(0, 0, 1000, 600), GREEN)
            self.screen.blit(self.bg, (0,0))
            self.screen.blit(self.divs[self.div_index], (0, 0));

            pygame.display.flip()

    """
    Fonction pour passer du score local au score online
    """
    def switch_score(self):
        pass

