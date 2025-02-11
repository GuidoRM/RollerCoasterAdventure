import sys
import time
import random
import numpy as np
import sympy as sp
import pygame
import pygame_menu

# -----------------------
# CONFIGURACIÓN GENERAL
# -----------------------

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 1024

# Área de animación: parte superior (todo el ancho, altura definida)
ANIM_HEIGHT = 500
# Área de quiz: parte inferior
QUIZ_HEIGHT = SCREEN_HEIGHT - ANIM_HEIGHT

# Colores (RGB)
COLOR_BG = (20, 20, 20)          # Fondo general
COLOR_TRACK = (255, 165, 0)      # Pista (naranja dorado)
COLOR_CAR = (220, 20, 60)        # Carrito (crimson)
COLOR_OPTION_BG = (240, 240, 240)
COLOR_OPTION_HOVER = (230, 230, 230)
COLOR_TEXT = (255, 255, 255)
COLOR_TIMER = (255, 215, 0)      # Oro
COLOR_FEEDBACK = (173, 216, 230) # Azul claro
COLOR_MODAL_BG = (30, 30, 30)    # Fondo de la modal
COLOR_MODAL_BORDER = (255, 255, 255)

# -------------------------------
# FUNCIONES DE TRANSICIÓN (FADE)
# -------------------------------
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

# -------------------------------
# FUNCIONES DE DIBUJADO DE GRADIENTE
# -------------------------------
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

# -------------------------------
# CLASE DEL JUEGO CON PYGAME
# -------------------------------
class RollerCoasterGame:
    def __init__(self, func_str, xmin, xmax):
        # Usamos la misma pantalla definida en el menú
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption("Roller Coaster Adventure: Quiz del Mundo")
        self.clock = pygame.time.Clock()

        # Fuentes mejoradas
        self.font = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.large_font = pygame.font.SysFont("Arial", 36)

        # Áreas de la pantalla
        self.anim_rect = pygame.Rect(0, 0, SCREEN_WIDTH, ANIM_HEIGHT)
        self.quiz_rect = pygame.Rect(0, ANIM_HEIGHT, SCREEN_WIDTH, QUIZ_HEIGHT)

        # --- CONFIGURACIÓN DE LA PISTA ---
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

        # --- VARIABLES DEL JUEGO ---
        self.car_index = 0.0          # Posición actual del carrito (índice en track_points)
        self.speed_factor = 0.5        # Velocidad inicial
        self.unanswered_count = 0      # Veces sin respuesta en tiempo
        self.quiz_correct = 0          # Número de respuestas correctas
        self.question_time_limit = 5   # Tiempo límite por pregunta (segundos)
        self.question_start_time = time.time()  # Inicio del temporizador para la pregunta actual
        self.current_question_index = 0
        self.quiz_questions = self.get_quiz_questions()  # 5 preguntas aleatorias
        self.feedback_message = ""     # Mensaje de feedback para la pregunta actual
        self.game_start_time = time.time()
        self.game_over = False

        self.option_rects = []         # Rectángulos de las opciones (para detectar clics)
        self.transition_alpha = 0      # Para efecto de transición en el panel quiz

    def show_story(self):
        """Muestra la pantalla introductoria con la historia del juego."""
        splash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_vertical_gradient(splash_surface, (0, 0, 80), (0, 0, 0))  # Degradado azul oscuro a negro
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
        """Convierte coordenadas 'mundo' (definidas por la función) a la zona de animación."""
        margin = 40
        screen_x = margin + (x - self.xmin) / (self.xmax - self.xmin) * (SCREEN_WIDTH - 2 * margin)
        screen_y = ANIM_HEIGHT - margin - (y - self.min_y) / (self.max_y - self.min_y) * (ANIM_HEIGHT - 2 * margin)
        return (int(screen_x), int(screen_y))

    def draw_animation(self):
        """Dibuja la animación de la montaña rusa en la parte superior."""
        anim_surface = self.screen.subsurface(self.anim_rect)
        # Fondo degradado simulando el cielo
        draw_vertical_gradient(anim_surface, (135, 206, 250), (25, 25, 112))
        # Dibujar la pista de la montaña rusa
        track_points_screen = [self.world_to_screen(x, y) for (x, y) in self.track_points]
        if len(track_points_screen) > 1:
            pygame.draw.lines(anim_surface, COLOR_TRACK, False, track_points_screen, 4)
        # Dibujar el carrito con efecto sombra
        pos = self.world_to_screen(*self.track_points[int(self.car_index)])
        shadow_pos = (pos[0] + 3, pos[1] + 3)
        pygame.draw.circle(anim_surface, (0, 0, 0), shadow_pos, 12)
        pygame.draw.circle(anim_surface, COLOR_CAR, pos, 10)
        # Mostrar marcador de respuestas correctas
        score_text = self.small_font.render(f"Respuestas correctas: {self.quiz_correct}", True, COLOR_TEXT)
        anim_surface.blit(score_text, (20, 20))

    def draw_quiz(self):
        """Dibuja el panel del quiz en la parte inferior."""
        quiz_surface = self.screen.subsurface(self.quiz_rect)
        # Fondo degradado para el panel del quiz
        draw_vertical_gradient(quiz_surface, (60, 60, 60), (20, 20, 20))
        # Mostrar la pregunta
        if self.current_question_index < len(self.quiz_questions):
            q = self.quiz_questions[self.current_question_index]
            question_text = q["question"]
        else:
            question_text = "¡Desafío completado!"
        question_surface = self.font.render("Desafío: " + question_text, True, COLOR_TEXT)
        quiz_surface.blit(question_surface, (20, 10))
        # Dibujar opciones con rectángulos redondeados y efecto hover
        self.option_rects = []
        mx, my = pygame.mouse.get_pos()
        rel_mx = mx - self.quiz_rect.x
        rel_my = my - self.quiz_rect.y
        if self.current_question_index < len(self.quiz_questions):
            options = self.quiz_questions[self.current_question_index]["options"]
            for i, opt in enumerate(options):
                rect = pygame.Rect(20, 60 + i * 50, self.quiz_rect.width - 40, 40)
                self.option_rects.append((rect, opt))
                # Efecto hover: si el mouse está sobre la opción, se cambia el color de fondo
                if rect.collidepoint(rel_mx, rel_my):
                    color = COLOR_OPTION_HOVER
                else:
                    color = COLOR_OPTION_BG
                pygame.draw.rect(quiz_surface, color, rect, border_radius=8)
                # Dibujar borde si está en hover
                if rect.collidepoint(rel_mx, rel_my):
                    pygame.draw.rect(quiz_surface, COLOR_TIMER, rect, 2, border_radius=8)
                opt_surface = self.small_font.render(opt, True, (0, 0, 0))
                text_rect = opt_surface.get_rect(center=rect.center)
                quiz_surface.blit(opt_surface, text_rect)
        # Temporizador
        remaining = max(0, int(self.question_time_limit - (time.time() - self.question_start_time)))
        timer_surface = self.small_font.render(f"Tiempo: {remaining} seg", True, COLOR_TIMER)
        quiz_surface.blit(timer_surface, (20, 260))
        # Velocidad actual
        speed_surface = self.small_font.render(f"Velocidad: {self.speed_factor:.1f}", True, COLOR_TEXT)
        quiz_surface.blit(speed_surface, (20, 290))
        # Progreso de preguntas
        progress_surface = self.small_font.render(
            f"Pregunta {min(self.current_question_index+1, len(self.quiz_questions))} de {len(self.quiz_questions)}", True, COLOR_TEXT)
        quiz_surface.blit(progress_surface, (20, 320))
        # Feedback
        feedback_surface = self.small_font.render(self.feedback_message, True, COLOR_FEEDBACK)
        quiz_surface.blit(feedback_surface, (20, 350))
        # Barra de progreso
        bar_width = self.quiz_rect.width - 40
        bar_height = 10
        progress = (self.current_question_index) / len(self.quiz_questions)
        progress_bar_rect = pygame.Rect(20, self.quiz_rect.height - 30, bar_width, bar_height)
        pygame.draw.rect(quiz_surface, (100, 100, 100), progress_bar_rect, border_radius=5)
        progress_fill_rect = pygame.Rect(20, self.quiz_rect.height - 30, int(bar_width * progress), bar_height)
        pygame.draw.rect(quiz_surface, (0, 200, 0), progress_fill_rect, border_radius=5)

        # Efecto de transición entre preguntas (fade en el panel quiz)
        if self.transition_alpha > 0:
            transition_surface = pygame.Surface((self.quiz_rect.width, self.quiz_rect.height))
            transition_surface.fill((0, 0, 0))
            transition_surface.set_alpha(self.transition_alpha)
            quiz_surface.blit(transition_surface, (0, 0))

    def get_quiz_questions(self):
        """Retorna una lista de 5 preguntas aleatorias para el quiz."""
        pool = [
            {"question": "¿Cuál es la derivada de x**2?", "options": ["2*x", "x", "2", "x**2"], "answer": "2*x"},
            {"question": "¿Cuál es la integral de 1/x dx?", "options": ["ln|x| + C", "1/(x**2) + C", "x + C", "e^x + C"], "answer": "ln|x| + C"},
            {"question": "¿Cuál es la derivada de sin(x)?", "options": ["cos(x)", "-cos(x)", "sin(x)", "-sin(x)"], "answer": "cos(x)"},
            {"question": "¿Cuál es la integral de cos(x) dx?", "options": ["sin(x) + C", "-sin(x) + C", "cos(x) + C", "-cos(x) + C"], "answer": "sin(x) + C"},
            {"question": "¿Cuál es la derivada de e^x?", "options": ["e^x", "x*e^(x-1)", "e^(x) + C", "ln(e)*e^x"], "answer": "e^x"},
            {"question": "¿Cuál es la derivada de ln(x)?", "options": ["1/x", "ln(x)/x", "x", "e^x"], "answer": "1/x"}
        ]
        return random.sample(pool, 5)

    def process_timeout(self):
        """Procesa el evento cuando se agota el tiempo de respuesta."""
        self.feedback_message = "Tiempo agotado. Velocidad reducida."
        self.speed_factor = max(0.5, self.speed_factor - 0.5)
        self.unanswered_count += 1
        self.current_question_index += 1
        self.question_start_time = time.time()
        self.transition_alpha = 200  # Activa efecto de transición

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
        self.transition_alpha = 200  # Activa efecto de transición

    def update(self, dt):
        """Actualiza la posición del carrito y verifica el temporizador del quiz."""
        if not self.game_over:
            self.car_index += self.speed_factor * dt * 50  # Ajuste visual de velocidad
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

        # Reducir progresivamente el efecto de transición en el panel quiz
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
            dt = self.clock.tick(60) / 1000.0  # Delta time en segundos (60 FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return  # Salir del juego
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # Si el clic está en el área del quiz, verificar las opciones
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
                running = False  # Salir del bucle principal

# -------------------------------
# MENÚ DE CONFIGURACIÓN CON PYGAME-MENU
# -------------------------------
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
    # Transición: fade out del menú
    surface = pygame.display.get_surface()
    fade_out(surface, speed=10)
    game = RollerCoasterGame(func_str, xmin, xmax)
    game.run()
    # Al finalizar el juego, se hace fade in para volver al menú
    fade_in(surface, speed=10)
    main_menu()

def main_menu():
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Definir una lista de estrellas para el fondo épico
    stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
             for _ in range(100)]
    menu_theme = pygame_menu.themes.THEME_DARK.copy()
    menu_theme.title_font = 'Impact'
    menu_theme.title_font_size = 60
    menu_theme.widget_font = 'Arial'
    menu_theme.widget_font_size = 30
    menu_theme.widget_margin = (25, 25)  # Se requiere una tupla de dos valores
    menu_theme.background_color = (0, 0, 0)
    
    menu = pygame_menu.Menu('Roller Coaster Adventure', SCREEN_WIDTH, SCREEN_HEIGHT, theme=menu_theme)
    menu.add.label("Forjando leyendas en las alturas", font_size=30, padding=(0, 0))
    menu.add.text_input('Función f(x): ', default='10 - x**2', textinput_id='func')
    menu.add.text_input('Valor mínimo de x: ', default='0', textinput_id='xmin')
    menu.add.text_input('Valor máximo de x: ', default='10', textinput_id='xmax')
    menu.add.button('Iniciar Juego', lambda: start_game_from_menu(menu.get_input_data()))
    menu.add.button('Salir', pygame_menu.events.EXIT)

    # Efecto fade in para el menú
    fade_in(surface, speed=10)
    
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        # Dibujar el fondo épico
        draw_epic_menu_background(surface, stars)
        menu.update(events)
        menu.draw(surface)
        pygame.display.flip()

# -------------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------------
if __name__ == '__main__':
    main_menu()
