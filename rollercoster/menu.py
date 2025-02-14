# menu.py
import sys
import pygame
import pygame_menu
from rollercoster.config import SCREEN_WIDTH, SCREEN_HEIGHT
from rollercoster.transitions import fade_in
from rollercoster.game import RollerCoasterGame
from rollercoster.levels import mostrar_nivel


pygame.init()

# Cargar imágenes
fondo = pygame.image.load("imagen/background-menu.png")
jugarButton = pygame.image.load("imagen/button-jugar.png")
historialButton = pygame.image.load("imagen/button-historial.png")
instrtuccionesButton = pygame.image.load("imagen/button-instrucciones.png")
creditosButton = pygame.image.load("imagen/button-creditos.png")

# Guardar imágenes originales para restaurarlas después
jugarButton_original = jugarButton.copy()
historialButton_original = historialButton.copy()
instrtuccionesButton_original = instrtuccionesButton.copy()
creditosButton_original = creditosButton.copy()

# Coordenadas botón 
global_x1, global_x2 = 376, 635

def cambiar_opacidad(imagen):
    imagen = imagen.copy()  # Crear una copia para no modificar la original
    imagen.fill((150, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return imagen

def menu():
    global jugarButton, historialButton, instrtuccionesButton, creditosButton  # Declarar variables globales
    
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_in(surface, speed=10)
    
    while True:
        events = pygame.event.get()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Restaurar imágenes originales antes de modificar
        jugarButton = jugarButton_original
        historialButton = historialButton_original
        instrtuccionesButton = instrtuccionesButton_original
        creditosButton = creditosButton_original

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if (global_x1 <= mouse_x <= global_x2) and (440 <= mouse_y <= 538):
                jugarButton = cambiar_opacidad(jugarButton_original) 
            else:
                jugarButton = jugarButton_original

            if (global_x1 <= mouse_x <= global_x2) and (558 <= mouse_y <= 652):
                historialButton = cambiar_opacidad(historialButton_original)
            else:
                historialButton = historialButton_original

            if (global_x1 <= mouse_x <= global_x2) and (672 <= mouse_y <= 768):
                instrtuccionesButton = cambiar_opacidad(instrtuccionesButton_original)
            else:
                instrtuccionesButton = instrtuccionesButton_original

            if (global_x1 <= mouse_x <= global_x2) and (788 <= mouse_y <= 882):
                creditosButton = cambiar_opacidad(creditosButton_original)
            else:
                creditosButton = creditosButton_original

            # Detectar clic del mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (global_x1 <= mouse_x <= global_x2) and (440 <= mouse_y <= 538):
                    from rollercoster.levels import mostrar_nivel 
                    mostrar_nivel()
                    return 
                
                # Boton historial
                if (global_x1 <= mouse_x <= global_x2) and (558 <= mouse_y <= 652):
                    print("Pressed")
                
                # Boton instrucciones
                if (global_x1 <= mouse_x <= global_x2) and (672 <= mouse_y <= 768):
                    print("Pressed")

                # Boton creditos
                if (global_x1 <= mouse_x <= global_x2) and (788 <= mouse_y <= 882):
                    print("Pressed")

        surface.blit(fondo, (0, 0))
        surface.blit(jugarButton, (0, 0))
        surface.blit(historialButton, (0, 0))
        surface.blit(instrtuccionesButton, (0, 0))
        surface.blit(creditosButton, (0, 0))

        pygame.display.flip()
