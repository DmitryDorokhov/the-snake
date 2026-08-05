from random import randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_X = SCREEN_WIDTH // 2 - (SCREEN_WIDTH // 2) % GRID_SIZE
CENTER_Y = SCREEN_HEIGHT // 2 - (SCREEN_HEIGHT // 2) % GRID_SIZE
CELL_BORDER_THICKNESS = 1
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
ALL_DIRECTIONS = [UP, DOWN, LEFT, RIGHT]
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 7

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех объектов на игровом поле."""

    def __init__(self, position=(0, 0), body_color=None):
        self.position = position
        self.body_color = body_color

    def _draw_cell(self, fill_color, border=True, border_color=BORDER_COLOR):
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        # Если передан булевый False вместо кортежа цвета, пропускаем заливку
        if isinstance(fill_color, tuple):
            pygame.draw.rect(screen, fill_color, rect)
        if border:
            pygame.draw.rect(screen, border_color, rect, CELL_BORDER_THICKNESS)

    def draw(self):
        """Отрисовывает объект на экране."""
        pass


class Apple(GameObject):
    """Класс яблока, представляющего еду для змейки."""

    def __init__(self):
        """Создает экземпляр яблока с заданным цветом."""
        super().__init__(body_color=APPLE_COLOR)
        self.position = (0, 0)

    def randomize_position(self, occupied_positions):
        """Находит случайную свободную ячейку на сетке."""
        return self._draw_cell(BOARD_BACKGROUND_COLOR, border=False)

    @staticmethod
    def _get_random_grid_position(occupied_positions):
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if (x, y) not in occupied_positions:
                return x, y

    def place_on_free_spot(self, snake_positions):
        """Устанавливает новую позицию яблока."""
        apple_x, apple_y = self._get_random_grid_position(snake_positions)
        self.position = (apple_x, apple_y)
        self._draw_cell(self.body_color)

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self._draw_cell(self.body_color)


class Snake(GameObject):
    """Класс змейки, управляемой игроком."""

    def __init__(self):
        super().__init__(position=(CENTER_X, CENTER_Y), body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [(CENTER_X, CENTER_Y)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.grow_pending = False

    def get_head_position(self):
        """Возвращает текущие координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """
        Перемещает змейку на один шаг вперед
        и очищает освободившийся хвост.
        """
        current_x, current_y = self.get_head_position()
        dx, dy = self.direction
        new_x = (current_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (current_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Определяем хвост до вставки головы
        if len(self.positions) >= self.length:
            self.last = self.positions[-1]

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length and not self.grow_pending:
            tail_to_clear = self.positions.pop()
            temp_pos = self.position
            self.position = tail_to_clear
            # --- ИСПРАВЛЕНИЕ ПУНКТА 2: очищаем фон корректно ---
            # Передаем цвет заливки, иначе клетка останется прозрачной/битой
            self._draw_cell(fill_color=BOARD_BACKGROUND_COLOR,
                            border=True,
                            border_color=BOARD_BACKGROUND_COLOR
                            )
            self.position = temp_pos

        self.grow_pending = False

    def update_direction(self):
        """Обновляет направление движения на основе ввода пользователя."""
        if self.next_direction:
            opposite_checks = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
            if self.next_direction != opposite_checks[self.direction]:
                self.direction = self.next_direction
            self.next_direction = None

    def reset(self):
        """Сбрасывает состояние змейки к начальным значениям после смерти."""
        for pos in self.positions:
            temp_pos = self.position
            self.position = pos
            self._draw_cell(fill_color=BOARD_BACKGROUND_COLOR,
                            border=True,
                            border_color=BOARD_BACKGROUND_COLOR
                            )
            self.position = temp_pos
        self.length = 1
        self.positions = [(CENTER_X, CENTER_Y)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.grow_pending = False

    def check_self_collision(self):
        """Проверяет столкновение головы змейки с её собственным телом."""
        head = self.positions[0]
        return head in self.positions[1:]

    def grow(self):
        """
        Увеличивает целевую длину змейки.
        Рост произойдет после следующего хода.
        """
        self.length += 1
        self.grow_pending = True

    def draw(self):
        """Отрисовывает змейку на экране."""
        for pos in self.positions:
            temp_pos = self.position
            self.position = pos
            self._draw_cell(self.body_color, border=True)
            self.position = temp_pos


def handle_keys(game_object):
    """Обрабатывает события очереди Pygame (клавиатура и закрытие окна)."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                game_object.next_direction = RIGHT


def main():
    """Главная функция игры."""
    snake = Snake()
    apple = Apple()

    # Устанавливаем начальную позицию яблока вне тела змейки
    apple.place_on_free_spot(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()

        # Флаг фиксирует факт поедания ДО движения змеи
        apple_eaten = snake.get_head_position() == apple.position

        if snake.check_self_collision():
            snake.reset()
            # При смерти убираем старое яблоко вручную
            temp_pos = apple.position
            apple.position = apple.position
            # Но лучше очистить явно, чтобы не было артефактов
            temp_apple_draw = apple.position
            apple.position = temp_apple_draw
            # Оставим это на совести цикла, главное — сброс змеи

        snake.move()

        if apple_eaten:
            # 1. Стираем старое яблоко (координаты еще старые)
            temp_pos = apple.position
            apple.position = temp_pos
            apple._draw_cell(BOARD_BACKGROUND_COLOR, border=False)

            # 2. Растим змейку
            snake.grow()
            apple.place_on_free_spot(snake.positions)

        # Рисуем всё заново
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
