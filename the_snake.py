from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Координаты центра игрового поля (в индексах ячеек)
CENTER_GRID_X = GRID_WIDTH // 2
CENTER_GRID_Y = GRID_HEIGHT // 2
CENTER_GRID = (CENTER_GRID_X, CENTER_GRID_Y)

CELL_BORDER_THICKNESS = 1

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
ALL_DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость игрового цикла (кадров в секунду):
SPEED = 7

# Настройка PyGame:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс, который хранит общие свойства игровых объектов."""

    def __init__(self, position=(0, 0), body_color=None):
        self.position = position
        self.body_color = body_color

    def _draw_cell(self, surface, fill_color, border_color=BORDER_COLOR):
        """
        Универсальный метод отрисовки одной ячейки на заданной поверхности.
        :param surface: Поверхность Pygame для отрисовки.
        :param fill_color: Цвет заливки прямоугольника.
        :param border_color: Цвет рамки (по умолчанию BORDER_COLOR).
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, fill_color, rect)
        pygame.draw.rect(surface, border_color, rect, CELL_BORDER_THICKNESS)

    def draw(self):
        """Заглушка"""
        pass


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, occupied_positions=None):
        super().__init__(body_color=APPLE_COLOR)
        if occupied_positions:
            self.occupied_cells = {
                (pos[0] // GRID_SIZE, pos[1] // GRID_SIZE)
                for pos in occupied_positions
            }
        else:
            self.occupied_cells = set()
        self.randomize_position()

    def randomize_position(self):
        """Генерация случайного положения свободного от змейки."""
        total_cells = GRID_WIDTH * GRID_HEIGHT
        if len(self.occupied_cells) >= total_cells:
            return

        while True:
            grid_x = randint(0, GRID_WIDTH - 1)
            grid_y = randint(0, GRID_HEIGHT - 1)

            if (grid_x, grid_y) not in self.occupied_cells:
                break

        self.position = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)

    def update_occupied(self, snake_positions):
        """Обновляет карту занятых клеток перед следующей генерацией."""
        self.occupied_cells.clear()
        for pos in snake_positions:
            self.occupied_cells.add((pos[0] // GRID_SIZE, pos[1] // GRID_SIZE))

    def draw(self) -> None:
        """Отрисовка яблока с использованием метода родителя"""
        self._draw_cell(screen, self.body_color)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        # Преобразуем центральные индексы сетки в пиксели
        start_x = CENTER_GRID[0] * GRID_SIZE
        start_y = CENTER_GRID[1] * GRID_SIZE
        super().__init__(position=(start_x, start_y), body_color=SNAKE_COLOR)
        self.length: int = 1
        self.positions: list[tuple[int, int]] = [(start_x, start_y)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self) -> tuple[int, int]:
        """Получение позиции головы змейки"""
        return self.positions[0]

    def move(self) -> None:
        """Обработка движения змейки"""
        current_x, current_y = self.get_head_position()
        dx, dy = self.direction
        new_x = (current_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (current_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Сохраняем хвост перед изменением списка для корректной очистки экрана
        if len(self.positions) > self.length:
            self.last = self.positions[-1]
        else:
            self.last = None

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def update_direction(self) -> None:
        """Обновление направления движения"""
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

    def reset(self) -> None:
        """
        Возвращает змейку в начальное состояние
        после столкновения с собой.
        """
        start_x = CENTER_GRID[0] * GRID_SIZE
        start_y = CENTER_GRID[1] * GRID_SIZE
        self.length = 1
        self.positions = [(start_x, start_y)]
        self.direction = choice(ALL_DIRECTIONS)
        self.next_direction = None
        self.last = None

    def _draw_snake_segments(self, positions_list):
        """Вспомогательный метод для отрисовки группы сегментов."""
        for position in positions_list:
            old_pos = self.position
            self.position = position
            self._draw_cell(screen, self.body_color)
            self.position = old_pos

    def draw(self):
        """Отрисовка змейки с очисткой хвоста"""
        if self.last:
            tail_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, tail_rect)

        if len(self.positions) > 1:
            self._draw_snake_segments(self.positions[1:])

        if self.positions:
            head_pos = self.positions[0]
            old_pos = self.position
            self.position = head_pos
            self._draw_cell(screen, self.body_color)
            self.position = old_pos

    def check_self_collision(self) -> bool:
        """Проверяет столкновение головы с телом."""
        head = self.get_head_position()
        return head in self.positions[1:]


def handle_keys(game_object):
    """Обработка нажатия клавиш"""
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
    """Запуск"""
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        # Очистка всего экрана одним цветом (вместо ручной очистки хвоста)
        screen.fill(BOARD_BACKGROUND_COLOR)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.update_occupied(snake.positions)
            apple.randomize_position()

        if snake.check_self_collision():
            snake.reset()
            apple.update_occupied(snake.positions)
            apple.randomize_position()

        # Теперь порядок отрисовки важен: сначала яблоко, потом змейка
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
