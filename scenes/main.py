import sys
import os
import pygame
import math
import random

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.player import Player
from classes.entity import spawn_enemies, EMP_Tower, ExpOrb, Wall
from classes.camera import Camera
from scenes.map import draw_grid, MAP_WIDTH, MAP_HEIGHT
from scenes.game_over import game_over_screen
from hud import draw_level, draw_ammo, draw_dash_indicator

# 초기화
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("슈팅게임 프로토타입")

# FPS
clock = pygame.time.Clock()
FPS = 60

def main():
    # 모든 스프라이트 그룹
    player = Player()
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    exp_orbs = pygame.sprite.Group()
    towers = pygame.sprite.Group(
        EMP_Tower(2000, 1500),
    )
    all_sprites.add(towers)
    all_sprites.add(player)

    spawn_timer = 300        
    camera = Camera(WIDTH, HEIGHT)  # 카메라 초기화
    last_hit_time = 0  # 마지막으로 플레이어가 적에게 맞은 시간
    shooting = False

    while True:
        dt = clock.tick(FPS) / 1000.0
        WIN.fill((0,0,0))

        current_time = pygame.time.get_ticks()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 무기 교체
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

                # # 울타리 설치
                # if event.key == pygame.K_SPACE:
                #     walls.add(Wall(player.rect.centerx, player.rect.top - WALL_SIZE))

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

        # 플레이어 상태 업데이트 (대쉬, 무적, 무기)
        player.update(current_time)

        # 카메라 업데이트
        camera.update(player)

       # EMP 타워 업데이트
        for tower in towers:
            tower.update(dt, player, enemies, all_sprites, exp_orbs, current_time)
            
        spawn_timer = spawn_enemies(player, enemies, all_sprites, spawn_timer, current_time)

        # 총알 이동 및 제거
        for bullet in bullets.copy():
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                enemy.hp -= bullet.damage
                bullet.kill()
                if enemy.hp <= 0:
                    exp_orb = ExpOrb(enemy.rect.centerx, enemy.rect.centery, random.randint(4, 7))
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

        # 적 이동
        for enemy in enemies:
            enemy.move(player.rect, enemies)

            # else:
                # 색상 복구 로직 (적과 충돌하지 않을 때)
                # if current_time - last_hit_time > 100:  # 0.2초 동안 색상 유지
                #     PLAYER_COLOR = (0, 200, 255)  # 원래 색상으로 복구

        # 경험치 오브 흡수
        for orb in exp_orbs.copy():
            if player.rect.colliderect(orb.rect):
                player.gain_exp(orb.value)  # 경험치 획득
                orb.kill()

        # 격자 그리기
        draw_grid(WIN, camera)

        for sprite in all_sprites:
            if hasattr(sprite, "draw"):  # EMP_Tower, Player 등은 draw 있음
                sprite.draw(WIN, camera)
            else:  # 일반 Enemy 같은 경우는 그냥 이미지 블릿
                WIN.blit(sprite.image, camera.apply(sprite))

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
