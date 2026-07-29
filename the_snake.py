from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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

    def draw(self):
        """Заглушка"""
        pass


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self):
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Генерация случайного положения"""
        grid_x = randint(0, GRID_WIDTH - 1)
        grid_y = randint(0, GRID_HEIGHT - 1)
        self.position = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)

    def draw(self) -> None:
        """Отрисовка"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        start_x = GRID_WIDTH // 2 * GRID_SIZE
        start_y = GRID_HEIGHT // 2 * GRID_SIZE
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
        """Обновление напарвления движения"""
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
        start_x = GRID_WIDTH // 2 * GRID_SIZE
        start_y = GRID_HEIGHT // 2 * GRID_SIZE
        self.length = 1
        self.positions = [(start_x, start_y)]
        self.direction = choice(ALL_DIRECTIONS)
        self.next_direction = None
        self.last = None

    def draw(self):
        """Затираем старый хвост цветом фона ДО отрисовки новых сегментов"""
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        # Рисуем тело (все сегменты, кроме головы)
        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Рисуем голову поверх тела
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

    def check_self_collision(self) -> bool:
        """
        Проверяет столкновение головы с телом.
        Возвращает True при столкновении.
        """
        head = self.get_head_position()
        # Проверяем пересечение головы со всеми сегментами, начиная со второго
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
    apple = Apple()

    running = True
    while running:
        clock.tick(SPEED)

        # 1. Обработка ввода пользователя
        handle_keys(snake)
        # 2. Применение выбранного направления
        snake.update_direction()
        # 3. Перемещение змейки
        snake.move()
        # 4. Проверка съеденного яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            # Простая защита от появления яблока внутри змейки
            while True:
                apple.randomize_position()
                if apple.position not in snake.positions:
                    break
        # 5. Проверка столкновения с собой
        if snake.check_self_collision():
            snake.reset()
            # Очищаем экран полностью перед новой игрой
            screen.fill(BOARD_BACKGROUND_COLOR)
        # 6. Отрисовка всех объектов
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        # 7. Обновление изображения на экране
        pygame.display.update()


if __name__ == '__main__':
    main()
