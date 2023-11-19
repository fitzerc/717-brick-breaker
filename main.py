import pygame
from pygame.locals import *

from game_objects import Ball, Brick, Paddle, RedBrick

WIDTH, HEIGHT = 600, 333
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker!")

SLATE_RGB = (44, 50, 56)
INITIAL_FILL_COLOR = SLATE_RGB

FPS = 60

BALL_RADIUS = 7
WHITE_RGB = (255, 255, 255)
BALL_COLOR = WHITE_RGB
PADDLE_MOVE_SPEED = 3

PADDLE_WIDTH = WIDTH / 4
PADDLE_HEIGHT = PADDLE_WIDTH / 20
PADDLE_TOP_POS = HEIGHT - (PADDLE_HEIGHT * 4)
paddle_left_pos = (WIDTH / 2) - (PADDLE_WIDTH / 2)

paddle_surface = pygame.Surface([PADDLE_WIDTH, PADDLE_HEIGHT])
paddle_surface_pos = (paddle_left_pos, PADDLE_TOP_POS)

paddle = Paddle(
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
    paddle_left_pos,
    PADDLE_TOP_POS,
    0,
    WIDTH - PADDLE_WIDTH,
)


def build_bricks_list(left_start_pos, top_start_pos, bricks_wide, bricks_high):
    row = 1
    brick_list = []
    next_brick_top_pos = top_start_pos
    while row <= bricks_high:
        column = 1

        next_brick_left_pos = left_start_pos
        while column <= bricks_wide:
            brick_list.append(RedBrick(next_brick_left_pos, next_brick_top_pos))
            next_brick_left_pos += Brick.DEFAULT_BRICK_WIDTH + 2
            column += 1

        next_brick_top_pos += Brick.DEFAULT_BRICK_HEIGHT + 2
        row += 1

    return brick_list


def draw_window(paddle, ball, bricks_left):
    WIN.fill(INITIAL_FILL_COLOR)
    WIN.blit(paddle.surface, paddle.position)
    pygame.draw.circle(WIN, ball.color, ball.center_pos, ball.radius)

    for brick in bricks_left:
        WIN.blit(brick.surface, brick.position)

    pygame.display.update()


def calc_left_pos_of_brick_list(bricks_wide, brick_width):
    return (WIDTH - (bricks_wide * (brick_width + 2))) / 2


def detect_collision_update_velocities(paddle, ball):
    (paddle_left_pos, paddle_top_pos) = paddle.position

    if paddle.has_collision(ball):
        ball.y_velocity = ball.y_velocity * -1
        side_impacted = paddle.get_collision_info(ball)

        if side_impacted == "left":
            if ball.x_velocity == 0:
                ball.x_velocity = -0.1
            if ball.x_velocity > 0:
                ball.x_velocity = ball.x_velocity * -1
        else:
            if ball.x_velocity == 0:
                ball.x_velocity = 0.1
            if ball.x_velocity < 0:
                ball.x_velocity = ball.x_velocity * -1


def main(paddle):
    clock = pygame.time.Clock()
    run = True

    bricks_wide = bricks_high = 9
    start_left_pos = calc_left_pos_of_brick_list(bricks_wide, Brick.DEFAULT_BRICK_WIDTH)
    bricks_left = build_bricks_list(start_left_pos, 30, bricks_wide, bricks_high)

    ball = Ball(
        [WIDTH / 2, HEIGHT / 2], BALL_RADIUS, BALL_COLOR, 0, 0.1, [WIDTH, HEIGHT]
    )

    draw_window(paddle, ball, bricks_left)

    move = 0

    while run:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    move -= PADDLE_MOVE_SPEED
                if event.key == K_RIGHT:
                    move += PADDLE_MOVE_SPEED
            if event.type == KEYUP:
                if event.key == K_LEFT and not event.key == K_RIGHT:
                    move = 0
                if event.key == K_RIGHT and not event.key == K_LEFT:
                    move = 0

        paddle.update_position(move)
        ball.update_position(dt)

        if ball.y_velocity > 0:
            detect_collision_update_velocities(paddle, ball)
        draw_window(paddle, ball, bricks_left)

    pygame.quit()


if __name__ == "__main__":
    main(paddle)
