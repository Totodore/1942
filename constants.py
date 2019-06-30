from os import path

WIDTH = 1000
HEIGHT = 600
FPS = 60

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WRITE_TIME = 5  #vitesse d'écriture
FLASH_DELAY = 400
TYPEWRITER_LEN = 6383   
ARROW_MOVE = 20     #représente l'amplitude de deplacement des flèches
ARROW_DELAY = 20    #représente la vitesse de deplacement des flèches

IMG_DIR = path.join(path.dirname (__file__), 'img')
ENGINE_DIR = path.join(path.dirname(__file__), "engine")
MENU_DIR = path.join(path.dirname(__file__), "img/menu")
START_DIR = path.join(path.dirname(__file__), "img/menu/start")
THUMB_DIR = path.join(path.dirname(__file__), "img/menu/level_select/levels")
ARCADE_DIR = path.join(path.dirname(__file__), "img/menu/arcade_select")
SCORE_DIR = path.join(path.dirname(__file__), "img/menu/scores")
FONT_DIR = path.join(path.dirname(__file__), "fonts")
DATA_DIR = path.join(path.dirname(__file__), "data")
SOUND_DIR = path.join(path.dirname(__file__), "sounds")
FONT_DIR = path.join(path.dirname(__file__), "fonts")


