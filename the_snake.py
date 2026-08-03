from random import randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20

# Новые константы, которые требуются тестам
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Координаты центра экрана в пикселях (выровнены по сетке)
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

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32
)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех объектов на игровом поле."""

    def __init__(self, position=(0, 0), body_color=None):
        """Инициализирует объект.

        Args:
            position: Кортеж координат (x, y) в пикселях.
            body_color: Цвет заливки объекта в формате RGB.
        """
        self.position = position
        self.body_color = body_color

    def _draw_cell(
            self,
            surface,
            fill_color,
            border=True,
            border_color=BORDER_COLOR):
        """Отрисовывает одну клетку игрового поля."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, fill_color, rect)
        if border:
            pygame.draw.rect(
                surface, border_color, rect, CELL_BORDER_THICKNESS
            )

    def draw(self):
        """Отрисовывает объект на экране."""
        pass


class Apple(GameObject):
    """Класс яблока, представляющего еду для змейки."""

    def __init__(self):
        """Создает экземпляр яблока с заданным цветом."""
        super().__init__(body_color=APPLE_COLOR)
        self.position = (0, 0)

    @staticmethod
    def _get_random_grid_position(occupied_positions):
        """Находит случайную свободную ячейку на сетке.

        Args:
            occupied_positions: Множество занятых ячеек в координатах сетки.

        Returns:
            Кортеж координат (grid_x, grid_y).
        """
        while True:
            grid_x = randint(0, GRID_WIDTH - 1)
            grid_y = randint(0, GRID_HEIGHT - 1)
            if (grid_x, grid_y) not in occupied_positions:
                return grid_x, grid_y

    def randomize_position(self, snake_positions):
        """Устанавливает новую позицию яблока, избегая тела змейки."""
        # Переводим пиксельные координаты змейки в сетку
        occupied = {
            (pos[0] // GRID_SIZE, pos[1] // GRID_SIZE)
            for pos in snake_positions
        }

        grid_x, grid_y = self._get_random_grid_position(occupied)
        self.position = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self._draw_cell(screen, self.body_color)


class Snake(GameObject):
    """Класс змейки, управляемой игроком."""

    def __init__(self):
        """Инициализирует змейку в центре экрана со стартовой длиной 1."""
        super().__init__(
            position=(CENTER_X, CENTER_Y),
            body_color=SNAKE_COLOR
        )
        self.length = 1
        self.positions = [(CENTER_X, CENTER_Y)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает текущие координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Перемещает змейку на один шаг вперед."""
        current_x, current_y = self.get_head_position()
        dx, dy = self.direction
        new_x = (current_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (current_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Определяем позицию хвоста ДО вставки новой головы
        if len(self.positions) >= self.length:
            self.last = self.positions[-1]

        self.positions.insert(0, new_head)

        # Обрезаем очередь только если она превысила лимит длины
        if len(self.positions) > self.length:
            self.positions.pop()

    def update_direction(self):
        """Обновляет направление движения на основе ввода пользователя."""
        if self.next_direction:
            opposite_checks = {
                UP: DOWN,
                DOWN: UP,
                LEFT: RIGHT,
                RIGHT: LEFT
            }
            if self.next_direction != opposite_checks[self.direction]:
                self.direction = self.next_direction
            self.next_direction = None

    def reset(self):
        """Сбрасывает состояние змейки к начальным значениям после смерти."""
        self.length = 1
        self.positions = [(CENTER_X, CENTER_Y)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def check_self_collision(self):
        """Проверяет столкновение головы змейки с её собственным телом."""
        head = self.positions[0]
        return head in self.positions[1:]

    def draw(self):
        """Отрисовывает всю змейку на экране."""
        # Стираем ТОЛЬКО самый последний хвост, если змейка не росла
        if self.last and len(self.positions) > self.length:
            tail_to_erase = self.last
            temp_pos = self.position
            self.position = tail_to_erase
            self._draw_cell(screen, BOARD_BACKGROUND_COLOR, border=False)
            self.position = temp_pos

        # Рисуем всё тело (кроме головы)
        if len(self.positions) > 1:
            for pos in self.positions[1:]:
                temp_pos = self.position
                self.position = pos
                self._draw_cell(screen, self.body_color, border=True)
                self.position = temp_pos

        # Рисуем голову поверх всего
        if self.positions:
            head_pos = self.positions[0]
            temp_pos = self.position
            self.position = head_pos
            self._draw_cell(screen, self.body_color, border=True)
            self.position = temp_pos


def handle_keys(game_object):
    """Обрабатывает события очереди Pygame (клавиатура и закрытие окна)."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Главная функция игры."""
    snake = Snake()
    apple = Apple()

    apple.randomize_position(snake.positions)

    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)

        handle_keys(snake)
        snake.update_direction()

        # Проверяем смерть
        if snake.check_self_collision():
            snake.reset()
            apple.randomize_position(snake.positions)
        else:
            # Проверяем поедание яблока
            if snake.positions[0] == apple.position:
                snake.length += 1
                apple.randomize_position(snake.positions)

            snake.move()

        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
