import pygame

SPEED = 4

NORMAL_JUMP_VELOCITY = -13
SPRING_JUMP_VELOCITY = -22


class Player:

    def __init__(self, x, y):

        self.rect = pygame.Rect(
            x,
            y,
            32,
            32
        )

        self.vel_y = 0

        self.on_ground = False

        self.color = (60, 160, 220)

        # Task 3:
        # Controls the visual spring recoil animation.
        self.spring_bounce_until = 0

    def update(
        self,
        keys,
        platforms,
        width
    ):

        dx = 0

        # -------------------------
        # Horizontal movement
        # -------------------------

        if (
            keys[pygame.K_LEFT]
            or keys[pygame.K_a]
        ):
            dx = -SPEED

        if (
            keys[pygame.K_RIGHT]
            or keys[pygame.K_d]
        ):
            dx = SPEED

        # -------------------------
        # Normal jump
        # -------------------------

        if (
            (
                keys[pygame.K_SPACE]
                or keys[pygame.K_w]
                or keys[pygame.K_UP]
            )
            and self.on_ground
        ):
            self.vel_y = NORMAL_JUMP_VELOCITY
            self.on_ground = False

        # -------------------------
        # Gravity
        # -------------------------

        self.vel_y = min(
            self.vel_y + 0.55,
            12
        )

        # -------------------------
        # Horizontal movement
        # -------------------------

        self.rect.x = max(
            0,
            min(
                width - self.rect.width,
                self.rect.x + dx
            )
        )

        # Store player's feet position
        # before vertical movement.
        previous_bottom = self.rect.bottom

        # -------------------------
        # Vertical movement
        # -------------------------

        self.rect.y += int(self.vel_y)

        self.on_ground = False

        # -------------------------
        # Platform collision
        # -------------------------

        for p in platforms:

            if (
                self.rect.colliderect(p.rect)
                and self.vel_y > 0
                and previous_bottom <= p.top + 2
            ):

                # Place player exactly
                # on top of platform.
                self.rect.bottom = p.top

                # Stop normal downward movement.
                self.vel_y = 0

                self.on_ground = True

                # -------------------------
                # Task 2
                # Crumbling platform
                # -------------------------

                if (
                    p.crumbling
                    and p.crumble_started_at is None
                ):

                    p.crumble_started_at = (
                        pygame.time.get_ticks()
                    )

                # -------------------------
                # Task 3
                # Spring platform
                # -------------------------

                if p.spring:

                    # Strong upward launch
                    self.vel_y = SPRING_JUMP_VELOCITY

                    # Player is immediately
                    # launched upward.
                    self.on_ground = False

                    # Start recoil animation.
                    self.spring_bounce_until = (
                        pygame.time.get_ticks() + 180
                    )

    def draw(
        self,
        screen,
        cam_y
    ):

        dr = self.rect.move(
            0,
            -int(cam_y)
        )

        # -------------------------
        # Task 3:
        # Small visual recoil
        # -------------------------

        current_time = pygame.time.get_ticks()

        if current_time < self.spring_bounce_until:

            # Slightly squash the player
            # during spring launch.
            bounce_rect = dr.inflate(
                6,
                -4
            )

            bounce_rect.bottom = dr.bottom

            pygame.draw.rect(
                screen,
                self.color,
                bounce_rect,
                border_radius=6
            )

            pygame.draw.circle(
                screen,
                (255, 220, 180),
                (
                    bounce_rect.centerx,
                    bounce_rect.top + 8
                ),
                7
            )

        else:

            pygame.draw.rect(
                screen,
                self.color,
                dr,
                border_radius=6
            )

            pygame.draw.circle(
                screen,
                (255, 220, 180),
                (
                    dr.centerx,
                    dr.top + 8
                ),
                7
            )