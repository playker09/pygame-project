import pygame

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