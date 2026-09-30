import pygame

from game.player import Player
from game.world import (
    generate_platforms,
    draw_lava,
    PLATFORM_COLOR,
    CRUMBLING_PLATFORM_COLOR
)


WIDTH, HEIGHT = 500, 640
FPS = 60
BG = (20, 15, 30)
GROUND_Y = HEIGHT + 200

CRUMBLE_DURATION = 1000


class GameEngine:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption("Lava Escape")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "monospace",
            24,
            bold=True
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            42,
            bold=True
        )

        self.reset()

    def reset(self):
        self.platforms = generate_platforms(
            WIDTH,
            GROUND_Y
        )

        self.player = Player(
            WIDTH // 2 - 16,
            GROUND_Y - 50
        )

        self.cam_y = 0

        self.lava_y = GROUND_Y + 60
        self.lava_rise = 0.4

        self.score = 0

        self.game_over = False
        self.won = False

        self.top_y = self.platforms[-1].y

        self.frame = 0

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):
                self.reset()

        return True

    def update_crumbling_platforms(self):
        current_time = pygame.time.get_ticks()

        remaining_platforms = []

        for p in self.platforms:

            # Normal platform
            if not p.crumbling:
                remaining_platforms.append(p)
                continue

            # Crumbling platform that has not been activated yet
            if p.crumble_started_at is None:
                remaining_platforms.append(p)
                continue

            elapsed = current_time - p.crumble_started_at

            # Remove the platform after 1 second
            if elapsed >= CRUMBLE_DURATION:
                continue

            remaining_platforms.append(p)

        self.platforms = remaining_platforms

    def update(self):
        if self.game_over or self.won:
            return

        keys = pygame.key.get_pressed()

        self.player.update(
            keys,
            self.platforms,
            WIDTH
        )

        # Task 2:
        # Check whether any activated crumbling
        # platforms should now disappear.
        self.update_crumbling_platforms()

        target = self.player.rect.centery - HEIGHT // 2

        if target < self.cam_y:
            self.cam_y = target

        self.lava_y -= self.lava_rise

        self.lava_rise = min(
            1.2,
            self.lava_rise + 0.0003
        )

        self.score = max(
            0,
            (GROUND_Y - self.player.rect.y) // 10
        )

        self.frame += 1

        if self.player.rect.bottom >= self.lava_y:
            self.game_over = True

        if self.player.rect.top <= self.top_y - 20:
            self.won = True

    def draw(self):
        self.screen.fill(BG)

        current_time = pygame.time.get_ticks()

        for p in self.platforms:

            draw_rect = p.rect.copy()

            # Task 2:
            # Draw crumbling platforms with a shaking animation.
            if p.crumbling and p.crumble_started_at is not None:

                elapsed = (
                    current_time
                    - p.crumble_started_at
                )

                # Shake more visibly while crumbling
                if elapsed < CRUMBLE_DURATION:

                    shake_x = 0
                    shake_y = 0

                    if (elapsed // 80) % 2 == 0:
                        shake_x = 3
                    else:
                        shake_x = -3

                    draw_rect.x += shake_x
                    draw_rect.y += shake_y

                    color = CRUMBLING_PLATFORM_COLOR

                else:
                    color = CRUMBLING_PLATFORM_COLOR

            else:
                color = (
                    CRUMBLING_PLATFORM_COLOR
                    if p.crumbling
                    else PLATFORM_COLOR
                )

            dr = draw_rect.move(
                0,
                -int(self.cam_y)
            )

            pygame.draw.rect(
                self.screen,
                color,
                dr,
                border_radius=4
            )

        self.player.draw(
            self.screen,
            self.cam_y
        )

        draw_lava(
            self.screen,
            self.lava_y,
            self.cam_y,
            WIDTH,
            HEIGHT,
            self.frame
        )

        sc = self.font.render(
            f"Height: {self.score}m  R=Restart",
            True,
            (220, 200, 180)
        )

        self.screen.blit(sc, (8, 10))

        if self.game_over:
            self._msg(
                "LAVA GOT YOU!",
                (220, 80, 40)
            )

        if self.won:
            self._msg(
                "ESCAPED!",
                (80, 220, 100)
            )

        pygame.display.flip()

    def _msg(self, text, color):
        ov = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        ov.fill((0, 0, 0, 150))

        self.screen.blit(
            ov,
            (0, 0)
        )

        m = self.big_font.render(
            text,
            True,
            color
        )

        s = self.font.render(
            "Press R to Play Again",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            m,
            (
                WIDTH // 2 - m.get_width() // 2,
                HEIGHT // 2 - 40
            )
        )

        self.screen.blit(
            s,
            (
                WIDTH // 2 - s.get_width() // 2,
                HEIGHT // 2 + 20
            )
        )

    def run(self):
        running = True

        while running:
            running = self.handle_events()

            self.update()
            self.draw()

            self.clock.tick(FPS)

        pygame.quit()