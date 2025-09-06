import pygame
import random
from classes.weapon import Weapon

# ---------------- Upgrade 클래스 ----------------
class Upgrade:
    def __init__(self, name, desc, effect, extra_effects=None, max_level=5):
        self.name = name
        self.desc = desc
        self.effect = effect                # (player, level) -> 기본 효과
        self.extra_effects = extra_effects or {}  # {레벨: 함수(player)}
        self.level = 0                      # 현재 레벨
        self.max_level = max_level          # 최대 레벨 (None이면 무제한)

    def apply(self, player):
        if self.max_level is not None and self.level >= self.max_level:
            print(f"[최대 레벨] {self.name} Lv.{self.level}")
            return  # 최대 레벨 도달하면 적용 안함
        
        self.level += 1
        # 기본 효과
        self.effect(player, self.level)
        # 추가 효과
        if self.level in self.extra_effects:
            self.extra_effects[self.level](player)
            print(f"[추가 효과 발동] {self.name} Lv.{self.level}")


# ---------------- 공용 업그레이드 ----------------
COMMON_UPGRADES = [
    Upgrade(
        "속사 모드", "무기 발사 속도가 빨라집니다.",
        effect=lambda p, lvl: setattr(p.current_weapon, "fire_rate", max(50, p.current_weapon.fire_rate - 10)),
        extra_effects={
            3: lambda p: setattr(p.current_weapon, "spread", max(1, p.current_weapon.spread - 1)),
            5: lambda p: setattr(p.current_weapon, "crit_chance", getattr(p.current_weapon, "crit_chance", 0.1) + 0.2),
        },
    ),
    Upgrade(
        "체력 증가", "최대 체력이 증가합니다.",
        effect=lambda p, lvl: setattr(p, "max_hp", p.max_hp + 20),
        extra_effects={
            3: lambda p: setattr(p, "hp_regen", getattr(p, "hp_regen", 0) + 1)
        }
    ),
    Upgrade(
        "대용량 탄창", "탄약 수가 늘어납니다.",
        effect=lambda p, lvl: setattr(p.current_weapon, "mag_size", p.current_weapon.mag_size + 3)
    ),
    Upgrade(
        "이동 속도 증가", "이동 속도가 증가합니다.",
        effect=lambda p, lvl: setattr(p, "speed", p.speed + 0.2)
    ),
    Upgrade(
        "관통 공격", "총알이 적을 관통합니다.",
        effect=lambda p, lvl: setattr(p.current_weapon, "pierce_level", lvl)
    ),
]

# ---------------- 무기별 전용 업그레이드 ----------------
WEAPON_SPECIFIC = {
    "DMR": [
        Upgrade(
            "DMR - 치명타 확률 증가", "치명타 확률이 증가합니다.",
            effect=lambda p, lvl: setattr(p.current_weapon, "crit_chance",
                                          getattr(p.current_weapon, "crit_chance", 0.1) + 0.1)
        )
    ],
    "SMG": [
        Upgrade(
            "SMG - 반동 감소", "반동이 줄어듭니다.",
            effect=lambda p, lvl: setattr(p.current_weapon, "spread", max(1, p.current_weapon.spread - 1))
        )
    ],
    "Rifle": [
        Upgrade(
            "돌격 소총 - 추가 탄환", "버스트 발사 시 탄환이 추가됩니다.",
            effect=lambda p, lvl: setattr(p.current_weapon, "burst_count", p.current_weapon.burst_count + 1)
        )
    ],
    "Shotgun": [
        Upgrade(
            "샷건 - 산탄 수 증가", "산탄 수가 늘어납니다.",
            effect=lambda p, lvl: setattr(p.current_weapon, "pellet_count", p.current_weapon.pellet_count + 2)
        )
    ],
}

# ---------------- 보조 무기 ----------------
SECONDARIES = [
    Upgrade(
        "드론 잠금 해제 / 강화", "드론을 해제하거나 강화합니다.",
        effect=lambda p, lvl: unlock_or_upgrade(p, "drone", lvl)
    ),
    Upgrade(
        "수류탄 잠금 해제 / 강화", "수류탄을 해제하거나 강화합니다.",
        effect=lambda p, lvl: unlock_or_upgrade(p, "grenade", lvl)
    ),
]

# ---------------- 악세사리 ----------------
ACCESSORIES = [
    Upgrade(
        "HP 회복 속도 증가", "체력이 즉시 회복됩니다.",
        effect=lambda p, lvl: setattr(p, "hp", min(p.max_hp, p.hp + 20))
    ),
    Upgrade(
        "에너지 음료", "대쉬 쿨타임 감소",
        effect=lambda p, lvl: setattr(p, "dash_cooldown_time", max(1000, p.dash_cooldown_time - 500))
    ),
    Upgrade(
        "베테랑", "추가 경험치 획득",
        effect=lambda p, lvl: setattr(p, "exp", p.exp + 5)
    ),
]

# ---------------- 보조 무기 해제 & 강화 ----------------
def unlock_or_upgrade(player, weapon_type, level):
    if weapon_type == "drone":
        if not getattr(player, "drone_unlocked", False):
            player.drone_unlocked = True
        else:
            player.drone_damage = getattr(player, "drone_damage", 10) + 5
    elif weapon_type == "grenade":
        if not getattr(player, "grenade_unlocked", False):
            player.grenade_unlocked = True
        else:
            player.grenade_radius = getattr(player, "grenade_radius", 50) + 10

# ---------------- 업그레이드 후보 생성 ----------------
def generate_upgrades(player):
    upgrades = []
    if player.primary_weapon and player.primary_weapon.name in WEAPON_SPECIFIC:
        upgrades.extend(WEAPON_SPECIFIC[player.primary_weapon.name])
    upgrades.extend(COMMON_UPGRADES)
    if len(player.upgrades["secondary"]) < player.max_secondary_upgrades:
        upgrades.extend(SECONDARIES)
    if len(player.upgrades["accessory"]) < player.max_accessory:
        upgrades.extend(ACCESSORIES)
    return random.sample(upgrades, min(3, len(upgrades)))

# ---------------- UI 그리기 ----------------
def draw_upgrade_ui(surface, player, choices):
    font = pygame.font.SysFont("malgungothic", 24)
    small_font = pygame.font.SysFont("malgungothic", 18)

    ui_width, ui_height = 500, 360
    overlay = pygame.Surface((ui_width, ui_height))
    overlay.fill((50, 50, 50))
    overlay.set_alpha(230)
    rect = overlay.get_rect(center=(surface.get_width()//2, surface.get_height()//2))
    surface.blit(overlay, rect.topleft)

    btn_rects = []
    for i, up in enumerate(choices):
        btn_rect = pygame.Rect(rect.x + 50, rect.y + 40 + i*100, ui_width-100, 80)
        btn_rects.append(btn_rect)

        # 버튼 배경
        pygame.draw.rect(surface, (100, 100, 100), btn_rect, border_radius=10)
        pygame.draw.rect(surface, (200, 200, 200), btn_rect, 2, border_radius=10)

        # 레벨 가져오기
        level = up.level

        # 이름 + 레벨
        text = font.render(f"{up.name} (Lv.{level})", True, (255, 255, 255))
        surface.blit(text, (btn_rect.x + 10, btn_rect.y + 10))

        # 설명
        desc = small_font.render(up.desc, True, (200, 200, 200))
        surface.blit(desc, (btn_rect.x + 10, btn_rect.y + 45))

    return btn_rects
