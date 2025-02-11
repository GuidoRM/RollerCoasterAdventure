# drawing.py
import pygame

def draw_vertical_gradient(surface, top_color, bottom_color):
    """Dibuja un degradado vertical en la superficie dada."""
    height = surface.get_height()
    width = surface.get_width()
    for y in range(height):
        ratio = y / height
        color = [int(top_color[i]*(1 - ratio) + bottom_color[i]*ratio) for i in range(3)]
        pygame.draw.line(surface, color, (0, y), (width, y))

def draw_epic_menu_background(surface, stars):
    """Dibuja el fondo épico para el menú con un degradado y estrellas."""
    draw_vertical_gradient(surface, (10, 10, 40), (0, 0, 0))
    for pos in stars:
        pygame.draw.circle(surface, (255, 255, 255), pos, 2)
