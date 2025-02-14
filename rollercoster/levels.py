
import pygame
import pygame_menu
from rollercoster.config import SCREEN_WIDTH, SCREEN_HEIGHT
from rollercoster.transitions import fade_in, fade_out
from rollercoster.game import RollerCoasterGame

def cambiar_opacidad(imagen):
    imagen = imagen.copy()  # Crear una copia para no modificar la original
    imagen.fill((150, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return imagen

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
    mostrar_nivel()

def mostrar_nivel():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    fondo = pygame.image.load("imagen/background-levels.png")
    level1 = pygame.image.load("imagen/level-1.png")
    level2 = pygame.image.load("imagen/level-2.png")
    level3 = pygame.image.load("imagen/level-3.png")
    level4 = pygame.image.load("imagen/level-4.png")
    level5 = pygame.image.load("imagen/level-5.png")
    makeLevel = pygame.image.load("imagen/makelevel.png")


    level1_origial = level1.copy()
    level2_origial = level2.copy()
    level3_origial = level3.copy()
    level4_origial = level4.copy()
    level5_origial = level5.copy()
    makeLevel_origial = makeLevel.copy()

    running = True
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        level1 = level1_origial
        level2 = level2_origial
        level3 = level3_origial
        level4 = level4_origial
        level5 = level5_origial
        makeLevel = makeLevel_origial


        if (190 <= mouse_x <= 485) and (193 <= mouse_y <= 393):
            level1 = cambiar_opacidad(level1) 
        else:
            level1 = level1_origial
        if (497 <= mouse_x <= 792) and (193 <= mouse_y <= 393):
            level2 = cambiar_opacidad(level2) 
        else:
            level2 = level2_origial
        if (190 <= mouse_x <= 485) and (405 <= mouse_y <= 605):
            level3 = cambiar_opacidad(level3) 
        else:
            level3 = level3_origial
        if (497 <= mouse_x <= 792) and (405 <= mouse_y <= 605):
            level4 = cambiar_opacidad(level4) 
        else:
            level4 = level4_origial
        if (366 <= mouse_x <= 662) and (643 <= mouse_y <= 843):
            level5 = cambiar_opacidad(level5) 
        else:
            level5 = level5_origial
        if (365 <= mouse_x <= 663) and (910 <= mouse_y <= 995):
            makeLevel = cambiar_opacidad(makeLevel) 
        else:
            makeLevel = makeLevel_origial


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (190 <= mouse_x <= 485) and (193 <= mouse_y <= 393):
                    start_game_from_menu({'func': 'x+1', 'xmin': 0, 'xmax' : 10})
                if (497 <= mouse_x <= 792) and (193 <= mouse_y <= 393):
                    start_game_from_menu({'func': 'x+1', 'xmin': 0, 'xmax' : 10})
                if (190 <= mouse_x <= 485) and (405 <= mouse_y <= 605):
                    start_game_from_menu({'func': '10 - x**2', 'xmin': 0, 'xmax' : 10})
                if (497 <= mouse_x <= 792) and (405 <= mouse_y <= 605):
                    start_game_from_menu({'func': 'x+1', 'xmin': 0, 'xmax' : 10})
                if (366 <= mouse_x <= 662) and (643 <= mouse_y <= 843):
                    start_game_from_menu({'func': 'x+1', 'xmin': 0, 'xmax' : 10})
                if (365 <= mouse_x <= 663) and (910 <= mouse_y <= 995):
                    print("Pressed")
    
               


        screen.blit(fondo, (0, 0))
        screen.blit(level1, (0, 0))
        screen.blit(level2, (0, 0))
        screen.blit(level3, (0, 0))
        screen.blit(level4, (0, 0))
        screen.blit(level5, (0, 0))
        screen.blit(makeLevel, (0, 0))
    
        pygame.display.flip()
