import pygame
from scenes.map import MAP_WIDTH, MAP_HEIGHT
from classes.weapon import Weapon


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 이미지 및 위치
        self.original_image = pygame.image.load("image//player.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (34.5, 66))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(MAP_WIDTH / 2, MAP_HEIGHT / 2))

        # 이동
        self.speed = 3.2

        # 체력
        self.max_hp = 100
        self.hp = 100

        # 레벨
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 10

        # 무기
        self.weapons = {
            "pistol": Weapon("Pistol", fire_rate=130, spread=2, mode="single", mag_size=12,
                             reserve_ammo=float("inf")),
            "smg": Weapon("SMG", fire_rate=100, spread=5, mode="auto"),
            "burst_rifle": Weapon("Burst Rifle", fire_rate=500, spread=3, mode="burst", burst_count=3),
            "shotgun": Weapon("Shotgun", fire_rate=700, spread=15, mode="shotgun", pellet_count=10)
        }
        self.current_weapon = self.weapons["pistol"]

        # 대쉬 관련
        self.is_dashing = False
        self.dash_vector = (0, 0)
        self.dash_speed = 25
        self.dash_duration = 70
        self.dash_start_time = 0
        self.dash_cooldown_time = 3000
        self.dash_cooldown = 0
        self.is_invincible = False

    def move(self, keys):
        if self.is_dashing:
            return
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < MAP_HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < MAP_WIDTH:
            self.rect.x += self.speed

    def dash(self, direction_vector, current_time):
        if not self.is_dashing and self.dash_cooldown <= 0:
            self.is_dashing = True
            self.dash_start_time = current_time
            self.dash_vector = direction_vector
            self.is_invincible = True

    def update(self, current_time):
        # 대쉬 처리
        if self.is_dashing:
            elapsed = current_time - self.dash_start_time
            if elapsed < self.dash_duration:
                self.rect.x += self.dash_vector[0] * self.dash_speed
                self.rect.y += self.dash_vector[1] * self.dash_speed
            else:
                self.is_dashing = False
                self.is_invincible = False
                self.dash_cooldown = self.dash_cooldown_time

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 16

        self.update_weapon(current_time)

    def shoot(self, mx, my, camera, bullets, current_time):
        px, py = self.rect.center
        self.current_weapon.shoot(px, py, mx, my, camera, bullets, current_time)

    def switch_weapon(self, name):
        if name in self.weapons:
            self.current_weapon = self.weapons[name]

    def reload(self, current_time):
        self.current_weapon.reload(current_time)

    def update_weapon(self, current_time):
        self.current_weapon.update(current_time)

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            self.level += 1
            self.exp -= self.exp_to_next_level
            self.exp_to_next_level += 5

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))

    def draw_hp_bar(self, surface, camera):
        bar_width = 50
        bar_height = 8
        bar_x = self.rect.centerx - bar_width // 2 - camera.offset_x
        bar_y = self.rect.top - 15 - camera.offset_y
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0),(bar_x, bar_y, bar_width * hp_ratio, bar_height))
