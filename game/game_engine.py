import pygame
import sys
import random
from .paddle import Paddle
from .ball import Ball

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

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
        self.target_score = 5
        
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
        """
        If someone reached target_score, show result, then show replay menu
        and reset the game according to the user's choice.
        Returns True if game-over handled (and game restarted), False otherwise.
        """
        # No winner yet
        if self.player_score < self.target_score and self.ai_score < self.target_score:
            return False

        # Determine winner text
        if self.player_score >= self.target_score:
            winner_text = "Player Wins!"
        else:
            winner_text = "AI Wins!"

        # Show winner text centered
        font_large = pygame.font.SysFont("Arial", 60, bold=True)
        text_surface = font_large.render(winner_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 - 80))

        # Also show small instruction to prepare transition
        small = pygame.font.SysFont("Arial", 28)
        instr = small.render("Showing replay options shortly...", True, WHITE)
        instr_rect = instr.get_rect(center=(self.width // 2, self.height // 2 - 20))

        # Draw and flip
        screen.fill(BLACK)
        screen.blit(text_surface, text_rect)
        screen.blit(instr, instr_rect)
        pygame.display.flip()

        # Pause briefly so player sees the winner
        pygame.time.delay(1200)

        # Show replay menu and wait for a choice
        best_of = self.show_replay_menu(screen)

        # Reset engine state according to user's choice
        self.reset_game(best_of)

        return True


    


    def show_replay_menu(self, screen):
        """
        Displays the replay options on screen and blocks until the player
        presses 3, 5, 7 or ESC. Returns the integer best_of chosen (3,5,7).
        ESC exits the program.
        """
        font_title = pygame.font.SysFont("Arial", 48, bold=True)
        font_options = pygame.font.SysFont("Arial", 30)

        options = [
            ("Press 3 for Best of 3", pygame.K_3),
            ("Press 5 for Best of 5", pygame.K_5),
            ("Press 7 for Best of 7", pygame.K_7),
            ("Press ESC to Exit", pygame.K_ESCAPE),
        ]

        # Render loop until a valid key is pressed
        while True:
            screen.fill(BLACK)
            title = font_title.render("GAME OVER", True, WHITE)
            screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 160))

            # Show which side won previously (smaller)
            winner_small = font_options.render(
                f"Score: Player {self.player_score}  -  AI {self.ai_score}", True, WHITE
            )
            screen.blit(winner_small, (self.width // 2 - winner_small.get_width() // 2, self.height // 2 - 100))

            # Show options
            for i, (text, _) in enumerate(options):
                t = font_options.render(text, True, WHITE)
                screen.blit(t, (self.width // 2 - t.get_width() // 2, self.height // 2 - 40 + i * 40))

            pygame.display.flip()

            # Event processing (keeps UI responsive)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_3:
                        return 3
                    elif event.key == pygame.K_5:
                        return 5
                    elif event.key == pygame.K_7:
                        return 7
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # small sleep to avoid burning CPU
            pygame.time.delay(50)




    def reset_game(self, best_of):
        """
        best_of: 3, 5, or 7. Convert to required wins: (best_of // 2) + 1.
        Reset scores, reset paddles, and reset ball position/speeds.
        """
        # Validate input
        if best_of not in (3, 5, 7):
            best_of = 5

        # compute target (first-to)
        self.target_score = (best_of // 2) + 1

        # reset scores and positions
        self.player_score = 0
        self.ai_score = 0
        # center paddles
        self.player.y = self.height // 2 - self.player.height // 2
        self.ai.y = self.height // 2 - self.ai.height // 2

        # reset ball (Ball.reset should put ball back to original center)
        # If you want a short pause before next round, you could call pygame.time.delay(500)
        self.ball.reset()

