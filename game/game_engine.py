import pygame
from .paddle import Paddle
from .ball import Ball

# Game Engine

WHITE = (255, 255, 255)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)



    def update(self):
        # Move the ball
        self.ball.move()
        ball_rect = self.ball.rect()

        # --- Player paddle collision ---
        player_rect = self.player.rect()
        if ball_rect.colliderect(player_rect) and self.ball.velocity_x < 0:
            self.ball.velocity_x = abs(self.ball.velocity_x)  # Move right
            self.ball.x = player_rect.x + player_rect.width  # Place outside paddle

        # --- AI paddle collision ---
        ai_rect = self.ai.rect()
        if ball_rect.colliderect(ai_rect) and self.ball.velocity_x > 0:
            self.ball.velocity_x = -abs(self.ball.velocity_x)  # Move left
            self.ball.x = ai_rect.x - self.ball.width  # Place outside paddle

        # --- Top/Bottom wall collisions (bounce) ---
        if self.ball.y <= 0:
            self.ball.y = 0
            self.ball.velocity_y = abs(self.ball.velocity_y)  # Bounce down
        elif self.ball.y + self.ball.height >= self.height:
            self.ball.y = self.height - self.ball.height
            self.ball.velocity_y = -abs(self.ball.velocity_y)  # Bounce up

        # --- Left/Right walls (score & reset) ---
        if self.ball.x <= 0:
            self.ai_score += 1
            self.ball.reset()
        elif self.ball.x + self.ball.width >= self.width:
            self.player_score += 1
            self.ball.reset()

        # --- Update AI paddle ---
        self.ai.auto_track(self.ball, self.height)


    def render(self, screen):
        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        # Draw score
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4, 20))
        screen.blit(ai_text, (self.width * 3//4, 20))
        
        
    def check_game_over(self, screen):
        if self.player_score >= 5:
            winner_text = "Player Wins!"
        elif self.ai_score >= 5:
            winner_text = "AI Wins!"
        else:
            return False  # No one reached 5 yet

        # Display winner text
        font_large = pygame.font.SysFont("Arial", 60, bold=True)
        text_surface = font_large.render(winner_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

        # Wait for a few seconds so players can see it
        pygame.time.delay(3000)

        # End the game after showing the message
        pygame.quit()
        exit()

        return True

