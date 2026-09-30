import pygame

from game.player import Player

from game.world import (
    generate_platforms,
    draw_lava,
    PLATFORM_COLOR,
    CRUMBLING_PLATFORM_COLOR,
    SPRING_PLATFORM_COLOR
)


WIDTH = 500
HEIGHT = 640

FPS = 60

BG = (20, 15, 30)

GROUND_Y = HEIGHT + 200

# Task 2
CRUMBLE_DURATION = 1000

# Task 4
LAVA_BURST_INTERVAL = 15000       # 15 seconds
LAVA_BURST_DURATION = 3000       # 3 seconds
LAVA_BURST_MULTIPLIER = 3.0


class GameEngine:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Lava Escape"
        )

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

    # ==================================================
    # RESET
    # ==================================================

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

        # Store the normal lava speed.
        self.normal_lava_rise = 0.4

        self.score = 0

        self.game_over = False

        self.won = False

        self.top_y = self.platforms[-1].y

        self.frame = 0

        # ==================================================
        # TASK 4
        # Lava Burst timing
        # ==================================================

        self.game_start_time = pygame.time.get_ticks()

        self.lava_burst_active = False

        self.lava_burst_started_at = None

    # ==================================================
    # EVENTS
    # ==================================================

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

    # ==================================================
    # TASK 2
    # CRUMBLING PLATFORM UPDATE
    # ==================================================

    def update_crumbling_platforms(self):

        current_time = pygame.time.get_ticks()

        remaining_platforms = []

        for p in self.platforms:

            # Normal platform
            if not p.crumbling:

                remaining_platforms.append(p)

                continue

            # Crumbling platform which
            # has not been activated yet.
            if p.crumble_started_at is None:

                remaining_platforms.append(p)

                continue

            elapsed = (
                current_time
                - p.crumble_started_at
            )

            # Remove after 1 second.
            if elapsed >= CRUMBLE_DURATION:

                continue

            remaining_platforms.append(p)

        self.platforms = remaining_platforms

    # ==================================================
    # TASK 4
    # UPDATE LAVA BURST
    # ==================================================

    def update_lava_burst(self):

        current_time = pygame.time.get_ticks()

        elapsed_since_start = (
            current_time
            - self.game_start_time
        )

        # --------------------------------------------------
        # Start a new Lava Burst every 15 seconds
        # --------------------------------------------------

        if (
            not self.lava_burst_active
            and elapsed_since_start > 0
            and elapsed_since_start
            % LAVA_BURST_INTERVAL < 50
        ):

            self.lava_burst_active = True

            self.lava_burst_started_at = current_time

            # Temporarily increase lava speed.
            self.lava_rise = (
                self.normal_lava_rise
                * LAVA_BURST_MULTIPLIER
            )

        # --------------------------------------------------
        # If a burst is active, check its duration
        # --------------------------------------------------

        if self.lava_burst_active:

            burst_elapsed = (
                current_time
                - self.lava_burst_started_at
            )

            if burst_elapsed >= LAVA_BURST_DURATION:

                self.lava_burst_active = False

                self.lava_burst_started_at = None

                # Return to normal lava speed.
                self.lava_rise = self.normal_lava_rise

    # ==================================================
    # GAME UPDATE
    # ==================================================

    def update(self):

        if self.game_over or self.won:
            return

        keys = pygame.key.get_pressed()

        # Update player.
        self.player.update(
            keys,
            self.platforms,
            WIDTH
        )

        # Task 2
        self.update_crumbling_platforms()

        # Task 4
        self.update_lava_burst()

        # --------------------------------------------------
        # Camera tracking
        # --------------------------------------------------

        target = (
            self.player.rect.centery
            - HEIGHT // 2
        )

        if target < self.cam_y:

            self.cam_y = target

        # --------------------------------------------------
        # Lava movement
        # --------------------------------------------------

        self.lava_y -= self.lava_rise

        # Gradually increase normal lava speed.
        self.normal_lava_rise = min(
            1.2,
            self.normal_lava_rise + 0.0003
        )

        # If there is no burst, use normal speed.
        if not self.lava_burst_active:

            self.lava_rise = self.normal_lava_rise

        # --------------------------------------------------
        # Score
        # --------------------------------------------------

        self.score = max(
            0,
            (
                GROUND_Y
                - self.player.rect.y
            ) // 10
        )

        self.frame += 1

        # --------------------------------------------------
        # Lava collision
        # --------------------------------------------------

        if (
            self.player.rect.bottom
            >= self.lava_y
        ):

            self.game_over = True

        # --------------------------------------------------
        # Victory
        # --------------------------------------------------

        if (
            self.player.rect.top
            <= self.top_y - 20
        ):

            self.won = True

    # ==================================================
    # DRAW
    # ==================================================

    def draw(self):

        self.screen.fill(BG)

        current_time = pygame.time.get_ticks()

        # ==================================================
        # DRAW PLATFORMS
        # ==================================================

        for p in self.platforms:

            draw_rect = p.rect.copy()

            # ------------------------------------------------
            # TASK 2
            # CRUMBLING PLATFORM SHAKE
            # ------------------------------------------------

            if (
                p.crumbling
                and p.crumble_started_at is not None
            ):

                elapsed = (
                    current_time
                    - p.crumble_started_at
                )

                if elapsed < CRUMBLE_DURATION:

                    if (
                        elapsed // 80
                    ) % 2 == 0:

                        shake_x = 3

                    else:

                        shake_x = -3

                    draw_rect.x += shake_x

                color = (
                    CRUMBLING_PLATFORM_COLOR
                )

            # ------------------------------------------------
            # TASK 3
            # SPRING PLATFORM
            # ------------------------------------------------

            elif p.spring:

                color = SPRING_PLATFORM_COLOR

            # ------------------------------------------------
            # NORMAL PLATFORM
            # ------------------------------------------------

            else:

                color = PLATFORM_COLOR

            # Move according to camera.
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

            # ==================================================
            # TASK 3
            # DRAW SPRING COILS
            # ==================================================

            if p.spring:

                spring_x = dr.centerx

                spring_bottom = dr.bottom

                pygame.draw.line(
                    self.screen,
                    (255, 245, 150),
                    (
                        spring_x - 12,
                        spring_bottom - 2
                    ),
                    (
                        spring_x - 6,
                        spring_bottom - 9
                    ),
                    3
                )

                pygame.draw.line(
                    self.screen,
                    (255, 245, 150),
                    (
                        spring_x - 6,
                        spring_bottom - 9
                    ),
                    (
                        spring_x,
                        spring_bottom - 2
                    ),
                    3
                )

                pygame.draw.line(
                    self.screen,
                    (255, 245, 150),
                    (
                        spring_x,
                        spring_bottom - 2
                    ),
                    (
                        spring_x + 6,
                        spring_bottom - 9
                    ),
                    3
                )

                pygame.draw.line(
                    self.screen,
                    (255, 245, 150),
                    (
                        spring_x + 6,
                        spring_bottom - 9
                    ),
                    (
                        spring_x + 12,
                        spring_bottom - 2
                    ),
                    3
                )

        # ==================================================
        # PLAYER
        # ==================================================

        self.player.draw(
            self.screen,
            self.cam_y
        )

        # ==================================================
        # LAVA
        # ==================================================

        draw_lava(
            self.screen,
            self.lava_y,
            self.cam_y,
            WIDTH,
            HEIGHT,
            self.frame
        )

        # ==================================================
        # NORMAL HUD
        # ==================================================

        sc = self.font.render(
            f"Height: {self.score}m  R=Restart",
            True,
            (220, 200, 180)
        )

        self.screen.blit(
            sc,
            (8, 10)
        )

        # ==================================================
        # TASK 4
        # DANGER METER
        # ==================================================

        self.draw_danger_meter()

        # ==================================================
        # TASK 4
        # LAVA BURST WARNING
        # ==================================================

        if self.lava_burst_active:

            warning = self.big_font.render(
                "LAVA BURST!",
                True,
                (255, 80, 40)
            )

            self.screen.blit(
                warning,
                (
                    WIDTH // 2
                    - warning.get_width() // 2,
                    55
                )
            )

        # ==================================================
        # GAME OVER
        # ==================================================

        if self.game_over:

            self._msg(
                "LAVA GOT YOU!",
                (220, 80, 40)
            )

        # ==================================================
        # VICTORY
        # ==================================================

        if self.won:

            self._msg(
                "ESCAPED!",
                (80, 220, 100)
            )

        pygame.display.flip()

    # ==================================================
    # TASK 4
    # DANGER METER DRAWING
    # ==================================================

    def draw_danger_meter(self):

        meter_x = WIDTH - 170
        meter_y = 12

        meter_width = 155
        meter_height = 18

        # Normal lava speed ranges roughly
        # from 0.4 to 1.2.
        min_speed = 0.4
        max_speed = 1.2

        danger = (
            self.lava_rise - min_speed
        ) / (
            max_speed - min_speed
        )

        danger = max(
            0.0,
            min(1.0, danger)
        )

        # Background
        pygame.draw.rect(
            self.screen,
            (60, 60, 60),
            (
                meter_x,
                meter_y,
                meter_width,
                meter_height
            ),
            border_radius=5
        )

        # Filled portion
        fill_width = int(
            meter_width * danger
        )

        if fill_width > 0:

            pygame.draw.rect(
                self.screen,
                (230, 70, 40),
                (
                    meter_x,
                    meter_y,
                    fill_width,
                    meter_height
                ),
                border_radius=5
            )

        # Border
        pygame.draw.rect(
            self.screen,
            (230, 220, 200),
            (
                meter_x,
                meter_y,
                meter_width,
                meter_height
            ),
            width=2,
            border_radius=5
        )

        label = self.font.render(
            "DANGER",
            True,
            (240, 220, 200)
        )

        self.screen.blit(
            label,
            (
                meter_x,
                meter_y + 22
            )
        )

    # ==================================================
    # MESSAGE
    # ==================================================

    def _msg(
        self,
        text,
        color
    ):

        ov = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        ov.fill(
            (0, 0, 0, 150)
        )

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
                WIDTH // 2
                - m.get_width() // 2,
                HEIGHT // 2 - 40
            )
        )

        self.screen.blit(
            s,
            (
                WIDTH // 2
                - s.get_width() // 2,
                HEIGHT // 2 + 20
            )
        )

    # ==================================================
    # MAIN LOOP
    # ==================================================

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()