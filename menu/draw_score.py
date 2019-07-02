from pygame import image, font, rect, time
from constants import *
from menu.save_handler import set_save_arcade, get_save_arcade
from menu.account_handler import set_online_score, get_online_score
from threading import Thread
import pygame

class Score_Interface:
    """
    stats : tuple [score, plane_kill]
    """
    def __init__(self, screen, stats=(0, 0)):
        self.json_data_local = get_save_arcade()
        self.json_data_online = {}
        t1 = Thread(target=self.load_online_score)
        self.stats = stats
        self.screen = screen
        self.clock = time.Clock()
        self.keep_drawing = True
        self.add_stats = False
        
        self.write_font = font.Font("ath.ttf", 30)

        self.bg = image.load(path.join(SCORE_DIR, "scores_background.png")).convert_alpha()
        self.divs = (image.load(path.join(SCORE_DIR, "div_online.png")).convert_alpha(), image.load(path.join(SCORE_DIR, "div_local.png")).convert_alpha())
        self.tabs = (image.load(path.join(SCORE_DIR, "tab_online.png")).convert_alpha(), image.load(path.join(SCORE_DIR, "tab_local.png")).convert_alpha())
        self.score_window = image.load(path.join(SCORE_DIR, "div_ask_score.png")).convert_alpha()

        self.last_anim = 0
        self.arrow_l = image.load(path.join(ARCADE_DIR, "arrow_left.png")).convert_alpha()
        self.arrow_r = image.load(path.join(ARCADE_DIR, "arrow_right.png")).convert_alpha()
        self.arrow_l_left = 100
        self.arrow_r_left = WIDTH-100
        self.forward = True

        self.arrow_r_rect = self.arrow_r.get_rect()
        self.arrow_r_rect.center = (WIDTH-40, int(HEIGHT/2))
        self.arrow_l_rect = self.arrow_l.get_rect()
        self.arrow_l_rect.center = (40, int(HEIGHT/2))

        self.div_index = 0
        self.input_str = ""
        
        #Doit être appelé avant check score pour récupérer tous les scores
        t1.start()
        self.screen.blit(self.bg, (0, 0))
        pygame.display.flip()
        t1.join()
        if self.stats[0] > 1:
            self.check_score()

    def load_online_score(self):
        self.json_data_online = get_online_score()

    def getBasicEvent(self, event):
        if event.type == pygame.QUIT:                
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F4:
                return True


    """
    Méthode qui détermine si l'on est dans le top 10 ou pas en mode local et en mode hors ligne
    si name est passé en argument on sauvegarde les scores
    """
    def check_score(self, name=None):
        #Si il reste encore de la place parmis les 5 meilleurs local
        if len(self.json_data_local) < 5:
            self.add_stats = True
            if name:
                self.save_score(name, False)
        #Si on est parmis les 5 meilleurs local
        if len(self.json_data_local) >= 5 and self.json_data_local[-1]["score"] < self.stats[0]:
            self.add_stats = True
            if name:
                self.save_score(name, True)

        #Si il reste encore de la place parmis les 10 meilleurs online
        if len(self.json_data_online) < 5:
            self.add_stats = True
            if name:
                self.save_score(name, False, online=True)
        #Si on est parmis les 10 meilleurs online
        if len(self.json_data_online) >= 5 and self.json_data_online[-1]["score"] < self.stats[0]:
            self.add_stats = True
            if name:
                self.save_score(name, True, online=True)
            
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
        if online: set_online_score(json_data)
        else: set_save_arcade(json_data)

    """
    Méthode de gestion de l'affichage des flèches
    """
    def arrow_handler(self):
        #si les flèches doivent avancer on change les positions en fonction
        if self.forward == True:
            self.arrow_r_rect.left += 1
            self.arrow_l_rect.left -= 1
            #si la position de la fleches dépasse un maximum on la fait reculer
            if self.arrow_r_rect.left > self.arrow_r_left + ARROW_MOVE:
                self.forward = False
        #si les fleches doivent reculer on change les positions en fonction
        else:
            self.arrow_r_rect.left -= 1
            self.arrow_l_rect.left += 1
            #si la position de la fleche depasse sa position initiale on la fait a nouveau avancer
            if self.arrow_r_rect.left <= self.arrow_r_left:
                self.forward = True

    def event_handler(self):
        #on récupère les evenements
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if self.add_stats:
                    if event.key == pygame.K_BACKSPACE and len(self.input_str) > 0:
                        self.input_str = self.input_str[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.add_stats = False
                    elif event.key == pygame.K_RETURN:
                        if len(self.input_str) > 2:
                            self.check_score(self.input_str)
                        self.add_stats = False
                    elif len(self.input_str) < 15 and len(self.input_str) >= 0:
                        if event.key != pygame.K_BACKSPACE and event.key != pygame.K_TAB:
                            self.input_str += event.unicode
                else:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.keep_drawing = False
                    elif event.key == pygame.K_RIGHT:
                        self.div_index += 1
                        if self.div_index > 1:
                            self.div_index = 0
                    elif event.key == pygame.K_LEFT:
                        self.div_index -=1
                        if self.div_index < 0:
                            self.div_index = 1
            if self.getBasicEvent(event):
                self.keep_drawing = False
                return pygame.QUIT


    def draw_score(self):
        while self.keep_drawing:
            self.now = time.get_ticks()
            #si il ya a un event retourné alors on le retourne a nouveau
            event = self.event_handler()
            if event != None:
                return event

            # self.screen.blit(Rect(0, 0, 1000, 600), GREEN)
            self.screen.blit(self.bg, (0,0))
            div_rect = self.divs[self.div_index].get_rect()
            div_rect.center = (int(WIDTH/2), int(HEIGHT/2))
            self.screen.blit(self.divs[self.div_index], div_rect)
            tab_rect_local = self.tabs[1].get_rect()
            tab_rect_local.topleft = (div_rect.left + 100, div_rect.top)
            tab_rect_online = self.tabs[0].get_rect()
            tab_rect_online.topleft = (tab_rect_local.right, div_rect.top)
            self.screen.blit(self.tabs[1], tab_rect_local)
            self.screen.blit(self.tabs[0], tab_rect_online)
            
            if self.div_index == 0:
                i = 0
                for score in self.json_data_online:
                    name_text = self.write_font.render(str(score["name"]), True, WHITE)
                    name_rect = name_text.get_rect()
                    name_rect.topleft = (div_rect.left + 170, div_rect.top + 222 + 48*i)
                    plane_text = self.write_font.render(str(score["plane_kills"]), True, WHITE)
                    plane_rect = plane_text.get_rect()
                    plane_rect.topleft = (div_rect.left + 480, div_rect.top + 222 + 48*i)
                    score_text = self.write_font.render(str(score["score"]), True, WHITE)
                    score_rect = score_text.get_rect()
                    score_rect.topleft = (div_rect.left + 605, div_rect.top + 222 + 48*i)

                    self.screen.blit(score_text, score_rect)
                    self.screen.blit(name_text, name_rect)
                    self.screen.blit(plane_text, plane_rect)

                    i += 1
            elif self.div_index == 1:
                i = 0
                for score in self.json_data_local:
                    name_text = self.write_font.render(str(score["name"]), True, WHITE)
                    name_rect = name_text.get_rect()
                    name_rect.topleft = (div_rect.left + 170, div_rect.top + 222 + 48*i)
                    plane_text = self.write_font.render(str(score["plane_kills"]), True, WHITE)
                    plane_rect = plane_text.get_rect()
                    plane_rect.topleft = (div_rect.left + 480, div_rect.top + 222 + 48*i)
                    score_text = self.write_font.render(str(score["score"]), True, WHITE)
                    score_rect = score_text.get_rect()
                    score_rect.topleft = (div_rect.left + 605, div_rect.top + 222 + 48*i)

                    self.screen.blit(score_text, score_rect)
                    self.screen.blit(name_text, name_rect)
                    self.screen.blit(plane_text, plane_rect)
                    i += 1

            if self.add_stats:
                window_rect = self.score_window.get_rect()
                window_rect.center = (int(WIDTH/2), int(HEIGHT/2))
                input_rect = rect.Rect(window_rect.left + 172, window_rect.top + 288, 388, 34)
                text = self.write_font.render(self.input_str, True, BLACK)
                self.screen.blit(self.score_window, window_rect)
                self.screen.blit(text, input_rect)
            
            #on fait bouger les fleches avec un certain délai pour pas que ca aille trop vite
            if self.now - self.last_anim > ARROW_DELAY:
                self.last_anim = self.now
                self.arrow_handler()
            #on affiche les fleches
            if self.div_index != 0 and not self.add_stats:
                self.screen.blit(self.arrow_l, self.arrow_l_rect)   
            if self.div_index != 1 and not self.add_stats:
                self.screen.blit(self.arrow_r, self.arrow_r_rect)

            pygame.display.flip()

