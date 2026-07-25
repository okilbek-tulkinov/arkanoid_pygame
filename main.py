import pygame
import settings as cfg
from game.entities import Ball, Brick, Paddle
from game.level import load_level


def _bounce_off_rect(ball: Ball, rect: pygame.Rect) -> None:
    """Bounce the ball off a rectangle using the smallest overlap axis."""

    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top

    min_overlap = min(overlap_bottom, overlap_left, overlap_right, overlap_top)

    if min_overlap == overlap_top and ball.vy > 0:
        ball.rect.bottom = rect.top
        ball.vy = -abs(ball.vy)
    elif min_overlap == overlap_bottom and ball.vy < 0:
        ball.rect.top = rect.bottom
        ball.vy = abs(ball.vy)
    elif min_overlap == overlap_left and ball.vx > 0:
        ball.rect.right = rect.left
        ball.vx = -abs(ball.vx)
    elif min_overlap == overlap_right and ball.vx < 0:
        ball.rect.left = rect.right
        ball.vx = abs(ball.vx)


def _handle_ball_vs_bricks(ball: Ball, bricks: list[Brick]) -> int:
    scored = 0
    for brick in bricks[:]:
        if not ball.rect.colliderect(brick.rect):
            continue

        _bounce_off_rect(ball, brick.rect)
        if brick.hp == -1:
            continue

        brick.hit()
        if brick.hp <= 0:
            bricks.remove(brick)
            scored += 10

    return scored


def _handle_ball_vs_paddle(ball: Ball, paddle: Paddle) -> None:
    """Handle ball bounce over the paddle."""
    _bounce_off_rect(ball, paddle.rect)
    offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
    max_vx = cfg.MAX_BALL_SPEED_X
    ball.vx = max(-max_vx, min(max_vx, offset * max_vx))


def _handle_ball_vs_walls(ball: Ball) -> bool:
    """Bounce the ball off the walls and stop if it falls below the screen."""
    if ball.rect.left <= cfg.FIELD_LEFT:
        ball.rect.left = cfg.FIELD_LEFT
        ball.vx = abs(ball.vx)
    elif ball.rect.right >= cfg.FIELD_RIGHT:
        ball.rect.right = cfg.FIELD_RIGHT
        ball.vx = -abs(ball.vx)

    if ball.rect.top <= cfg.TOP_OFFSET:
        ball.rect.top = cfg.TOP_OFFSET
        ball.vy = abs(ball.vy)

    if ball.rect.bottom >= cfg.HEIGHT + 20:
        return False

    return True


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Arkanoid")
    clock = pygame.time.Clock()

    running = True
    paddle = Paddle()
    bricks, _, _ = load_level(1)
    ball = Ball(cfg.WIDTH // 2, cfg.HEIGHT - 60)

    while running:
        screen.fill(cfg.BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        if not running:
            break

        keys = pygame.key.get_pressed()
        paddle.move(keys)

        ball.update()
        if not _handle_ball_vs_walls(ball):
            running = False
            break

        _handle_ball_vs_bricks(ball, bricks)
        if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
            _handle_ball_vs_paddle(ball, paddle)

        for brick in bricks:
            brick.draw(screen)

        paddle.draw(screen)
        ball.draw(screen)

        pygame.display.flip()
        clock.tick(cfg.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
