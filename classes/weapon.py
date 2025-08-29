import math, random
from classes.bullet import Bullet

class Weapon:
    def __init__(self, name, fire_rate, spread, mode="single", burst_count=3, pellet_count=5,
                 mag_size=30, reserve_ammo=90, reload_time=1500):
        self.name = name
        self.fire_rate = fire_rate
        self.spread = spread
        self.mode = mode
        self.last_shot = 0
        self.burst_count = burst_count
        self.pellet_count = pellet_count

        # 🔫 탄약 관련
        self.mag_size = mag_size
        self.ammo_in_mag = mag_size
        self.reserve_ammo = reserve_ammo
        self.reload_time = reload_time  # ms
        self.is_reloading = False
        self.reload_start_time = 0

    def shoot(self, px, py, mx, my, camera, bullets, current_time):
        # 탄창 비었으면 발사 불가
        if self.ammo_in_mag <= 0:
            if not self.is_reloading:
                self.reload(current_time)
            return
        
        # 장전 중이면 장전 중단
        if self.is_reloading:
            self.is_reloading = False
            self.reload_start_time = 0

        if current_time - self.last_shot < self.fire_rate:
            return

        self.last_shot = current_time
        self.ammo_in_mag -= 1  # 🔥 탄약 소모

        # 카메라 오프셋 적용
        mx += camera.offset_x
        my += camera.offset_y

        dx, dy = mx - px, my - py
        length = math.hypot(dx, dy)
        if length == 0:
            return
        dx, dy = dx / length, dy / length

        if self.mode == "single" or self.mode == "auto":
            self.spawn_bullet(px, py, dx, dy, bullets)

        elif self.mode == "burst":
            for _ in range(self.burst_count):
                self.spawn_bullet(px, py, dx, dy, bullets)

        elif self.mode == "shotgun":
            for _ in range(self.pellet_count):
                self.spawn_bullet(px, py, dx, dy, bullets)

    def reload(self, current_time):
        if self.is_reloading:
            return
        if self.ammo_in_mag == self.mag_size or self.reserve_ammo == 0:
            return

        self.is_reloading = True
        self.reload_start_time = current_time

    def update(self, current_time):
        # 장전 중이면 장전 시간 체크
        if self.is_reloading and current_time - self.reload_start_time >= self.reload_time:
            needed = self.mag_size - self.ammo_in_mag
            to_load = min(needed, self.reserve_ammo)

            self.ammo_in_mag += to_load
            self.reserve_ammo -= to_load
            self.is_reloading = False

    def spawn_bullet(self, px, py, dx, dy, bullets):
        spread_angle = math.radians(random.uniform(-self.spread, self.spread))
        cos_a, sin_a = math.cos(spread_angle), math.sin(spread_angle)
        sdx = dx * cos_a - dy * sin_a
        sdy = dx * sin_a + dy * cos_a

        bullets.append(Bullet(px, py, sdx, sdy))


