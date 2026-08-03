from random import randint
import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20

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
    """Базовый класс для всех объектов на игровом поле.

    Предоставляет общие свойства позиции и цвета, а также утилитарный метод
    отрисовки одной клетки с рамкой.
    """

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
        """Отрисовывает одну клетку игрового поля.

        Args:
            surface: Поверхность Pygame для рисования.
            fill_color: Цвет заливки клетки.
            border: Флаг, указывающий, нужно ли рисовать рамку.
            border_color: Цвет рамки клетки.
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, fill_color, rect)
        if border:
            pygame.draw.rect(
                surface, border_color, rect, CELL_BORDER_THICKNESS
            )

    def draw(self):
        """Отрисовывает объект на экране.

        Должен быть переопределен в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Класс яблока, представляющего еду для змейки."""

    def __init__(self):
        """Создает экземпляр яблока с заданным цветом."""
        super().__init__(body_color=APPLE_COLOR)
        self.position = (0, 0)

    def set_position(self, pixel_pos):
        """Устанавливает новую позицию яблока.

        Args:
            pixel_pos: Новые координаты (x, y) в пикселях.
        """
        self.position = pixel_pos

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self._draw_cell(screen, self.body_color)


class Snake(GameObject):
    """Класс змейки, управляемой игроком.

    Управляет массивом позиций сегментов, направлением движения,
    проверкой коллизий и логикой роста.
    """

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
        """Возвращает текущие координаты головы змейки.

        Returns:
            Кортеж координат (x, y) первого сегмента.
        """
        return self.positions[0]

    def move(self):
        """Перемещает змейку на один шаг вперед.

        Добавляет новую голову в направлении движения и удаляет хвост,
        если длина массива превышает лимит `self.length`.
        """
        current_x, current_y = self.get_head_position()
        dx, dy = self.direction
        new_x = (current_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (current_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Определяем позицию хвоста ДО вставки новой головы
        if len(self.positions) > self.length:
            self.last = self.positions[-1]

        # Вставляем новую голову
        self.positions.insert(0, new_head)

        # Обрезаем очередь только если она превысила лимит длины.
        if len(self.positions) > self.length:
            self.positions.pop()

    def update_direction(self):
        """Обновляет направление движения на основе ввода пользователя.

        Защищает от разворота змейки на 180 градусов.
        """
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
        """Проверяет столкновение головы змейки с её собственным телом.

        Returns:
            True, если произошло столкновение, иначе False.
        """
        head = self.positions[0]
        return head in self.positions[1:]

    def draw(self):
        """Отрисовывает всю змейку на экране.

        Выполняет три действия:
        1. Стирает старый хвост фоном.
        2. Рисует тело змейки (все сегменты, кроме головы).
        3. Рисует голову поверх тела.
        """
        # 1. Стираем ТОЛЬКО самый последний хвост, если змейка не росла
        if self.last and len(self.positions) > 1:
            old_pos = self.position
            self.position = self.last
            self._draw_cell(
                screen, BOARD_BACKGROUND_COLOR, border=False
            )
            self.position = old_pos

        # 2. Рисуем всё тело (кроме головы)
        if len(self.positions) > 1:
            for pos in self.positions[1:]:
                old_pos = self.position
                self.position = pos
                self._draw_cell(screen, self.body_color, border=True)
                self.position = old_pos

        # 3. Рисуем голову поверх всего
        if self.positions:
            head_pos = self.positions[0]
            old_pos = self.position
            self.position = head_pos
            self._draw_cell(screen, self.body_color, border=True)
            self.position = old_pos


def handle_keys(game_object):
    """Обрабатывает события очереди Pygame (клавиатура и закрытие окна).

    Устанавливает следующее направление движения для переданного объекта.

    Args:
        game_object: Объект (обычно Snake), чье направление нужно изменить.
    """
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


def find_free_position(snake_positions):
    """Находит случайную свободную ячейку на сетке, не занятую змейкой.

    Args:
        snake_positions: Список кортежей координат, занятых змейкой.

    Returns:
        Кортеж координат (x, y) свободной ячейки в пикселях.
    """
    occupied = {
        (pos[0] // GRID_SIZE, pos[1] // GRID_SIZE)
        for pos in snake_positions
    }

    while True:
        grid_x = randint(0, SCREEN_WIDTH // GRID_SIZE - 1)
        grid_y = randint(0, SCREEN_HEIGHT // GRID_SIZE - 1)

        if (grid_x, grid_y) not in occupied:
            return (grid_x * GRID_SIZE, grid_y * GRID_SIZE)


def main():
    """Главная функция игры.

    Инициализирует объекты, содержит основной игровой цикл,
    обрабатывает логику столкновений и обновляет экран.
    """
    snake = Snake()
    apple = Apple()

    apple.set_position(find_free_position(snake.positions))

    while True:
        clock.tick(SPEED)
        # Отрисовка фона необходима для очистки следов при поворотах
        screen.fill(BOARD_BACKGROUND_COLOR)

        handle_keys(snake)
        snake.update_direction()

        # Проверяем смерть
        if snake.check_self_collision():
            snake.reset()
            apple.set_position(find_free_position(snake.positions))
        else:
            # Проверяем поедание яблока
            if snake.positions[0] == apple.position:
                snake.length += 1

                # Очищаем место съеденного яблока
                old_pos = snake.position
                snake.position = apple.position
                snake._draw_cell(
                    screen, BOARD_BACKGROUND_COLOR, border=False
                )
                snake.position = old_pos

                apple.set_position(find_free_position(snake.positions))

            snake.move()

        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
