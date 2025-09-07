# bullet.py
import pygame
import math

BULLET_COLOR = (255, 255, 0)
BULLET_WIDTH = 30
BULLET_HEIGHT = 4

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, width=BULLET_WIDTH, height=BULLET_HEIGHT, speed=30, damage=1, max_pierce=0):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, BULLET_COLOR, (0, 0, width, height))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.angle = math.degrees(math.atan2(-dy, dx))
        self.original_image = self.image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.pierce_count = 0  # 관통 횟수 (0이면 관통 없음)
        self.max_pierce = max_pierce   # 최대 관통 수

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

    def draw(self, surface, camera):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera.offset_x
        draw_rect.y -= camera.offset_y
        surface.blit(self.image, draw_rect.topleft)
