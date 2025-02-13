# menu.py
import sys
import random
import pygame
import pygame_menu
from rollercoster.config import SCREEN_WIDTH, SCREEN_HEIGHT
from rollercoster.transitions import fade_in, fade_out
from rollercoster.drawing import draw_epic_menu_background
from rollercoster.game import RollerCoasterGame


fondo = pygame.image.load("imagen/background-menu.png")

def start_game_from_menu(values):
    try:
        func_str = values['func']
    except KeyError:
        func_str = "10 - x**2"
    try:
        xmin = float(values['xmin'])
    except:
        xmin = 0
    try:
        xmax = float(values['xmax'])
    except:
        xmax = 10
    surface = pygame.display.get_surface()
    fade_out(surface, speed=10)
    game = RollerCoasterGame(func_str, xmin, xmax)
    game.run()
    fade_in(surface, speed=10)
    main_menu()

def main_menu():
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    menu_theme = pygame_menu.themes.THEME_DARK.copy()
    menu_theme.title_font = 'Impact'
    menu_theme.title_font_size = 60
    menu_theme.widget_font = 'Arial'
    menu_theme.widget_font_size = 30
    menu_theme.widget_margin = (25, 25)
    menu_theme.background_color = (0, 0, 0)
    
    menu = pygame_menu.Menu('Roller Coaster Adventure', SCREEN_WIDTH, SCREEN_HEIGHT, theme=menu_theme)
    menu.add.label("Forjando leyendas en las alturas", font_size=30, padding=(0, 0))
    menu.add.text_input('Función f(x): ', default='10 - x**2', textinput_id='func')
    menu.add.text_input('Valor mínimo de x: ', default='0', textinput_id='xmin')
    menu.add.text_input('Valor máximo de x: ', default='10', textinput_id='xmax')
    menu.add.button('Iniciar Juego', lambda: start_game_from_menu(menu.get_input_data()))
    menu.add.button('Salir', pygame_menu.events.EXIT)

    fade_in(surface, speed=10)
    
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        surface.blit(fondo, (0, 0))
        menu.draw(surface)
        menu.update(events)
        pygame.display.flip()
