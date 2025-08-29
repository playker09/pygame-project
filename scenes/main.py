import sys
import os
import pygame
import math
import time
import random

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.player import Player
from classes.entity import Enemy, Wall, ExpOrb
from classes.camera import Camera
from scenes.map import draw_grid, MAP_WIDTH, MAP_HEIGHT
from scenes.game_over import game_over_screen
from hud import draw_level, draw_ammo




# 초기화
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("슈팅게임 프로토타입")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 200, 255)
BULLET_COLOR = (255, 255, 0)
ENEMY_COLOR = (255, 50, 50)
WALL_COLOR = (100, 100, 100)

# 객체 크기
PLAYER_SIZE = 40
BULLET_SIZE = 8
ENEMY_SIZE = 30
WALL_SIZE = 40

# FPS
clock = pygame.time.Clock()
FPS = 60


def main():
    global PLAYER_COLOR  # PLAYER_COLOR를 전역 변수로 선언
    global WHITE
    global WALL_COLOR
    global WALL_SIZE

    PLAYER_COLOR = (0, 200, 255)  # 플레이어 색상 초기화

    player = Player()  # Player 객체 생성
      # 현재 무기
    bullets = []
    enemies = []
    walls = []
    exp_orbs = []  # 경험치 오브 리스트
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
                    walls.append(Wall(player.rect.centerx, player.rect.top - WALL_SIZE))

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
        
        player.update_weapon(current_time)
            
        # 플레이어 이동
        keys = pygame.key.get_pressed()
        player.move(keys)

        # 카메라 업데이트
        camera.update(player)

        # 적 스폰
        spawn_timer += 1
        if spawn_timer > 60:  # 1초마다 적 스폰
            while True:
                spawn_x = random.randint(0, MAP_WIDTH - ENEMY_SIZE)
                spawn_y = random.randint(0, MAP_HEIGHT - ENEMY_SIZE)
                new_enemy = Enemy(spawn_x, spawn_y)
                # 기존 적들과 겹치지 않는 위치에 생성
                if not any(enemy.rect.colliderect(new_enemy.rect) for enemy in enemies):
                    enemies.append(new_enemy)
                    break
            spawn_timer = 0

        # 총알 이동 및 제거
        for bullet in bullets[:]:
            bullet.move()
            if (bullet.rect.x < 0 or bullet.rect.x > MAP_WIDTH or
                bullet.rect.y < 0 or bullet.rect.y > MAP_HEIGHT):
                bullets.remove(bullet)

        # 적 이동
        for enemy in enemies[:]:
            enemy.move(player.rect, enemies)  # 다른 적들과의 충돌 정보 전달

            # 총알 피격 처리
            for bullet in bullets[:]:
                if enemy.rect.colliderect(bullet.rect):
                    enemy.hp -= bullet.damage
                    bullets.remove(bullet)
                    
            if enemy.hp <= 0:
                    exp_orbs.append(ExpOrb(enemy.rect.centerx, enemy.rect.centery))  # 경험치 오브 생성
                    enemies.remove(enemy)

            # 울타리에 부딪히면 제거
            for wall in walls[:]:
                if enemy.rect.colliderect(wall.rect):
                    enemies.remove(enemy)
                    walls.remove(wall)
                    break

            # 플레이어와 적 충돌 시 HP 감소 (딜레이 적용)
            if player.rect.colliderect(enemy.rect):
                if current_time - last_hit_time > 1000:  # 1초 딜레이
                    player.hp -= 10  # 체력 감소
                    PLAYER_COLOR = (255, 0, 0) # 맞았을 때 색상 변경
                    last_hit_time = current_time  # 마지막으로 맞은 시간 갱신

                    if player.hp <= 0:
                        # 게임 오버 화면 호출
                        action = game_over_screen(WIN, player.level, WIDTH, HEIGHT)
                        if action == "retry":
                            main()  # 게임 다시 시작
                        elif action == "quit":
                            pygame.quit()
                            sys.exit()
            else:
                # 색상 복구 로직 (적과 충돌하지 않을 때)
                if current_time - last_hit_time > 100:  # 0.2초 동안 색상 유지
                    PLAYER_COLOR = (0, 200, 255)  # 원래 색상으로 복구


        # 경험치 오브 흡수
        for orb in exp_orbs[:]:
            if player.rect.colliderect(orb.rect):
                player.gain_exp(5)  # 경험치 획득
                exp_orbs.remove(orb)

        # 격자 그리기
        draw_grid(WIN, camera)

        # 그리기
        for bullet in bullets:
            bullet.draw(WIN, camera)  # 회전된 총알 그리기
        for enemy in enemies:
            enemy.draw(WIN, camera)
        for wall in walls:
            wall.draw(WIN)  # WIN을 매개변수로 전달
        for orb in exp_orbs:
            orb.draw(WIN, camera)  # 경험치 오브 그리기
        player.draw(WIN, camera)

        # 플레이어 HP 바 및 레벨 표시
        player.draw_hp_bar(WIN, camera)

        font = pygame.font.SysFont(None, 36)

        draw_level(WIN, font, player)
        draw_ammo(WIN, font, player)

        pygame.display.update()

if __name__ == "__main__":
    main()
