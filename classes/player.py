import pygame
from scenes.map import MAP_WIDTH, MAP_HEIGHT  # config.py에서 전역 변수 가져오기
from classes.weapon import Weapon

class Player:
    def __init__(self):
        self.original_image = pygame.image.load("image//player.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image,(40,40))
        self.image = self.original_image.copy()
        
        self.weapons = {
            "pistol": Weapon("Pistol", fire_rate=170, spread=2, mode="single"),
            "smg": Weapon("SMG", fire_rate=100, spread=5, mode="auto"),
            "burst_rifle": Weapon("Burst Rifle", fire_rate=500, spread=3, mode="burst", burst_count=3),
            "shotgun": Weapon("Shotgun", fire_rate=700, spread=15, mode="shotgun", pellet_count=10)
        }
        self.current_weapon = self.weapons["pistol"]


        self.x = MAP_WIDTH // 2
        self.y = MAP_HEIGHT // 2
        self.speed = 5
        self.size = 40
        self.rect = self.image.get_rect(center= (400,300))
        self.max_hp = 100  # 최대 체력
        self.hp = 100      # 현재 체력
        self.level = 1     # 초기 레벨
        self.exp = 0       # 경험치
        self.exp_to_next_level = 10  # 다음 레벨까지 필요한 경험치

    def move(self, keys):
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < MAP_HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < MAP_WIDTH:
            self.rect.x += self.speed

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            self.level += 1
            self.exp -= self.exp_to_next_level
            self.exp_to_next_level += 5  # 레벨업마다 필요한 경험치 증가

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))
        
    def draw_hp_bar(self, surface, camera):
        # HP 바의 위치와 크기
        bar_width = 50
        bar_height = 8
        bar_x = self.rect.centerx - bar_width // 2 - camera.offset_x
        bar_y = self.rect.top - 15 - camera.offset_y

        # 체력 비율 계산
        hp_ratio = self.hp / self.max_hp

        # HP 바 그리기
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))  # 빨간색 배경
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * hp_ratio, bar_height))  # 초록색 체력

    def draw_level(self, surface):
        font = pygame.font.SysFont(None, 30)
        level_text = font.render(f"Level: {self.level}, {self.exp}/{self.exp_to_next_level}", True, (255, 255, 255))
        surface.blit(level_text, (10, 10))  # 화면 왼쪽 상단에 표시

    def shoot(self, mx, my, camera, bullets, current_time):
        px, py = self.rect.center
        self.current_weapon.shoot(px, py, mx, my, camera, bullets, current_time)

    
    def switch_weapon(self, name):
        if name in self.weapons:
            self.current_weapon = self.weapons[name]