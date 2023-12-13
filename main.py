import pygame
import random
import sys

pygame.init()

scr_width = 800
scr_height = 600


screen = pygame.display.set_mode((scr_width, scr_height))
pygame.display.set_caption("Brick Breaker")

# COLORS IN GAME
bkgrd_color = (200, 200, 200)
ball_color = (50, 40, 255)
paddle_color = (80, 50, 30)
brick_color = [
    (200, 50, 80),  # Red
    (255, 255, 0),  # Yellow
]


class Bricks:
    def __init__(self):
        self.rows = 7
        self.rows_bricks = 9
        self.length = int(scr_width * 0.8) // self.rows_bricks
        self.width = 40
        self.spacing = 4
        self.cordinates = []
        self.brick_list = []

        for i in range(10, self.rows * self.width, self.width):
            for j in range(
                int(scr_width * 0.1),
                int(scr_width * 0.9 - self.length) + 1,
                self.length,
            ):
                brick = None
                if random.choice(
                    [True, False]
                ):  # Randomly choose between RedBrick and YellowBrick
                    brick = RedBrick(j, i)
                else:
                    brick = YellowBrick(j, i)
                self.brick_list.append(brick)

    def show(self):
        for brick in self.brick_list:
            if brick.visible:
                screen.blit(brick.surface, brick.rect.topleft)

    def update(self, cordinate):
        for brick in self.brick_list:
            if brick.has_collision(cordinate):
                brick.handle_collision(cordinate)


class Paddle:
    def __init__(self, paddleX):
        self.paddleX = paddleX
        self.paddleY = int(scr_height * 0.95)
        self.length = 120

    def show(self):
        thickness = 10
        pygame.draw.rect(
            screen,
            paddle_color,
            ((self.paddleX, self.paddleY), (self.length, thickness)),
        )

    def move_left(self):
        self.velocity = 15
        self.paddleX += -self.velocity

    def move_right(self):
        self.velocity = 15
        self.paddleX += self.velocity

    def stop(self):
        self.velocity = 0

    def boundries(self):
        if self.paddleX >= (scr_width - self.length):
            self.paddleX = scr_width - self.length
        elif self.paddleX <= 0:
            self.paddleX = 0


# have to initial here because there is a reference to paddle in Ball object
paddle = Paddle(int(scr_width * 0.45))


class Ball:
    def __init__(self, ballX, ballY):
        self.ballX = ballX
        self.ballY = ballY
        self.x_vel = 8
        self.y_vel = -8
        self.ball_radius = 10
        self.max_x_vel = 10
        self.hit_paddle = False  # Flag to check if the ball has hit the paddle
        self.NEGATIVE_VELOCITY_FLOOR = -3
        self.VELOCITY_FLOOR = 3

    def show(self):
        pygame.draw.circle(
            screen, ball_color, (self.ballX, self.ballY), self.ball_radius
        )

    def move(self):
        self.ballX += self.x_vel
        self.ballY += self.y_vel

    def collision_change(self):
        center = paddle.paddleX + paddle.length // 2
        left_end = paddle.paddleX
        right_end = paddle.paddleX + paddle.length

        if left_end < self.ballX < right_end and not self.hit_paddle:
            self.y_vel = -self.y_vel
            self.hit_paddle = True

            # Adjust the ball's velocity based on the position relative to the paddle center
            if self.ballX < center:
                ratio = (center - self.ballX) / (paddle.length // 2)
                self.x_vel += -self.max_x_vel * ratio
            else:
                ratio = (self.ballX - center) / (paddle.length // 2)
                self.x_vel += self.max_x_vel * ratio

            if self.x_vel < 0 and self.x_vel > self.NEGATIVE_VELOCITY_FLOOR:
                self.x_vel = self.NEGATIVE_VELOCITY_FLOOR
            elif self.x_vel > 0 and self.x_vel < self.VELOCITY_FLOOR:
                self.x_vel = self.VELOCITY_FLOOR

            self.hit_paddle = False

    def brick_collision_change(self, brick):
        brick_center_x = brick.rect.left + brick.rect.width // 2
        brick_center_y = brick.rect.top + brick.rect.height // 2

        # Calculate the direction vector from the ball to the center of the brick
        dir_x = brick_center_x - self.ballX
        dir_y = brick_center_y - self.ballY

        # Calculate the distance between the ball and the center of the brick
        distance = (dir_x**2 + dir_y**2) ** 0.5

        # Normalize the direction vector
        if distance != 0:
            dir_x /= distance
            dir_y /= distance

        # Adjust the ball's velocity based on the normalized direction vector
        self.x_vel = -self.max_x_vel * dir_x
        self.y_vel = -self.max_x_vel * dir_y

    def boundries(self):
        if self.ballY <= (0 + self.ball_radius):
            self.y_vel = -self.y_vel
        if self.ballX <= (0 + self.ball_radius):
            self.x_vel = -self.x_vel
        if self.ballX >= (scr_width - self.ball_radius):
            self.x_vel = -self.x_vel

    def limit_vel(self):
        if -self.max_x_vel > self.x_vel:
            self.x_vel = -self.max_x_vel
        elif self.x_vel > self.max_x_vel:
            self.x_vel = self.max_x_vel


class Brick(pygame.sprite.Sprite):
    DEFAULT_BRICK_WIDTH = 40
    DEFAULT_BRICK_HEIGHT = 20

    def __init__(self, width, height, left_position, top_position, color):
        pygame.sprite.Sprite.__init__(self)
        self.surface = pygame.Surface((width, height))
        self.surface.fill(color)
        self.rect = self.surface.get_rect(topleft=(left_position, top_position))
        self.visible = True
        self.original_color = color
        self.hit_points = 2 if color == YellowBrick.YELLOW else 1
        self.changed_color = False  # Added attribute to track color change
        self.invisible_after_hit = (
            False  # Added attribute to track invisibility after the second hit
        )
        self.hit_count = 0  # New attribute to track hits

    def has_collision(self, with_object):
        with_object_right_edge_pos = with_object.ballX + with_object.ball_radius

        with_object_bottom_edge_pos = with_object.ballY + with_object.ball_radius

        brick_right_edge_pos = self.rect.left + self.rect.width
        brick_bottom_edge_pos = self.rect.top + self.rect.height

        # ball-x is over brick-x
        if (
            with_object_right_edge_pos > self.rect.left
            and with_object.ballX < brick_right_edge_pos
        ):
            # ball-y is over brick-y
            if (
                with_object_bottom_edge_pos >= self.rect.top
                and with_object.ballY < brick_bottom_edge_pos
            ):
                return True

        return False

    def handle_collision(self, with_object):
        if self.visible:
            if self.original_color == YellowBrick.YELLOW and not self.changed_color:
                # Change color to red after the first hit for yellow bricks
                self.surface.fill(RedBrick.RED)
                self.changed_color = True
            else:
                # Decrement hit points for red bricks or yellow bricks that have already changed color
                self.hit_points -= 1

                if self.hit_points <= 0:
                    if (
                        self.original_color == YellowBrick.YELLOW
                        and not self.invisible_after_hit
                    ):
                        # Set the brick to be invisible after the second hit for yellow bricks
                        self.invisible_after_hit = True
                    else:
                        # Set visibility to False for subsequent hits
                        self.visible = False
                        global score
                        score += 1

            # Adjust the ball's velocity after hitting a brick
            with_object.brick_collision_change(self)


class RedBrick(Brick):
    RED = (200, 50, 80)

    def __init__(self, left_position, top_position):
        self.hit_points = 1
        Brick.__init__(
            self,
            Brick.DEFAULT_BRICK_WIDTH,
            Brick.DEFAULT_BRICK_HEIGHT,
            left_position,
            top_position,
            RedBrick.RED,
        )


class YellowBrick(Brick):
    YELLOW = (255, 255, 0)
    RED = (200, 50, 80)

    def __init__(self, left_position, top_position):
        self.hit_points = 2
        Brick.__init__(
            self,
            Brick.DEFAULT_BRICK_WIDTH,
            Brick.DEFAULT_BRICK_HEIGHT,
            left_position,
            top_position,
            YellowBrick.YELLOW,
        )


def brick_collision(brick_list, brick_breaked, ball):
    for brick in brick_list:
        if brick.has_collision(ball):
            brick.handle_collision(ball)
            brick_breaked.append(ball)


score = 0
lives = 3
clock = pygame.time.Clock()
ball = Ball(int(scr_width / 2), int(scr_height * 0.8))
brick = Bricks()
brick_list = brick.brick_list

while True:
    # paddle movement switches
    key_left = False
    key_right = False

    while True:
        # initial positions
        brick_breaked = []
        over = False
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    key_left = True
                if event.key == pygame.K_RIGHT:
                    key_right = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    paddle.stop()
                    key_left = False
                if event.key == pygame.K_RIGHT:
                    paddle.stop()
                    key_right = False

        # GAME LOGIC
        def show_gameover():
            global scr_width, scr_height, screen
            text = pygame.font.Font("freesansbold.ttf", int(scr_height * 0.1))
            gameover = text.render("GAME OVER", True, (255, 23, 20))
            screen.blit(gameover, (int(scr_width * 0.25), int(scr_height * 0.4)))
            pygame.display.flip()  # Update the display after rendering the game over message
            pygame.time.delay(3000)  # Pause for 3 seconds before restarting

        # paddle movement switches
        if key_left:
            paddle.move_left()
        if key_right:
            paddle.move_right()

        # ball mechanics
        ball.move()
        ball.boundries()
        ball.limit_vel()

        if (
            paddle.paddleY + 10 > ball.ballY + ball.ball_radius > paddle.paddleY
            and paddle.paddleX < ball.ballX < paddle.paddleX + paddle.length
        ):
            ball.collision_change()

        # brick collision
        brick_collision(brick_list, brick_breaked, ball)

        # paddle boundaries
        paddle.boundries()

        # Deduct life if ball falls off the paddle
        if ball.ballY > scr_height:
            lives -= 1
            if lives == 0:
                show_gameover()
                over = True
                # Reset points and lives
                score = 0
                lives = 3
                brick = Bricks()
            else:
                # Reset ball and paddle position
                ball = Ball(int(scr_width / 2), int(scr_height * 0.8))
                paddle = Paddle(int(scr_width * 0.45))

        # Display things
        screen.fill(bkgrd_color)
        paddle.show()
        brick.show()
        for brk in brick_breaked:
            brick.update(brk)
        ball.show()

        # Display score and lives

        # Display score and lives
        font = pygame.font.Font("freesansbold.ttf", 20)
        score_text = font.render("Score: " + str(score), True, (0, 0, 0))
        lives_text = font.render("Lives: " + str(lives), True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (scr_width - 80, 10))

        pygame.display.update()

        if over:
            break
            pygame.quit()

    pygame.display.update()
