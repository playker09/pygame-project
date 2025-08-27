import pygame
import random

from scenes.map import MAP_WIDTH, MAP_HEIGHT  # 맵 크기 가져오기

ENEMY_COLOR = (255, 50, 50)
WALL_COLOR = (100, 100, 100)

ENEMY_SIZE = 30
WALL_SIZE = 40

class Enemy:
    def __init__(self, x, y, size=30, speed=2, max_hp=3):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed
        self.max_hp = max_hp
        self.hp = max_hp

    def move(self, player_rect, enemies):
        # 플레이어를 추적
        if random.random() < 0.9:  # 90% 확률로 플레이어를 추적
            if self.rect.x < player_rect.x:
                self.rect.x += self.speed
            elif self.rect.x > player_rect.x:
                self.rect.x -= self.speed
            if self.rect.y < player_rect.y:
                self.rect.y += self.speed
            elif self.rect.y > player_rect.y:
                self.rect.y -= self.speed

        # 다른 적들과 겹치지 않도록 조정
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
        pygame.draw.rect(surface, ENEMY_COLOR, camera.apply(self.rect))
        # 체력 바 그리기
        bar_width = self.rect.width
        bar_height = 5
        bar_x = self.rect.centerx - bar_width // 2 - camera.offset_x
        bar_y = self.rect.top - 10 - camera.offset_y
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * hp_ratio, bar_height))

# 울타리 클래스
class Wall:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, WALL_SIZE, WALL_SIZE)

    def draw(self, surface):  # surface를 매개변수로 받음
        pygame.draw.rect(surface, WALL_COLOR, self.rect)

# 경험치 오브 클래스
class ExpOrb:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 15, 15)  # 오브 크기
        self.color = (0, 255, 0)  # 초록색

    def draw(self, surface, camera):
        pygame.draw.ellipse(surface, self.color, camera.apply(self.rect))
