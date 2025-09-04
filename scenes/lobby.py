import pygame
import sys

def lobby_screen(surface, WIDTH, HEIGHT):
    # 버튼 위치와 크기
    button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 60)
    title_font = pygame.font.SysFont("arial", 80, bold=True)
    button_font = pygame.font.SysFont("arial", 40)

    while True:
        surface.fill((30, 30, 60))  # 배경 색

        # 제목
        title_surface = title_font.render("My Game", True, (255, 255, 255))
        surface.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, HEIGHT//4))

        # 버튼 그리기
        pygame.draw.rect(surface, (200, 200, 200), button_rect, border_radius=10)
        text_surface = button_font.render("Start", True, (0, 0, 0))
        surface.blit(text_surface, (button_rect.x + (button_rect.width - text_surface.get_width())//2,
                                button_rect.y + (button_rect.height - text_surface.get_height())//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    return  # 다음 장면으로 이동