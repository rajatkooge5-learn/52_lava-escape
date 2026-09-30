import pygame
import random

PLATFORM_COLOR = (100, 80, 50)
CRUMBLING_PLATFORM_COLOR = (210, 140, 70)
SPRING_PLATFORM_COLOR = (240, 210, 40)

LAVA_COLOR = (220, 60, 20)


class Platform:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        crumbling=False,
        spring=False
    ):
        self.rect = pygame.Rect(
            x,
            y,
            width,
            height
        )

        # Task 2
        self.crumbling = crumbling
        self.crumble_started_at = None

        # Task 3
        self.spring = spring
        self.spring_started_at = None

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    @property
    def top(self):
        return self.rect.top

    @property
    def bottom(self):
        return self.rect.bottom


def generate_platforms(width, base_y, count=30):

    # Ground platform
    # Ground is neither crumbling nor spring.
    plats = [
        Platform(
            0,
            base_y,
            width,
            20,
            crumbling=False,
            spring=False
        )
    ]

    y = base_y - 110

    for i in range(count):

        w = random.randint(80, 200)
        x = random.randint(0, width - w)

        # -------------------------
        # Task 2
        # -------------------------
        is_crumbling = random.random() < 0.25

        # -------------------------
        # Task 3
        # -------------------------
        # About 15% of platforms
        # become spring platforms.
        is_spring = (
            not is_crumbling
            and random.random() < 0.15
        )

        plats.append(
            Platform(
                x,
                y,
                w,
                16,
                crumbling=is_crumbling,
                spring=is_spring
            )
        )

        y -= random.randint(80, 130)

    return plats


def draw_lava(
    screen,
    lava_y,
    cam_y,
    width,
    height,
    frame
):
    import math

    ly = int(lava_y - cam_y)

    if ly < height:

        # Lava surface wave
        pts = [(0, ly)]

        for x in range(0, width + 20, 20):
            pts.append(
                (
                    x,
                    ly + int(
                        math.sin(
                            x * 0.08 + frame * 0.1
                        ) * 8
                    )
                )
            )

        pts.append((width, height))
        pts.append((0, height))

        pygame.draw.polygon(
            screen,
            LAVA_COLOR,
            pts
        )

        # Glow
        s = pygame.Surface(
            (width, 30),
            pygame.SRCALPHA
        )

        for i in range(15):
            pygame.draw.line(
                s,
                (
                    255,
                    100,
                    0,
                    max(0, 60 - i * 4)
                ),
                (0, i),
                (width, i),
                1
            )

        screen.blit(
            s,
            (0, ly - 15)
        )