import pygame
import math
from scenes.map import MAP_WIDTH, MAP_HEIGHT  # 맵 크기 가져오기

ENEMY_COLOR = (255, 50, 50)
WALL_COLOR = (100, 100, 100)
GREEN = (0, 255, 0)

ENEMY_SIZE = 30
WALL_SIZE = 40


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, size=30, speed=3, max_hp=3):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.max_hp = max_hp
        self.hp = max_hp

    def move(self, player_rect, enemies):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx /= distance
            dy /= distance
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

        # 다른 적들과 겹치지 않도록
        for enemy in enemies:
            if enemy is not self and self.rect.colliderect(enemy.rect):
                if self.rect.x < enemy.rect.x:
                    self.rect.x -= self.speed
                elif self.rect.x > enemy.rect.x:
                    self.rect.x += self.speed
                if self.rect.y < enemy.rect.y:
                    self.rect.y -= self.speed
                elif self.rect.y > enemy.rect.y:
                    self.rect.y += self.speed

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))
        # 체력바
        bar_width = self.rect.width
        bar_height = 5
        bar_x = self.rect.centerx - bar_width // 2 - camera.offset_x
        bar_y = self.rect.top - 10 - camera.offset_y
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0),(bar_x, bar_y, bar_width * hp_ratio, bar_height))


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((WALL_SIZE, WALL_SIZE))
        self.image.fill(WALL_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):  # 카메라 적용 필요 없으면 유지
        surface.blit(self.image, self.rect)


class ExpOrb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (0, 255, 0), (0, 0, 15, 15))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))

class EMP_Tower(pygame.sprite.Sprite):
    def __init__(self, x, y, radius=150, duration=5):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = radius
        self.duration = duration
        self.activated = False
        self.start_time = None

    def activate(self):
        if not self.activated:
            self.activated = True
            self.start_time = pygame.time.get_ticks()  # 시작 시간 기록

    def update(self, enemies):
        if self.activated:
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
            if elapsed >= self.duration:
                # 범위 내 적 전부 제거
                for enemy in enemies:
                    if self.rect.centerx - self.radius < enemy.rect.centerx < self.rect.centerx + self.radius and \
                       self.rect.centery - self.radius < enemy.rect.centery < self.rect.centery + self.radius:
                        enemy.kill()
                self.activated = False  # 다시 비활성화