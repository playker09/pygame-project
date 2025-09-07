import pygame
import math

def draw_level(surface, font, player):
    """플레이어 레벨과 경험치 표시"""
    level_text = font.render(f"Level: {player.level}  Exp: {player.exp}/{player.exp_to_next_level}", True, (255, 255, 255))
    surface.blit(level_text, (10, 10))

def draw_ammo(surface, font, player):
    """현재 무기 탄약 표시"""
    weapon = player.current_weapon
    text = font.render(f"Ammo: {weapon.ammo_in_mag}/{weapon.reserve_ammo}", True, (255, 255, 255))
    surface.blit(text, (10, 540)) 

def draw_dash_indicator(surface, font, player):
    """대쉬 가능 표시"""
    if player.dash_cooldown <= 0:
        text = font.render("DASH READY", True, (0, 255, 0))
        surface.blit(text, (10, 570))
    else: 
        text = font.render(f"{player.dash_cooldown/1000+1:.1f}", True, (2, 255, 0))
        surface.blit(text, (10, 570))
# --- 마우스 조준선 ---
def draw_crosshair(surface, mx, my, size=10, color=(255,255,255), width=2):
    pygame.draw.line(surface, color, (mx - size, my), (mx + size, my), width)
    pygame.draw.line(surface, color, (mx, my - size), (mx, my + size), width)

# --- 재장전 원 표시 ---
def draw_reload_circle(surface, pos, radius, weapon):
    if not weapon.is_reloading:
        return
    
    # 진행률 계산
    current_time = pygame.time.get_ticks()
    elapsed = current_time - weapon.reload_start_time
    progress = min(elapsed / weapon.reload_time, 1)  # 0~1
    
    start_angle = math.pi/2  # 위쪽에서 시작
    end_angle = start_angle - progress * 2 * math.pi  # 반시계 방향
    
    # 항상 같은 두께로 그림
    pygame.draw.arc(surface, (255, 255, 0), 
                    (pos[0]-radius, pos[1]-radius, radius*2, radius*2),
                    end_angle, start_angle, 3)  # <- width=3 고정
    
def draw_emp_indicator(surface, player, towers):
    """
    플레이어 기준 가장 가까운 **활성화되지 않은 타워**만 표시
    """
    # 활성화되지 않은 타워만 선택
    inactive_towers = [t for t in towers if not t.activated]
    if not inactive_towers:
        return

    # 가장 가까운 타워 선택
    nearest_tower = min(
        inactive_towers,
        key=lambda t: math.hypot(t.rect.centerx - player.rect.centerx,
                                 t.rect.centery - player.rect.centery)
    )

    dx = nearest_tower.rect.centerx - player.rect.centerx
    dy = nearest_tower.rect.centery - player.rect.centery
    distance = math.hypot(dx, dy)

    if distance < 300:  # 너무 가까우면 표시 안 함
        return

    # 방향 계산
    angle = math.atan2(dy, dx)
    cx, cy = surface.get_width() // 2, surface.get_height() // 2
    offset = 100
    indicator_size = 20
    arrow_x = cx + math.cos(angle) * offset
    arrow_y = cy + math.sin(angle) * offset

    points = [
        (arrow_x + math.cos(angle) * indicator_size, arrow_y + math.sin(angle) * indicator_size),
        (arrow_x + math.cos(angle + 2.5) * indicator_size, arrow_y + math.sin(angle + 2.5) * indicator_size),
        (arrow_x + math.cos(angle - 2.5) * indicator_size, arrow_y + math.sin(angle - 2.5) * indicator_size),
    ]
    
    pygame.draw.polygon(surface, (255, 255, 0), points)
