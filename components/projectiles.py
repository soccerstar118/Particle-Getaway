from random import uniform

import pygame.math
import pygame.draw
import math

# self made inputs
from components.calculations import *  # calculations file
from components.player_class import Player  # player file
from components.config import *  # initial information
from abc import ABC, abstractmethod

screen: pygame.surface.Surface = None
player: Player = None


# this is used to get the variables from the main file to be used inside here
def globals_initializer(global_screen, global_player) -> None:
    global screen, player
    screen = global_screen
    player = global_player


# used for glow effect on projectiles
def circle_surf(radius, color, border_length=0):
    surf = pygame.Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius, border_length)
    # surf.set_colorkey((0, 0, 0))
    return surf


def polygon_surf(points: list[pygame.math.Vector2] | list[tuple[float, float]] | list[list[float, float]], radius,
                 color,
                 border_length=0):
    surf = pygame.Surface((radius * 2, radius * 2))
    pygame.draw.polygon(surf, color, points, border_length)
    return surf


class ColorRainbow:
    def __init__(self, start_RGB: list[float] = None, min_RGB: list[float] = None, max_RGB: list[float] = None,
                 min_change_RGB: list[float] = None, max_change_RGB: list[float] = None,
                 speed_to_bring_to_bounds_RGB: list[float] = None):
        self.min_RGB = min_RGB
        self.max_RGB = max_RGB
        self.min_change_RGB = min_change_RGB
        self.max_change_RGB = max_change_RGB
        self.speed_to_bring_to_bounds_RGB = speed_to_bring_to_bounds_RGB
        self.instantly_bring_RGB_into_bounds = False

        self.current_RGB = start_RGB
        if self.current_RGB is None:
            self.current_RGB = [255, 255, 255]
        if self.min_RGB is None:
            self.min_RGB = [0, 0, 0]
        if self.max_RGB is None:
            self.max_RGB = [255, 255, 255]
        if self.min_change_RGB is None:
            self.min_change_RGB = [0, 0, 0]
        if self.max_change_RGB is None:
            self.max_change_RGB = [0, 0, 0]
        if self.speed_to_bring_to_bounds_RGB is None:
            self.speed_to_bring_to_bounds_RGB = [0, 0, 0]
            self.instantly_bring_RGB_into_bounds = True
        if len(self.min_RGB) == 1:
            self.min_RGB *= 3
        if len(self.max_RGB) == 1:
            self.max_RGB *= 3
        if len(self.min_change_RGB) == 1:
            self.min_change_RGB *= 3
        if len(self.max_change_RGB) == 1:
            self.max_change_RGB *= 3
        if len(self.speed_to_bring_to_bounds_RGB) == 1:
            self.speed_to_bring_to_bounds_RGB *= 3

        self.current_change = [uniform(self.min_change_RGB[i], self.max_change_RGB[i]) for i in range(3)]

    def get_new_color(self, continue_changing_RGB=True) -> list[float]:
        if continue_changing_RGB:
            for i in range(3):
                self.current_RGB[i] += self.current_change[i]
                if self.current_RGB[i] < self.min_RGB[i]:
                    self.current_change[i] = uniform(self.min_change_RGB[i], self.max_change_RGB[i])
                    self.current_RGB[i] += abs(self.speed_to_bring_to_bounds_RGB[i])
                elif self.current_RGB[i] > self.max_RGB[i]:
                    self.current_change[i] = -uniform(self.min_change_RGB[i], self.max_change_RGB[i])
                    self.current_RGB[i] -= abs(self.speed_to_bring_to_bounds_RGB[i])

                self.current_RGB[i] = within_bounds(0, self.current_RGB[i], 255)
                if self.instantly_bring_RGB_into_bounds:
                    self.current_RGB[i] = within_bounds(self.min_RGB[i], self.current_RGB[i], self.max_RGB[i])
        return self.current_RGB.copy()


class Movement(ABC):
    pos: pygame.math.Vector2
    vel: pygame.math.Vector2

    @abstractmethod
    def move(self) -> None:
        pass

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y

    @x.setter
    def x(self, num):
        self.pos.x = num

    @y.setter
    def y(self, num):
        self.pos.y = num


class MovementStandard(Movement):
    """ Standard Movement System for Projectiles (polynomial movement)"""

    def __init__(self, x, y, vel_x: float = 0, vel_y: float = 0, acc_x: float = 0,
                 acc_y: float = 0, jer_x: float = 0, jer_y: float = 0, unn_x: float = 0,
                 unn_y: float = 0):
        self.pos = pygame.math.Vector2((x, y))

        self.vel = pygame.math.Vector2(vel_x, vel_y)
        self.acc = pygame.math.Vector2(acc_x, acc_y)
        self.jer = pygame.math.Vector2(jer_x, jer_y)
        self.unn = pygame.math.Vector2(unn_x, unn_y)

    def move(self) -> None:
        self.pos += self.vel
        self.vel += self.acc
        self.acc += self.jer
        self.jer += self.unn

    @classmethod
    def from_polar(cls, x, y, vel_amount: float = 0, vel_angle: float = 0, acc_amount: float = 0,
                   acc_angle: float = 0, jer_amount: float = 0, jer_angle: float = 0,
                   unn_amount: float = 0, unn_angle: float = 0):
        """all angles must be in radians """
        return cls(x, y, math.cos(vel_angle) * vel_amount, math.sin(vel_angle) * vel_amount,
                   math.cos(acc_angle) * acc_amount, math.sin(acc_angle) * acc_amount,
                   math.cos(jer_angle) * jer_amount, math.sin(jer_angle) * jer_amount,
                   math.cos(unn_angle) * unn_amount, math.sin(unn_angle) * unn_amount)


class MovementRotate(Movement):
    """ A movement system involving rotating about a center position """

    def __init__(self, x, y,
                 center_to_rotate_around: pygame.math.Vector2 | list[float] | tuple[float],
                 angle_incr, dist_incr: float = 0, *, angle_incr_incr: float = 0, dist_incr_incr: float = 0):
        """ all angles must be in radians """

        self.pos = pygame.math.Vector2(x, y)

        self.past_pos = pygame.math.Vector2(self.pos)  # used to determine velocity

        if isinstance(center_to_rotate_around, list | tuple):
            self.center_to_rotate_around = pygame.math.Vector2(center_to_rotate_around)
        elif isinstance(center_to_rotate_around, pygame.math.Vector2):
            self.center_to_rotate_around = center_to_rotate_around
        else:
            raise Exception

        self.angle = math.atan2(self.pos.y - self.center_to_rotate_around.y,
                                self.pos.x - self.center_to_rotate_around.x)
        self.dist = math.dist(self.pos, self.center_to_rotate_around)

        self.angle_incr = angle_incr
        self.dist_incr = dist_incr

        self.angle_incr_incr = angle_incr_incr
        self.dist_incr_incr = dist_incr_incr

    def move(self) -> None:
        self.angle += self.angle_incr
        self.dist += self.dist_incr

        self.angle_incr += self.angle_incr_incr
        self.dist_incr += self.dist_incr_incr

        # finding vector around the center, and then adding center to it for position
        self.pos.from_polar((self.dist, math.degrees(self.angle)))
        self.past_pos = self.pos.copy()
        self.pos += self.center_to_rotate_around

    @classmethod
    def from_center(cls, dist_from_center, angle_from_center,
                    center_to_rotate_around: pygame.math.Vector2 | list[float] | tuple[float],
                    angle_incr, dist_incr: float = 0, *, angle_incr_incr: float = 0,
                    dist_incr_incr: float = 0):
        """ all angles must be in radians """
        if isinstance(center_to_rotate_around, list | float):
            return cls(center_to_rotate_around[0] + math.cos(angle_from_center) * dist_from_center,
                       center_to_rotate_around[1] + math.sin(angle_from_center) * dist_from_center,
                       center_to_rotate_around, angle_incr, dist_incr,
                       angle_incr_incr=angle_incr_incr, dist_incr_incr=dist_incr_incr)
        elif isinstance(center_to_rotate_around, pygame.math.Vector2):
            return cls(center_to_rotate_around.x + math.cos(angle_from_center) * dist_from_center,
                       center_to_rotate_around.y + math.sin(angle_from_center) * dist_from_center,
                       center_to_rotate_around, angle_incr, dist_incr,
                       angle_incr_incr=angle_incr_incr, dist_incr_incr=dist_incr_incr)
        else:
            raise Exception

    @property
    def vel(self):
        return self.pos - self.past_pos

    # Note: Fix the incredibly slow way drawing transparent surfaces is currently being done with the increasing radius


class Shape(ABC):
    radius: float
    color: list[float]

    @abstractmethod
    def draw(self, pos: pygame.Vector2) -> None:
        pass

    @abstractmethod
    def collide(self, own_pos, pos: pygame.math.Vector2, radius: float) -> bool:
        pass


class ShapeCircle(Shape):
    """Only use this to create Projectiles"""

    def __init__(self, radius, color, *,
                 radius_incr=0, radius_max=float('inf'), radius_min=-1, border_length=0, should_glow=True,
                 pulsate_mult=1.6, border_glow_func: callable = None):
        self.radius = radius
        self.color = color

        # Changes the radius so that the projectile can increase/decrease in size during lifetime
        self.radius_incr = radius_incr
        self.radius_max = radius_max
        self.radius_min = radius_min

        self.border_length = border_length

        self.should_glow = should_glow
        self.pulsate_mult = pulsate_mult
        self.current_pulsate_mult = pulsate_mult
        self.pulsate_mult_add_subtract = -1
        if self.should_glow:
            if border_glow_func is None:
                border_glow_func = col_mult_half
            self.circle_glow = border_glow_func(self.color)

    def draw(self, movement: Movement) -> None:
        pos = movement.pos
        """takes an input position since the actual position is contained inside the Movement classes"""

        # draws an intermediary screen first so that transparency can be rendered
        if self.should_glow:
            pygame.draw.circle(screen, self.color, movement.pos, self.radius, self.border_length)

            self.current_pulsate_mult += self.pulsate_mult / 300 * self.pulsate_mult_add_subtract
            if self.current_pulsate_mult > self.pulsate_mult:
                self.pulsate_mult_add_subtract = -1
            elif self.current_pulsate_mult < 0.5 + self.pulsate_mult / 2:
                self.pulsate_mult_add_subtract = 1
            screen.blit(circle_surf(self.radius * self.current_pulsate_mult, self.circle_glow, self.border_length),
                        (pos.x - self.radius - (self.current_pulsate_mult - 1) * self.radius,
                         pos.y - self.radius - (self.current_pulsate_mult - 1) * self.radius),
                        special_flags=pygame.BLEND_RGB_ADD)
        elif len(self.color) == 4:
            screen_mid = pygame.surface.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(screen_mid, self.color, (self.radius, self.radius), self.radius, self.border_length)
            screen.blit(screen_mid, (pos.x - self.radius, pos.y - self.radius))
        else:
            pygame.draw.circle(screen, self.color, pos, self.radius, self.border_length)

        self.radius += self.radius_incr
        # resets radius back to the radius max or min if necessary
        if self.radius > self.radius_max:
            self.radius = self.radius_max
        elif self.radius < self.radius_min:
            self.radius = self.radius_min

    def collide(self, own_pos, pos: pygame.math.Vector2, radius: float) -> bool:
        if (own_pos.x - pos.x) ** 2 + (own_pos.y - pos.y) ** 2 < (self.radius + radius - 2) ** 2:
            return True
        return False


# very inefficient try not to use and also maybe bad collision detection, and not fully drawn
class ShapeCircleBright(Shape):
    """Only use this to create Projectiles"""

    def __init__(self, radius, color, border_glow_func: callable = None):
        """pulsate_mult only does things when full_glow is True"""
        self.radius = radius
        self.color = [color[i] for i in range(3)]

        self.surf_arr: list[pygame.Surface] = [None] * 21

        circle_avg = max(self.color) + 10

        if border_glow_func is None:
            temp_circle_glow = [(20 * (self.color[0] + 10)) // circle_avg + 1,
                                (20 * (self.color[1]) + 10) // circle_avg + 1,
                                (20 * (self.color[2]) + 10) // circle_avg + 1]
        else:
            temp_circle_glow = border_glow_func(self.color)
        self.surf_arr[0] = circle_surf(self.radius, temp_circle_glow)
        temp_circle_radius = self.radius

        for i in range(1, 21):
            temp_circle_radius += 0.5
            for j in range(3):
                if temp_circle_glow[j] >= 1:
                    temp_circle_glow[j] -= 1
            self.surf_arr[i] = circle_surf(temp_circle_radius, temp_circle_glow)

    def draw(self, movement: Movement) -> None:
        pos = movement.pos
        """takes an input position since the actual position is contained inside the Movement classes"""
        for surf in self.surf_arr:
            screen.blit(surf, (pos.x - surf.get_width() / 2, pos.y - surf.get_width() / 2),
                        special_flags=pygame.BLEND_RGB_ADD)

    def collide(self, own_pos, pos: pygame.math.Vector2, radius: float) -> bool:
        if (own_pos.x - pos.x) ** 2 + (own_pos.y - pos.y) ** 2 < (self.radius + radius - 2) ** 2:
            return True
        return False


class ShapePolygon2OldDoNotUseAgain(Shape):
    """Only use this to create Projectiles"""

    points: list[pygame.math.Vector2]

    def __init__(self, radius, color, side_num, rotate_incr=0, *,
                 radius_incr=0, radius_max=float('inf'), radius_min=-1, fast_collision=False, border_length=0,
                 should_glow=False, pulsate_mult=1.6, border_glow_func: callable = None):
        self.radius = radius

        self.inradius = self.radius * math.cos(math.pi / side_num)  # max dist from center without exceeding polygon

        self.color = color
        self.side_num = side_num
        self.rotate_incr = rotate_incr

        # keyword only inputs due to how rarely they are used
        self.radius_incr = radius_incr
        self.radius_max = radius_max
        self.radius_min = radius_min

        # if fast_collision is True it only does inradius circle collision, no line collision
        self.fast_collision = fast_collision

        # creates list of points which are the polygon represented around the unit circle
        self.points = [None] * side_num
        for i in range(side_num):
            self.points[i] = pygame.math.Vector2(0, 0)
            self.points[i].from_polar((1, i * 360 / side_num))

        self.border_length = border_length

        self.should_glow = should_glow
        self.pulsate_mult = pulsate_mult
        self.current_pulsate_mult = pulsate_mult
        self.pulsate_mult_add_subtract = -1
        if self.should_glow:
            if border_glow_func is None:
                self.circle_glow = col_mult_half(self.color)
            else:
                self.circle_glow = border_glow_func(self.color)

    def draw(self, pos: pygame.Vector2) -> None:
        """has to take an input for the position since the position is managed inside the movement classes"""
        for i in range(self.side_num):  # rotates the points
            self.points[i] = self.points[i].rotate_rad(self.rotate_incr)  # Rotate points around unit circle

        # draws an intermediary screen first so that transparency can be rendered
        if self.should_glow:
            temp_points = [(point.x * self.radius + pos.x, point.y * self.radius + pos.y) for point in self.points]
            pygame.draw.polygon(screen, self.color, temp_points, self.border_length)

            self.current_pulsate_mult += self.pulsate_mult / 300 * self.pulsate_mult_add_subtract
            if self.current_pulsate_mult > self.pulsate_mult:
                self.pulsate_mult_add_subtract = -1
            elif self.current_pulsate_mult < 0.5 + self.pulsate_mult / 2:
                self.pulsate_mult_add_subtract = 1

            temp_radius = self.radius * self.current_pulsate_mult
            temp_points = [((point.x + 1) * temp_radius, (point.y + 1) * temp_radius) for point in self.points]
            screen.blit(polygon_surf(temp_points, temp_radius, self.circle_glow, self.border_length),
                        (pos.x - temp_radius,
                         pos.y - temp_radius),
                        special_flags=pygame.BLEND_RGB_ADD)
        elif len(self.color) == 4:
            # creates list of points of what the actual shape is
            temp_points = [((1 + point.x) * self.radius, (1 + point.y) * self.radius) for point in self.points]

            screen_mid = pygame.surface.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.polygon(screen_mid, self.color, temp_points, self.border_length)
            screen.blit(screen_mid, (pos.x - self.radius, pos.y - self.radius))
        else:  # draws normally if no alpha value specified
            temp_points = [(point.x * self.radius + pos.x, point.y * self.radius + pos.y) for point in self.points]
            pygame.draw.polygon(screen, self.color, temp_points, self.border_length)

        self.radius += self.radius_incr
        # resets radius back to the radius max or min if necessary
        if self.radius > self.radius_max:
            self.radius = self.radius_max
        elif self.radius < self.radius_min:
            self.radius = self.radius_min

        self.inradius = self.radius * math.cos(math.pi / self.side_num)

    def collide(self, own_pos, pos: pygame.math.Vector2, radius: float) -> bool:
        if (own_pos.x - pos.x) ** 2 + (own_pos.y - pos.y) ** 2 < (self.inradius + radius - 2) ** 2:
            return True  # return True if within inradius

        if not self.fast_collision:
            # return True if one of lines collides w circle
            for i in range(self.side_num):
                if dist_line_point(self.points[i].x * self.radius + own_pos.x,
                                   self.points[i].y * self.radius + own_pos.y,
                                   self.points[(i + 1) % self.side_num].x * self.radius + own_pos.x,
                                   self.points[(i + 1) % self.side_num].y * self.radius + own_pos.y,
                                   pos.x, pos.y) < radius - 5:
                    return True
        return False


class ShapePolygon(Shape):
    """Only use this to create Projectiles"""

    points: list[pygame.math.Vector2]

    def __init__(self, radius, color, side_num, rotate_incr=0, *,
                 start_point_angle=0, radius_incr=0, radius_max=float('inf'), radius_min=-1, fast_collision=False,
                 border_length=0, should_glow=False, pulsate_mult=1.6, border_length_glow=0,
                 border_glow_func: callable = None, point_at_vel=False):
        self.radius = radius

        self.inradius = self.radius * math.cos(math.pi / side_num)  # max dist from center without exceeding polygon

        self.color = color
        self.side_num = side_num
        self.rotate_incr = rotate_incr

        # keyword only inputs due to how rarely they are used
        self.radius_incr = radius_incr
        self.radius_max = radius_max
        self.radius_min = radius_min

        # if fast_collision is True it only does inradius circle collision, no line collision
        self.fast_collision = fast_collision

        self.angle = start_point_angle
        self.point_at_vel = point_at_vel
        self.points = [None] * side_num
        for i in range(side_num):
            self.points[i] = pygame.math.Vector2(0, 0)
            self.points[i].from_polar((1, i * 360 / side_num))

        self.border_length = border_length

        self.should_glow = should_glow
        self.pulsate_mult = pulsate_mult
        self.current_pulsate_mult = pulsate_mult
        self.pulsate_mult_add_subtract = -1
        self.border_length_glow = border_length_glow
        if self.should_glow:
            if border_glow_func is None:
                self.circle_glow = col_mult_half(self.color)
            else:
                self.circle_glow = border_glow_func(self.color)

    def draw(self, movement: Movement) -> None:
        pos = movement.pos
        """has to take an input for the position since the position is managed inside the movement classes"""
        temp_angle_change = self.angle
        self.angle += self.rotate_incr
        if self.point_at_vel:
            self.angle = math.atan2(movement.vel.y, movement.vel.x)
        temp_angle_change = self.angle - temp_angle_change

        for i in range(self.side_num):  # rotates the points
            self.points[i] = self.points[i].rotate_rad(temp_angle_change)  # Rotate points around unit circle

        # draws an intermediary screen first so that transparency can be rendered
        if self.should_glow:
            temp_points = [(point.x * self.radius + pos.x, point.y * self.radius + pos.y) for point in self.points]
            pygame.draw.polygon(screen, self.color, temp_points, self.border_length)

            self.current_pulsate_mult += self.pulsate_mult / 300 * self.pulsate_mult_add_subtract
            if self.current_pulsate_mult > self.pulsate_mult:
                self.pulsate_mult_add_subtract = -1
            elif self.current_pulsate_mult < 0.5 + self.pulsate_mult / 2:
                self.pulsate_mult_add_subtract = 1

            temp_radius = self.radius * self.current_pulsate_mult
            temp_points = [((point.x + 1) * temp_radius, (point.y + 1) * temp_radius) for point in self.points]
            screen.blit(polygon_surf(temp_points, temp_radius, self.circle_glow, self.border_length_glow),
                        (pos.x - temp_radius,
                         pos.y - temp_radius),
                        special_flags=pygame.BLEND_RGB_ADD)
        elif len(self.color) == 4:
            # creates list of points of what the actual shape is
            temp_points = [((1 + point.x) * self.radius, (1 + point.y) * self.radius) for point in self.points]

            screen_mid = pygame.surface.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.polygon(screen_mid, self.color, temp_points, self.border_length)
            screen.blit(screen_mid, (pos.x - self.radius, pos.y - self.radius))
        else:  # draws normally if no alpha value specified
            temp_points = [(point.x * self.radius + pos.x, point.y * self.radius + pos.y) for point in self.points]
            pygame.draw.polygon(screen, self.color, temp_points, self.border_length)

        self.radius += self.radius_incr
        # resets radius back to the radius max or min if necessary
        if self.radius > self.radius_max:
            self.radius = self.radius_max
        elif self.radius < self.radius_min:
            self.radius = self.radius_min

        self.inradius = self.radius * math.cos(math.pi / self.side_num)

    def collide(self, own_pos, pos: pygame.Vector2, radius: float) -> bool:
        if (own_pos.x - pos.x) ** 2 + (own_pos.y - pos.y) ** 2 < (self.inradius + radius - 2) ** 2:
            return True  # return True if within inradius

        if not self.fast_collision:
            # return True if one of lines collides w circle
            for i in range(self.side_num):
                if dist_line_point(self.points[i].x * self.radius + own_pos.x,
                                   self.points[i].y * self.radius + own_pos.y,
                                   self.points[(i + 1) % self.side_num].x * self.radius + own_pos.x,
                                   self.points[(i + 1) % self.side_num].y * self.radius + own_pos.y,
                                   pos.x, pos.y) < radius - 5:
                    return True
        return False


# remember to separate the bouncing functionality to a different class later on
class Projectile:
    def __init__(self, movement: Movement, shape: ShapeCircle | ShapePolygon, *,
                 min_x=0, min_y=0, max_x=width, max_y=height, bounce_back=False):
        self.movement = movement
        self.shape = shape

        # these values determine where the projectile will be destroyed
        # assigned to screen borders by default
        self.min_x = min_x
        self.min_y = min_y

        self.max_x = max_x
        self.max_y = max_y

        # makes projectile bounce back once hitting boundaries if not deleting at boundary
        # separate this into a different inherited class later on
        self.bounce_back = bounce_back

    @property
    def pos(self):
        return self.movement.pos

    @pos.setter
    def pos(self, num):
        self.movement.pos = num

    @property
    def radius(self):
        return self.shape.radius

    @radius.setter
    def radius(self, num):
        self.shape.radius = num

    # rework bouncing functionality into different inherited projectile class later
    def move(self) -> None:
        self.movement.move()

        if self.bounce_back:
            if self.pos.x - self.radius < self.min_x:
                # self.pos.x = self.min_x
                self.movement.vel.x = abs(self.movement.vel.x)
            if self.pos.x + self.radius > self.max_x:
                # self.pos.x = self.max_x
                self.movement.vel.x = -abs(self.movement.vel.x)
            if self.pos.y - self.radius < self.min_y:
                # self.pos.x = self.min_y
                self.movement.vel.y = abs(self.movement.vel.y)
            if self.pos.y + self.radius > self.max_y:
                # self.pos.x = self.max_y
                self.movement.vel.y = -abs(self.movement.vel.y)

    def draw(self) -> None:
        self.shape.draw(self.movement)

    def collide(self, pos_to_collide: pygame.math.Vector2 = None, pos_to_collide_radius: float = None) -> bool:
        if pos_to_collide is None:  # defaults to None indicating to collide w player
            return self.shape.collide(self.pos, player.pos, player.radius)
        else:
            return self.shape.collide(self.pos, pos_to_collide, pos_to_collide_radius)

    def update(self) -> None:
        self.draw()
        self.move()

    # function to test to destroy projectile based on out of bounds
    def destroy(self, check_min_x=True, check_max_x=True, check_min_y=True, check_max_y=True) -> bool:

        # option to only check certain parts of collision in parameters
        if check_min_x:
            if self.pos.x + self.radius < self.min_x:
                return True
        if check_max_x:
            if self.pos.x - self.radius > self.max_x:
                return True
        if check_min_y:
            if self.pos.y + self.radius < self.min_y:
                return True
        if check_max_y:
            if self.pos.y - self.radius > self.max_y:
                return True

        return False


class ProjectileList:
    """Should be used to keep track of at least several projectiles"""

    def __init__(self):
        self.projectile_list: list[Projectile] = []

    def __len__(self):
        return len(self.projectile_list)

    def add_projectile(self, proj: Projectile) -> None:
        """adds a projectile onto the projectile list"""
        self.projectile_list.append(proj)

    def has_projectiles(self) -> bool:
        """
        :return: True if there are any projectiles inside the object (useful for ending an attack
        once all projectiles are gone)
        """
        return len(self.projectile_list) > 0

    def list_update(self, should_collide=True, thing_to_collide: Player | Projectile = None,
                    delete_proj_after_colliding=False) -> None:
        """
        :param should_collide: the Projectiles collide with thing_to_collide if True
        :param thing_to_collide: If not initialized defaults to colliding with the player
        :param delete_proj_after_colliding: if True then deletes the projectile after colliding, set to False by default
        """

        if should_collide:
            if thing_to_collide is None:
                thing_to_collide = player

            # does collision checking based on making player lose health if the thing to collide is player
            # and also deleting the projectile after colliding if set to True
            for proj in self.projectile_list:
                if proj.collide(thing_to_collide.pos, thing_to_collide.radius):
                    if thing_to_collide is player:
                        player.lose_health()
                    if delete_proj_after_colliding:
                        # overrides the destroy function to return True always so that it gets deleted
                        proj.destroy = lambda: True

        # update all the projectiles
        for proj in self.projectile_list:
            proj.update()

        self.projectile_list = [proj for proj in self.projectile_list if not proj.destroy()]
