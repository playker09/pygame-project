import pygame
import math

BULLET_COLOR = (255, 255, 0)
BULLET_WIDTH = 30  # 총알의 너비
BULLET_HEIGHT = 4  # 총알의 높이 (길게 설정)

class Bullet:
    def __init__(self, x, y, dx, dy, width=BULLET_WIDTH, height=BULLET_HEIGHT, speed=30, damage=1):
        self.rect = pygame.Rect(x, y, width, height)  # 총알 크기 설정
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.angle = math.degrees(math.atan2(-dy, dx))  # 총알의 회전 각도 계산

    def move(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

    def draw(self, surface, camera):
        # 총알을 회전시키기 위해 Surface 생성
        rotated_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(rotated_surface, BULLET_COLOR, (0, 0, self.rect.width, self.rect.height))  # 직사각형으로 그리기
        rotated_surface = pygame.transform.rotate(rotated_surface, self.angle)  # 각도만큼 회전
        rotated_rect = rotated_surface.get_rect(center=self.rect.center)  # 중심을 유지

        # 카메라 오프셋 적용
        rotated_rect.x -= camera.offset_x
        rotated_rect.y -= camera.offset_y

        # 회전된 총알 그리기
        surface.blit(rotated_surface, rotated_rect.topleft)