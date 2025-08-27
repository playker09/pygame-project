import pygame

# 맵 크기
MAP_WIDTH, MAP_HEIGHT = 1600, 1200  # 창 크기보다 큰 맵

# 격자 그리기 함수
def draw_grid(surface,camera):
    grid_color = (50, 50, 50)  # 격자 색상
    grid_size = 40  # 격자 간격

    # 수직선 그리기
    for x in range(0, MAP_WIDTH, grid_size):
        pygame.draw.line(surface, grid_color, (x - camera.offset_x, 0 - camera.offset_y), (x - camera.offset_x, MAP_HEIGHT - camera.offset_y))

    # 수평선 그리기
    for y in range(0, MAP_HEIGHT, grid_size):
        pygame.draw.line(surface, grid_color, (0 - camera.offset_x, y - camera.offset_y), (MAP_WIDTH - camera.offset_x, y - camera.offset_y))
