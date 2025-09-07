import pygame
import os
from scenes.map import MAP_WIDTH, MAP_HEIGHT
from classes.weapon import Weapon
# from scenes.upgrade import show_upgrade_screen

ASSET_IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "image")
ASSET_SFX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sfx")

player_img = pygame.image.load(os.path.join(ASSET_IMAGE_DIR, "player.png"))

# 사운드 로드 예시
smg_shoot_sound = pygame.mixer.Sound(os.path.join(ASSET_SFX_DIR, "smg_shoot.wav"))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = player_img.convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (34, 66))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(MAP_WIDTH/2, MAP_HEIGHT/2))

        # 이동
        self.speed = 3.2

        # 체력
        self.max_hp = 100
        self.hp = 100

        # 레벨
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 10

        # 주무기 & 무기 선택
        self.weapons = {
            "dmr": Weapon("DMR", fire_rate=130, spread=1, mode="single", mag_size=25, reload_time=900, damage=5),
            "smg": Weapon("SMG", fire_rate=90, spread=5, mode="auto", reload_time=1200,damage=2),
            "rifle": Weapon("Rifle", fire_rate=120, spread=3, mode="auto", reload_time= 1600, damage=4),
            "shotgun": Weapon("Shotgun", fire_rate=700, spread=15, mode="shotgun", pellet_count=10,damage=2)
        }
        self.primary_weapon = None
        self.current_weapon = None

        # 업그레이드 관리
        self.upgrades = {
            "weapon": [],      # Upgrade 객체 리스트
            "secondary": [],
            "accessory": []
        }
        self.max_weapon_upgrades = 3
        self.max_secondary_upgrades = 3
        self.max_accessory = 4

        # 보조 무기 잠금 상태
        self.drone_unlocked = False
        self.grenade_unlocked = False

        # 대쉬 관련
        self.is_dashing = False
        self.dash_vector = (0, 0)
        self.dash_speed = 25
        self.dash_duration = 70
        self.dash_start_time = 0
        self.dash_cooldown_time = 3000
        self.dash_cooldown = 0
        self.is_invincible = False

        # 레벨업 큐 시스템
        self.level_up_queue = 0
        self.upgrading = False

    def choose_primary_weapon(self, surface, WIDTH, HEIGHT):
        font_title = pygame.font.SysFont("malgungothic", 36, bold=True)
        font_stats = pygame.font.SysFont("malgungothic", 20)
        weapons_list = list(self.weapons.values())
        selected = None

        slot_width = 150
        slot_height = 250
        margin = 20

        while selected is None:
            surface.fill((0,0,0))

            # 제목
            title_surf = font_title.render("Select your weapon", True, (255, 255, 255))
            surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 50))

            start_x = (WIDTH - (slot_width + margin) * len(weapons_list) + margin) // 2
            y = HEIGHT//2 - slot_height//2

            slots = []
            mx, my = pygame.mouse.get_pos()
            for i, w in enumerate(weapons_list):
                x = start_x + i * (slot_width + margin)
                rect = pygame.Rect(x, y, slot_width, slot_height)
                slots.append((rect, w))

                # 마우스 오버 강조
                if rect.collidepoint((mx,my)):
                    pygame.draw.rect(surface, (70,70,70), rect, border_radius=10)  # 배경 밝게
                    border_color = (255, 255, 0)
                else:
                    pygame.draw.rect(surface, (50,50,50), rect, border_radius=10)
                    border_color = (200,200,200)

                pygame.draw.rect(surface, border_color, rect, 2, border_radius=10)

                # 총 이미지
                img = pygame.transform.scale(w.image if hasattr(w, "image") else pygame.Surface((80,50)), (80,50))
                surface.blit(img, (rect.centerx - 40, rect.y + 15))

                # 스탯
                stats_y = rect.y + 90
                stats = [
                    f"DMG: {w.damage}",
                    f"Pierce: {w.pierce_level}",
                    f"Reload: {w.reload_time/1000:.1f}s",
                    f"Spread: {w.spread}"
                ]
                for s in stats:
                    stat_surf = font_stats.render(s, True, (255,255,255))
                    surface.blit(stat_surf, (rect.x + 10, stats_y))
                    stats_y += 25

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, w in slots:
                        if rect.collidepoint((mx,my)):
                            selected = w
                            break

        self.primary_weapon = selected
        self.current_weapon = selected



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
        leveled_up = False
        while self.exp >= self.exp_to_next_level:
            self.exp -= self.exp_to_next_level
            self.level += 1
            self.exp_to_next_level += 5 * self.level
            self.level_up_queue += 1   # 큐에 쌓기
            leveled_up = True
        return leveled_up

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))

    def draw_hp_bar(self, surface, camera):
        bar_width = 50
        bar_height = 8
        bar_x = self.rect.centerx - bar_width // 2 - camera.offset_x
        bar_y = self.rect.top - 15 - camera.offset_y
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (255,0,0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0,255,0),(bar_x, bar_y, bar_width * hp_ratio, bar_height))
