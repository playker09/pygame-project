import pygame
import math
import random
from scenes.map import MAP_WIDTH, MAP_HEIGHT  # 맵 크기 가져오기

ENEMY_COLOR = (255, 50, 50)
WALL_COLOR = (100, 100, 100)
GREEN = (0, 255, 0)

ENEMY_SIZE = 30
WALL_SIZE = 40


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, size=30, speed=3, max_hp=2):
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
    def __init__(self, x, y, value=1):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (0, 255, 0), (0, 0, 15, 15))
        self.rect = self.image.get_rect(center=(x, y))
        self.value = value 

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect))

class EMP_Tower(pygame.sprite.Sprite):
    def __init__(self, x, y, survive_time=30):
        super().__init__()
        self.image = pygame.Surface((100,100))
        self.image.fill((0, 200, 255))  # 파란 EMP 타워
        self.rect = self.image.get_rect(center=(x, y))
        
        self.activated = False   # 최종 발동 여부
        self.active = False      # 플레이어가 활성화 시켰는지 여부
        self.survive_time = survive_time  # 버텨야 하는 시간(초)
        self.timer = 0           # 남은 시간
        self.font = pygame.font.SysFont(None, 24)

        # 타워마다 개별 스폰 타이머 관리
        self.spawn_timer = 0  

    def start(self):
        """플레이어가 타워와 상호작용하면 호출"""
        if not self.active and not self.activated:
            self.active = True
            self.timer = self.survive_time
            print("EMP Tower challenge started!")

    def activate(self, enemies, exp_orbs, all_sprites):
        """타워 발동: 모든 적 제거 (경험치 오브 생성)"""
        if not self.activated:
            self.activated = True
            self.active = False

            # 적 모두 제거 + 경험치 드랍
            for enemy in list(enemies):  # 복사본으로 순회
                # 경험치 오브 생성 (Enemy 클래스에 exp 값 있다고 가정)
                orb = ExpOrb(enemy.rect.centerx, enemy.rect.centery, random.randint(1, 7))
                exp_orbs.add(orb)
                all_sprites.add(orb)

                enemy.kill()

            print("EMP Tower Activated! All enemies destroyed!")

    def update(self, dt, player, enemies, all_sprites, exp_orbs, current_time):
        """타워 로직"""
        keys = pygame.key.get_pressed()
        if not self.active and not self.activated:
            if self.rect.colliderect(player.rect) and keys[pygame.K_e]:
                self.start()

        # 버티는 중이면 타이머 감소 + 적 스폰
        if self.active:
            self.timer -= dt
            self.spawn_timer = spawn_enemies(
                player, enemies, all_sprites,
                self.spawn_timer, current_time,
                base_interval=120,
                base_num=25,
                spawn_radius=1000,
                enemy_speed=2,
                difficulty_scale=False,
                extra_multiplier=2
            )
            if self.timer <= 0:
                self.activate(enemies, exp_orbs, all_sprites)

    def draw(self, screen, camera):
        """타워와 남은 시간 표시"""
        screen.blit(self.image, camera.apply(self.rect))

        if self.active and not self.activated:
            text = self.font.render(str(int(self.timer) + 1), True, (255, 255, 0))
            text_rect = text.get_rect(center=(self.rect.centerx - camera.offset_x,
                                              self.rect.top - 20 - camera.offset_y))
            screen.blit(text, text_rect)
        elif self.activated:
            text = self.font.render("ONLINE", True, (0, 255, 0))
            text_rect = text.get_rect(center=(self.rect.centerx - camera.offset_x,
                                              self.rect.top - 20 - camera.offset_y))
            screen.blit(text, text_rect)

def spawn_enemies(
        player, enemies, all_sprites,
        spawn_timer, current_time,
        base_interval=300,          # 기본 스폰 주기 (tick 단위)
        base_num=5,                # 기본 스폰 수
        margin=600,                 # 플레이어 최소 거리
        spawn_radius=1200,          # 최대 거리
        enemy_size=32,              # 적 크기
        enemy_speed=2,              # 적 속도
        difficulty_scale=True,      # 시간 경과에 따른 난이도 증가 여부
        extra_multiplier=1          # 웨이브일 때 배수 (기본은 1)
    ):
        """적 스폰 함수. 기본 스폰 및 웨이브 이벤트 모두 지원."""

        spawn_timer += 1
        if spawn_timer > base_interval:  
            # 난이도 스케일 (시간에 따라 강해짐)
            elapsed_sec = current_time // 1000
            level_scale = (1 + elapsed_sec // 30) if difficulty_scale else 1

            # 이번에 스폰할 적 수
            num_to_spawn = (base_num + level_scale) * extra_multiplier

            # 적 스폰
            for _ in range(num_to_spawn):
                while True:
                    angle = random.uniform(0, 2*math.pi)
                    distance = random.randint(margin, spawn_radius)
                    spawn_x = int(player.rect.centerx + math.cos(angle) * distance)
                    spawn_y = int(player.rect.centery + math.sin(angle) * distance)

                    # 맵 범위 제한
                    spawn_x = max(0, min(MAP_WIDTH - enemy_size, spawn_x))
                    spawn_y = max(0, min(MAP_HEIGHT - enemy_size, spawn_y))

                    # 새 적 생성
                    new_enemy = Enemy(
                        spawn_x, spawn_y,
                        size=enemy_size,
                        speed=enemy_speed,
                        max_hp=1 + level_scale
                    )

                    if not pygame.sprite.spritecollideany(new_enemy, enemies):
                        enemies.add(new_enemy)
                        all_sprites.add(new_enemy)
                        break

            spawn_timer = 0

        return spawn_timer
