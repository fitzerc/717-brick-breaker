import pygame


class GameObject:
    def get_height(self):
        pass

    def get_width(self):
        pass

    def get_left_pos(self):
        pass

    def get_top_pos(self):
        pass


class Rectangle(GameObject):
    def __init__(self, width, height, left_position, top_position, color):
        self.surface = pygame.Surface([width, height])
        self.surface.fill(color)
        self.position = (left_position, top_position)

    def get_left_pos(self):
        left, top = self.position
        return left

    def get_top_pos(self):
        left, top = self.position
        return top

    def get_height(self):
        return self.surface.get_height()

    def get_width(self):
        return self.surface.get_width()


class Brick(Rectangle):
    DEFAULT_BRICK_WIDTH = 30
    DEFAULT_BRICK_HEIGHT = 10

    def __init__(self, width, height, left_position, top_position, color):
        Rectangle.__init__(self, width, height, left_position, top_position, color)


class RedBrick(Brick):
    RED = (128, 0, 0)

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
    YELLOW = (255, 215, 0)

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


class Paddle(Rectangle):
    def __init__(
        self,
        width,
        height,
        left_position,
        top_position,
        left_edge_min_x,
        left_edge_max_x,
    ):
        self.left_edge_min_x = left_edge_min_x
        self.left_edge_max_x = left_edge_max_x
        Rectangle.__init__(self, width, height, left_position, top_position, (0, 0, 0))

    def update_position(self, move_by):
        cur_left_pos, cur_top_pos = self.position
        new_left_pos = cur_left_pos + move_by

        if new_left_pos < self.left_edge_min_x:
            new_left_pos = self.left_edge_min_x
        if new_left_pos > self.left_edge_max_x:
            new_left_pos = self.left_edge_max_x

        self.position = (new_left_pos, cur_top_pos)

    def has_collision(self, with_object):
        with_object_right_edge_pos = (
            with_object.get_left_pos() + with_object.get_width()
        )

        with_object_bottom_edge_pos = (
            with_object.get_top_pos() + with_object.get_height()
        )

        paddle_right_edge_pos = self.get_left_pos() + self.get_width()
        paddle_bottom_edge_pos = self.get_top_pos() + self.get_height()

        # ball-x is over paddle-x
        if (
            with_object_right_edge_pos > self.get_left_pos()
            and with_object.get_left_pos() < paddle_right_edge_pos
        ):
            # ball-y is over paddle-y
            if (
                with_object_bottom_edge_pos >= self.get_top_pos()
                and with_object.get_top_pos() < paddle_bottom_edge_pos
            ):
                return True

        return False

    def get_collision_info(self, with_object):
        if with_object.get_left_pos() < self.get_left_pos() + (self.get_width() / 2):
            return "left"
        return "right"


class Ball(GameObject):
    def __init__(
        self,
        center_pos,
        radius,
        color,
        init_x_velocity,
        init_y_velocity,
        parent_dimensions,
    ):
        self.center_pos = center_pos
        self.radius = radius
        self.color = color
        self.x_velocity = init_x_velocity
        self.y_velocity = init_y_velocity
        self.parent_dimensions = parent_dimensions

    def get_height(self):
        return self.radius

    def get_width(self):
        return self.radius

    def get_left_pos(self):
        x, y = self.center_pos
        return x - self.radius

    def get_top_pos(self):
        x, y = self.center_pos
        return y - self.radius

    def update_position(self, dt):
        x_move = dt * self.x_velocity
        y_move = dt * self.y_velocity
        [cur_x, cur_y] = self.center_pos

        new_x = cur_x + x_move
        new_y = cur_y + y_move

        if new_y + (self.radius / 2) >= (self.parent_dimensions[1]):
            # TODO: game over
            self.y_velocity = self.y_velocity * -1
            pass

        if new_y - (self.radius / 2) <= 0:
            # TODO: flip y_velocity
            self.y_velocity = self.y_velocity * -1
            pass

        if (new_x + (self.radius / 2)) >= (self.parent_dimensions[0]) or (
            new_x - (self.radius / 2)
        ) <= 0:
            # TODO: flip x_velocity
            self.x_velocity = self.x_velocity * -1
            pass

        self.center_pos = [cur_x + x_move, cur_y + y_move]
