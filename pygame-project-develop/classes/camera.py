from scenes.map import MAP_WIDTH, MAP_HEIGHT

class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.width = width
        self.height = height

    def update(self, target):
        self.offset_x = target.rect.centerx - self.width // 2
        self.offset_y = target.rect.centery - self.height // 2
        self.offset_x = max(0, min(self.offset_x, MAP_WIDTH - self.width))
        self.offset_y = max(0, min(self.offset_y, MAP_HEIGHT - self.height))

    def apply(self, rect):
        return rect.move(-self.offset_x, -self.offset_y)