# transitions.py
import pygame
from rollercoster.config import SCREEN_WIDTH, SCREEN_HEIGHT

def fade_out(surface, speed=5):
    """Efecto fade out: de transparente a negro."""
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 256, speed):
        fade_surface.set_alpha(alpha)
        surface.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

def fade_in(surface, speed=5):
    """Efecto fade in: de negro a transparente."""
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))
    for alpha in range(255, -1, -speed):
        fade_surface.set_alpha(alpha)
        surface.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)
