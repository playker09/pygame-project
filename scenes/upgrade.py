import pygame
import random

# --- 공용 업그레이드 ---
COMMON_UPGRADES = [
    {"name": "공격 속도 증가", "effect": lambda player: setattr(player.current_weapon, "fire_rate", max(50, player.current_weapon.fire_rate - 10))},
    {"name": "재장전 속도 증가", "effect": lambda player: setattr(player.current_weapon, "reload_time", max(200, getattr(player.current_weapon, "reload_time", 1000) - 100))},
    {"name": "탄창 크기 증가", "effect": lambda player: setattr(player.current_weapon, "mag_size", player.current_weapon.mag_size + 3)},
    {"name": "이동 속도 증가", "effect": lambda player: setattr(player, "speed", player.speed + 0.2)},
    {"name": "체력 증가", "effect": lambda player: setattr(player, "max_hp", player.max_hp + 20)},
]

# --- 무기별 전용 업그레이드 ---
WEAPON_SPECIFIC = {
    "Pistol": [
        {"name": "권총 - 치명타 확률 증가", "effect": lambda player: setattr(player.current_weapon, "crit_chance", getattr(player.current_weapon, "crit_chance", 0.1) + 0.1)},
    ],
    "SMG": [
        {"name": "SMG - 반동 감소", "effect": lambda player: setattr(player.current_weapon, "spread", max(1, player.current_weapon.spread - 1))},
    ],
    "Burst Rifle": [
        {"name": "3점사 - 추가 탄환", "effect": lambda player: setattr(player.current_weapon, "burst_count", player.current_weapon.burst_count + 1)},
    ],
    "Shotgun": [
        {"name": "샷건 - 산탄 수 증가", "effect": lambda player: setattr(player.current_weapon, "pellet_count", player.current_weapon.pellet_count + 2)},
    ],
}

# --- 보조 무기 ---
SECONDARIES = [
    {"name": "드론 잠금 해제 / 강화", "effect": lambda player: unlock_or_upgrade(player, "drone")},
    {"name": "수류탄 잠금 해제 / 강화", "effect": lambda player: unlock_or_upgrade(player, "grenade")},
]

# --- 악세사리 ---
ACCESSORIES = [
    {"name": "HP 회복 속도 증가", "effect": lambda player: setattr(player, "hp", min(player.max_hp, player.hp + 20))},
    {"name": "대쉬 쿨다운 감소", "effect": lambda player: setattr(player, "dash_cooldown_time", max(1000, player.dash_cooldown_time - 500))},
    {"name": "경험치 획득량 증가", "effect": lambda player: setattr(player, "exp", player.exp + 5)},
]

# --- 보조 무기 해제 & 강화 ---
def unlock_or_upgrade(player, weapon_type):
    if weapon_type == "drone":
        if not player.drone_unlocked:
            player.drone_unlocked = True
            print("드론 잠금 해제!")
        else:
            player.upgrades["secondary"].append("드론 강화")
            print("드론 강화!")
    elif weapon_type == "grenade":
        if not player.grenade_unlocked:
            player.grenade_unlocked = True
            print("수류탄 잠금 해제!")
        else:
            player.upgrades["secondary"].append("수류탄 강화")
            print("수류탄 강화!")

# --- 업그레이드 선택 화면 ---
def show_upgrade_screen(surface, player, WIDTH, HEIGHT):
    font = pygame.font.SysFont("malgungothic", 24)

    # --- 창 크기 설정 ---
    ui_width, ui_height = 400, 300
    overlay = pygame.Surface((ui_width, ui_height), pygame.SRCALPHA)
    overlay.fill((50, 50, 50))           # 회색 배경
    overlay.set_alpha(255)               # 약간 투명

    rect = overlay.get_rect(center=(WIDTH//2, HEIGHT//2))

    # --- 업그레이드 후보 생성 ---
    upgrades = []

    if player.primary_weapon and player.primary_weapon.name in WEAPON_SPECIFIC:
        upgrades.extend(WEAPON_SPECIFIC[player.primary_weapon.name])
    upgrades.extend(COMMON_UPGRADES)
    if len(player.upgrades["secondary"]) < player.max_secondary_upgrades:
        upgrades.extend(SECONDARIES)
    if len(player.upgrades["accessory"]) < player.max_accessory:
        upgrades.extend(ACCESSORIES)

    choices = random.sample(upgrades, min(3, len(upgrades)))

    selected = None
    while selected is None:
        # 게임 화면 그대로 두고 창만
        surface.blit(overlay, rect.topleft)

        # 버튼 표시
        for i, up in enumerate(choices):
            btn_rect = pygame.Rect(rect.x + 50, rect.y + 40 + i*80, ui_width-100, 60)
            pygame.draw.rect(surface, (100, 100, 100), btn_rect, border_radius=10)
            pygame.draw.rect(surface, (200, 200, 200), btn_rect, 2, border_radius=10)
            text = font.render(up["name"], True, (255, 255, 255))
            surface.blit(text, (btn_rect.x + 10, btn_rect.y + 15))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for i, up in enumerate(choices):
                    btn_rect = pygame.Rect(rect.x + 50, rect.y + 40 + i*80, ui_width-100, 60)
                    if btn_rect.collidepoint((mx, my)):
                        selected = up

    # 업그레이드 적용
    selected["effect"](player)
    if selected in COMMON_UPGRADES or selected in WEAPON_SPECIFIC.get(player.primary_weapon.name, []):
        player.upgrades["weapon"].append(selected["name"])
    elif selected in SECONDARIES:
        player.upgrades["secondary"].append(selected["name"])
    elif selected in ACCESSORIES:
        player.upgrades["accessory"].append(selected["name"])
