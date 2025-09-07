import pygame
import sys

def game_over_screen(surface, player_level, width, height):
    font = pygame.font.SysFont(None, 50)
    small_font = pygame.font.SysFont(None, 36)

    # 게임 오버 메시지
    game_over_text = font.render("Game Over!", True, (255, 0, 0))
    level_text = small_font.render(f"Your Final Level: {player_level}", True, (255, 255, 255))

    # 버튼 설정
    retry_button = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
    quit_button = pygame.Rect(width // 2 - 100, height // 2 + 70, 200, 50)

    while True:
        surface.fill((0, 0, 0))  # 검은 배경

        # 텍스트 그리기
        surface.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - 100))
        surface.blit(level_text, (width // 2 - level_text.get_width() // 2, height // 2 - 50))

        # 버튼 그리기
        pygame.draw.rect(surface, (0, 200, 0), retry_button)
        pygame.draw.rect(surface, (200, 0, 0), quit_button)

        retry_text = small_font.render("Retry", True, (255, 255, 255))
        quit_text = small_font.render("Quit", True, (255, 255, 255))
        surface.blit(retry_text, (retry_button.centerx - retry_text.get_width() // 2, retry_button.centery - retry_text.get_height() // 2))
        surface.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2, quit_button.centery - quit_text.get_height() // 2))

        pygame.display.update()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.collidepoint(event.pos):  # 다시하기 버튼 클릭
                    return "retry"
                if quit_button.collidepoint(event.pos):  # 끝내기 버튼 클릭
                    return "quit"