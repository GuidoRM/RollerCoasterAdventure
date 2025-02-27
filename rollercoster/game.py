# game.py
import sys
import time
import random
import numpy as np
import sympy as sp
import pygame
import pygame_menu

from rollercoster.config import SCREEN_WIDTH, SCREEN_HEIGHT, ANIM_HEIGHT, QUIZ_HEIGHT,     COLOR_BG, COLOR_TRACK, COLOR_CAR, COLOR_OPTION_BG, COLOR_OPTION_HOVER, COLOR_TEXT,     COLOR_TIMER, COLOR_FEEDBACK, COLOR_MODAL_BG, COLOR_MODAL_BORDER
from rollercoster.transitions import fade_in, fade_out
from rollercoster.drawing import draw_vertical_gradient

nivel = 0

class RollerCoasterGame:
    def __init__(self, func_str, xmin, xmax, level):
        global nivel
        nivel = level
        # Usamos la misma pantalla definida en el menú
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption("Roller Coaster Adventure: Quiz del Mundo")
        self.clock = pygame.time.Clock()

        # Fuentes
        self.font = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.large_font = pygame.font.SysFont("Arial", 36)

        # Áreas de la pantalla
        self.anim_rect = pygame.Rect(0, 0, SCREEN_WIDTH, ANIM_HEIGHT)
        self.quiz_rect = pygame.Rect(0, ANIM_HEIGHT, SCREEN_WIDTH, QUIZ_HEIGHT)

        # Configuración de la pista
        self.func_str = func_str
        self.xmin = xmin
        self.xmax = xmax
        x = sp.symbols('x')
        try:
            f_sym = sp.sympify(func_str)
        except Exception as e:
            f_sym = sp.sympify("10 - x**2")
        self.f_sym = f_sym
        self.f = lambda val: float(f_sym.subs(x, val))
        self.num_points = 1000
        xs = np.linspace(self.xmin, self.xmax, self.num_points)
        self.track_points = [(x_val, self.f(x_val)) for x_val in xs]
        self.min_y = min(pt[1] for pt in self.track_points)
        self.max_y = max(pt[1] for pt in self.track_points)

        # Variables del juego
        self.car_index = 0.0
        self.speed_factor = 0.5
        self.unanswered_count = 0
        self.quiz_correct = 0
        self.question_time_limit = 5
        self.question_start_time = time.time()
        self.current_question_index = 0
        self.quiz_questions = self.get_quiz_questions()
        self.feedback_message = ""
        self.game_start_time = time.time()
        self.game_over = False

        self.option_rects = []
        self.transition_alpha = 0


    def show_story(self):
        """Muestra la pantalla introductoria con la historia del juego."""
        splash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_vertical_gradient(splash_surface, (0, 0, 80), (0, 0, 0))
        story_lines = [
            "¡Bienvenido a Roller Coaster Adventure!",
            "Eres un ingeniero visionario encargado de crear",
            "la montaña rusa más espectacular del mundo.",
            "Responde desafíos matemáticos para diseñar tu pista",
            "y acelerar tu carrito.",
            "¡Cada respuesta correcta te acerca a tu leyenda!",
            "Presiona cualquier tecla para comenzar..."
        ]
        self.screen.blit(splash_surface, (0, 0))
        y = SCREEN_HEIGHT // 3
        for line in story_lines:
            text_surf = self.large_font.render(line, True, COLOR_TEXT)
            x = (SCREEN_WIDTH - text_surf.get_width()) // 2
            self.screen.blit(text_surf, (x, y))
            y += 50
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    waiting = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.clock.tick(15)
        fade_in(self.screen, speed=10)

    def world_to_screen(self, x, y):
        """Convierte coordenadas 'mundo' a la zona de animación."""
        margin = 40
        screen_x = margin + (x - self.xmin) / (self.xmax - self.xmin) * (SCREEN_WIDTH - 2 * margin)
        screen_y = ANIM_HEIGHT - margin - (y - self.min_y) / (self.max_y - self.min_y) * (ANIM_HEIGHT - 2 * margin)
        return (int(screen_x), int(screen_y))

    def draw_animation(self):
        """Dibuja la animación de la montaña rusa."""
        anim_surface = self.screen.subsurface(self.anim_rect)
        draw_vertical_gradient(anim_surface, (135, 206, 250), (25, 25, 112))
        track_points_screen = [self.world_to_screen(x, y) for (x, y) in self.track_points]
        if len(track_points_screen) > 1:
            pygame.draw.lines(anim_surface, COLOR_TRACK, False, track_points_screen, 4)
        if int(self.car_index) >= len(self.track_points):
            self.car_index = len(self.track_points) - 1
        pos = self.world_to_screen(*self.track_points[int(self.car_index)])
        shadow_pos = (pos[0] + 3, pos[1] + 3)
        pygame.draw.circle(anim_surface, (0, 0, 0), shadow_pos, 12)
        pygame.draw.circle(anim_surface, COLOR_CAR, pos, 10)
        score_text = self.small_font.render(f"Respuestas correctas: {self.quiz_correct}", True, COLOR_TEXT)
        anim_surface.blit(score_text, (20, 20))

    def draw_quiz(self):
        """Dibuja el panel del quiz."""
        quiz_surface = self.screen.subsurface(self.quiz_rect)
        draw_vertical_gradient(quiz_surface, (60, 60, 60), (20, 20, 20))
        if self.current_question_index < len(self.quiz_questions):
            q = self.quiz_questions[self.current_question_index]
            question_text = q["question"]
        else:
            question_text = "¡Desafío completado!"
        question_surface = self.font.render("Desafío: " + question_text, True, COLOR_TEXT)
        quiz_surface.blit(question_surface, (20, 10))
        self.option_rects = []
        mx, my = pygame.mouse.get_pos()
        rel_mx = mx - self.quiz_rect.x
        rel_my = my - self.quiz_rect.y
        if self.current_question_index < len(self.quiz_questions):
            options = self.quiz_questions[self.current_question_index]["options"]
            for i, opt in enumerate(options):
                rect = pygame.Rect(20, 60 + i * 50, self.quiz_rect.width - 40, 40)
                self.option_rects.append((rect, opt))
                if rect.collidepoint(rel_mx, rel_my):
                    color = COLOR_OPTION_HOVER
                else:
                    color = COLOR_OPTION_BG
                pygame.draw.rect(quiz_surface, color, rect, border_radius=8)
                if rect.collidepoint(rel_mx, rel_my):
                    pygame.draw.rect(quiz_surface, COLOR_TIMER, rect, 2, border_radius=8)
                opt_surface = self.small_font.render(opt, True, (0, 0, 0))
                text_rect = opt_surface.get_rect(center=rect.center)
                quiz_surface.blit(opt_surface, text_rect)
        remaining = max(0, int(self.question_time_limit - (time.time() - self.question_start_time)))
        timer_surface = self.small_font.render(f"Tiempo: {remaining} seg", True, COLOR_TIMER)
        quiz_surface.blit(timer_surface, (20, 260))
        speed_surface = self.small_font.render(f"Velocidad: {self.speed_factor:.1f}", True, COLOR_TEXT)
        quiz_surface.blit(speed_surface, (20, 290))
        progress_surface = self.small_font.render(
            f"Pregunta {min(self.current_question_index+1, len(self.quiz_questions))} de {len(self.quiz_questions)}", True, COLOR_TEXT)
        quiz_surface.blit(progress_surface, (20, 320))
        feedback_surface = self.small_font.render(self.feedback_message, True, COLOR_FEEDBACK)
        quiz_surface.blit(feedback_surface, (20, 350))
        bar_width = self.quiz_rect.width - 40
        bar_height = 10
        progress = (self.current_question_index) / len(self.quiz_questions)
        progress_bar_rect = pygame.Rect(20, self.quiz_rect.height - 30, bar_width, bar_height)
        pygame.draw.rect(quiz_surface, (100, 100, 100), progress_bar_rect, border_radius=5)
        progress_fill_rect = pygame.Rect(20, self.quiz_rect.height - 30, int(bar_width * progress), bar_height)
        pygame.draw.rect(quiz_surface, (0, 200, 0), progress_fill_rect, border_radius=5)

        if self.transition_alpha > 0:
            transition_surface = pygame.Surface((self.quiz_rect.width, self.quiz_rect.height))
            transition_surface.fill((0, 0, 0))
            transition_surface.set_alpha(self.transition_alpha)
            quiz_surface.blit(transition_surface, (0, 0))

    def get_quiz_questions(self):
        """Retorna una lista de 5 preguntas aleatorias para el quiz."""
        pool_facil = [
            {"question": "¿Cuánto es 5 + 3?", "options": ["10", "6", "8", "7"], "answer": "8"},
            {"question": "¿Cuánto es 7 × 6?", "options": ["36", "42", "40", "48"], "answer": "42"},
            {"question": "Si un triángulo tiene dos lados de 5 cm y 5 cm, ¿cómo se llama?", "options": ["Equilátero", "Escaleno", "Rectángulo","Isósceles"], "answer": "Isósceles"},
            {"question": "¿Cuál es el resultado de 2²?", "options": ["4", "2", "8", "6"], "answer": "4"},
            {"question": "¿Cuál es la raíz cuadrada de 81?", "options": ["8", "9", "7", "6"], "answer": "9"}
        ]
        pool_medio = [
            {"question": "¿Cuánto es 12 ÷ 4?", "options": ["4", "3", "6", "2"], "answer": "3"},
            {"question": "Si x + 3 = 10, ¿cuánto vale x?", "options": ["7", "10", "3", "13"], "answer": "7"},
            {"question": "Si un cuadrado tiene un área de 16 cm², ¿cuánto mide cada lado?", "options": ["3 cm", "5 cm", "6 cm", "4 cm"], "answer": "4 cm"},
            {"question": "¿Cuál es el valor de π aproximadamente?", "options": ["3.21", "3.41", "3.04", "3.14"], "answer": "3.14"},
            {"question": "¿Cuál es la derivada de x³?", "options": ["3x", "x²", "3x²", "x³"], "answer": "3x²"}
        ]
        pool_dificil = [
            {"question": "¿Cuál es la derivada de ln(x)?", "options": ["ln(x)", "1/x", "x", "e^x"], "answer": "1/x"},
            {"question": "¿Cuál es la integral de x dx?", "options": ["(1/2)x² + C", "x + C", "x² + C", "e^x + C"], "answer": "(1/2)x² + C"},
            {"question": "Si f(x) = x² + 2x, ¿cuál es f'(x)?", "options": ["x + 2", "x² + 2", "2x + 2", "2x"], "answer": "2x + 2"},
            {"question": "¿Cuál es el área de un círculo de radio 5?", "options": ["25π", "10π", "5π", "50π"], "answer": "25π"},
            {"question": "¿Cuál es la derivada de e^(3x)?", "options": ["3e^(3x)", "e^(3x)", "x*e^(3x)", "ln(e)*e^(3x)"], "answer": "3e^(3x)"}
        ]
        pool_muyDificil = [
            {"question": "Si f(x) = e^x + ln(x), ¿cuál es f'(x)?", "options": ["ln(x) + 1/x", "e^x", "e^x + 1/x", "x e^x"], "answer": "e^x + 1/x"},
            {"question": "Si la función f(x) = x³ - 3x² + 2x tiene un máximo, ¿dónde ocurre?", "options": ["x = 1", "x = 2", "x = 0", "x = -1"], "answer": "x = 1"},
            {"question": "Si la hipotenusa de un triángulo rectángulo es 10 y un cateto es 6, ¿cuánto mide el otro cateto?", "options": ["4", "8", "6", "5"], "answer": "8"},
            {"question": "¿Cuál es la integral de sec²(x) dx?", "options": ["cos(x) + C", "tan(x) + C", "sin(x) + C", "-tan(x) + C"], "answer": "tan(x) + C"},
            {"question": "Si la serie geométrica infinita a + ar + ar² + ... converge, ¿qué condición debe cumplirse para r?", "options": ["r < -1", "|r| > 1", "r > 1", "|r| < 1"], "answer": "|r| < 1"}
        ]
        pool_einstein = [
            {"question": "¿Cuál es la solución real de la ecuación x^4 - 5x² + 4 = 0?", "options": ["0, ±1", "±3, ±2", "±2, ±1", "±4, ±2"], "answer": "±2, ±1"},
            {"question": "¿Cuál es la derivada de sinh(x)?", "options": ["sinh(x)", "cosh(x)", "-cosh(x)", "-sinh(x)"], "answer": "cosh(x)"},
            {"question": "Si f(x) = x^x, ¿cuál es f'(x)?", "options": ["x^x(1 + ln(x))", "x^(x-1)", "ln(x)", "x^x * ln(x)"], "answer": "x^x(1 + ln(x))"},
            {"question": "Si una matriz A tiene un determinante de 0, ¿qué significa?", "options": ["Es diagonal", "Es invertible", "Tiene traza 0", "Es singular"], "answer": "Es singular"},
            {"question": "Si A es una matriz ortogonal, ¿qué se cumple para A⁻¹?", "options": ["A⁻¹ no existe", "A⁻¹ = -A", "A⁻¹ = A²", "A⁻¹ = Aᵀ"], "answer": "A⁻¹ = Aᵀ"}
        ]

        if nivel == 1:
            return random.sample(pool_facil, 5)
        elif nivel == 2:
            return random.sample(pool_medio, 5)
        elif nivel == 3:
            return random.sample(pool_dificil, 5)
        elif nivel == 4:
            return random.sample(pool_muyDificil, 5)
        elif nivel == 5:
            return random.sample(pool_einstein, 5)

    def process_timeout(self):
        """Procesa el evento cuando se agota el tiempo de respuesta."""
        self.feedback_message = "Tiempo agotado. Velocidad reducida."
        self.speed_factor = max(0.5, self.speed_factor - 0.5)
        self.unanswered_count += 1
        self.current_question_index += 1
        self.question_start_time = time.time()
        self.transition_alpha = 200

    def process_answer(self, selected_option):
        """Procesa la respuesta seleccionada por el usuario."""
        q = self.quiz_questions[self.current_question_index]
        if selected_option == q["answer"]:
            self.feedback_message = "¡Correcto! Velocidad aumentada."
            self.quiz_correct += 1
            self.speed_factor = min(5.0, self.speed_factor + 0.5)
        else:
            self.feedback_message = f"Incorrecto. La respuesta es: {q['answer']}. Velocidad reducida."
            self.speed_factor = max(0.5, self.speed_factor - 0.5)
        self.current_question_index += 1
        self.question_start_time = time.time()
        self.transition_alpha = 200

    def update(self, dt):
        """Actualiza la posición del carrito y verifica el temporizador del quiz."""
        if not self.game_over:
            self.car_index += self.speed_factor * dt * 50
            if self.car_index >= len(self.track_points) - 1:
                self.game_over = True
            if self.current_question_index < len(self.quiz_questions):
                elapsed = time.time() - self.question_start_time
                if elapsed >= self.question_time_limit:
                    self.process_timeout()
                    if self.unanswered_count >= 2:
                        self.game_over = True
            if self.unanswered_count >= 2:
                self.game_over = True

        if self.transition_alpha > 0:
            self.transition_alpha = max(0, self.transition_alpha - 5)

    def show_final_modal(self):
        """Muestra una ventana modal con los resultados finales."""
        modal_width = 600
        modal_height = 350
        modal_rect = pygame.Rect((SCREEN_WIDTH - modal_width) // 2,
                                 (SCREEN_HEIGHT - modal_height) // 2,
                                 modal_width, modal_height)
        modal_surface = pygame.Surface((modal_width, modal_height))
        draw_vertical_gradient(modal_surface, (50, 50, 50), (10, 10, 10))
        pygame.draw.rect(modal_surface, COLOR_MODAL_BORDER, modal_surface.get_rect(), 4, border_radius=10)

        elapsed = time.time() - self.game_start_time
        outcome = "¡Éxito en la Montaña Rusa!" if self.quiz_correct >= 3 else "Fracaso en la Aventura"
        result_text = f"{outcome}\nRespuestas correctas: {self.quiz_correct}/{len(self.quiz_questions)}\nTiempo: {elapsed:.1f} seg"
        lines = result_text.split('\n')
        for i, line in enumerate(lines):
            text_surf = self.large_font.render(line, True, COLOR_TEXT)
            modal_surface.blit(text_surf, ((modal_width - text_surf.get_width()) // 2, 40 + i * 60))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(modal_surface, modal_rect.topleft)
        pygame.display.flip()
        pygame.time.delay(4000)

    def run(self):
        """Bucle principal del juego."""
        self.show_story()
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if self.quiz_rect.collidepoint(mx, my):
                        rel_x = mx - self.quiz_rect.x
                        rel_y = my - self.quiz_rect.y
                        for rect, opt in self.option_rects:
                            if rect.collidepoint(rel_x, rel_y):
                                self.process_answer(opt)
                                break
            self.update(dt)
            self.screen.fill(COLOR_BG)
            self.draw_animation()
            self.draw_quiz()
            pygame.display.flip()
            if self.game_over:
                fade_out(self.screen, speed=10)
                self.show_final_modal()
                running = False
