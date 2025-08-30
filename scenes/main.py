import sys
import os
import pygame
import math
import random

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.player import Player
from classes.entity import Enemy, Wall, ExpOrb
from classes.camera import Camera
from scenes.map import draw_grid, MAP_WIDTH, MAP_HEIGHT
from scenes.game_over import game_over_screen
from hud import draw_level, draw_ammo, draw_dash_indicator

# 초기화
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("슈팅게임 프로토타입")

# 모든 스프라이트 그룹
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
walls = pygame.sprite.Group()
exp_orbs = pygame.sprite.Group()
towers = pygame.sprite.Group()

# FPS
clock = pygame.time.Clock()
FPS = 60


def main():
    # PLAYER_COLOR = (0, 200, 255)  # 플레이어 색상 초기화
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    exp_orbs = pygame.sprite.Group()
    spawn_timer = 0
    camera = Camera(WIDTH, HEIGHT)  # 카메라 초기화
    last_hit_time = 0  # 마지막으로 플레이어가 적에게 맞은 시간
    shooting = False

    while True:
        clock.tick(FPS)
        WIN.fill(BLACK)

        current_time = pygame.time.get_ticks()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 총알 발사
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.switch_weapon("pistol")
                if event.key == pygame.K_2:
                    player.switch_weapon("smg")
                if event.key == pygame.K_3:
                    player.switch_weapon("burst_rifle")
                if event.key == pygame.K_4:
                    player.switch_weapon("shotgun")
                
                if event.key == pygame.K_r:
                    player.reload(current_time)

                # 울타리 설치
                if event.key == pygame.K_SPACE:
                    walls.add(Wall(player.rect.centerx, player.rect.top - WALL_SIZE))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    mode = player.current_weapon.mode
                    if mode == "single" or mode == "burst" or mode == "shotgun":
                        player.shoot(mx, my, camera, bullets, current_time)
                    elif mode == "auto":
                        shooting = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    shooting = False
            
        if shooting:
            mx, my = pygame.mouse.get_pos()
            player.shoot(mx, my, camera, bullets, current_time)
        bullets.update()
        
        player.update_weapon(current_time)
            
        # 플레이어 이동
        keys = pygame.key.get_pressed()
        dash_dir = [0, 0]

        # 이동 방향 벡터 생성
        if keys[pygame.K_w]: dash_dir[1] -= 1
        if keys[pygame.K_s]: dash_dir[1] += 1
        if keys[pygame.K_a]: dash_dir[0] -= 1
        if keys[pygame.K_d]: dash_dir[0] += 1

        # 대쉬 시작 (방향이 있을 때만)
        if dash_dir != [0, 0] and keys[pygame.K_LSHIFT]:
            player.dash(tuple(dash_dir), current_time)

        # 이동 처리
        player.move(keys)

        # 🔥 플레이어 상태 업데이트 (대쉬, 무적, 무기)
        player.update(current_time)

        # 카메라 업데이트
        camera.update(player)

        spawn_timer += 1
        if spawn_timer > 60:  # 1초마다 스폰 체크
            # 난이도 스케일
            elapsed_sec = current_time // 1000
            level_scale = 1 + elapsed_sec // 30  # 30초마다 강해짐

            if len(enemies) < 300 + level_scale * 3:  # 적 최대 수 제한
                num_to_spawn = 10 + level_scale  # 스폰할 적 수
                for _ in range(num_to_spawn):
                    while True:
                        # 플레이어 주변 랜덤 위치 스폰
                        margin = 400       # 플레이어 주변 최소 거리
                        spawn_radius = 1200  # 최대 거리
                        angle = random.uniform(0, 2*math.pi)
                        distance = random.randint(margin, spawn_radius)
                        spawn_x = int(player.rect.centerx + math.cos(angle) * distance)
                        spawn_y = int(player.rect.centery + math.sin(angle) * distance)

                        # 맵 범위 안으로 제한
                        spawn_x = max(0, min(MAP_WIDTH - ENEMY_SIZE, spawn_x))
                        spawn_y = max(0, min(MAP_HEIGHT - ENEMY_SIZE, spawn_y))

                        new_enemy = Enemy(spawn_x, spawn_y, size=ENEMY_SIZE, speed=2 , max_hp=3 + level_scale)

                        if not pygame.sprite.spritecollideany(new_enemy, enemies):
                            enemies.add(new_enemy)
                            all_sprites.add(new_enemy)
                            break

            spawn_timer = 0


        # 총알 이동 및 제거
        for bullet in bullets.copy():
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                enemy.hp -= bullet.damage
                bullet.kill()
                if enemy.hp <= 0:
                    exp_orb = ExpOrb(enemy.rect.centerx, enemy.rect.centery)
                    exp_orbs.add(exp_orb)
                    all_sprites.add(exp_orb)
                    enemy.kill()
        
        hit_enemies = pygame.sprite.spritecollide(player, enemies, False)
        if hit_enemies and current_time - last_hit_time > 1000:
            player.hp -= 10
            last_hit_time = current_time
            if player.hp <= 0:
                action = game_over_screen(WIN, player.level, WIDTH, HEIGHT)
                if action == "retry":
                    main()
                else:
                    pygame.quit()
                    sys.exit()

        # # 적 이동
        for enemy in enemies:
            enemy.move(player.rect, enemies)

        #     # 울타리에 부딪히면 제거
        #     for wall in walls[:]:
        #         if enemy.rect.colliderect(wall.rect):
        #             enemies.remove(enemy)
        #             walls.remove(wall)
        #             break

            # else:
                # 색상 복구 로직 (적과 충돌하지 않을 때)
                # if current_time - last_hit_time > 100:  # 0.2초 동안 색상 유지
                #     PLAYER_COLOR = (0, 200, 255)  # 원래 색상으로 복구

        # 경험치 오브 흡수
        for orb in exp_orbs.copy():
            if player.rect.colliderect(orb.rect):
                player.gain_exp(5)  # 경험치 획득
                orb.kill()

        # 격자 그리기
        draw_grid(WIN, camera)
        for sprite in all_sprites:
            sprite.draw(WIN, camera)

        # 그리기
        for bullet in bullets:
            bullet.draw(WIN, camera)  # 회전된 총알 그리기

        # 플레이어 HP 바 및 HUD
        player.draw_hp_bar(WIN, camera)
        font = pygame.font.SysFont(None, 36)
        draw_level(WIN, font, player)
        draw_ammo(WIN, font, player)
        draw_dash_indicator(WIN, font, player)

        pygame.display.update()

if __name__ == "__main__":
    main()
