from os import path

WIDTH = 1000
HEIGHT = 600
FPS = 30

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

SPEED_FACTOR_Y = 20
SPEED_FACTOR_X = 100
SPEED_BACKGROUND = 5
AMMO_SPEED_FACTOR = 20
GIF_SPEED = 30

BULLET_SOUND_ENNEMY = 0.05
BULLET_SOUND_PLAYER = 0.6
SOUND_ENNEMY = 0.1
SOUND_PLAYER = 0.4
EXPLOSION_SOUND = 1
PLAYER_CHANNEL = 1
MUSIC_CHANNEL = 0
AMMO_CHANNEL = 2
EXPLOSION_CHANNEL = (3, 4, 5)

IMG_DIR = path.join(path.dirname (__file__), '../img')
SOUND_DIR = path.join(path.dirname(__file__), "../sounds")
EXPLOSION_DIR = path.join(path.dirname(__file__), '../img/explosions')
SPEC_DIR = path.join(path.dirname(__file__), '../data/player.json')
LEVEL_DIR = path.join(path.dirname(__file__), "../data/levels.json")
ARCADE_DIR = path.join(path.dirname(__file__), "../data/arcade.json")
PLANES_DIR = path.join(path.dirname(__file__), "../img/mobs/planes")
BOSS_DIR = path.join(path.dirname(__file__), "../img/mobs/boss")
BULLET_DIR = path.join(path.dirname(__file__), "../img/mobs/bullets")
ENNEMIES_DIR = path.join(path.dirname(__file__), "../img/mobs/ennemies")
MAP_DIR = path.join(path.dirname(__file__), "../img/map/")
ATH_DIR = path.join(path.dirname(__file__), "../img/ath")
FONT_DIR = path.join(path.dirname(__file__), "../fonts")
AMMO_DIR = path.join(path.dirname(__file__), "../img/mobs/bullets/ammo_box")
