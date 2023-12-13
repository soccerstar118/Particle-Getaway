import random

import pygame
import math
from sys import exit
import sys
from random import randint, choice
from pygame.locals import *
from typing import List, Set, Tuple, Dict, Union

SET_THIS_VARIABLE_TO_FALSE = False
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True
# SET_THIS_VARIABLE_TO_FALSE = True

pygame.init()
width = 889  # originally 800
height = 500

true_screen_width, true_screen_height = pygame.display.get_desktop_sizes()[0]
true_screen = pygame.display.set_mode((true_screen_width, true_screen_height))

# game works on same size for everyone essentially and is just scaled up for actual displaying
screen = pygame.Surface((width, height))
screen_scale_factor = min(true_screen_width / width, true_screen_height / height)

# don't use these values when coding other things - just for scaling the game surface up to display
screen_scaled_width = int(width * screen_scale_factor)
screen_scaled_height = int(height * screen_scale_factor)
screen_scaled = pygame.Surface((screen_scaled_width, screen_scaled_height))
screen_scaled_position_blit = ((true_screen_width - width * screen_scale_factor) / 2,
                               (true_screen_height - height * screen_scale_factor) / 2)

clock = pygame.time.Clock()  # use frame rate rather than precise time - only use this for setting frame rate
clock_frame_rate = 60  # change this to affect the frames per second - this will mess up almost all aspects of the game


# just updates the pygame screen, keeps the framerate, etc.
def update_pygame():
    pygame.display.update()  # update screen
    clock.tick(clock_frame_rate)  # delays time

    # scales, and transforms the game screen onto true screen
    pygame.transform.scale(screen, (screen_scaled_width, screen_scaled_height), screen_scaled)
    true_screen.blit(screen_scaled, screen_scaled_position_blit)


pygame.display.set_caption('Particle Getaway')
background_color = (0, 0, 10)
screen.fill(background_color)


def circle_surf(radius, color):
    surf = pygame.Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((255, 255, 255))  # used to be (0,0,255)
    return surf


# name is XY since its literally just used to keep track of x and y values for movement, position, etc.
# (Having 2 seperate variables or 1 array with len 2 seemed worse)
class XY:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def square_val(self):
        return self.x ** 2 + self.y ** 2

    def sqrt_val(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)


CENTER_POINT = XY(width // 2, height // 2)


class Movement:

    def __init__(self, x, y):
        self.pos = XY(x, y)  # used for pos
        self.movement = None

    def move(self):
        self.movement.update()

    # all functions starting with d_ are used to change movement type

    def d_standard(self, vel_x, vel_y, acc_x, acc_y):
        self.movement = self.Standard(self.pos, vel_x, vel_y, acc_x, acc_y)

    def d_to_pos(self, pos_x, pos_y, vel_num, acc_num=0, angle_add=0):
        temp_angle = math.atan2(pos_y - self.pos.y, pos_x - self.pos.x) + angle_add
        temp_change_x, temp_change_y = math.cos(temp_angle), math.sin(temp_angle)
        self.movement = self.Standard(self.pos, temp_change_x * vel_num, temp_change_y * vel_num,
                                      temp_change_x * acc_num, temp_change_y * acc_num)

    def d_to_player(self, vel_num, acc_num=0, angle_add=0):
        self.d_to_pos(player.pos[0], player.pos[1], vel_num, acc_num, angle_add)

    def d_hover(self, acc_num, time_wait, dist_hover, speed_cap, hover_num, pos_follow=None):
        self.movement = self.Hover(self.pos, acc_num, time_wait, dist_hover, speed_cap, hover_num, pos_follow)

    def d_homing(self, speed, angle_incr, initial_angle, time_start_home=None, time_end_home=None,
                 pos_follow: XY = None):
        self.movement = self.Homing(self.pos, speed, angle_incr, initial_angle, time_start_home, time_end_home,
                                    pos_follow)

    def d_homing_pointing_to_follow(self, speed, angle_incr, angle_to_add_start=0,
                                    time_start_home=None, time_end_home=None, pos_follow: XY = None):
        if pos_follow is None:
            pos_follow = player.pt
        self.d_homing(speed, angle_incr, self.Calc.angle_pt(self.pos, pos_follow) + angle_to_add_start,
                      time_start_home, time_end_home, pos_follow)

    def d_homing_pointing_to_diff_pos(self, speed, angle_incr, pos_start_direction: XY,
                                      angle_to_add_start=0, time_start_home=None, time_end_home=None,
                                      pos_follow: XY = None):
        self.d_homing(speed, angle_incr, self.Calc.angle_pt(self.pos, pos_start_direction) + angle_to_add_start,
                      time_start_home, time_end_home, pos_follow)

    def d_rotate(self, center: XY, angle_incr, angle_current, dist_incr, dist_incr_incr: float = 0,
                 dist_current: float = 0):
        self.movement = self.Rotate(self.pos, center, angle_incr, angle_current, dist_incr, dist_incr_incr,
                                    dist_current)

    def d_rotate_from_pos(self, pos_x, pos_y, center, angle_incr, dist_incr: float = 0, dist_incr_incr: float = 0):
        self.d_rotate(center, angle_incr, math.atan2(pos_y - center.y, pos_x - center.x)
                      , dist_incr, dist_incr_incr, dist(pos_x, pos_y, center.x, center.y))

    def d_rotate_from_own_pos(self, center, angle_incr, dist_incr, dist_incr_incr: float = 0):
        self.d_rotate_from_pos(self.pos.x, self.pos.y, center, angle_incr, dist_incr, dist_incr_incr)

    def d_rotate_stable(self, stable_num, stable_mult, center: XY, angle_incr, angle_current, dist_incr,
                        dist_incr_incr: float = 0, dist_current: float = 0):
        self.movement = self.Rotate_stable(self.pos, stable_num, stable_mult, center, angle_incr, angle_current,
                                           dist_incr, dist_incr_incr, dist_current)

    def d_rotate_stable_from_pos(self, stable_num, stable_mult, pos_x, pos_y, center, angle_incr, dist_incr: float = 0,
                                 dist_incr_incr: float = 0):
        self.d_rotate_stable(stable_num, stable_mult, center, angle_incr, math.atan2(pos_y - center.y, pos_x - center.x)
                             , dist_incr, dist_incr_incr, dist(pos_x, pos_y, center.x, center.y))

    def d_rotate_stable_from_own_pos(self, stable_num, stable_mult, center, angle_incr, dist_incr,
                                     dist_incr_incr: float = 0):
        self.d_rotate_stable_from_pos(stable_num, stable_mult, self.pos.x, self.pos.y, center, angle_incr, dist_incr,
                                      dist_incr_incr)

    class Calc:

        # vector as in math vector
        # returns change arr from prev too new to make pt go to new_pt
        @classmethod
        def vect_pt_pt(cls, pt, new_pt):
            temp_angle = math.atan2(new_pt.y - pt.y, new_pt.x - pt.x)
            return math.cos(temp_angle), math.sin(temp_angle)

        # returns vector to player
        @classmethod
        def vect_pt_player(cls, pt):
            return cls.vect_pt_pt(pt, player.pt)

        @classmethod
        def dist_pt(cls, pt_1, pt_2):
            return dist(pt_1.x, pt_1.y, pt_2.x, pt_2.y)

        @classmethod
        def dist_player(cls, pt):
            return dist(pt.x, pt.y, player.pt.x, player.pt.y)

        @classmethod
        def dist_center(cls, pt):
            return dist(width // 2, height // 2, pt.x, pt.y)

        @classmethod
        def dist_player_center(cls):
            return dist(player.pt.x, player.pt.y, width // 2, height // 2)

        @classmethod
        def angle_pt(cls, pt_1, pt_2):
            return (math.atan2(pt_2.y - pt_1.y, pt_2.x - pt_1.x)) % math.tau

        @classmethod
        def angle_player(cls, pt):
            return cls.angle_pt(pt, player.pt)

    class Standard(Calc):
        def __init__(self, pos, vel_x, vel_y, acc_x, acc_y):
            self.pos = pos
            self.vel = XY(vel_x, vel_y)
            self.acc = XY(acc_x, acc_y)

        def update(self):
            self.pos.x += self.vel.x;
            self.pos.y += self.vel.y
            self.vel.x += self.acc.x;
            self.vel.y += self.acc.y

    class Hover(Calc):
        def __init__(self, pos, acc_num, time_wait, dist_hover, speed_cap, hover_num, pos_follow=None):
            # pos_follow must be of type XY
            self.pos = pos
            self.vel = XY(0, 0)
            self.acc = XY(0, 0)
            self.acc_num = acc_num
            self.timer = 0
            self.time_wait = time_wait
            self.dist_hover = dist_hover
            self.speed_cap = speed_cap
            self.hover_num = hover_num  # has to be below 1 and > 0

            self.acc_mult_negative = 1

            if pos_follow is None:
                self.pos_follow = player.pt
            else:
                self.pos_follow = pos_follow

        def update(self):
            self.acc.x, self.acc.y = self.vect_pt_pt(self.pos, self.pos_follow)
            self.acc.x *= self.acc_num;
            self.acc.y *= self.acc_num

            if dist_squared(self.pos.x, self.pos.y, player.pt.x, player.pt.y) < self.dist_hover ** 2:
                self.acc_mult_negative = max(-1, self.acc_mult_negative - self.hover_num)
            else:
                self.acc_mult_negative = min(self.acc_mult_negative + self.hover_num, 1)

            self.pos.x += self.vel.x;
            self.pos.y += self.vel.y
            self.vel.x += self.acc.x * self.acc_mult_negative;
            self.vel.y += self.acc.y * self.acc_mult_negative

            temp_sqrt = self.vel.sqrt_val() / self.speed_cap
            if temp_sqrt > 1:
                self.vel.x /= temp_sqrt;
                self.vel.y /= temp_sqrt

    class Homing(Calc):
        def __init__(self, pos: XY, speed, angle_incr, initial_angle, time_start_home=None,
                     time_end_home=None, pos_follow: XY = None):
            self.pos = pos
            self.speed = speed
            self.angle_incr = angle_incr
            self.angle = initial_angle % math.tau

            self.timer = 0
            if time_start_home is None:
                self.should_time_start_home = False
                self.time_start_home = 0
            else:
                self.should_time_start_home = True
                self.time_start_home = time_start_home

            if time_end_home is None:
                self.should_time_end_home = False
                self.time_end_home = 0
            else:
                self.should_time_end_home = True
                self.time_end_home = time_end_home

            if pos_follow is None:
                self.pos_follow = player.pt
            else:
                self.pos_follow = pos_follow

        def update(self) -> None:
            self.timer += 1

            if (self.timer <= self.time_end_home or (not self.should_time_end_home)) \
                    and (self.timer >= self.should_time_start_home or (not self.should_time_start_home)):
                angle_to_player = self.angle_pt(self.pos, self.pos_follow)
                angle_to_player = angle_to_player % math.tau

                diff_angle = self.angle - angle_to_player

                if diff_angle > 0:
                    if diff_angle < math.pi:
                        self.angle -= self.angle_incr
                    elif diff_angle > math.pi:
                        self.angle += self.angle_incr
                elif diff_angle < 0:
                    if diff_angle > -math.pi:
                        self.angle += self.angle_incr
                    elif diff_angle < -math.pi:
                        self.angle -= self.angle_incr

                self.angle = self.angle % math.tau

            self.pos.x += self.speed * math.cos(self.angle)
            self.pos.y += self.speed * math.sin(self.angle)

    class Rotate(Calc):
        def __init__(self, pos: XY, center: XY, angle_incr, angle_current, dist_incr, dist_incr_incr, dist_current):
            self.pos = pos  # projectile pos
            self.center = center  # not the projectile pos - its the position projectile rotates around

            self.angle_incr = angle_incr
            self.angle_current = angle_current

            self.dist_incr = dist_incr
            self.dist_incr_incr = dist_incr_incr
            self.dist_current = dist_current

        def update(self):
            self.dist_current += self.dist_incr
            self.dist_incr += self.dist_incr_incr

            self.angle_current += self.angle_incr

            self.pos.x = self.center.x + self.dist_current * math.cos(self.angle_current)
            self.pos.y = self.center.y + self.dist_current * math.sin(self.angle_current)

    class Rotate_stable(Rotate):
        def __init__(self, pos: XY, stable_num, stable_mult, center: XY, angle_incr, angle_current, dist_incr,
                     dist_incr_incr, dist_current):
            super().__init__(pos, center, angle_incr, angle_current, dist_incr, dist_incr_incr, dist_current)
            self.stable_num = stable_num
            self.stable_mult = stable_mult

        def update(self):
            self.dist_current += self.dist_incr
            self.dist_incr += self.dist_incr_incr

            self.angle_current += self.stable_mult * self.angle_incr / (self.stable_num + abs(self.dist_current))

            self.pos.x = self.center.x + self.dist_current * math.cos(self.angle_current)
            self.pos.y = self.center.y + self.dist_current * math.sin(self.angle_current)


'''
angle_to_player = math.atan2(player.pos[1]-self.projectiles[i].pos[1],player.pos[0]-self.projectiles[i].pos[0])
            if angle_to_player <0:
                angle_to_player+=2*math.pi
            if self.angles[i]<0:
                self.angles[i]+=2*math.pi
            if self.angles[i]>2*math.pi:
                self.angles[i] -=2*math.pi

            diff_angle = self.angles[i]-angle_to_player
            if diff_angle>0:
                if diff_angle<math.pi:
                    self.angles[i] -=self.angles_increment[i]
                elif diff_angle > math.pi:
                    self.angles[i] +=self.angles_increment[i]
            elif diff_angle<0:
                if diff_angle > -math.pi:
                    self.angles[i] += self.angles_increment[i]
                elif diff_angle < -math.pi:
                    self.angles[i] -= self.angles_increment[i]
            self.projectiles[i].pos[0] += self.speed[i]*math.cos(self.angles[i])
            self.projectiles[i].pos[1] += self.speed[i]*math.sin(self.angles[i])

'''


class Projectile(Movement):
    def __init__(self, x, y, radius, color, should_glow=True, pulsate_mult=1.5, no_glow=False,
                 should_dim_farther_player: list[float, float, float] = None, dist_dim: list[int, int, int] = None):
        # should_dim_farther_player only works when should_glow is False
        super().__init__(x, y)
        self.radius = radius

        self.color = [color[0], color[1], color[2]]
        self.should_glow = should_glow
        self.pulsate_mult = pulsate_mult
        self.current_pulsate_mult = pulsate_mult
        self.pulsate_mult_add_subt = -1
        self.no_glow = no_glow

        if should_dim_farther_player is None:
            self.should_dim_farther_player = [False, False, False]
        else:
            if should_dim_farther_player == True:
                self.should_dim_farther_player = [True, True, True]
            else:
                self.should_dim_farther_player = should_dim_farther_player.copy()
            if type(dist_dim) is int:
                self.dist_dim = [dist_dim, dist_dim, dist_dim]
            else:
                self.dist_dim = dist_dim.copy()

        if self.should_glow:
            self.surf_arr: list[pygame.Surface] = [0] * 21
            self.surf_arr[0] = circle_surf(self.radius, self.color)
            circle_avg = max(self.color) + 10

            temp_circle_glow = [(20 * (self.color[0] + 10)) // circle_avg + 1,
                                (20 * (self.color[1]) + 10) // circle_avg + 1,
                                (20 * (self.color[2]) + 10) // circle_avg + 1]

            temp_circle_radius = self.radius

            for i in range(1, 21):
                temp_circle_radius += 0.5
                for j in range(3):
                    if temp_circle_glow[j] >= 1:
                        temp_circle_glow[j] -= 1
                self.surf_arr[i] = circle_surf(temp_circle_radius, temp_circle_glow)
        elif not self.no_glow:
            self.circle_avg = max(self.color) + 10
            self.circle_glow = [(60 * (self.color[0] + 15)) // self.circle_avg + 1,
                                (60 * (self.color[1]) + 15) // self.circle_avg + 1,
                                (60 * (self.color[2]) + 15) // self.circle_avg + 1]

        self.past_pos = XY(x, y)

    def draw(self):
        if not self.no_glow:
            if self.should_glow and PROJECTILES_CAN_GLOW_OVERRIDES_ALL_OTHER_CONDITIONS:
                for i in range(21):
                    screen.blit(self.surf_arr[i], (
                        self.pos.x - self.surf_arr[i].get_width() / 2, self.pos.y - self.surf_arr[i].get_width() / 2),
                                special_flags=BLEND_RGB_ADD)

            else:
                temp_color = self.color.copy()
                for i in range(3):
                    if self.should_dim_farther_player[i]:
                        temp_color[i] *= self.dist_dim[i] / (self.Calc.dist_player(self.pos) + self.dist_dim[i])

                pygame.draw.circle(screen, temp_color, [self.pos.x, self.pos.y], self.radius)

                if not self.should_glow:
                    self.current_pulsate_mult += (self.pulsate_mult) / 300 * self.pulsate_mult_add_subt
                    if self.current_pulsate_mult > self.pulsate_mult:
                        self.pulsate_mult_add_subt = -1
                    elif self.current_pulsate_mult < 0.5 + self.pulsate_mult / 2:
                        self.pulsate_mult_add_subt = 1

                temp_color = self.circle_glow.copy()
                for i in range(3):
                    if self.should_dim_farther_player[i]:
                        temp_color[i] *= self.dist_dim[i] / (self.Calc.dist_player(self.pos) + self.dist_dim[i])

                screen.blit(circle_surf(self.radius * self.current_pulsate_mult, self.circle_glow),
                            (self.pos.x - self.radius - (self.current_pulsate_mult - 1) * self.radius,
                             self.pos.y - self.radius - (self.current_pulsate_mult - 1) * self.radius),
                            special_flags=BLEND_RGB_ADD)
        else:
            temp_color = self.color.copy()
            for i in range(3):
                if self.should_dim_farther_player[i]:
                    temp_color[i] *= self.dist_dim[i] / (self.Calc.dist_player(self.pos) + self.dist_dim[i])

            pygame.draw.circle(screen, self.color, [self.pos.x, self.pos.y], self.radius)

    def update(self):
        self.move()
        self.draw()

    def destroy(self, forgiving_amount_x=0, forgiving_amount_y=0):
        if self.pos.x - self.radius > width + forgiving_amount_x:
            return True
        if self.pos.x + self.radius < -forgiving_amount_x:
            return True
        if self.pos.y + self.radius < -forgiving_amount_y:
            return True
        if self.pos.y - self.radius > height + forgiving_amount_y:
            return True
        return False

    def give_info(self):
        return [self.pos, self.radius]

    @classmethod
    def list_update(cls, proj_list, forgiving_x=0, forgiving_y=None, should_collide=True):
        if forgiving_y is None:
            forgiving_y = forgiving_x

        for i in range(len(proj_list)):
            proj_list[i].update()

        index = 0
        while index < len(proj_list):
            if proj_list[index].destroy(forgiving_x, forgiving_y):
                del proj_list[index]
                index -= 1
            index += 1

        if should_collide: player.collision(proj_list)

        if proj_list:
            return True
        return False


# FOR ALL THE FOLLOWING PROJECTILES:
# 1 - STANDARD
# 2 AND 4 - old version of lasers (don't use)
# 3 STANDARD but movement rotates
# 5 laser but newer version

# circle projectile - standard projectile use for most cases
class Projectile1:
    def __init__(self, pos, radius, velocity, acceleration, color, should_glow=True, pulsate_mult=1.5, no_glow=False):
        self.pos = pos
        self.radius = radius
        self.velocity = velocity
        self.acceleration = acceleration

        self.color = color
        self.should_glow = should_glow
        self.pulsate_mult = pulsate_mult
        self.current_pulsate_mult = pulsate_mult
        self.pulsate_mult_add_subt = -1
        self.no_glow = no_glow

    def draw(self):
        if not self.no_glow:
            if self.should_glow and PROJECTILES_CAN_GLOW_OVERRIDES_ALL_OTHER_CONDITIONS:
                temp_circle_radius = self.radius
                temp_circle_avg = max(self.color) + 10
                temp_num = 1
                temp_circle_glow = [(20 * (self.color[0] + 10)) // temp_circle_avg + 1,
                                    (20 * (self.color[1]) + 10) // temp_circle_avg + 1,
                                    (20 * (self.color[2]) + 10) // temp_circle_avg + 1]
                screen.blit(circle_surf(temp_circle_radius, temp_circle_glow),
                            (self.pos[0] - temp_circle_radius, self.pos[1] - temp_circle_radius),
                            special_flags=BLEND_RGB_ADD)
                for i in range(20):
                    temp_circle_radius += 0.5
                    for j in range(3):
                        if temp_circle_glow[j] >= temp_num:
                            temp_circle_glow[j] -= temp_num
                    temp_circle_glow = [
                        temp_circle_glow[0], temp_circle_glow[1], temp_circle_glow[2]]
                    screen.blit(circle_surf(temp_circle_radius, temp_circle_glow),
                                (self.pos[0] - temp_circle_radius, self.pos[1] - temp_circle_radius),
                                special_flags=BLEND_RGB_ADD)
            else:
                pygame.draw.circle(screen, self.color, self.pos, self.radius)
                temp_circle_radius = self.radius
                temp_circle_avg = max(self.color) + 10
                temp_circle_glow = [(60 * (self.color[0] + 15)) // temp_circle_avg + 1,
                                    (60 * (self.color[1]) + 15) // temp_circle_avg + 1,
                                    (60 * (self.color[2]) + 15) // temp_circle_avg + 1]
                if not self.should_glow:
                    self.current_pulsate_mult += (self.pulsate_mult) / 300 * self.pulsate_mult_add_subt
                    if self.current_pulsate_mult > self.pulsate_mult:
                        self.pulsate_mult_add_subt = -1
                    elif self.current_pulsate_mult < 0.5 + self.pulsate_mult / 2:
                        self.pulsate_mult_add_subt = 1
                screen.blit(circle_surf(temp_circle_radius * self.current_pulsate_mult, temp_circle_glow),
                            (self.pos[0] - temp_circle_radius - (self.current_pulsate_mult - 1) * temp_circle_radius,
                             self.pos[1] - temp_circle_radius - (self.current_pulsate_mult - 1) * temp_circle_radius),
                            special_flags=BLEND_RGB_ADD)
        else:
            pygame.draw.circle(screen, self.color, self.pos, self.radius)

    def move(self):
        for i in range(2):
            self.pos[i] += self.velocity[i]
            self.velocity[i] += self.acceleration[i]

    def update(self):
        self.move()
        self.draw()

    def destroy(self, forgiving_amount=0):
        if self.pos[0] - self.radius > width + forgiving_amount:
            return True
        if self.pos[0] + self.radius < -forgiving_amount:
            return True
        if self.pos[1] + self.radius < -forgiving_amount:
            return True
        if self.pos[1] - self.radius > height + forgiving_amount:
            return True
        return False

    def give_info(self):
        return [self.pos, self.radius]

    @classmethod
    def to_player(cls, pos, radius, dist_incr, dist_incr_incr, angle_add, color, should_glow=True, pulsate_mult=1.5,
                  no_glow=False):
        temp_angle = math.atan2(player.pos[1] - pos[1], player.pos[0] - pos[0]) + angle_add
        return Projectile1(pos, radius, [math.cos(temp_angle) * dist_incr, math.sin(temp_angle) * dist_incr],
                           [math.cos(temp_angle) * dist_incr_incr, math.sin(temp_angle) * dist_incr_incr],
                           color, should_glow, pulsate_mult, no_glow)


# Line projectile - for lasers, not moving lines
# Class lazer class laser
# the gradient effect is currently not finished - just draws same width and color gradient
# the standard drawing is fine for any type laser however
class Projectile2:
    # if you're using the center pt and rotating you probably want to just have pt 2
    # color_prior should be of ex: [0,1,2] or [2,0,1]
    def __init__(self, pos_1_x, pos_1_y, pos_2_x, pos_2_y, color_prior, width, is_from_center=False,
                 center_x=width // 2, center_y=height // 2,
                 angle_from_center=0, angle_increment=0, dist_from_center_1=0, dist_from_center_2=0,
                 should_gradient=False, color=(255, 255, 255)):
        self.pos_1_x = pos_1_x
        self.pos_1_y = pos_1_y
        self.pos_2_x = pos_2_x
        self.pos_2_y = pos_2_y
        self.color_prior = color_prior
        self.color = color
        self.width = width
        self.center_x = center_x
        self.center_y = center_y
        self.angle_from_center = angle_from_center
        self.angle_increment = angle_increment
        self.dist_from_center_1 = dist_from_center_1
        self.dist_from_center_2 = dist_from_center_2
        self.is_from_center = is_from_center
        self.should_gradient = should_gradient

    def draw(self):
        if self.should_gradient:
            for i in range(160, 10, -10):
                temp_color = [351 - 9 * i, -3 * i + 285, int(-1.7 * i + 272)]
                if temp_color[0] < 0: temp_color[0] = 0
                if temp_color[1] < 0: temp_color[1] = 0
                if temp_color[2] < 0: temp_color[2] = 0

                temp_arr = temp_color.copy()
                for j in range(3):
                    temp_color[j] = temp_arr[self.color_prior[j]]

                pygame.draw.line(screen, temp_color, [self.pos_1_x, self.pos_1_y], [self.pos_2_x, self.pos_2_y],
                                 int(i / 2))

            pygame.draw.line(screen, (255, 255, 255), [self.pos_1_x, self.pos_1_y], [self.pos_2_x, self.pos_2_y], 10)
        else:
            pygame.draw.line(screen, self.color, [self.pos_1_x, self.pos_1_y], [self.pos_2_x, self.pos_2_y], self.width)

    def collision(self):
        if line_circle_collision(self.pos_1_x, self.pos_1_y, self.pos_2_x, self.pos_2_y, player.pos[0],
                                 player.pos[1], player.radius + self.width // 2 - 3):
            player.lose_health()
            return  # remove this if you decide to return something instead of instantly decreasing player's health

    def update(self, should_rotate=True, should_draw=True, should_check_collision=True):

        if should_rotate:
            self.angle_from_center += self.angle_increment
        if self.is_from_center:
            self.pos_1_x = self.dist_from_center_1 * math.cos(self.angle_from_center) + self.center_x
            self.pos_1_y = self.dist_from_center_1 * math.sin(self.angle_from_center) + self.center_y

            self.pos_2_x = -self.dist_from_center_2 * math.cos(self.angle_from_center) + self.center_x
            self.pos_2_y = -self.dist_from_center_2 * math.sin(self.angle_from_center) + self.center_y

        if should_draw:
            self.draw()

        if should_check_collision:
            self.collision()


# used for circle projectiles but they just move out based on increasing distance and angle
# there is no velocity, no acceleration - just the dist, dist incr, and incr for dist incr
# THE CENTER VARIABLE IS NOT THE ACTUAL POSITION IT IS WHERE THE PROJECTILE ROTATES AROUND
class Projectile_Rotate(Projectile1):
    def __init__(self, radius, center, color, should_glow, no_glow, pulsate_mult,
                 angle_incr, angle_current, dist_incr, dist_incr_incr=0, dist_current=0):
        super().__init__(center.copy(), radius, None, None, color, should_glow, pulsate_mult, no_glow)

        self.dist_incr = dist_incr
        self.dist_incr_incr = dist_incr_incr
        self.angle_incr = angle_incr

        self.dist_current = dist_current
        self.angle_current = angle_current

        # THE CENTER VARIABLE IS NOT THE ACTUAL POSITION IT IS WHERE THE PROJECTILE ROTATES AROUND
        self.center = center

    def move(self):
        self.dist_current += self.dist_incr
        self.dist_incr += self.dist_incr_incr
        self.angle_current += self.angle_incr
        self.pos[0] = self.center[0] + self.dist_current * math.cos(self.angle_current)
        self.pos[1] = self.center[1] + self.dist_current * math.sin(self.angle_current)

    @classmethod
    def from_pos(cls, radius, center, color, should_glow, no_glow, pulsate_mult,
                 angle_incr, dist_incr, dist_incr_incr, pos):
        return cls(radius, center, color, should_glow, no_glow, pulsate_mult,
                   angle_incr, math.atan2(pos[1] - center[1], pos[0] - center[0])
                   , dist_incr, dist_incr_incr, dist(center[0], center[1], pos[0], pos[1]))


class Projectile3:
    def __init__(self, radius, color, dist_incr, angle_incr, center, dist_current=0, angle_current=0,
                 should_glow=True, pulsate_mult=1.5, set_by_pos=False, pos=None, no_glow=False):
        if pos is None:
            pos = center.copy()

        self.pt = XY(pos[0], pos[1])

        self.dist_current = dist_current
        self.dist_incr = dist_incr
        self.angle_current = angle_current
        self.angle_incr = angle_incr
        self.center = center

        self.proj = Projectile1(pos, radius, [0, 0], [0, 0], color, should_glow, pulsate_mult, no_glow)

        if set_by_pos:
            self.dist_current = dist(self.center[0], self.center[1], pos[0], pos[1])
            self.angle_current = math.atan2(pos[1] - self.center[1], pos[0] - self.center[0])

    def update(self, should_draw=True):
        self.dist_current += self.dist_incr
        self.angle_current += self.angle_incr
        self.proj.pos[0] = self.center[0] + self.dist_current * math.cos(self.angle_current)
        self.proj.pos[1] = self.center[1] + self.dist_current * math.sin(self.angle_current)
        self.pt.x = self.proj.pos[0]
        self.pt.y = self.proj.pos[1]
        if should_draw: self.draw()

    def draw(self):
        self.proj.draw()

    def destroy(self, forgiving_amount=0):
        return self.proj.destroy(forgiving_amount)

    def give_info(self):
        return self.proj.give_info()


# This class is basically the same as Projectile2 just more general
# Essentially this just takes 2 projectile inputs (any non array type projectile should work)
#                                                     -if a non array type doesn't work then make it work
# (array type just if the proj type keeps track of a list of them instead of just 1)
# The .update is just updating the 2 projectiles, and creating a laser (Projectile2) between them
class Projectile5:
    def __init__(self, proj_1, proj_2, proj_laser):
        self.proj_1 = proj_1
        self.proj_2 = proj_2
        self.proj_laser = proj_laser

    def draw(self):
        self.proj_laser.draw()
        self.proj_1.draw()
        self.proj_2.draw()

    def update(self, do_collision=True):
        self.proj_1.update()
        self.proj_2.update()

        self.proj_laser.pos_1_x = self.proj_1.give_info()[0][0]
        self.proj_laser.pos_1_y = self.proj_1.give_info()[0][1]
        self.proj_laser.pos_2_x = self.proj_2.give_info()[0][0]
        self.proj_laser.pos_2_y = self.proj_2.give_info()[0][1]

        if do_collision:
            player.collision([self.proj_1, self.proj_2])
            self.proj_laser.collision()

        self.draw()

    def destroy(self, forgiving_amount=0):
        if self.proj_1.destroy(forgiving_amount) and self.proj_2.destroy(forgiving_amount):
            return True
        return False


class Player:
    def __init__(self, pos, radius, velocity, acceleration, color, total_health, can_dash, immunity_milliseconds=2000):
        self.invincible = 0
        self.pos = pos
        self.radius = radius
        self.velocity = velocity
        self.acceleration = acceleration
        self.color = color
        self.color_health = self.color
        self.max_health = 45
        self.health = self.max_health
        self.time = 0
        self.immunity_milliseconds = immunity_milliseconds
        self.dash_time_remaining = 0
        self.dash_cooldown = 0
        self.max_dash_cooldown = 60
        self.can_dash = can_dash
        self.dash_length = 10
        self.is_dashing = False
        self.dash_speed = 3

        self.tri_angles = [0 * math.tau / 6, 2 * math.tau / 6, 4 * math.tau / 6]
        self.tri_angle_incr = [0.03, 0.03, 0.03]
        self.tri_dist = 50
        # math.tau/6
        self.particles_past_pos = [[self.pos[0], self.pos[1]], [self.pos[0], self.pos[1]], [self.pos[0], self.pos[1]],
                                   [self.pos[0], self.pos[1]], [self.pos[0], self.pos[1]], [self.pos[0], self.pos[1]],
                                   [self.pos[0], self.pos[1]], [self.pos[0], self.pos[1]], [self.pos[0], self.pos[1]]]

        self.pt = XY(self.pos[0], self.pos[1])

        self.score = 0
        self.timer_immunity = 0

    def immunity(self):
        if self.invincible:  # this code should never run - ignore it
            self.time = pygame.time.get_ticks()
            self.invincible = False
            return False

        elif pygame.time.get_ticks() - self.time >= self.immunity_milliseconds:
            return True
        return False

    def draw(self):

        self.particles_past_pos.insert(0, self.pos.copy())
        self.particles_past_pos.pop()
        if self.immunity():
            for i in range(len(self.particles_past_pos)):
                pygame.draw.circle(screen, self.color, self.particles_past_pos[i], max(0, 12 - i))

            pygame.draw.circle(screen, (255, 255, 255), self.pos, self.radius)
            temp_player_radius = self.radius

            temp_player_glow = [(20),
                                (20 + 5 * (1 - self.health / self.max_health)),
                                (20 + 5 * self.health / self.max_health)]
            temp_num = 1
            screen.blit(circle_surf(temp_player_radius, temp_player_glow),
                        (player.pos[0] - temp_player_radius, player.pos[1] - temp_player_radius),
                        special_flags=BLEND_RGB_ADD)
            for i in range(20):
                temp_player_radius += 0.5
                temp_player_glow = [
                    temp_player_glow[0] - temp_num, temp_player_glow[1] - temp_num, temp_player_glow[2] - temp_num]
                for j in range(3):
                    if temp_player_glow[j] < 0: temp_player_glow[j] = 0
                screen.blit(circle_surf(temp_player_radius, temp_player_glow),
                            (player.pos[0] - temp_player_radius, player.pos[1] - temp_player_radius),
                            special_flags=BLEND_RGB_ADD)
            for i in range(len(self.tri_angles)):
                pygame.draw.line(screen, self.color,
                                 [(self.tri_dist * math.cos(self.tri_angles[i]) + self.pt.x),
                                  (self.tri_dist * math.sin(self.tri_angles[i])) + self.pt.y],
                                 [(self.tri_dist * math.cos(
                                     self.tri_angles[(i + 1) % len(self.tri_angles)])) + self.pt.x,
                                  (self.tri_dist * math.sin(
                                      self.tri_angles[(i + 1) % len(self.tri_angles)])) + self.pt.y],
                                 2)
        else:
            for i in range(len(self.particles_past_pos)):
                pygame.draw.circle(screen, (255, 0, 0), self.particles_past_pos[i], max(0, 12 - i))

            pygame.draw.circle(screen, (255, 255, 255), self.pos, self.radius)
            temp_player_radius = self.radius

            temp_player_glow = [(20 + 10 * (1 - ((pygame.time.get_ticks() - self.time) / self.immunity_milliseconds))),
                                ((20 + (5 * (1 - self.health / self.max_health)))) * (
                                    ((pygame.time.get_ticks() - self.time) / self.immunity_milliseconds)),
                                ((20 + (5 * self.health / self.max_health))) * (
                                    ((pygame.time.get_ticks() - self.time) / self.immunity_milliseconds))]
            temp_num = 1
            screen.blit(circle_surf(temp_player_radius, temp_player_glow),
                        (player.pos[0] - temp_player_radius, player.pos[1] - temp_player_radius),
                        special_flags=BLEND_RGB_ADD)

            for i in range(20):
                temp_player_radius += 0.5
                temp_player_glow = [
                    temp_player_glow[0] - temp_num, temp_player_glow[1] - temp_num, temp_player_glow[2] - temp_num]
                for j in range(3):
                    if temp_player_glow[j] < 0: temp_player_glow[j] = 0
                screen.blit(circle_surf(temp_player_radius, temp_player_glow),
                            (player.pos[0] - temp_player_radius, player.pos[1] - temp_player_radius),
                            special_flags=BLEND_RGB_ADD)
            for i in range(len(self.tri_angles)):
                pygame.draw.line(screen, (255, 0, 0),
                                 [(self.tri_dist * math.cos(self.tri_angles[i]) + self.pt.x),
                                  (self.tri_dist * math.sin(self.tri_angles[i])) + self.pt.y],
                                 [(self.tri_dist * math.cos(
                                     self.tri_angles[(i + 1) % len(self.tri_angles)])) + self.pt.x,
                                  (self.tri_dist * math.sin(
                                      self.tri_angles[(i + 1) % len(self.tri_angles)])) + self.pt.y],
                                 2)
            for i in range(len(self.tri_angles)):
                self.tri_angles[i] += self.tri_angle_incr[i] * 5

        for i in range(len(self.tri_angles)):
            self.tri_angles[i] += self.tri_angle_incr[i]

    def update(self, tick_amount=60):
        self.player_input(
            tick_amount)  # using acceleration will probably require telegraphing to be rewritten so moving doesn't goes wrong
        for i in range(2):
            self.pos[i] += self.velocity[i]
            if self.pos[i] < 0:
                self.pos[i] = 0
            self.velocity[i] += self.acceleration[i]
        if self.pos[0] > width:
            self.pos[0] = width
        if self.pos[1] > height:
            self.pos[1] = height

        self.pt.x = self.pos[0]
        self.pt.y = self.pos[1]

        self.draw()
        self.timer_immunity += 1
        self.score += self.timer_immunity ** 0.5

    def player_input(self, tick_amount=60):
        get_pressed = pygame.key.get_pressed()
        if self.can_dash:
            if not self.is_dashing and get_pressed[pygame.K_LCTRL] and self.dash_cooldown >= self.max_dash_cooldown:
                self.dash_cooldown = 0
                self.dash_time_remaining = 0
                # pos_mouse = pygame.mouse.get_pos()
                self.velocity[0] *= self.dash_speed
                self.velocity[1] *= self.dash_speed
                self.is_dashing = True
        if self.is_dashing:
            self.dash_time_remaining += 1
            if self.dash_time_remaining > self.dash_length:
                self.is_dashing = False
        else:
            self.dash_cooldown += 1
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                self.velocity[0] = 0
            elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                self.velocity[0] = 4
            elif (keys[pygame.K_a] or keys[pygame.K_LEFT]):
                self.velocity[0] = -4
            else:
                self.velocity[0] = 0
            if (keys[pygame.K_w] or keys[pygame.K_UP]) and (keys[pygame.K_s] or keys[pygame.K_DOWN]):
                self.velocity[1] = 0
            elif (keys[pygame.K_w] or keys[pygame.K_UP]):
                self.velocity[1] = -4
            elif (keys[pygame.K_s] or keys[pygame.K_DOWN]):
                self.velocity[1] = 4
            else:
                self.velocity[1] = 0
            if keys[pygame.K_LSHIFT]:
                self.velocity[0] *= 0.35
                self.velocity[1] *= 0.35
            self.velocity[0] *= (60 / tick_amount)
            self.velocity[1] *= (60 / tick_amount)

    def lose_health(self):
        if self.immunity():
            self.time = pygame.time.get_ticks()
            self.health -= 1
            self.timer_immunity = 0
            self.color_health = (self.color[0] * (self.health / self.max_health),
                                 self.color[1] * (self.health / self.max_health),
                                 self.color[2] * (self.health / self.max_health))

    def is_alive(self):
        if self.health <= 0:
            return False
        return True

    def collision(self, list_circles):
        for proj in list_circles:
            if not isinstance(proj, Projectile):
                temp = proj.give_info()
                if ((self.pos[0] - temp[0][0]) ** 2 + (self.pos[1] - temp[0][1]) ** 2) < (temp[1] + self.radius) ** 2:
                    self.lose_health()
            else:
                if ((self.pos[0] - proj.pos.x) ** 2 + (self.pos[1] - proj.pos.y) ** 2) < (
                        proj.radius + self.radius) ** 2:
                    self.lose_health()

        if self.is_alive(): return False
        return True

    def coords(self):
        return self.pos

    def changeRadius(self, newRadius):
        self.radius = newRadius

    def keep_in_circle(self, radius_circle, center_x, center_y, consider_player_radius):
        if consider_player_radius:
            is_outside = (dist(self.pos[0], self.pos[1], center_x, center_y) > radius_circle - self.radius)
        else:
            is_outside = (dist(self.pos[0], self.pos[1], center_x, center_y) > radius_circle)
        if is_outside:
            temp_angle = math.atan2(self.pos[1] - center_y, self.pos[0] - center_x)
            if consider_player_radius:
                self.pos[0] = center_x + math.cos(temp_angle) * (radius_circle - self.radius)
                self.pos[1] = center_y + math.sin(temp_angle) * (radius_circle - self.radius)
            else:
                self.pos[0] = center_x + math.cos(temp_angle) * (radius_circle)
                self.pos[1] = center_y + math.sin(temp_angle) * (radius_circle)


# global vars
angle = 0
time = 0
total_rotations = 0
projectile_list = []
player_info = ([400, 100], 10, [0, 0], [0, 0], [0, 0, 255], 20)
player = Player(player_info[0].copy(), player_info[1], player_info[2].copy(), player_info[3].copy(),
                player_info[4].copy(), player_info[5], False)
finished = False
start_attack = False
PROJECTILES_CAN_GLOW_OVERRIDES_ALL_OTHER_CONDITIONS = True  # set to False for better performance


# legacy do not use
def create_circle_angle(center, angle, velocity, acceleration_num, radius, color, should_glow=True):
    angleArr = [math.cos(angle), math.sin(angle)]
    velocityArr = [angleArr[0] * velocity, angleArr[1] * velocity]
    accelerationArr = [velocityArr[0] * acceleration_num, velocityArr[1] * acceleration_num]
    temp_projectile = Projectile1(center, radius, velocityArr, accelerationArr, color, should_glow)
    return temp_projectile


# legacy do not use
def spiral_bullet_spam_attack(time_per_proj, center, angle_increment, color, velocity, rotation_amount=10,
                              acceleration_num=0, check_ring=False, size_proj=5, should_glow=True):
    global angle, time, total_rotations, projectile_list, finished
    if not check_ring:
        if rotation_amount == total_rotations:
            finished = True
            if projectiles_finish(projectile_list, False):
                return True
            else:
                angle = 0
                time = 0
                total_rotations = 0
                projectile_list = []
                return False
    angle += angle_increment

    if x == 0 or x == 1:
        if angle >= 360:
            angle -= 360 * (math.pi / 3)
            total_rotations += 1
    else:
        if angle >= 2 * math.pi:
            angle -= 2 * math.pi
            total_rotations += 1

    time = (time + 1) % time_per_proj

    if time == 0:
        projectile_list.append(
            create_circle_angle(center, angle, velocity, acceleration_num, size_proj, color, should_glow))

    if projectiles_finish(projectile_list, False): return True
    return True


# legacy do not use
def circle_circle_attack(color=[100, 100, 255], center=(width // 2, height // 2), angle_increment=15 / 57.2957795131,
                         radius=5, dist_away=200):
    global angle, time, projectile_list, finished, start_attack
    check = True
    if time == 3:
        finished = True
        # if projectiles_finish(): return False
        # else:
        # angle = 0
        # time = 0
        check = False
    # INCREMENT MUST BE FACTOR OF 360

    num_circles = int(2 * math.pi / angle_increment)

    if not start_attack:
        finished = False
        time = 0
        angle = 0
        actual_angle = 0
        for i in range(num_circles):
            actual_angle += angle_increment
            temp_center = [center[0] + dist_away * math.cos(actual_angle),
                           center[1] + dist_away * math.sin(actual_angle)]
            # temp_projectile = Projectile(temp_center,radius,[0,0],[0,0],color)
            temp_projectile = Projectile(temp_center[0], temp_center[1], radius, color)  # [0,0],[0,0],color)
            temp_projectile.d_standard(0, 0, 0, 0)
            projectile_list.append(temp_projectile)
        start_attack = True
    angle += 0.005
    actual_angle = angle
    for i in range(num_circles):
        actual_angle += angle_increment
        # projectile_list[i].pos = [center[0] + dist_away * math.cos(actual_angle), center[1] + dist_away * math.sin(actual_angle)]
        projectile_list[i].pos.x = center[0] + dist_away * math.cos(actual_angle)
        projectile_list[i].pos.y = center[1] + dist_away * math.sin(actual_angle)

    if not finished:
        time += 1
    if time <= 120:
        for i in range(len(projectile_list)):
            projectile_list[i].update()
    return check


# USE THIS TO UPDATE PROJECTILES
def projectiles_finish(proj_list, should_update=False, forgiving_amount=0, should_collide=True):
    if should_update:
        if should_collide:
            for i in range(len(proj_list)):
                proj_list[i].update()
        else:
            for i in range(len(proj_list)):
                proj_list[i].update(False)
    index = 0
    while index < len(proj_list):
        if proj_list[index].destroy(forgiving_amount):
            del proj_list[index]
            index -= 1
        elif x == 0 or x == 1:
            if dist(player_initial_pos[0], player_initial_pos[1], proj_list[index].pos[0],
                    proj_list[index].pos[1]) > radius:
                del proj_list[index]
                index -= 1
        elif x == 2:
            if dist(width // 2, height // 2, proj_list[index].pos.x, proj_list[index].pos.y) > radius:
                del proj_list[index]
                index -= 1
        index += 1
    if proj_list:
        return True
    return False


projectile_list_shoot = []


# legacy do not use
def start_shoot_player_scuffed(speed, color):
    index = 0
    while index < len(projectile_list) - 0.5:
        int_index = int(index)
        projectile = projectile_list[int_index]
        # change_arr = [player.pos[0]-projectile.pos[0],player.pos[1]-projectile.pos[1]]
        change_arr = [player.pos[0] - projectile.pos.x, player.pos[1] - projectile.pos.y]
        # dist = math.sqrt((player.pos[0]-projectile.pos[0])**2+(player.pos[1]-projectile.pos[1])**2)
        dist = math.sqrt((player.pos[0] - projectile.pos.x) ** 2 + (player.pos[1] - projectile.pos.y) ** 2)
        change_arr[0] /= dist
        change_arr[1] /= dist
        change_arr[0] *= speed * 0.5
        change_arr[1] *= speed * 0.5
        # temp_projectile = Projectile1(projectile.pos.copy(),projectile.radius-1,change_arr,[0,0],color)
        temp_projectile = Projectile(projectile.pos.x, projectile.pos.y, projectile.radius - 1, color)
        temp_projectile.d_standard(change_arr[0], change_arr[1], 0, 0)
        projectile_list_shoot.append(temp_projectile)
        index += 1.7


# legacy do not use
def start_shoot_player_scuffed2(speed, color):
    for i in range(len(projectile_list)):
        projectile = projectile_list[i]
        # change_arr = [player.pos[1]-projectile.pos[1],player.pos[1]-projectile.pos[1]]
        change_arr = [player.pos[1] - projectile.pos.y, player.pos[1] - projectile.pos.y]
        # dist = math.sqrt((player.pos[0]-projectile.pos[0])**2+(player.pos[1]-projectile.pos[1])**2)
        dist = math.sqrt((player.pos[0] - projectile.pos.x) ** 2 + (player.pos[1] - projectile.pos.y) ** 2)
        change_arr[0] /= dist
        change_arr[1] /= dist
        change_arr[0] *= speed
        change_arr[1] *= speed
        # temp_projectile = Projectile1(projectile.pos.copy(),projectile.radius-1,change_arr,[0,0],color)
        temp_projectile = Projectile(projectile.pos.x, projectile.pos.y, projectile.radius - 1, color)
        temp_projectile.d_standard(change_arr[0], change_arr[1], 0, 0)
        projectile_list_shoot.append(temp_projectile)


# legacy do not use
def start_shoot_player(speed, color, increment=1):
    index = -increment
    while (index < (len(projectile_list) - increment)):
        index += increment
        projectile = projectile_list[math.floor(index)]
        # change_arr = [player.pos[1]-projectile.pos[0],player.pos[0]-projectile.pos[1]]
        change_arr = [player.pos[1] - projectile.pos.x, player.pos[0] - projectile.pos.y]
        # dist = math.sqrt((player.pos[0]-projectile.pos[0])**2+(player.pos[1]-projectile.pos[1])**2)
        dist = math.sqrt((player.pos[0] - projectile.pos.x) ** 2 + (player.pos[1] - projectile.pos.y) ** 2)
        change_arr[0] /= dist
        change_arr[1] /= dist
        change_arr[0] *= speed * 0.5
        change_arr[1] *= speed * 0.5
        # temp_projectile = Projectile1(projectile.pos.copy(),projectile.radius-1,change_arr,[0,0],color)
        temp_projectile = Projectile(projectile.pos.x, projectile.pos.y, projectile.radius - 1, color)
        temp_projectile.d_standard(change_arr[0], change_arr[1], 0, 0)
        projectile_list_shoot.append(temp_projectile)


# legacy do not use
class Homing:
    def __init__(self):
        self.projectiles = []  # If you want to add something make sure to update delete()
        self.speed = []
        # self.collision_circles = []     # If you want to add something make sure to update delete()
        self.inside_or_out = []
        self.num_projectiles = 0  # If you want to add something make sure to update delete()
        self.time_last_added = 0
        self.bool_arr = []  # If you want to add something make sure to update delete()
        self.angles = []
        self.angles_increment = []
        self.timer = pygame.time.get_ticks()

    # so I don't have to retype all the lists whenever I want to delete something
    def delete(self, index):
        del self.projectiles[index]
        del self.speed[index]
        # del self.collision_circles[index]
        # del self.inside_or_out[index]
        self.num_projectiles -= 1
        del self.bool_arr[index]
        del self.angles[index]
        del self.angles_increment[index]

    # inside_or_out is to check to delete projectile if collision of collision_circle or not collision
    # ,collision_circle,inside_or_out
    def add_projectile(self, projectile, speed, angle_increment=0.03, angle=-1):
        # projectile.velocity[0] = (player.pos[0] - projectile.pos[0])*0
        # projectile.velocity[1] = (player.pos[1] - projectile.pos[1])*0
        # projectile.velocity = [0,0]
        self.projectiles.append(projectile)
        self.speed.append(speed)
        self.num_projectiles += 1
        self.bool_arr.append(False)
        if angle == -1:
            self.angles.append(math.atan2(player.pos[1] - projectile.pos[1], player.pos[0] - projectile.pos[0]))
        else:
            self.angles.append(angle)
        if angle_increment == -1:
            self.angles_increment.append(0.03)
        else:
            self.angles_increment.append(angle_increment)
        # self.collision_circles.append(collision_circle)
        # self.inside_or_out.append(inside_or_out)

    def homing_circle(self):
        for i in range(self.num_projectiles):
            angle_to_player = math.atan2(player.pos[1] - self.projectiles[i].pos[1],
                                         player.pos[0] - self.projectiles[i].pos[0])
            if angle_to_player < 0:
                angle_to_player += 2 * math.pi
            if self.angles[i] < 0:
                self.angles[i] += 2 * math.pi
            if self.angles[i] > 2 * math.pi:
                self.angles[i] -= 2 * math.pi

            diff_angle = self.angles[i] - angle_to_player
            if diff_angle > 0:
                if diff_angle < math.pi:
                    self.angles[i] -= self.angles_increment[i]
                elif diff_angle > math.pi:
                    self.angles[i] += self.angles_increment[i]
            elif diff_angle < 0:
                if diff_angle > -math.pi:
                    self.angles[i] += self.angles_increment[i]
                elif diff_angle < -math.pi:
                    self.angles[i] -= self.angles_increment[i]
            self.projectiles[i].pos[0] += self.speed[i] * math.cos(self.angles[i])
            self.projectiles[i].pos[1] += self.speed[i] * math.sin(self.angles[i])

    def update(self):
        for projectile in self.projectiles:
            projectile.update()

    def is_outside(self):
        return False

    def collision(self):
        return player.collision(self.projectiles)

    def remove(self):
        index = 0
        while (index < len(self.projectiles)):
            if self.projectiles[index].destroy():
                self.delete(index)
                index -= 1
            index += 1

    def update_all(self):
        self.remove()
        self.homing_circle()
        self.update()
        self.collision()

    # def circle_boundary_collision_projectile(self):
    #    for i in range (self.num_projectiles):

    # make sure time is in milliseconds, time is for
    def add_projectile_on_timer(self, time_diff):
        if pygame.time.get_ticks() - self.time_last_added > time_diff:
            self.time_last_added = pygame.time.get_ticks()
            return True
        else:
            return False


continue_attack = False
game_active = True


def initialize():
    global angle, time, total_rotations, projectile_list, player, continue_attack, finished, game_active, \
        mini_attack_homing_completed, boss, attack_order, start_attack, projectile_list_shoot, check_ring, \
        projectile_object_homing, temp_choice, dont_change_attack, x, has_changed_music, music_change_time, \
        music_time_frames, start_music
    angle = 0
    time = 0
    total_rotations = 0
    projectile_list = []
    projectile_list_shoot = []
    player = Player(player_info[0].copy(), player_info[1], player_info[2].copy(), player_info[3].copy(),
                    player_info[4].copy(), player_info[5], False)
    attack_order = set_attack_order.copy()
    continue_attack = False
    finished = False
    start_attack = False
    game_active = False
    mini_attack_homing_completed = 0
    boss = Boss_square()
    check_ring = 0
    projectile_object_homing = Homing()
    temp_choice = 0
    dont_change_attack = False
    x = -10

    start_music = True
    pygame.mixer.stop()
    pygame.mixer.music.load(music_arr[4])
    pygame.mixer.music.play(-1, 0.0, 4000)

    has_changed_music = False
    music_change_time = 1000
    music_time_frames = 60


pygame.display.set_caption('Particle Getaway')
test_font = pygame.font.Font(None, 50)
title_surf = test_font.render('Particle Getaway', False, (64, 64, 64))
title_rect = title_surf.get_rect(midbottom=(400, 50))

instr_surf = test_font.render('Press Space to start', False, (64, 64, 64))
instr_rect = title_surf.get_rect(midbottom=(330, 150))

# attack_main_arr = #g
attack_order = [1, 2, 3, 0, 2, 3, 2, 4, 3, -1, 1, 2, 3, 0, 2, 3, 2, 4, 3, 1, 2, 3, 0, 2, 3, 2, 4, 3, 1, 2, 3, 0, 2, 3,
                2, 4, 3, 1, 2, 3, 0, 2, 3, 2, 4, 3]
if SET_THIS_VARIABLE_TO_FALSE:
    attack_order.insert(0, -1)
# boss_test = True
# if boss_test == False:
#    print('NOT TESTING BOSSFIGHT')
# Player(player_info[0].copy(),player_info[1],player_info[2].copy(),player_info[3].copy(),player_info[4].copy(),player_info[5],False)
set_attack_order = [1, 2, 3, 0, 2, 3, 2, 4, 3, -1, ]
mini_attack_homing_completed = 0


def dist(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def dist_squared(x1, y1, x2, y2):
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


def linePoint(x1, y1, x2, y2, px, py):
    d1 = dist(px, py, x1, y1)
    d2 = dist(px, py, x2, y2)
    lineLen = dist(x1, y1, x2, y2)
    buffer = 0.1
    if (d1 + d2 >= lineLen - buffer and d1 + d2 <= lineLen + buffer):
        return True
    return False

    return 0


def pointCircle(px, py, cx, cy, r):
    distX = px - cx
    distY = py - cy
    distance = math.sqrt((distX * distX) + (distY * distY))
    if (distance <= r):
        return True
    return False


def line_circle_collision(x1, y1, x2, y2, cx, cy, r):
    pass
    inside1 = pointCircle(x1, y1, cx, cy, r)
    inside2 = pointCircle(x2, y2, cx, cy, r)
    if (inside1 or inside2):
        return True
    distX = x1 - x2
    distY = y1 - y2
    temp_len = math.sqrt((distX ** 2) + (distY ** 2))
    dot = ((cx - x1) * (x2 - x1) + (cy - y1) * (y2 - y1)) / (temp_len ** 2)

    closestX = x1 + dot * (x2 - x1)
    closestY = y1 + dot * (y2 - y1)

    onSegment = linePoint(x1, y1, x2, y2, closestX, closestY)
    if (not onSegment): return False

    distX = closestX - cx
    distY = closestY - cy
    distance = math.sqrt((distX * distX) + (distY * distY))
    distance += 1
    if (distance <= r):
        return True
    return False


# For attack 4(spiral but delayed):
check_ring = 0

# For attack 3 (homing):
projectile_object_homing = Homing()
temp_choice = 0
dont_change_attack = False


# not neccessarily reserved for shapes
# just keeping track of info for a point (to be used for lines and other needs)
class Shape_pt:
    def __init__(self, pos_x, pos_y, center_x, center_y, dist=0, angle=0):
        self.x = pos_x
        self.y = pos_y
        self.center_x = center_x  # don't change this unless you want to move shape's center
        self.center_y = center_y  # don't change this unless you want to move shape's center
        self.dist = dist
        self.angle = angle

        self.pos = [self.x, self.y]

    def update_pt(self, angle_increment=0, new_dist=-1, new_center_x='I', new_center_y='I'):
        if new_center_x != 'I':
            self.center_x = new_center_x
        if new_center_y != 'I':
            self.center_y = new_center_y
        if new_dist != -1:
            self.dist = new_dist
        self.angle += angle_increment
        self.angle = self.angle % (2 * math.pi)

        self.x = math.cos(self.angle) * self.dist + self.center_x
        self.y = math.sin(self.angle) * self.dist + self.center_y

        self.pos = [self.x, self.y]


# dummy_laser = Projectile2(0,0,0,0,(255,255,255),5,True)

# For attack x == 2 final iteration (circle - line)
# note - not actual full code for when x == 2, just the part thats added on
# (this part was added later on than original)
class Boss_square(Movement):
    def __init__(self):
        super().__init__(width // 2, height // 2)
        self.center = self.pos

        self.HAS_NOT_STARTED = -1  # not used for anything as of now
        self.FADE_IN_SQUARE = 0  # don't change vars w/ all uppercase letters
        self.ROTATE_TO_ZERO = 1
        self.RAIN_1 = 2
        self.DASH_1 = 3
        self.DASH_2 = 4
        self.CHR = 5  # christmas attack
        self.MT_SPHERES_1 = 6  # mutant attack (from Mutant boss - Fargo's Souls mod of Terraria) - not implemented fully
        self.LASER_1 = 8
        self.HOVER_1 = 9
        self.HOVER_0 = 10
        self.PATTERN_1 = 11
        self.HOMING_1 = 12
        self.MT_SPHERES_OG_1 = 7
        self.MT_SPHERES_OG_2 = 13
        self.MT_SPHERES_OG_3 = 14
        self.ROTATE_1 = 15
        self.ROTATE_2 = 16
        self.RANDOM_1 = 17

        self.COLLIDE_WALLS = 0
        self.COLLIDE_OUTSIDE = 1

        # attack_order =
        self.ATTACK_ARR = [self.FADE_IN_SQUARE,
                           self.MT_SPHERES_1,
                           self.RAIN_1, self.MT_SPHERES_OG_1,
                           self.CHR, self.MT_SPHERES_OG_2,
                           self.DASH_2, self.LASER_1,
                           self.DASH_1, self.MT_SPHERES_OG_3,
                           self.HOMING_1, self.PATTERN_1,
                           self.HOVER_0, self.HOVER_1,
                           # self.ROTATE_1,self.ROTATE_2,
                           self.RANDOM_1]
        if SET_THIS_VARIABLE_TO_FALSE:
            self.ATTACK_ARR.insert(1, self.HOMING_1)

        self.ATTACK_INDEX_RETURN = 1
        self.attack_index = 0

        self.DASH_INVALID_DIST = -1
        # self.DASH = insert num here

        self.projectiles: list[Projectile] = []

        # this can be used to bypass the automatic projectile deletion after an attack
        # by just using .extend everything inside the carry arr into the projectiles arr in an initiailzer
        self.carry_over_projectiles: list[Projectile] = []

        self.num_projectiles = 0
        self.timer = 0
        self.current_attack = self.FADE_IN_SQUARE  # change this to affect starting attack
        self.finishing_attack = False

        # Info for dash attack
        self.dash_pos_x = 'I'
        self.dash_pos_y = 'I'
        self.dash_angle = 'I'
        self.dash_change_x = 'I'
        self.dash_change_y = 'I'
        self.DASH_DEFAULT_DIST = 300
        self.DASH_DEFAULT_SPEED = 10
        self.dash_started = False

        # Info for delaying time
        self.delay_timer = 0

        # info for visuals
        self.is_attack = False
        self.current_color = (255, 255, 255)
        self.current_width = 3

        # info for square creation and points
        self.angle = 0

        # NEVER CHANGE THIS - just pass a parameter of a certain angle to self.update_radius_angle_points()
        self.angle_increment = math.pi * (1 / 180)

        self.timer = 0

        self.min_dist = 0  # change this to affect min square radius
        self.dist_current = 0  # change to affect if square starts from point center or not
        self.dist_increment = 1
        self.max_dist = 150
        self.has_changed = False
        self.is_growing = True

        self.pt_1 = Shape_pt(self.center.x, self.center.y, self.center.x, self.center.y, 0, math.pi / 4)
        self.pt_2 = Shape_pt(self.center.x, self.center.y, self.center.x, self.center.y, 0, 3 * math.pi / 4)
        self.pt_3 = Shape_pt(self.center.x, self.center.y, self.center.x, self.center.y, 0, 5 * math.pi / 4)
        self.pt_4 = Shape_pt(self.center.x, self.center.y, self.center.x, self.center.y, 0, 7 * math.pi / 4)

        # for rotate_times

        self.amount_rotated = 0
        self.rotate_times_timer = 0

        # for projectile_rain_attack_1
        self.temp_check_rotate = 0

        self.attack_started = False  # make sure to set this to True whenever making initialzer function

        # INFO FOR MAIN ATTACKS WHICH ARE ONLY CALLED IN MAIN AND NOWHERE ELSE BELOW
        # INFO FOR MAIN ATTACKS WHICH ARE ONLY CALLED IN MAIN AND NOWHERE ELSE BELOW
        # INFO FOR MAIN ATTACKS WHICH ARE ONLY CALLED IN MAIN AND NOWHERE ELSE BELOW

    def attack_player(self):
        if self.is_attack:
            # self.current_width = 6
            if self.proj_collide_square(player):
                player.lose_health()

    def delay_time(self, frames_total, is_attack=False):
        # 60 frames per second
        self.delay_timer += 1

        self.is_attack = is_attack

        if self.delay_timer >= frames_total:
            self.delay_timer = 0
            return True
        return False

    def set_angle_points(self, new_angle='I'):
        if new_angle == 'I':
            new_angle = self.angle
        self.angle = new_angle
        self.pt_1.angle = new_angle + math.pi / 4
        self.pt_2.angle = self.pt_1.angle + math.pi / 2
        self.pt_3.angle = self.pt_2.angle + math.pi / 2
        self.pt_4.angle = self.pt_3.angle + math.pi / 2

    def update_points(self, should_rotate=True, rotate_incr='I'):
        if rotate_incr == 'I':
            rotate_incr = self.angle_increment
        if not should_rotate:
            rotate_incr = 0
        self.angle += rotate_incr
        self.angle = self.angle % (2 * math.pi)
        self.pt_1.update_pt(rotate_incr, self.dist_current, self.center.x, self.center.y)
        self.pt_2.update_pt(rotate_incr, self.dist_current, self.center.x, self.center.y)
        self.pt_3.update_pt(rotate_incr, self.dist_current, self.center.x, self.center.y)
        self.pt_4.update_pt(rotate_incr, self.dist_current, self.center.x, self.center.y)

    def proj_collide_square(self, proj):
        temp_return_1 = line_circle_collision(self.pt_1.x, self.pt_1.y, self.pt_2.x, self.pt_2.y, proj.pos[0],
                                              proj.pos[1], proj.radius)
        temp_return_2 = line_circle_collision(self.pt_2.x, self.pt_2.y, self.pt_3.x, self.pt_3.y, proj.pos[0],
                                              proj.pos[1], proj.radius)
        temp_return_3 = line_circle_collision(self.pt_3.x, self.pt_3.y, self.pt_4.x, self.pt_4.y, proj.pos[0],
                                              proj.pos[1], proj.radius)
        temp_return_4 = line_circle_collision(self.pt_4.x, self.pt_4.y, self.pt_1.x, self.pt_1.y, proj.pos[0],
                                              proj.pos[1], proj.radius)
        return max(temp_return_1, temp_return_2, temp_return_3, temp_return_4)

    # intended for not the
    def projectiles_collide_square(self, proj_list='I', collision_method='I'):
        if collision_method == 'I':
            collision_method = self.COLLIDE_WALLS
        index = 0
        if proj_list == 'I':
            proj_list = self.projectiles
        if collision_method == self.COLLIDE_WALLS:
            while (index < len(proj_list)):
                if self.proj_collide_square(proj_list[index]):
                    del proj_list[index]
                else:
                    index += 1
        elif collision_method == self.COLLIDE_OUTSIDE:
            while (index < len(proj_list)):
                if dist(proj_list[index].pos[0], proj_list[index].pos[1], self.center.x,
                        self.center.y) > self.dist_current / (math.sqrt(2)):
                    del proj_list[index]
                else:
                    index += 1
        else:
            print('invalid collision method')
            exit()

    def draw_square(self, color=None, width=None):
        if color is None:
            color = self.current_color
        if width is None:
            width = self.current_width
        pygame.draw.line(screen, color, (self.pt_1.x, self.pt_1.y), (self.pt_2.x, self.pt_2.y), width)
        pygame.draw.line(screen, color, (self.pt_2.x, self.pt_2.y), (self.pt_3.x, self.pt_3.y), width)
        pygame.draw.line(screen, color, (self.pt_3.x, self.pt_3.y), (self.pt_4.x, self.pt_4.y), width)
        pygame.draw.line(screen, color, (self.pt_4.x, self.pt_4.y), (self.pt_1.x, self.pt_1.y), width)

    def update_radius_angle_points(self, should_change_radius_default=True, should_rotate=True, rotate_incr='I',
                                   increase_to='I', decrease_to='I', dist_increment='I', should_draw=True):
        # dist_increment only changes things when manually setting radius
        # (dist increment when fading circle in from start can be adjusted in initial class constructor)

        # Don't give a value for both increase to and decrease to...

        if should_change_radius_default:
            if self.is_growing:
                if self.dist_current < self.max_dist:
                    self.dist_current += self.dist_increment
                else:
                    self.has_changed = True
                    self.is_growing = False
            else:
                if self.dist_current > self.min_dist:
                    self.dist_current -= self.dist_increment
                else:
                    self.has_changed = True
                    self.is_growing = True
        else:
            self.has_changed = True
            if dist_increment == 'I':
                dist_increment = self.dist_increment
            if increase_to != 'I' and decrease_to != 'I':
                print('you set the radius of square to both increase and decrease to !!!!!')
            if increase_to != 'I':
                if self.dist_current < increase_to:
                    self.has_changed = False
                    self.dist_current += dist_increment

            if decrease_to != 'I':
                if self.dist_current > decrease_to:
                    self.has_changed = False
                    self.dist_current -= dist_increment

        self.update_points(should_rotate, rotate_incr)
        if should_draw: self.draw_square()
        return self.has_changed

    def rotate_times(self, rotate_incr, rotate_amount_desired, angle_desired='I', rotate_time_frames='I'):
        if rotate_time_frames != 'I':
            if self.rotate_times_timer >= rotate_time_frames:
                self.rotate_times_timer = 0
                return True

        # if self.rotate_times_timer*rotate_incr> 120*math.pi:
        #     self.rotate_times_timer = 0
        #     self.amount_rotated +=1

        self.rotate_times_timer += 1
        self.angle = (self.angle) % (2 * math.pi)
        self.update_radius_angle_points(False, True, rotate_incr)
        if self.amount_rotated >= rotate_amount_desired:
            if angle_desired == 'I':
                return True
            is_close = False
            if math.isclose((angle_desired) % (2 * math.pi), self.angle, abs_tol=rotate_incr):
                is_close = True
            elif math.isclose((angle_desired + math.pi / 2) % (2 * math.pi), self.angle, abs_tol=rotate_incr):
                is_close = True
            elif math.isclose((angle_desired + math.pi) % (2 * math.pi), self.angle, abs_tol=rotate_incr):
                is_close = True
            elif math.isclose((angle_desired + 3 * math.pi / 2) % (2 * math.pi), self.angle, abs_tol=rotate_incr):
                is_close = True

            if is_close:
                self.angle = angle_desired
                self.amount_rotated = 0
                self.rotate_times_timer = 0
                self.set_angle_points()
                return True
        return False

    def ring(self, amount_proj, speed_proj, color_proj, should_glow, radius, acceleration_num=0,
             should_close_player=False, close_player_amount=0, should_home_player=False,
             start_from_center=False, angle=0, projectile_list_append_to='I', add_vel_x=0, add_vel_y=0,
             start_pos_x='I', start_pos_y='I', player_pos='I', add_acc_x=0, add_acc_y=0, end_angle=2 * math.pi,
             dist_from='I'):
        if dist_from == 'I':
            dist_from = self.dist_current
        if player_pos == 'I':
            player_pos = (player.pos[0], player.pos[1])
        if start_pos_x == 'I':
            start_pos_x = self.center.x
        if start_pos_y == 'I':
            start_pos_y = self.center.y
        angle_increment = end_angle / amount_proj
        if should_home_player:
            print('add homing functionality')
            exit()
        angle_ring = angle
        for i in range(amount_proj):
            if start_from_center:
                temp_pos_x = start_pos_x
                temp_pos_y = start_pos_y
            else:
                temp_pos_x = start_pos_x + math.cos(angle_ring) * dist_from
                temp_pos_y = start_pos_y + math.sin(angle_ring) * dist_from
            angle_ring += angle_increment
            change_x = math.cos(angle_ring) * speed_proj
            change_y = math.sin(angle_ring) * speed_proj
            if should_close_player:
                angle_to_player = math.atan2(temp_pos_y - player_pos[1], temp_pos_x - player_pos[0])
                acceleration_x = -math.cos(angle_to_player) * close_player_amount
                acceleration_y = -math.sin(angle_to_player) * close_player_amount
            else:
                acceleration_x = change_x * acceleration_num
                acceleration_y = change_y * acceleration_num
            temp_projectile = Projectile1([temp_pos_x, temp_pos_y], radius,
                                          [change_x + add_vel_x, change_y + add_vel_y],
                                          [acceleration_x + add_acc_x, acceleration_y + add_acc_y], color_proj,
                                          should_glow)
            if projectile_list_append_to == 'I':
                self.projectiles.append(temp_projectile)
            else:
                projectile_list_append_to.append(temp_projectile)

    def initialize_dash(self, dist, speed, to_player=True, new_pos_x='I', new_pos_y='I'):
        self.is_attack = True
        if to_player:
            self.dash_pos_x = player.pos[0]
            self.dash_pos_y = player.pos[1]
        else:
            self.dash_pos_x = new_pos_x
            self.dash_pos_y = new_pos_y

        self.dash_angle = math.atan2(self.dash_pos_y - self.center.y, self.dash_pos_x - self.center.x)
        if to_player:
            if dist != self.DASH_INVALID_DIST:
                self.dash_pos_x = math.cos(self.dash_angle) * dist + self.center.x
                self.dash_pos_y = math.sin(self.dash_angle) * dist + self.center.y

        self.dash_change_x = math.cos(self.dash_angle) * speed
        self.dash_change_y = math.sin(self.dash_angle) * speed
        self.dash_started = True

    def dash(self, dist, speed, to_player=True, new_pos_x='I', new_pos_y='I'):
        if not self.dash_started:
            self.initialize_dash(dist, speed, to_player, new_pos_x, new_pos_y)
        self.center.x += self.dash_change_x
        self.center.y += self.dash_change_y
        if math.isclose(self.center.x, self.dash_pos_x, abs_tol=abs(self.dash_change_x)) and math.isclose(self.center.y,
                                                                                                          self.dash_pos_y,
                                                                                                          abs_tol=abs(
                                                                                                              self.dash_change_y)):
            self.dash_started = False
            return True
        return False

    def dash_to_center(self, speed='I'):
        if speed == 'I':
            speed = self.DASH_DEFAULT_SPEED
        return self.dash(self.DASH_INVALID_DIST, speed, False, width // 2, height // 2)

    def initialize_dash_1(self):
        self.attack_started = True

        self.is_attack = False
        self.current_color = (50, 50, 50)
        self.center.x = width // 2
        self.center.y = height // 2

        # self.dist_current = 100

        self.dash_1_index = -1
        self.dash_1_pre_projectiles = []

        self.laser_line = Projectile2(0, 0, 0, 0, [0, 1, 2], 10, True, width // 2, height // 2, self.angle, 0, 500, 500,
                                      True)
        self.projectile_center_laser = Projectile1([0, 0], 15, [0, 0], [0, 0], (255, 50, 0), False, 7.5)

    def dash_1(self):
        if not self.attack_started:
            self.initialize_dash_1()

        finish_attack = False
        if self.dash_1_index == -1:
            self.projectile_rain(250, 0, -0.1, False, self.timer / 50, (randint(50, 60), randint(50, 60), 70),
                                 False, 2, False, int(width - self.timer * width / 500), width, False)
            self.projectile_rain(250, 0, 0.03, False, 1 + self.timer / 70, (randint(50, 60), randint(50, 60), 70),
                                 False, 2, True, int(height - self.timer * 1.7), height, False)
            finish_attack = self.projectile_rain(250, width, -0.03, False, -1 - self.timer / 70,
                                                 (randint(50, 60), randint(50, 60), 70), False, 2, True,
                                                 int(height - self.timer * 1.7), height, False)
            if self.timer < 250:
                pygame.draw.line(screen, (110, 15, 15), (0, int(height - self.timer * 1.6)),
                                 (width, int(height - self.timer * 1.6)), 2)
                pygame.draw.line(screen, (110, 15, 15), (width - 1.6 * self.timer, height),
                                 (width - 1.6 * self.timer, 0), 2)
                if self.timer % 15 == 0 and self.timer > 30:  # and self.timer<220
                    temp_projectile = Projectile1.to_player([width - 1.6 * self.timer, int(height - self.timer * 1.6)],
                                                            20 - self.timer / 25, -3, 0.15, math.pi / 6, (170, 120, 50))
                    self.dash_1_pre_projectiles.append(temp_projectile)
                    temp_projectile = Projectile1.to_player([width - 1.6 * self.timer, int(height - self.timer * 1.6)],
                                                            20 - self.timer / 25, -3, 0.15, -math.pi / 6,
                                                            (170, 120, 50))
                    self.dash_1_pre_projectiles.append(temp_projectile)

                    temp_projectile = Projectile1.to_player([width - 1.6 * self.timer, int(height - self.timer * 1.6)],
                                                            20 - self.timer / 25, 0, 0.15, math.pi / 4, (255, 240, 240)
                                                            , False, 3)
                    self.dash_1_pre_projectiles.append(temp_projectile)
                    temp_projectile = Projectile1.to_player([width - 1.6 * self.timer, int(height - self.timer * 1.6)],
                                                            20 - self.timer / 25, 0, 0.15, -math.pi / 4,
                                                            (255, 240, 240), False, 3)
                    self.dash_1_pre_projectiles.append(temp_projectile)
                if self.timer % 40 == 0 and self.timer > 45:  # and self.timer < 220
                    temp_projectile = Projectile1.to_player([width - 1.6 * self.timer, int(height - self.timer * 1.6)],
                                                            20 - self.timer / 25, 8, -0.04, 0, (255, 180, 160))
                    self.dash_1_pre_projectiles.append(temp_projectile)

                pygame.draw.circle(screen, (160, 120, 120), [width - 1.6 * self.timer, int(height - self.timer * 1.6)],
                                   50 - self.timer / 10)

            if self.timer >= 250:
                finish_attack = True
                self.current_color = (30, 120, 180)
        if self.dash_1_index == 0:
            finish_attack = self.dash(self.DASH_INVALID_DIST, self.DASH_DEFAULT_SPEED / (4), False,
                                      width - self.dist_current, self.dist_current)
        elif self.dash_1_index in [1, 5]:
            finish_attack = self.dash(self.DASH_INVALID_DIST, self.DASH_DEFAULT_SPEED / (2.6), False, self.dist_current,
                                      self.dist_current)
        elif self.dash_1_index in [2, 6]:
            finish_attack = self.dash(self.DASH_INVALID_DIST, self.DASH_DEFAULT_SPEED / (2.8 * 2), False,
                                      self.dist_current, height - self.dist_current)
        elif self.dash_1_index in [3, 7]:
            finish_attack = self.dash(self.DASH_INVALID_DIST, self.DASH_DEFAULT_SPEED / (2.6), False,
                                      width - self.dist_current, height - self.dist_current)
        elif self.dash_1_index in [4, 8]:
            finish_attack = self.dash(self.DASH_INVALID_DIST, self.DASH_DEFAULT_SPEED / (2.8 * 2), False,
                                      width - self.dist_current, self.dist_current)
        elif self.dash_1_index == 9:
            finish_attack = self.dash_to_center()

        if self.dash_1_index < 10 and self.dash_1_index >= 0:
            self.laser_line.angle_from_center = math.atan2(self.center.y - self.laser_line.center_y,
                                                           self.center.x - self.laser_line.center_x)
            self.laser_line.dist_from_center_1 = dist(self.center.x, self.center.y, self.laser_line.center_x,
                                                      self.laser_line.center_y)

            self.laser_line.update(True, True, self.dash_1_index > 0)

            pygame.draw.line(screen, (255, 255, 255), (self.pt_1.x, self.pt_1.y), (self.pt_3.x, self.pt_3.y), 4)
            pygame.draw.line(screen, (255, 255, 255), (self.pt_2.x, self.pt_2.y), (self.pt_4.x, self.pt_4.y), 4)

            self.projectile_center_laser.pos = [self.center.x, self.center.y]
            self.projectile_center_laser.draw()

            pygame.draw.circle(screen, (255, 255, 255), (self.center.x, self.center.y), 25)

        if finish_attack:
            if self.dash_1_index < 9 and self.dash_1_index >= 0:
                self.ring(15, 2, (140, 220, 255), False, 10, 0, True, 1, False, False, 0, 'I', 0, 0, 'I', 'I',
                          [width - self.center.x, height - self.center.y])
                self.ring(3, 0.45, (30, 40, 45), False, 30, -0.02, True, 0.15, False, False, 0)
                self.ring(3, 0.25, (30, 40, 45), False, 30, -0.02, True, 0.15, False, False, 0.4 * math.pi)
                self.ring(3, 0, (30, 40, 45), False, 30, -0.02, True, 0.15, False, False, 0.8 * math.pi)
                self.ring(3, -0.25, (30, 40, 45), False, 30, -0.02, True, 0.15, False, False, 1.2 * math.pi)
                self.ring(3, -0.45, (30, 40, 45), False, 30, -0.02, True, 0.15, False, False, 1.6 * math.pi)
                pos_neg = 1
                if self.center.y > height // 2: pos_neg = -1
                self.ring(12, 3, self.current_color, True, 10, 0, True, 0.05, False,
                          False,  # hmm
                          0, 'I', 0, 5 * pos_neg, 'I', 'I', (width // 2, height // 2), 0, -0.12 * pos_neg)
            self.dash_1_index += 1

        projectiles_finish(self.projectiles, True, 75)
        projectiles_finish(self.dash_1_pre_projectiles, True)
        player.collision(self.dash_1_pre_projectiles)

        if self.dash_1_index == 10 and (not self.projectiles):
            return True
        return False

    def projectile_rain(self, time_attack=200, start_pos=0, gravity=0.1, update_list=True,
                        velocity=0, color=(255, 0, 0), should_glow=False, delay=7,
                        attack_from_side=False, low_bound='I', upp_bound='I', proj_collide_square=True):
        if self.timer > time_attack:
            self.finishing_attack = True

        if low_bound == 'I':
            low_bound = 0
        if not attack_from_side:
            if upp_bound == 'I':
                upp_bound = width
        else:
            if upp_bound == 'I':
                upp_bound = height

        if proj_collide_square: self.projectiles_collide_square()

        projectiles_finish(self.projectiles, update_list)
        if not self.finishing_attack:
            if self.timer % delay == 0:
                if not attack_from_side:
                    temp_projectile = Projectile1([randint(low_bound, upp_bound), start_pos], randint(10, 15),
                                                  [0, velocity], [0, gravity],
                                                  color, should_glow)
                else:
                    temp_projectile = Projectile1([start_pos, randint(low_bound, upp_bound)], randint(10, 15),
                                                  [velocity, 0], [gravity, 0],
                                                  color, should_glow)
                self.projectiles.append(temp_projectile)
        if self.projectiles or (not self.finishing_attack):
            return False
        return True

    def rain_1(self):
        if not self.temp_check_rotate:
            self.temp_check_rotate = 0
            self.current_color = (250, 80, 80)
            self.is_attack = False
            self.d_homing_pointing_to_follow(3, 0.02, math.pi)
            self.rain_1_time_additive = 0
            self.rain_1_time_mult = 10
            self.rain_1_dist_add = 100

            if self.timer > 100:
                self.temp_check_rotate = True
                self.timer = 0
            else:
                self.dist_current = max(self.dist_current - 1, 75)
                self.update_radius_angle_points(False, True, 0.1)

        if self.temp_check_rotate:
            self.update_radius_angle_points(False, True)
            self.move()
            self.is_attack = True
            self.current_color = (255, 0, 0)
            temp_finish_attack_1 = self.projectile_rain(600, 0, 0.2, True, 0, (255, randint(50, 100), randint(0, 50)),
                                                        False, 5, False, (self.timer * 20) % (width + 400),
                                                        (self.timer * 20) % (width + 400) + 1)
            temp_finish_attack_2 = self.projectile_rain(600, height, -0.05, False, 0,
                                                        (255, randint(0, 50), randint(50, 100)),
                                                        False, 5, False,
                                                        width - (self.timer * self.rain_1_time_mult) % (
                                                                width + self.rain_1_time_additive) - self.rain_1_dist_add,
                                                        width - (self.timer * self.rain_1_time_mult) % (
                                                                width + self.rain_1_time_additive))
            # if temp_finish_attack_1 and temp_finish_attack_2:
            #     self.temp_check_rotate = 0

            if temp_finish_attack_1 and temp_finish_attack_2:
                self.temp_check_rotate = False
                self.current_color = (250, 80, 80)
                self.timer = 0
                self.is_attack = False
                return True
        else:
            return False

    def initialize_dash_2(self):
        self.attack_started = True

        self.is_attack = True  # forces collision

        self.center.x = width // 2
        self.center.y = height // 2

        self.dash_2_index = 0
        self.dash_2_speed = 2.2
        self.dash_2_num = 7  # approx how many dashes
        self.has_dashed_center = False
        self.current_color = (180, 220, 255)
        self.projectiles_inside = []
        self.dash_2_ring = []

    def dash_2(self):
        if not self.attack_started:
            self.initialize_dash_2()

        finish_attack = False
        finish_rain = False

        if finish_attack:
            self.dash_2_index += 1

        # right here is just boss movement and raining projectiles inside if statement
        if self.dash_2_index < self.dash_2_num:
            if self.dash_2_index == 0:
                finish_attack = self.update_radius_angle_points(False, True, 'I', 150, 'I', 3)

            elif self.dash_2_index == 1:
                finish_attack = self.dash(self.DASH_INVALID_DIST, self.dash_2_speed, False, width - self.dist_current,
                                          height - self.dist_current)

            elif self.dash_2_index % 2 == 1:
                finish_attack = self.dash(self.DASH_INVALID_DIST, self.dash_2_speed, False, self.dist_current,
                                          height - self.dist_current)

            elif self.dash_2_index % 2 == 0:
                finish_attack = self.dash(self.DASH_INVALID_DIST, self.dash_2_speed, False, width - self.dist_current,
                                          height - self.dist_current)

            if self.timer % 5 == 0:
                temp_speed_x = self.dash_change_x / 1.3
                temp_speed_y = self.dash_change_y / 1.3
                self.ring(7, 2, self.current_color, False, 3, 0, False, 0, False, True, self.angle,
                          self.projectiles_inside, temp_speed_x, temp_speed_y)
            if self.timer % 252 > 40:
                pygame.draw.circle(screen, (90, 90, 170), [self.center.x, self.center.y], ((self.timer - 40) % 252) / 2)
            if self.timer % 252 == 0:
                self.dist_current = 100
                self.ring(15, -2, (20, 20, 50), False, 20, 0, True, 0.13, False, False, 0, self.dash_2_ring)
                self.ring(15, -2, (20, 20, 50), False, 20, 0, True, -0.13, False, False, 0, self.dash_2_ring)
                self.dist_current = 150

            self.projectile_rain(8000, 0, -0.02, True, randint(3, 5) / 2, (randint(140, 180), randint(180, 220), 255),
                                 False, 3)
            self.projectile_rain(8000, 0, -0.02, False, randint(2, 4) / 2, (randint(140, 180), randint(180, 220), 255),
                                 False, 5, True)
            self.projectile_rain(8000, width, 0.02, False, -randint(2, 4) / 2,
                                 (randint(140, 180), randint(180, 220), 255), False, 5, True)
        else:
            if not self.has_dashed_center:
                finish_attack = self.dash_to_center()
            finish_rain = self.projectile_rain(0)

        # inside this if sxtatement is where the rings of projectiles are created
        if finish_attack and self.dash_2_index != self.dash_2_num:
            if self.dash_2_index != 0: self.ring(30, 6, (180, 150, 255), True, 10, 0, True, -0.2, False, False, 0,
                                                 self.dash_2_ring, 0, 0, 'I', 'I')
            if self.dash_2_index != 0: self.ring(45, 8, (180, 150, 255), True, 10, 0, True, -0.08, False, False, 0,
                                                 self.dash_2_ring, 0, 0, 'I', 'I')
            if self.dash_2_index != 0: self.ring(10, -1.3, (140, 180, 170), True, 7, 0, True, 0.09, False, False, 0,
                                                 self.dash_2_ring, 0, 0, 'I', 'I')
            if self.dash_2_index != 0: self.ring(20, -2.2, (130, 60, 90), True, 6, 0, False, 0.09, False, False, 0,
                                                 self.dash_2_ring, 0, 0, 'I', 'I')
            self.dash_2_index += 1
        # this elif statement is where I modify the accleration/velocity
        elif finish_attack:
            self.has_dashed_center = True
            for projectile in self.projectiles:
                projectile.acceleration[0] *= 7
                projectile.acceleration[1] *= 7
            for projectile in self.dash_2_ring:
                if projectile.color == (130, 60, 90):
                    projectile.velocity[0] *= 3
                    projectile.velocity[1] *= 3
                else:
                    projectile.acceleration[0] *= 2
                    projectile.acceleration[1] *= 2
        player.collision(self.dash_2_ring)
        projectiles_finish(self.dash_2_ring, True)

        player.collision(self.projectiles_inside)
        self.projectiles_collide_square(self.projectiles_inside, self.COLLIDE_OUTSIDE)
        projectiles_finish(self.projectiles_inside, True)
        self.update_radius_angle_points(False, True, self.angle_increment * 3)
        if finish_rain and (not self.dash_2_ring):
            # self.dash_2_ring = [] # uncomment this if theres errors with this attacks projectiles not dissapearing
            # or some other type of proj related error
            return True
        return False
        self.is_attack = True

        self.fall_index

    # Christmas attack - chr
    def initialize_chr(self):
        self.attack_started = True

        self.is_attack = True  # force collision

        self.chr_FALL = 0
        self.chr_PINES = 1
        self.chr_SNOW = 2

        self.chr_index = 0
        self.chr_attack_type = 0
        self.chr_snow_color = (250, 250, 250)
        self.chr_pines_color = (30, 100, 30)
        self.chr_pines_proj = []
        self.chr_snow_proj = []

        self.center.x = width // 2
        self.center.y = 0
        self.dist_current = 50
        self.set_angle_points(0)

        self.chr_temp_index = 0

    def chr(self):
        if not self.attack_started:
            self.initialize_chr()

        finish_attack = False
        if self.chr_attack_type == self.chr_FALL:
            finish_attack = self.dash(self.DASH_INVALID_DIST, 15, False, self.center.x, height + self.dist_current)

        elif self.chr_attack_type == self.chr_PINES:
            for projectile in self.chr_pines_proj:
                projectile.update()
                if projectile.pos[1] <= height: continue
                for j in range(5):
                    for i in range(8):
                        temp_projectile = Projectile1([projectile.pos[0], -i * 5 - 150 * j], 10, [0, 15], [0, 0],
                                                      self.chr_snow_color, False)
                        self.chr_snow_proj.append(temp_projectile)

            finish_attack = not self.chr_pines_proj
        elif self.chr_attack_type == self.chr_SNOW:
            finish_attack = not self.chr_snow_proj

        if finish_attack:
            self.chr_attack_type += 1

            if self.chr_attack_type == self.chr_PINES:
                self.is_attack = False
                self.ring(27, 5, self.chr_pines_color, False, 5, 0, False, 0, False,
                          False, -math.pi, self.chr_pines_proj, 0, -8, self.center.x, height + self.dist_current / 2,
                          'I', 0, 0.19, math.pi)
                self.ring(20, 7, (255, 255, 255), True, 5, 0, False, 0, False,
                          False, -math.pi, self.projectiles, 0, -10, self.center.x, height, 'I',
                          0, 0.3, math.pi)
            if self.chr_attack_type == 3:
                self.chr_temp_index += 1
                self.is_attack = True
                self.chr_attack_type = self.chr_FALL
                self.center.x = randint(100, width - 100)
                self.center.y = 0

        projectiles_finish(self.chr_snow_proj, True, 500)
        projectiles_finish(self.chr_pines_proj, False)
        projectiles_finish(self.projectiles, True, 200)

        player.collision(self.chr_pines_proj)
        player.collision(self.chr_snow_proj)
        player.collision(self.projectiles)

        if self.chr_temp_index >= 3:
            self.center.x = width // 2
            self.center.y = height // 2
            self.dist_current = self.max_dist
            return True

        if self.chr_attack_type == 3:
            self.update_radius_angle_points(False, False, 'I', 'I', 'I', 'I', False)
        else:
            self.update_radius_angle_points(False, False)

        return False

    # inspiration from mutant attack (from Mutant boss - Fargo's Souls mod of Terraria)
    # used for both og and normal mt_spheres
    # edit: this is absolutely nothing like how the mutant attack is and I don't feel like changing it anyway :)
    def initialize_mt_spheres_og(self, index=0, reset_arr=True):
        self.current_color = (255, 255, 255)

        self.attack_started = True
        self.is_attack = False

        self.center.x = width // 2
        self.center.y = height // 2

        self.mt_spheres_timer = 0
        self.mt_spheres_num_arr = [-3, 3], [-5, 7], [-2, 1.5], [-1.7, 1.5], [2, -0.45, -0.8], [-5, -2], [3, 2, -4], [
            -0.1, 3 / 2, 8 / 2, -8 / 2]
        self.mt_spheres_num2_arr = [-1], [2, 1.5], [2, 1.5], [-1.7, -1.5], [0.4, -0.4], [-0.3, 0.4], [0.3, -0.3, 0], [
            -0.4, 0.6]
        self.mt_spheres_angle_incr_arr = self.angle_increment, self.angle_increment / 1.5, self.angle_increment / 1.3, \
                                         -self.angle_increment, self.angle_increment * 3, self.angle_increment, \
                                         self.angle_increment, self.angle_increment / 2
        self.mt_spheres_timer_arr = 5, 24, 5, 5, 16, 35, 63, 15
        self.mt_spheres_timer_wait_arr = 300, 400, 350, 400, 550, 600, 800, 1000
        self.mt_spheres_color_arr = [(255, 255, 255), (255, 255, 255)], [(255, 255, 255), (255, 255, 255)], \
                                    [(255, 255, 255), (255, 255, 255)], [(255, 255, 255), (255, 255, 255)], \
                                    [(150, 150, 255), (255, 150, 150), (255, 255, 255)], [(180, 90, 30),
                                                                                          (255, 255, 255)], \
                                    [(255, 255, 255), (255, 255, 255), (140, 50, 210), (255, 255, 255)], \
                                    [(255, 255, 255), (255, 255, 255), (50, 200, 200), (50, 200, 200)]

        self.mt_spheres_num_index = index

        self.mt_spheres_wait_start_attack_time = 25
        self.mt_spheres_telegraph_time = 75
        self.mt_spheres_telegraph_fade_time = 150
        self.mt_spheres_telegraph_color = [80, 20, 20]

        self.angle = self.angle % math.tau
        temp_angle_rotate_amount = (random.uniform(0, math.tau) - self.angle) % math.tau

        self.mt_spheres_1_prior_telegraph_angle_incr = temp_angle_rotate_amount / self.mt_spheres_wait_start_attack_time

        if reset_arr: self.mt_spheres_proj = []
        self.mt_spheres_telegraph: float[Projectile_Rotate] = []

    def mt_spheres_og(self, index, end_index=None):
        if not self.attack_started:
            self.initialize_mt_spheres_og(index)

        if end_index is None:
            end_index = len(self.mt_spheres_num_arr)

        if self.mt_spheres_timer < self.mt_spheres_telegraph_time + self.mt_spheres_wait_start_attack_time:
            proj_list = self.mt_spheres_telegraph
            # for adding proj to telegraph list so no collision w/ player
            # also makes allowing color changes to only telegraph proj and not the main proj
        else:
            proj_list = self.mt_spheres_proj

        if self.mt_spheres_timer > self.mt_spheres_wait_start_attack_time:
            if self.timer % self.mt_spheres_timer_arr[self.mt_spheres_num_index] == 0:
                temp_index = -1
                for num in self.mt_spheres_num_arr[self.mt_spheres_num_index]:
                    temp_index += 1
                    for num2 in self.mt_spheres_num2_arr[self.mt_spheres_num_index]:
                        for pt in [self.pt_1, self.pt_2, self.pt_3, self.pt_4]:
                            temp_color = self.mt_spheres_color_arr[self.mt_spheres_num_index][temp_index]
                            if self.mt_spheres_num_index == 4:
                                if num2 > 0:
                                    temp_color = self.mt_spheres_color_arr[self.mt_spheres_num_index][1]
                                else:
                                    temp_color = self.mt_spheres_color_arr[self.mt_spheres_num_index][0]

                            if self.mt_spheres_timer < self.mt_spheres_telegraph_time \
                                    + self.mt_spheres_wait_start_attack_time:
                                # if true makes proj which are part of telegraph and dark red
                                temp_color = self.mt_spheres_telegraph_color.copy()
                                temp_no_glow = True
                                temp_radius = 10
                            else:
                                temp_no_glow = False  # this if statement runs for normal proj
                                temp_radius = 10

                            temp_projectile = Projectile_Rotate.from_pos(temp_radius, [width // 2, height // 2],
                                                                         temp_color,
                                                                         False, temp_no_glow, 1.5,
                                                                         num2 * self.angle_increment,
                                                                         num, 0, [pt.x, pt.y])
                            proj_list.append(temp_projectile)

            self.update_radius_angle_points(False, True, self.mt_spheres_angle_incr_arr[self.mt_spheres_num_index])
        else:
            self.update_radius_angle_points(False, True, self.mt_spheres_1_prior_telegraph_angle_incr)

        if self.mt_spheres_timer < self.mt_spheres_telegraph_time + self.mt_spheres_wait_start_attack_time:
            projectiles_finish(self.mt_spheres_telegraph, True, 200)
        elif self.mt_spheres_timer <= self.mt_spheres_telegraph_time \
                + self.mt_spheres_telegraph_fade_time + self.mt_spheres_wait_start_attack_time:  # fading to black colors
            projectiles_finish(self.mt_spheres_telegraph, True, 200)
            if self.timer % 15 == 0:
                for proj in self.mt_spheres_telegraph:
                    proj.color[0] = max(0, proj.color[0] - 15 * self.mt_spheres_telegraph_color[
                        0] / self.mt_spheres_telegraph_fade_time)
                    proj.color[1] = max(0, proj.color[1] - 15 * self.mt_spheres_telegraph_color[
                        1] / self.mt_spheres_telegraph_fade_time)
                    proj.color[2] = max(0, proj.color[2] - 15 * self.mt_spheres_telegraph_color[
                        2] / self.mt_spheres_telegraph_fade_time)

        projectiles_finish(self.mt_spheres_proj, True)

        player.collision(self.mt_spheres_proj)

        self.mt_spheres_timer += 1
        if self.mt_spheres_timer > self.mt_spheres_timer_wait_arr[self.mt_spheres_num_index] \
                + self.mt_spheres_telegraph_time:
            self.mt_spheres_num_index += 1
            self.initialize_mt_spheres_og(self.mt_spheres_num_index, True)
            if self.mt_spheres_num_index >= end_index:
                return True
        return False

    def initialize_mt_spheres_1(self):
        self.attack_started = True
        self.is_attack = False
        self.center.x = width // 2
        self.center.y = height // 2

    # meh attack - if bossfight too bloated later consider removing this one
    def mt_spheres_1(self):
        if not self.attack_started:
            self.initialize_mt_spheres_1()

        if self.timer % 50 == 0:
            for pt in [self.pt_1, self.pt_2, self.pt_3, self.pt_4]:
                temp_projectile = Projectile3(10, [255, 255, 255], 0.5, self.angle_increment / 2,
                                              [width // 2, height // 2], 0, 0, False, 1.5, True, [pt.x, pt.y])
                self.projectiles.append(temp_projectile)

        if self.timer % 20 == 0:
            for pt in [self.pt_1, self.pt_2, self.pt_3, self.pt_4]:
                temp_projectile = Projectile3(10, [255, 120, 180], 2.5, -self.angle_increment / 2,
                                              [width // 2, height // 2], 0, pt.angle, False)
                self.projectiles.append(temp_projectile)

        projectiles_finish(self.projectiles, True, 150)
        self.update_radius_angle_points(False, True, self.angle_increment * 2 / 2)

        if self.timer > 600:
            return True
        return False

    def initialize_laser_1(self):
        self.attack_started = True
        self.is_attack = False
        self.current_color = (50, 50, 60)

        self.laser_1_lasers = []
        self.laser_1_lasers_2 = []
        self.laser_1_lasers_3 = []
        self.laser_1_rotating_color = (255, 255, 255)

        self.laser_1_counter = -1

        self.dist_current = 200

    def laser_1(self):
        if not self.attack_started:
            self.initialize_laser_1()

        if self.timer % 37 == 1:
            self.laser_1_counter *= -1
            temp_projectile_1 = Projectile1([width // 2, height // 2], 10, [-0.5, self.laser_1_counter * 9],
                                            [0, -self.laser_1_counter / 6], self.laser_1_rotating_color, False, 1.5,
                                            False)
            temp_projectile_2 = Projectile1([width // 2, height // 2], 10, [0.5, self.laser_1_counter * 9],
                                            [0, -self.laser_1_counter / 6], self.laser_1_rotating_color, False, 1.5,
                                            False)

            temp_projectile_laser = Projectile2(0, 0, 0, 0, [0, 1, 1], 20,
                                                False, width // 2, height // 2, 0, 0, 0, 0, False)
            temp_projectile = Projectile5(temp_projectile_1, temp_projectile_2, temp_projectile_laser)
            self.laser_1_lasers_2.append(temp_projectile)

        if self.timer % 37 == 1:
            temp_projectile_1 = Projectile1([width, (self.timer % 100) * 4], 25, [0, 0], [-0.07, 0.01],
                                            self.laser_1_rotating_color, False, 1.5, False)
            temp_projectile_2 = Projectile1([width, (self.timer % 100) * 4 + 120], 25, [0, 0], [-0.1, -0.015],
                                            self.laser_1_rotating_color, False,
                                            1.5, False)
            temp_projectile_laser = Projectile2(0, 0, 0, 0, [0, 1, 1], 20,
                                                False, width // 2, height // 2, 0, 0, 0, 0, True,
                                                self.laser_1_rotating_color)
            temp_projectile = Projectile5(temp_projectile_1, temp_projectile_2, temp_projectile_laser)
            self.laser_1_lasers.append(temp_projectile)

        self.update_radius_angle_points(False, True, self.angle_increment / 2)

        projectiles_finish(self.laser_1_lasers, True, 500)
        projectiles_finish(self.laser_1_lasers_2, True)

        if self.timer > 600:
            return True
        return False

    def initialize_hover_1(self):
        self.attack_started = True

        self.projectiles.extend(self.carry_over_projectiles)
        self.carry_over_projectiles = []
        self.current_color = (255, 255, 255)
        self.is_attack = True
        self.current_width = 8

        self.temp_num_color = 255
        self.temp_num_color2 = 0
        self.temp_num_color_change = -5
        self.temp_num_color_change2 = randint(2, 10)

        self.temp_attack_done = 0
        self.temp_sub_index_pattern_dont_1 = 0
        self.movt_pattern_dont = 1
        self.dist_current = 75

        self.temp_temp_initializer(self.movt_pattern_dont)

        self.temp_wait_time = 500
        self.temp_wait_time_extra = 200

    def temp_temp_initializer(self, index):
        if index == 1:
            self.d_hover(1.0, 0, 350, 0.1, 0.03)
            self.temp_start_acc_num = 0.01
            self.temp_end_acc_num = 1.7
            self.temp_start_speed_cap = 3
            self.temp_end_speed_cap = 15
            self.temp_start_hover_num = 0
            self.temp_end_hover_num = 0.22
            self.temp_start_dist_hover = 350
            self.temp_end_dist_hover = 350
            # original : 1.0, 9, 0.05
            # from 1.0 to 2.0
            # go from 0.1 to 15
            # from 0.05 to 0.1
        elif index == 2:
            self.d_hover(1.0, 0, 200, 5, 0.1)
            self.temp_start_acc_num = 20
            self.temp_end_acc_num = 30
            self.temp_start_speed_cap = 1
            self.temp_end_speed_cap = 12
            self.temp_start_hover_num = 0.01
            self.temp_end_hover_num = 0.09
            self.temp_start_dist_hover = 350
            self.temp_end_dist_hover = 200
            # MAKE SURE T
            # original: 1.0, 10, 0.1
            # go from 1.0 to 3.0
            # go from 5 to 15
            # go from 0.1 to 0.2

    def hover_1(self):
        if not self.attack_started:
            self.initialize_hover_1()

        self.move()
        self.update_radius_angle_points(False, False)  # True, self.angle_increment / 2)

        if (self.movt_pattern_dont in [1, 2]) and self.timer < self.temp_wait_time:
            self.movement.acc_num = self.timer * (
                    self.temp_end_acc_num - self.temp_start_acc_num) / self.temp_wait_time + self.temp_start_acc_num
            self.movement.speed_cap = self.timer * (
                    self.temp_end_speed_cap - self.temp_start_speed_cap) / self.temp_wait_time \
                                      + self.temp_start_speed_cap
            self.movement.hover_num = self.timer * (
                    self.temp_end_hover_num - self.temp_start_hover_num) / self.temp_wait_time \
                                      + self.temp_start_hover_num

            self.movement.dist_hover = self.timer * (
                    self.temp_end_dist_hover - self.temp_start_dist_hover) / self.temp_wait_time \
                                       + self.temp_start_dist_hover
        if self.timer <= 150:
            if self.movt_pattern_dont == 1:
                self.dist_current = (75 + self.timer // 2)
            else:
                self.dist_current = (150 - self.timer // 2)

        self.set_angle_points(math.atan2(self.center.y - player.pt.y, self.center.x - player.pt.x))
        if self.timer > 50 and (
                self.timer % 5 == 0 or (self.movement.acc_mult_negative < 0 and self.movt_pattern_dont == 2)):
            temp_color = (self.temp_num_color, self.temp_num_color2, 255 - self.temp_num_color)
            self.temp_num_color += self.temp_num_color_change
            self.temp_num_color2 += self.temp_num_color_change2

            if self.temp_num_color >= 255:
                self.temp_num_color = 255
                self.temp_num_color_change = -5
            elif self.temp_num_color <= 0:
                self.temp_num_color = 0
                self.temp_num_color_change = 5

            if self.temp_num_color2 >= 255:
                self.temp_num_color2 = 255
                self.temp_num_color_change2 = -randint(2, 10)
            elif self.temp_num_color2 <= 0:
                self.temp_num_color2 = 0
                self.temp_num_color_change2 = randint(2, 10)

            if self.movt_pattern_dont == 2:
                temp_vel = -7;
                temp_acc = 0.2
            else:
                temp_vel = -4;
                temp_acc = 0.2

            if self.movement.acc_mult_negative < 0 and self.movt_pattern_dont == 2:
                temp_vel *= -0.2

        if self.timer > 50 and (
                self.timer % 5 == 0 or (self.movement.acc_mult_negative < 0 and self.movt_pattern_dont == 2)):
            if self.movt_pattern_dont == 1 and self.timer > 100:
                temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                temp_projectile.d_to_player(temp_vel, temp_acc, math.pi * 0.5)
                self.projectiles.append(temp_projectile)

                temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                temp_projectile.d_to_player(temp_vel, temp_acc)
                self.projectiles.append(temp_projectile)

                temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                temp_projectile.d_to_player(temp_vel, temp_acc, -math.pi * 0.5)
                self.projectiles.append(temp_projectile)

                temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                temp_projectile.d_to_player(temp_vel, temp_acc, math.pi)
                self.projectiles.append(temp_projectile)

            elif self.movement.acc_mult_negative < 0 and self.timer > 100 and self.timer % 2 == 0 \
                    and (self.Calc.dist_player(self.center) > self.movement.dist_hover * 0.6):
                temp_temp_color = (temp_color[0] // 2, temp_color[1] // 2, temp_color[2] // 2)
                for temp_angle in [2 * math.pi / 126, -2 * math.pi / 16]:  # [2*math.pi/8,2*math.pi/12]:
                    for temp_temp_angle in (-temp_angle, temp_angle):
                        temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_temp_color, False, 2)
                        temp_projectile.d_to_player(temp_vel, temp_acc * 1.2, math.pi * 0.6 + temp_temp_angle)
                        self.projectiles.append(temp_projectile)

                        temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_temp_color, False, 2)
                        temp_projectile.d_to_player(temp_vel, temp_acc * 1.2, temp_temp_angle)
                        self.projectiles.append(temp_projectile)

                        temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_temp_color, False, 2)
                        temp_projectile.d_to_player(temp_vel, temp_acc * 1.2, -math.pi * 0.6 + temp_temp_angle)
                        self.projectiles.append(temp_projectile)

            if (self.movt_pattern_dont == 2 and (
                    self.Calc.dist_player(self.center) < 1.3 * self.movement.dist_hover and False) or
                self.movement.acc_mult_negative >= 0) or (
                    self.movt_pattern_dont == 1 and self.movement.acc_mult_negative >= 0 and self.timer > 100):
                if self.movt_pattern_dont == 1:
                    temp_vel *= -4
                    temp_acc = -0.3
                    temp_temp_color = (100 + self.timer % 50 // 4, 100, 100)
                    temp_projectile = Projectile(self.center.x, self.center.y, 25, temp_temp_color)
                    temp_projectile.d_to_player(temp_vel * 1.7 *
                                                self.timer / (self.temp_wait_time + self.temp_wait_time_extra),
                                                temp_acc * 1.3)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_color, False, 2)
                    temp_projectile.d_to_player(temp_vel * 0, -temp_acc, math.pi / 10)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_color, False, 2)
                    temp_projectile.d_to_player(temp_vel * 0, -temp_acc, -math.pi / 10)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_color, False, 2)
                    temp_projectile.d_to_player(temp_vel * 0, -temp_acc, math.pi / 3)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_color, False, 2)
                    temp_projectile.d_to_player(temp_vel * 0, -temp_acc, -math.pi / 3)
                    self.projectiles.append(temp_projectile)

                elif self.movement.acc_mult_negative < 0:
                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel, temp_acc, math.pi * 0.8)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel, temp_acc, -math.pi * 0.8)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel, temp_acc)
                    self.projectiles.append(temp_projectile)
                else:
                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel * 1.2, temp_acc * 1.4, math.pi * .9)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel * 1.2, temp_acc * 1.4, -math.pi * .9)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel * 1.2, temp_acc * 1.4)
                    self.projectiles.append(temp_projectile)
                # temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                # temp_projectile.d_to_player(temp_vel, temp_acc, math.pi)
                # self.projectiles.append(temp_projectile)

        if self.timer % (self.temp_wait_time + self.temp_wait_time_extra) == 0:
            self.temp_attack_done += 1
            self.timer = 1
            self.movt_pattern_dont = 3 - self.movt_pattern_dont
            self.temp_temp_initializer(self.movt_pattern_dont)

        Projectile.list_update(self.projectiles, 500, 500)

        if self.temp_attack_done == 2:
            return True
        return False

    def initialize_hover_0(self):
        self.attack_started = True

        self.current_color = (255, 255, 255)
        self.is_attack = True
        self.current_width = 8

        self.carry_over_projectiles = []
        self.temp_num_color = 255
        self.temp_num_color2 = 0
        self.temp_num_color_change = -5
        self.temp_num_color_change2 = randint(2, 10)
        self.temp_attack_done = 0
        self.movt_pattern_dont = 1
        self.dist_current = 75
        if self.movt_pattern_dont == 1:
            self.d_hover(1.0, 0, 350, 9, 0.05)
        else:
            self.d_hover(3.0, 0, 200, 10, 0.1)

    def hover_0(self):
        if not self.attack_started:
            self.initialize_hover_0()

        self.move()
        self.update_radius_angle_points(False, False)

        if self.timer <= 25 and self.movt_pattern_dont == 2:
            self.dist_current = (150 - 3 * self.timer)
        elif self.timer <= 300 and self.movt_pattern_dont == 1:
            self.dist_current = (75 + self.timer // 4)

        if self.timer <= 50 and self.movt_pattern_dont == 1:
            self.movement.dist_hover = 450
        elif self.movt_pattern_dont == 1:
            self.movement.dist_hover = 350

        self.set_angle_points(math.atan2(self.center.y - player.pt.y, self.center.x - player.pt.x))
        if self.timer > 50 and (
                self.timer % 5 == 0 or (self.movement.acc_mult_negative < 0 and self.movt_pattern_dont == 2)):
            temp_color = (self.temp_num_color, self.temp_num_color2, 255 - self.temp_num_color)
            self.temp_num_color += self.temp_num_color_change
            self.temp_num_color2 += self.temp_num_color_change2

            if self.temp_num_color >= 255:
                self.temp_num_color = 255
                self.temp_num_color_change = -5
            elif self.temp_num_color <= 0:
                self.temp_num_color = 0
                self.temp_num_color_change = 5

            if self.temp_num_color2 >= 255:
                self.temp_num_color2 = 255
                self.temp_num_color_change2 = -randint(2, 10)
            elif self.temp_num_color2 <= 0:
                self.temp_num_color2 = 0
                self.temp_num_color_change2 = randint(2, 10)

            if self.movt_pattern_dont == 2:
                temp_vel = -7;
                temp_acc = 0.2
            else:
                temp_vel = -4;
                temp_acc = 0.2

            if self.movement.acc_mult_negative < 0 and self.movt_pattern_dont == 2:
                temp_vel *= -0.2

        if self.timer > 50 and (
                self.timer % 5 == 0 or (self.movement.acc_mult_negative < 0 and self.movt_pattern_dont == 2)):
            if self.movt_pattern_dont == 1 and self.timer > 100:
                temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                temp_projectile.d_to_player(temp_vel, temp_acc, math.pi * 0.5)
                self.projectiles.append(temp_projectile)

                temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                temp_projectile.d_to_player(temp_vel, temp_acc)
                self.projectiles.append(temp_projectile)

                temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                temp_projectile.d_to_player(temp_vel, temp_acc, -math.pi * 0.5)
                self.projectiles.append(temp_projectile)

                temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                temp_projectile.d_to_player(temp_vel, temp_acc, math.pi)
                self.projectiles.append(temp_projectile)

            elif self.movement.acc_mult_negative < 0 and self.timer > 100 and self.timer % 3 == 0:
                temp_temp_color = (temp_color[0] // 2, temp_color[1] // 2, temp_color[2] // 2)
                for temp_angle in [2 * math.pi / 2, 2 * math.pi / 3]:
                    for temp_temp_angle in (-temp_angle, temp_angle):
                        temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_temp_color, False, 2)
                        temp_projectile.d_to_player(temp_vel, temp_acc * 0.5, math.pi * 0.8 + temp_temp_angle)
                        self.projectiles.append(temp_projectile)

                        temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_temp_color, False, 2)
                        temp_projectile.d_to_player(temp_vel, temp_acc * 0.5, temp_temp_angle)
                        self.projectiles.append(temp_projectile)

                        temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_temp_color, False, 2)
                        temp_projectile.d_to_player(temp_vel, temp_acc * 0.5, -math.pi * 0.8 + temp_temp_angle)
                        self.projectiles.append(temp_projectile)

            if (self.movt_pattern_dont == 2) or (
                    self.movt_pattern_dont == 1 and self.movement.acc_mult_negative >= 0 and self.timer > 100):
                if self.movt_pattern_dont == 1:
                    temp_vel *= -4
                    temp_acc = -0.3
                    temp_temp_color = (100 + self.timer % 50 // 4, 100, 100)
                    temp_projectile = Projectile(self.center.x, self.center.y, 25, temp_temp_color)
                    temp_projectile.d_to_player(temp_vel, temp_acc)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_color, False, 2)
                    temp_projectile.d_to_player(temp_vel * 0, -temp_acc, math.pi / 10)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_color, False, 2)
                    temp_projectile.d_to_player(temp_vel * 0, -temp_acc, -math.pi / 10)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_color, False, 2)
                    temp_projectile.d_to_player(temp_vel * 0, -temp_acc, math.pi / 3)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 15, temp_color, False, 2)
                    temp_projectile.d_to_player(temp_vel * 0, -temp_acc, -math.pi / 3)
                    self.projectiles.append(temp_projectile)

                elif self.movement.acc_mult_negative < 0:
                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel, temp_acc, math.pi * 0.8)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel, temp_acc, -math.pi * 0.8)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel, temp_acc)
                    self.projectiles.append(temp_projectile)
                else:
                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel * 1.2, temp_acc * 1.4, math.pi * .9)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel * 1.2, temp_acc * 1.4, -math.pi * .9)
                    self.projectiles.append(temp_projectile)

                    temp_projectile = Projectile(self.center.x, self.center.y, 10, temp_color)
                    temp_projectile.d_to_player(temp_vel * 1.2, temp_acc * 1.4)
                    self.projectiles.append(temp_projectile)

        if (self.timer >= 300 and self.movt_pattern_dont == 2 and self.movement.acc_mult_negative >= 0) or \
                (self.timer % 330 == 0 and self.movt_pattern_dont == 1):
            self.timer = 1
            self.temp_attack_done += 1
            self.movt_pattern_dont = 3 - self.movt_pattern_dont
            if self.movt_pattern_dont == 1:
                self.d_hover(1.0, 0, 350, 9, 0.05)
            else:
                self.d_hover(3.0, 0, 200, 10, 0.1)

        Projectile.list_update(self.projectiles, 500, 500)

        if self.temp_attack_done >= 4:
            self.carry_over_projectiles = self.projectiles
            return True
        return False

    def initialize_pattern_1(self):
        self.attack_started = True
        self.is_attack = False

        self.current_color = (50, 50, 60)
        self.dist_current = 200
        self.pos.x = width // 2
        self.pos.y = height // 2

        self.pattern_1_projectiles: list[Projectile_Rotate] = []
        self.pattern_1_projectiles_red: list[Projectile_Rotate] = []
        self.pattern_1_telegraph: list[Projectile] = []
        self.pattern_1_nums: float[int] = []

    def pattern_1(self):
        if not self.attack_started:
            self.initialize_pattern_1()

        if self.timer < 2545:
            if self.timer > 170:
                if self.timer % 15 == 1:
                    for pt in [self.pt_1, self.pt_2, self.pt_3, self.pt_4]:
                        temp_projectile = Projectile_Rotate(17, pt.pos.copy(), [255, 100, 100], False, False, 2,
                                                            self.angle_increment, math.pi + pt.angle, 1)
                        self.pattern_1_projectiles_red.append(temp_projectile)
                if self.timer % 30 == 1:
                    for pt in [self.pt_1, self.pt_3]:
                        temp_projectile = Projectile_Rotate(17, pt.pos.copy(), [255, 255, 255], False, False, 2,
                                                            -self.angle_increment * 0.7, pt.angle, 0.15)
                        self.pattern_1_projectiles.append(temp_projectile)
            else:
                if self.timer % 3 == 0:
                    for pt in [self.pt_1, self.pt_2, self.pt_3, self.pt_4]:
                        for pos in [[0, 0], [width, 0], [0, height], [width, height], [width, height / 2],
                                    [0, height / 2], [width / 2, 0], [width / 2, height]]:
                            temp_projectile = Projectile(pos[0], pos[1], 3, (255, 0, 0), False, 1.5, True)
                            temp_projectile.d_homing_pointing_to_follow(randint(0, 30) / 10, randint(1, 25) * 0.01, 0,
                                                                        None, 85, pt)
                            self.pattern_1_telegraph.append(temp_projectile)
                if self.timer % 20 == 1 and self.timer < 170:
                    self.pattern_1_nums.append(10)
                if self.timer == 170:
                    for proj in self.pattern_1_telegraph:
                        proj.movement.speed = 12
                        proj.movement.angle_incr = 0

            if self.timer < 400:
                for i in range(len(self.pattern_1_nums)):
                    num = self.pattern_1_nums[i] // 2
                    pygame.draw.circle(screen, (max(0, 100 - num), max(0, 80 - num), max(0, 80 - num))
                                       , player.pos, num, 3)
                    self.pattern_1_nums[i] += 1

                try:
                    self.pattern_1_nums.remove(200)
                except:
                    pass

            Projectile.list_update(self.pattern_1_telegraph, 0, 0, False)

            for proj in self.pattern_1_telegraph:
                if self.Calc.dist_center(proj.pos) < 161:
                    proj.pos.x = width * 2
        elif self.timer < 2645:
            for proj_list in [self.pattern_1_projectiles, self.pattern_1_projectiles_red]:
                for proj in proj_list:
                    proj.pulsate_mult -= 0.009
        else:
            for proj_list in [self.pattern_1_projectiles, self.pattern_1_projectiles_red]:
                for proj in proj_list:
                    proj.color[0] = max(proj.color[0] - 2, 0)
                    proj.color[1] = max(proj.color[1] - 2, 0)
                    proj.color[2] = max(proj.color[2] - 2, 10)
                    proj.radius = max(1, proj.radius - 0.1)
                    proj.no_glow = True

        projectiles_finish(self.pattern_1_projectiles, True, 200)
        projectiles_finish(self.pattern_1_projectiles_red, True, 300)
        self.update_radius_angle_points(False, True, self.angle_increment / 2.1)
        if self.timer < 2545:
            player.collision(self.pattern_1_projectiles)
            player.collision(self.pattern_1_projectiles_red)

        if self.timer > 2900:
            return True
        return False

    def initialize_homing_1(self):
        self.attack_started = True
        self.is_attack = False

        self.current_color = (255, 120, 0)
        self.dist_current = 50
        self.pos.x = width // 2
        self.pos.y = height // 2

        self.homing_1_circ = Projectile3(10, (255, 255, 255), 0, math.pi / 5, [width // 2, height // 2],
                                         250, randint(0, 360) / 360 * math.tau)
        self.homing_1_pt = self.homing_1_circ.pt

        self.d_homing_pointing_to_follow(3, math.pi / 50, 0, None, None, self.homing_1_pt)

        self.homing_1_projectiles: list[Projectile] = []

    def homing_1(self):
        if not self.attack_started:
            self.initialize_homing_1()

        self.move()
        if (self.timer % 3 == 0 or self.timer % 3 == 1):
            temp_rand_green = randint(0, 255)
            if temp_rand_green > 50:
                temp_rand_blue = randint(0, temp_rand_green)
            else:
                temp_rand_blue = randint(0, 100)

            temp_projectile = Projectile(self.pos.x, self.pos.y, 6,
                                         (randint(200, 255), temp_rand_green, temp_rand_blue), False, 5, False)
            temp_projectile.d_homing_pointing_to_diff_pos(3, 0.01 * 3, self.homing_1_pt, 0, None, 110, self.homing_1_pt)
            self.homing_1_projectiles.append(temp_projectile)

        self.homing_1_circ.update(False)

        for proj in self.homing_1_projectiles:
            if self.Calc.dist_player(proj.pos) < 100:
                proj.radius = max(proj.radius - 0.2, 3)
            else:
                proj.radius = min(proj.radius + 0.015, (self.Calc.dist_player(proj.pos)) // 50 + 5)
        Projectile.list_update(self.homing_1_projectiles, 400, 400)

        if self.timer > 1800:
            return True
        self.update_radius_angle_points(False, True, self.angle_increment)
        return False

    def initialize_rotate_1(self):
        self.attack_started = True
        self.is_attack = False

        self.current_color = (130, 140, 150)
        self.dist_current = 100
        self.pos.x = width // 2
        self.pos.y = height // 2
        # self.d_homing_pointing_to_follow(2,0.04,math.pi,50,None)
        # self.d_hover(0.3,60,150,10,3)
        self.d_rotate_from_pos(width // 2, height, CENTER_POINT, 0.03)

        self.rotate_1_projectiles: list[Projectile] = []

    def rotate_1(self):  # rotate_1
        if not self.attack_started:
            self.initialize_rotate_1()

        if self.timer % 20 == 0:
            for pt in [self.pt_1, self.pt_2, self.pt_3, self.pt_4]:
                temp_projectile = Projectile(pt.x, pt.y, 15, (255, 255, 255), False, 2, False, [True, True, True],
                                             [100, 200, 300])
                temp_projectile.d_rotate_stable_from_own_pos(200, 300, self.center, 0.04, 1)
                self.rotate_1_projectiles.append(temp_projectile)

        self.move()
        Projectile.list_update(self.rotate_1_projectiles, 200, 300)

        if self.timer > 1000:
            return True
        self.update_radius_angle_points(False, True, self.angle_increment * self.Calc.dist_player(self.pos) / 50)
        return False

    def initialize_rotate_2(self):
        self.attack_started = True
        self.is_attack = False

        self.current_color = (170, 140, 90)
        self.dist_current = 100
        self.pos.x = width // 2
        self.pos.y = height // 2

        # self.d_rotate_from_pos(width//2,height,CENTER_POINT,0.02)

        self.d_homing_pointing_to_follow(3, 0.02, math.pi * 0, 50, None)
        self.rotate_2_projectiles: list[Projectile] = []
        self.rotate_2_projectiles_2: list[Projectile] = []

    def rotate_2(self):  # rotate_2
        if not self.attack_started:
            self.initialize_rotate_2()

        if self.timer % 7 == 0:
            for pt in [self.pt_1, self.pt_2, self.pt_3, self.pt_4]:
                temp_projectile = Projectile(pt.x, pt.y, 15, (255, 255, 255), False, 2, False, [True, True, True],
                                             [400, 100, 50])
                temp_projectile.d_to_player(-1, 0.04, math.pi / 3)
                self.rotate_2_projectiles.append(temp_projectile)
        if self.timer % 33 == 0:
            for angle in [0, math.pi / 3, -math.pi / 3]:
                temp_projectile = Projectile(self.pos.x, self.pos.y, 15, (255, 255, 255), False, 2, False,
                                             [True, True, True], [50, 100, 400])
                temp_projectile.d_to_player(9, -0.2, angle)
                self.rotate_2_projectiles_2.append(temp_projectile)

        self.move()
        Projectile.list_update(self.rotate_2_projectiles, 200, 300)
        Projectile.list_update(self.rotate_2_projectiles_2, 500, 500)
        # self.rotate_2_projectiles_2

        if self.timer > 1000:
            return True
        self.update_radius_angle_points(False, True, 0.08)
        return False

    def initialize_random_1(self):
        self.attack_started = True
        self.is_attack = False

        self.random_1_generate_random()

        self.random_1_homing_proj = Projectile(width // 2, height // 2, 55, (255, 255, 255), False, 1.5, True)
        # self.random_1_homing_proj.d_homing(4,0.02,math.pi/2)

        self.random_1_color = [255, 255, 255]
        self.random_1_color_add = [random.randint(2, 10), random.randint(2, 10), random.randint(2, 10)]

    def random_1_generate_random(self):
        self.random_1_randint = randint(0, 2)
        self.random_1_randint2 = randint(0, 2)

        self.random_1_flip_trig = random.choice([False, True])

        self.random_1_angle = random.random() * math.tau
        self.random_1_angle2 = random.random() * math.tau
        self.random_1_angle3 = random.random() * math.tau

        self.random_1_speed = random.random() * 3
        self.random_1_acc = random.random() / 5
        self.random_1_timerMod = random.choice([2, 2, 3, 3])

        self.random_1_angle_add = random.random() / 3
        self.random_1_angle2_add = random.random() / 3
        self.random_1_angle3_add = random.random() / 10

        self.random_1_color_should_glow = random.choice([False, False, True])
        self.random_1_color_pulsate_mult = random.randint(20, 40) / 10
        self.random_1_color_no_glow = random.choice([True, False, False, False, False, False, False])

    def random_1(self):
        if not self.attack_started:
            self.initialize_random_1()

        # self.random_1_homing_proj.move()

        for i in range(3):
            self.random_1_color[i] += self.random_1_color_add[i] / 10
            if self.random_1_color[i] <= 0:
                self.random_1_color[i] = 0
                self.random_1_color_add[i] = random.randint(2, 10)
            if self.random_1_color[i] >= 255:
                self.random_1_color[i] = 255
                self.random_1_color_add[i] = -random.randint(2, 10)

        if self.timer % 1000 == 0:
            self.projectiles = []
            self.random_1_generate_random()

        # updating rand projectile angle
        if self.random_1_randint == 0:
            self.random_1_angle += self.random_1_speed
            self.random_1_angle2 += self.random_1_acc
        else:
            self.random_1_angle += self.random_1_angle_add
            self.random_1_angle2 += self.random_1_angle2_add
        # creating proj
        if self.timer % self.random_1_timerMod != 0:
            temp_projectile = Projectile(width // 2, height // 2, 10, self.random_1_color,
                                         self.random_1_color_should_glow, self.random_1_color_pulsate_mult,
                                         self.random_1_color_no_glow)
            if self.random_1_flip_trig:
                temp_projectile.d_standard(self.random_1_speed * math.cos(self.random_1_angle),
                                           self.random_1_speed * math.sin(self.random_1_angle),
                                           self.random_1_acc * math.cos(self.random_1_angle2) * math.cos(
                                               self.random_1_angle),
                                           self.random_1_acc * math.sin(self.random_1_angle2) * math.sin(
                                               self.random_1_angle))
            else:
                temp_projectile.d_standard(self.random_1_speed * math.sin(self.random_1_angle),
                                           self.random_1_speed * math.cos(self.random_1_angle),
                                           self.random_1_acc * math.cos(self.random_1_angle2) * math.cos(
                                               self.random_1_angle),
                                           self.random_1_acc * math.sin(self.random_1_angle2) * math.sin(
                                               self.random_1_angle))
            self.projectiles.append(temp_projectile)
        Projectile.list_update(self.projectiles, 200, 200)

    def main_update(self):
        self.timer += 1

        self.attack_player()

        self.current_attack = self.ATTACK_ARR[self.attack_index]
        temp_finish_attack = False

        if self.current_attack == self.FADE_IN_SQUARE:
            temp_finish_attack = self.update_radius_angle_points()

        elif self.current_attack == self.ROTATE_TO_ZERO:
            temp_finish_attack = self.rotate_times(self.angle_increment, 0, 0)

        elif self.current_attack == self.RAIN_1:
            temp_finish_attack = self.rain_1()

        elif self.current_attack == self.DASH_1:
            temp_finish_attack = self.dash_1()
            self.update_radius_angle_points(False, True)

        elif self.current_attack == self.DASH_2:
            temp_finish_attack = self.dash_2()
        elif self.current_attack == self.CHR:
            temp_finish_attack = self.chr()
        elif self.current_attack == self.MT_SPHERES_1:
            temp_finish_attack = self.mt_spheres_1()
        elif self.current_attack == self.MT_SPHERES_OG_1:
            temp_finish_attack = self.mt_spheres_og(0, 3)
        elif self.current_attack == self.MT_SPHERES_OG_2:
            temp_finish_attack = self.mt_spheres_og(3, 6)
        elif self.current_attack == self.MT_SPHERES_OG_3:
            temp_finish_attack = self.mt_spheres_og(6)
        elif self.current_attack == self.LASER_1:
            temp_finish_attack = self.laser_1()
        elif self.current_attack == self.HOVER_1:
            temp_finish_attack = self.hover_1()
        elif self.current_attack == self.HOVER_0:
            temp_finish_attack = self.hover_0()
        elif self.current_attack == self.PATTERN_1:
            temp_finish_attack = self.pattern_1()
        elif self.current_attack == self.HOMING_1:
            temp_finish_attack = self.homing_1()
        elif self.current_attack == self.ROTATE_1:
            temp_finish_attack = self.rotate_1()
        elif self.current_attack == self.ROTATE_2:
            temp_finish_attack = self.rotate_2()
        elif self.current_attack == self.RANDOM_1:
            temp_finish_attack = self.random_1()
        else:
            print("boss index went outside of index options")
            exit()

        player.collision(self.projectiles)

        if temp_finish_attack:
            self.attack_index += 1

            if self.attack_index == len(self.ATTACK_ARR):
                self.attack_index = self.ATTACK_INDEX_RETURN
            self.timer = 0
            self.dist_current = self.max_dist
            self.finishing_attack = False
            self.projectiles = []
            self.attack_started = False
            self.current_width = 6


boss = Boss_square()

wait_time = 0
# for i in range (5):
# clock.tick(10)
if wait_time:
    for i in range(100):
        clock.tick(10 * wait_time)
        should_break = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                should_break = True
        if should_break: break

'''
song list:
astrum deus devourer of gods - worm
astral biome



'''
music_arr = ['Music/The Devourer of Gods (Nonstop Mix).WAV',
             'Music/09. Treasures Within The Abomination.MP3',
             'Music/10. Pest of The Cosmos.MP3',
             'Music/DM DOKURO - Antarctic Reinforcement.MP3',
             'Music/08. The Heaven-Sent Abomination.MP3',
             "Music/23. Heaven's Hell-Sent Gift.MP3",
             'Music/00. The Tale of a Cruel World.MP3']

# music = pygame.mixer.Sound(music_arr[1])
# music.play(loops = -1)

has_changed_music = False
music_change_time = 1000
music_time_frames = 60
start_music = True

x = -10


def return_to_menu():
    global game_active

    values_to_return = player.score, list(background_color)
    initialize()
    game_active = True
    return values_to_return


def run_game():
    global angle, time, total_rotations, projectile_list, player, continue_attack, finished, game_active, \
        mini_attack_homing_completed, boss, attack_order, start_attack, projectile_list_shoot, check_ring, \
        projectile_object_homing, temp_choice, dont_change_attack, x, has_changed_music, music_change_time, \
        music_time_frames, start_music, player_initial_pos, radius, music_arr, wait_time, wait_time, set_attack_order, \
        game_active
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # pygame.quit()
                # exit()
                return return_to_menu()
            if not game_active:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # pygame.quit()
                    # exit()
                    return return_to_menu()

        if game_active:
            if start_music:
                pygame.mixer.stop()
                pygame.mixer.music.load(music_arr[1])
                pygame.mixer.music.play(-1, 0.0, 0)
                start_music = False
            # DO NOT UPDATE ANY CODE ABOVE THE FILL
            # ANY DRAWING IN HERE WILL NOT BE SHOWN
            screen.fill(background_color)
            # drawing from this line onward is fine

            # GLOBAL_ARR_LINE.update_all()

            # jjj.update()

            if x == -1:
                boss.main_update()
            if not continue_attack:
                continue_attack = True
                finished = False
                if attack_order and not dont_change_attack:
                    x = attack_order[0]
                    del attack_order[0]
                elif not dont_change_attack:
                    attack_order = set_attack_order

                if x == 0 or x == 1 or x == 4:
                    start_pos1 = randint(200, 600)
                    if x == 0:
                        while not (abs(player.coords()[0] - start_pos1)) > 50:
                            start_pos1 = randint(100, 700)
                        start_pos2 = randint(100, 400)
                        while not (abs(player.coords()[1] - start_pos2)) > 50:
                            start_pos2 = randint(100, 400)
                    elif x == 1:
                        while not (abs(player.coords()[0] - start_pos1)) > 200:
                            start_pos1 = randint(100, 700)

                        start_pos2 = randint(100, 400)
                        while not (abs(player.coords()[1] - start_pos2)) > 100:
                            start_pos2 = randint(50, 450)
                    if x == 4:
                        start_pos1 = width // 2
                        start_pos2 = height // 2
                    radius = 0
                    temp_color = (0, 255, 0)

                    if x == 0:
                        player.changeRadius(5)
                        temp_color = (64 + 50, 64 + 50, 100 + 50)
                        telegraph_tick = 60
                    elif x == 1:
                        telegraph_tick = 240
                        player.changeRadius(10)
                        temp_color = (255, 150, 150)
                    elif x == 4:
                        telegraph_tick = 60
                        player.changeRadius(10)
                        temp_color = (255, 0, 200)
                        angle_to_increment_ring = 37
                        num_ring = int(180 / angle_to_increment_ring)
                    if x == 1 or x == 0 or x == 4:
                        if x == 1:
                            temp_num_telegraph = 10
                            temp_num_telegraph_speed = -0.5
                            temp_num_telegraph_radius_mult = 1
                            temp_num_telegraph_angle_incr = 200
                            temp_num_telegraph_color = (255, 0, 0)
                            temp_radius_lim = 150
                            temp_radius_max = 150
                            temp_radius_incr = 1

                        if x == 0:
                            temp_num_telegraph = 2
                            temp_num_telegraph_speed = -1  # 0.1
                            temp_num_telegraph_radius_mult = 2
                            temp_num_telegraph_angle_incr = 25
                            temp_num_telegraph_color = (255, 255, 255)
                            temp_radius_lim = 100
                            temp_radius_max = 100
                            temp_radius_incr = 0.5
                        if x == 4:
                            temp_num_telegraph = 20
                            temp_num_telegraph_speed = -0.06
                            temp_num_telegraph_radius_mult = 1.4
                            temp_num_telegraph_angle_incr = 200
                            temp_num_telegraph_color = (255, 0, 200)
                            temp_radius_lim = 150
                            temp_radius_max = 225
                            temp_radius_incr = 1

                        while radius < temp_radius_max:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    # pygame.quit()
                                    # exit()
                                    return return_to_menu()
                                if event.type == KEYDOWN:
                                    if event.key == K_ESCAPE:
                                        # pygame.quit()
                                        # exit()
                                        return return_to_menu()
                            pygame.event.get()
                            screen.fill(background_color)
                            player.update(telegraph_tick)

                            boss.ring(temp_num_telegraph, temp_num_telegraph_speed, temp_num_telegraph_color, False, 1,
                                      0.15,
                                      False, 0.04, False, False, radius / temp_num_telegraph_angle_incr * math.pi,
                                      boss.projectiles, 0, 0, start_pos1, start_pos2, 'I', 0, 0, 2 * math.pi,
                                      240 - min(radius, temp_radius_lim) * temp_num_telegraph_radius_mult)
                            for proj in boss.projectiles:
                                proj.update()

                            radius += temp_radius_incr
                            update_pygame()

                        boss.projectiles = []
                    player_initial_pos = player.coords().copy()
                    if x == 0:
                        player_initial_pos = [start_pos1, start_pos2]
                    if x == 0:
                        radius = 800
                        circle_center = [start_pos1, start_pos2]
                    elif x == 1:
                        radius = 600
                        circle_center = player_initial_pos.copy()
                    elif x == 4:
                        radius = 800
                        radius_ring = 7
                        circle_center = [start_pos1, start_pos2]
                    projectiles_dead = False
                elif x == 2:
                    player.radius = 8
                    time = 0
                    start_part_2 = False
                    start_part_3 = False
                    line_width = 1
                    line_color = 'Gray'

                    arr_i = []
                    arr_i.append(randint(0, 23))
                    if mini_attack_homing_completed == 2:
                        for i in range(0, 24, 3):
                            arr_i.append((arr_i[0] + i) % 24)
                    elif mini_attack_homing_completed == 1:
                        arr_i.append((arr_i[0] + 6) % 24)
                    elif mini_attack_homing_completed == 0:
                        pass  # append no extra lines to arr
                    else:
                        print(
                            'mini_attack_homing_completed went out of bounds of 0 1 2, program will likely break if left')
                        print('code exited in attack x == 2')
                        print('mini_attack_homing_completed: ', mini_attack_homing_completed)
                        exit()
                    radius = 200
                    circle_center = (width // 2, height // 2)
                    temp_check = 0
                    temp_choice_list = mini_attack_homing_completed
                    if dist(player.pos[0], player.pos[1], width // 2, height // 2) > 200:
                        player.pos = [width // 2, height // 2]
                    color_arr_circles = [(150, 0, 0), (0, 150, 0), (0, 0, 150)]
                elif x == 3:
                    telegraph_tick = 125
                    temp_choice = mini_attack_homing_completed

                    if temp_choice == 2:
                        temp_pos_arr_at_border_white_homing = [[0, 0], [width, 0], [0, height], [width, height],
                                                               [width // 2, 0], [width // 2, height],
                                                               [width, height // 2], [0, height // 2]]
                    elif temp_choice == 1:
                        temp_pos_arr_at_border_white_homing = [[0, 0], [width, 0], [0, height], [width, height], ]
                    elif temp_choice == 0:
                        temp_pos_arr_at_border_white_homing = [[width // 2, 0], [width // 2, height],
                                                               [width, height // 2], [0, height // 2]]

                    for i in range(100):
                        pygame.event.get()
                        screen.fill(background_color)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                # pygame.quit()
                                # exit()
                                return return_to_menu()
                            if event.type == KEYDOWN:
                                if event.key == K_ESCAPE:
                                    # pygame.quit()
                                    # exit()
                                    return return_to_menu()

                        for pos in temp_pos_arr_at_border_white_homing:
                            player_coord = player.pos.copy()
                            temp_pos = pos.copy()
                            temp_close = 75
                            if temp_pos[0] == 0:
                                player_coord[0] -= temp_close
                                temp_pos[0] += temp_close
                            if temp_pos[0] == width:
                                player_coord[0] += temp_close
                                temp_pos[0] -= temp_close
                            if temp_pos[1] == 0:
                                player_coord[1] -= temp_close
                                temp_pos[1] += temp_close
                            if temp_pos[1] == height:
                                player_coord[1] += temp_close
                                temp_pos[1] -= temp_close

                            pygame.draw.line(screen, (150, 150, 150), temp_pos, player_coord, 2)

                        player.update(telegraph_tick)
                        update_pygame()

                    for pos in temp_pos_arr_at_border_white_homing:
                        temp_projectile = Projectile1(pos.copy(), 5, [0, 0], [0, 0], [255, 255, 255])
                        projectile_object_homing.add_projectile(temp_projectile, 7, 0.01)

                    projectile_object_homing.timer = pygame.time.get_ticks()

                    angle_spiral_homing = 0
                    temp_color = [150, 150, 255]
                    color_add_subt = [8, 15, 7]
                    time_reset = 8000
                    time_break = 1500
                    time_wait = 2500

                    radius_inside = 0
                    radius_outside = 200  # for temp_choice = 2
                    collide_border_circles = False  # so temp_choice = 2 circles dont collide when not drawn

                    if temp_choice == 0:
                        projectile_list = []
                        arr_pos = [[width // 4, height // 4], [width * 3 // 4, height * 3 // 4]]
                        wait_time = 500
                        main_radius = 10
                    elif temp_choice == 1:
                        projectile_list = []
                        arr_pos = [[width // 2, height // 2]]
                        wait_time = 110
                        main_radius = 20

                    elif temp_choice == 2:
                        projectile_list = []
                        arr_pos = [[width // 2, height // 2]]
                        wait_time = 50
                        time_counter_choice_2 = 0
                        main_radius = 10
                        time_reset = 19500
                        time_wait = 2500
                        reverse = False
                        collide_border_circles = False
                        circle_rect_3_1 = pygame.Rect(0, 0, 1, 1)

                    dont_change_attack = False
                    mini_attack_homing_completed += 1
                    if mini_attack_homing_completed == 3:
                        mini_attack_homing_completed = 0
                    player.radius = 10
            if x == 0:
                for i in range(len(projectile_list)):
                    projectile_list[i].update()
                if radius > 25:
                    if not finished:
                        radius -= 0.7
                    else:
                        radius -= .7
                else:
                    continue_attack = False
                if radius < 300:
                    player.radius = 4
                if not projectiles_dead:
                    continue_attack = spiral_bullet_spam_attack(1, [start_pos1, start_pos2], 7, (64, 64, 100), 2, 12)
                    if not continue_attack:
                        projectiles_dead = True
                        continue_attack = True
                else:
                    radius -= 1.5
                for i in range(24):
                    pygame.draw.circle(screen, (50 - 2 * i, 50 - 2 * i, 255 - 10 * i),
                                       [player_initial_pos[0], player_initial_pos[1]], radius + i, 2)


            elif x == 1:
                for i in range(len(projectile_list)):
                    projectile_list[i].update()
                if radius > 50:
                    if radius > 320:
                        radius -= .65
                    else:
                        radius -= 4
                else:
                    continue_attack = False
                if not projectiles_dead:
                    continue_attack = spiral_bullet_spam_attack(1, [start_pos1, start_pos2], 3, (255, 64, 100), 5, 3)

                    if not continue_attack:
                        projectiles_dead = True
                        continue_attack = True

                for i in range(24):
                    pygame.draw.circle(screen, (254 - 10 * i, 0, 0), [player_initial_pos[0], player_initial_pos[1]],
                                       radius + i, 2)


            elif x == 4:
                for i in range(len(projectile_list)):
                    projectile_list[i].update()
                if not projectiles_dead:
                    check_ring += 1
                    if check_ring > 500:
                        projectile_object_homing.update_all()
                    if check_ring % 250 == 0 and check_ring >= 250:
                        player.radius = 8
                        ring_speed = 0
                    if check_ring % 250 < 200 and check_ring % 250 > 120 and check_ring % 20 == 0 and check_ring >= 700:
                        radius_ring -= 2
                        temp_projectile = Projectile1([width // 2, height // 2], radius_ring, [0, 0], [0, 0],
                                                      [255, 0, 200])
                        projectile_object_homing.add_projectile(temp_projectile, 10 * (1.4 - radius_ring / 23),
                                                                0.04 * (abs(0.8 - radius_ring / 23)))
                    if (check_ring < 450):
                        if check_ring % 50 == 1:
                            num_ring += 2
                            radius_ring += 3
                            for i in range(num_ring):
                                spiral_bullet_spam_attack(1, [start_pos1, start_pos2],
                                                          angle_to_increment_ring * (math.pi / 180), (255, 0, 200), 0.7,
                                                          15, 0.01, True, radius_ring, False)
                    elif check_ring > 250 and check_ring < 1600:
                        if check_ring % 50 == 1:
                            num_ring += 0.7
                            ring_speed += 0.023
                            for i in range(int(num_ring)):
                                spiral_bullet_spam_attack(1, [start_pos1, start_pos2], 0.29670597283, (255, 0, 200),
                                                          0.2, 15, ring_speed, True, 4)

                    temp = projectiles_finish(projectile_list, False)

                    if check_ring > 1800:
                        for i in range(projectile_object_homing.num_projectiles):
                            projectile_object_homing.delete(0)
                        continue_attack = False
                        projectiles_dead = True
                        check_ring = 0
                        angle = 0
                        time = 0
                        total_rotations = 0
                        projectile_list = []
            elif x == 2:
                continue_attack = True

                if not finished:
                    if temp_choice_list == 0:
                        line_color = (150, 0, 0)
                    elif temp_choice_list == 1:
                        line_color = (0, 150, 0)
                    elif temp_choice_list == 2:
                        line_color = (0, 0, 150)

                circle_circle_attack(line_color)
                if finished:
                    time += 1
                    for projectile in projectile_list_shoot:
                        projectile.update()
                    if time == 120:
                        radius = 200
                        circle_center = (width // 2, height // 2)
                        if temp_choice == 2:
                            start_shoot_player(2, line_color, 1.5)
                            player.radius = 8
                        elif temp_choice == 1:
                            start_shoot_player_scuffed2(3, line_color)
                            player.radius = 8
                        else:
                            start_shoot_player_scuffed(3, line_color)
                            player.radius = 8
                        start_part_2 = True
                        line_width = 5
                    elif time == 80:
                        player_initial_pos = player.pos.copy()
                        temp_choice = temp_choice_list
                        if temp_choice == 0:
                            line_color = (150, 0, 0)
                        elif temp_choice == 1:
                            line_color = (0, 150, 0)
                        elif temp_choice == 2:
                            line_color = (0, 0, 150)
                    elif time == 1:
                        if temp_choice_list == 0:
                            line_color = (150, 0, 0)
                        elif temp_choice_list == 1:
                            line_color = (0, 150, 0)
                        elif temp_choice_list == 2:
                            line_color = (0, 0, 150)
                        for projectile in projectile_list:
                            projectile.color = line_color
                    elif time < 80:
                        player_initial_pos = player.pos.copy()
                    elif time > 120:
                        for i in range(24):
                            temp_color_border_circle = [0, 0, 0]
                            temp_color_border_circle[temp_choice] = 150 - 6 * i
                            pygame.draw.circle(screen, temp_color_border_circle, [width // 2, height // 2],
                                               radius + i, 2)
                        player.collision(projectile_list_shoot)
                        projectiles_finish(projectile_list_shoot)

                    for i in arr_i:
                        projectile = projectile_list[i]
                        projectile_center = [projectile.pos.x, projectile.pos.y]

                        if mini_attack_homing_completed != 2:
                            x1 = player_initial_pos[0]
                            y1 = player_initial_pos[1]

                            change_coord = [x1 - projectile_center[0], y1 - projectile_center[1]]
                            # change_coord = [x1 - projectile_center.x, y1 - projectile_center.y]
                            temp_dist = math.sqrt(change_coord[0] ** 2 + change_coord[1] ** 2)
                            change_coord[0] /= temp_dist
                            change_coord[1] /= temp_dist

                            while ((x1 - width // 2) ** 2 + (y1 - height // 2) ** 2 <= 200 ** 2):
                                x1 += change_coord[0]
                                y1 += change_coord[1]
                        if mini_attack_homing_completed == 2:
                            if time >= 80 and time <= 120:
                                pygame.draw.line(screen, line_color, projectile_center, (player_initial_pos.copy()), 2)
                            elif time <= 80:
                                pygame.draw.line(screen, [100, 100, 100], projectile_center,
                                                 (player_initial_pos.copy()), line_width)
                            else:
                                pygame.draw.line(screen, line_color, projectile_center, (player_initial_pos.copy()),
                                                 line_width)
                        else:
                            if time >= 80 and time <= 120:
                                pygame.draw.line(screen, line_color, projectile_center, (x1, y1), 2)
                            elif time <= 80:
                                pygame.draw.line(screen, [100, 100, 100], projectile_center, (x1, y1), line_width)
                            else:
                                pygame.draw.line(screen, line_color, projectile_center, (x1, y1), line_width)
                            # add code here

                        if line_width > 1 and mini_attack_homing_completed != 2:
                            if line_circle_collision(projectile_center[0], projectile_center[1], x1, y1, player.pos[0],
                                                     player.pos[1], player.radius):
                                player.lose_health()
                        if line_width > 1 and mini_attack_homing_completed == 2:
                            if line_circle_collision(projectile_center[0], projectile_center[1], player_initial_pos[0],
                                                     player_initial_pos[1], player.pos[0], player.pos[1],
                                                     player.radius):
                                player.lose_health()

                    if time >= 400:
                        time = 0
                        start_part_2 = False
                        start_part_3 = False
                        line_width = 1
                        line_color = 'Gray'
                        arr_i = []
                        arr_i = []
                        player.radius = 8
                        arr_i.append(randint(0, 23))
                        arr_i.append((arr_i[0] + 8) % 23)
                        arr_i.append((arr_i[0] + 16) % 23)
                        temp_check += 1
                        projectile_list_shoot = []
                        projectile_list = []
                        projectile_list_shoot = []
                        continue_attack = False
                        start_attack = False
            elif x == 3:
                if pygame.time.get_ticks() - projectile_object_homing.timer > time_reset:
                    collide_border_circles = False
                if pygame.time.get_ticks() - projectile_object_homing.timer > time_reset + time_break:
                    projectile_object_homing.timer = pygame.time.get_ticks()
                    continue_attack = False
                    projectile_list = []
                    # temp_choice = (temp_choice+1)%3
                elif pygame.time.get_ticks() - projectile_object_homing.timer < time_reset and pygame.time.get_ticks() - projectile_object_homing.timer > time_wait:
                    if temp_choice == 2:
                        if radius_outside > 300:
                            reverse = True
                        if reverse:
                            radius_inside -= 0.7
                            if radius_outside > 220:
                                radius_outside -= 0.5
                            if radius_inside < 0:
                                radius_inside = 0
                        if not reverse:
                            radius_inside += 0.27
                            radius_outside += 0.2

                        for i in range(5):
                            pygame.draw.circle(screen, (255, 255, 255),
                                               [width // 2, height // 2], radius_inside - i, 2)
                            pygame.draw.circle(screen, (255, 255, 255),
                                               [width // 2, height // 2], radius_outside - i, 2)

                        collide_border_circles = True
                    if projectile_object_homing.add_projectile_on_timer(wait_time):
                        for j in range(3):
                            temp_color[j] += color_add_subt[j]
                            if temp_color[j] > 255 or temp_color[j] < 0:
                                color_add_subt[j] *= -1
                                temp_color[j] += color_add_subt[j]
                        if temp_choice == 1 or temp_choice == 2:
                            if temp_choice == 1:
                                angle_spiral_homing += 1
                            elif temp_choice == 2:
                                angle_spiral_homing += 0.11
                            temp_projectile_2 = Projectile1(arr_pos[0].copy(), 8, [0, 0], [0, 0], temp_color)
                            projectile_object_homing.add_projectile(temp_projectile_2, 7, 0.02, angle_spiral_homing)
                            if (projectile_object_homing.num_projectiles) > 3:
                                projectile_object_homing.bool_arr[projectile_object_homing.num_projectiles - 3] = True
                        else:
                            for i in range(len(arr_pos)):
                                temp_projectile_2 = Projectile1(arr_pos[i].copy(), 8, [0, 0], [0, 0], temp_color)
                                projectile_object_homing.add_projectile(temp_projectile_2, 7, 0.02)
                                if (projectile_object_homing.num_projectiles) > 3:
                                    projectile_object_homing.bool_arr[
                                        projectile_object_homing.num_projectiles - 3] = True
                        if temp_choice == 2:
                            time_counter_choice_2 += 1
                            temp_size = 5
                            if time_counter_choice_2 % 25 == 0:
                                if reverse:
                                    circle_fast_speed = 3 + (
                                            pygame.time.get_ticks() - projectile_object_homing.timer) / 2000
                                    homing_amount = 0.007
                                else:
                                    circle_fast_speed = 8
                                    homing_amount = 0.01
                            if time_counter_choice_2 % 75 == 25:
                                homing_amount *= 1.5
                                circle_fast_speed /= 2
                                temp_size = 3
                            # circle_fast_speed = 0 # uncomment this line to make homing proj stop - for testing
                            if time_counter_choice_2 % 25 == 0:
                                temp_projectile = Projectile1([0, 0], temp_size, [0, 0], [0, 0], [255, 255, 255])
                                projectile_object_homing.add_projectile(temp_projectile, circle_fast_speed,
                                                                        homing_amount)
                                temp_projectile = Projectile1([width, 0], temp_size, [0, 0], [0, 0], [255, 255, 255])
                                projectile_object_homing.add_projectile(temp_projectile, circle_fast_speed,
                                                                        homing_amount)
                                temp_projectile = Projectile1([0, height], temp_size, [0, 0], [0, 0], [255, 255, 255])
                                projectile_object_homing.add_projectile(temp_projectile, circle_fast_speed,
                                                                        homing_amount)
                                temp_projectile = Projectile1([width, height], temp_size, [0, 0], [0, 0],
                                                              [255, 255, 255])
                                projectile_object_homing.add_projectile(temp_projectile, circle_fast_speed,
                                                                        homing_amount)
                            if time_counter_choice_2 % 75 == 25:
                                temp_projectile = Projectile1([width // 2, 0], temp_size, [0, 0], [0, 0],
                                                              [255, 255, 255])
                                projectile_object_homing.add_projectile(temp_projectile, circle_fast_speed,
                                                                        homing_amount)
                                temp_projectile = Projectile1([0, height // 2], temp_size, [0, 0], [0, 0],
                                                              [255, 255, 255])
                                projectile_object_homing.add_projectile(temp_projectile, circle_fast_speed,
                                                                        homing_amount)
                                temp_projectile = Projectile1([width, height // 2], temp_size, [0, 0], [0, 0],
                                                              [255, 255, 255])
                                projectile_object_homing.add_projectile(temp_projectile, circle_fast_speed,
                                                                        homing_amount)
                                temp_projectile = Projectile1([width // 2, height // 2], temp_size, [0, 0], [0, 0],
                                                              [255, 255, 255])
                                projectile_object_homing.add_projectile(temp_projectile, circle_fast_speed,
                                                                        homing_amount)
                            if time_counter_choice_2 % 75 == 25:
                                homing_amount /= 1.5
                                circle_fast_speed *= 2
                    for i in range(len(arr_pos)):
                        projectile_list[i].color = temp_color
                        projectile_list[i].draw()
                elif pygame.time.get_ticks() - projectile_object_homing.timer < time_wait:
                    if not projectile_list:
                        for pos in arr_pos:
                            temp_projectile = Projectile1(pos, main_radius, [0, 0], [0, 0], background_color)
                            projectile_list.append(temp_projectile)
                    if projectile_object_homing.add_projectile_on_timer(100):
                        for i in range(len(arr_pos)):
                            pygame.draw.circle(screen, (255, 255, 255), arr_pos[i], main_radius)
                    if temp_choice == 2 and pygame.time.get_ticks() - projectile_object_homing.timer > time_wait - 1000:
                        temp_telegraph_angle = 2 * math.pi * (
                                pygame.time.get_ticks() - projectile_object_homing.timer) / time_wait
                        pygame.draw.line(screen, (255, 255, 255), (width // 2, height // 2), (
                            width // 2 + (radius_outside - 3) * math.cos(temp_telegraph_angle),
                            height // 2 + (radius_outside - 3) * math.sin(temp_telegraph_angle)), 5)
                        temp_telegraph_angle2 = 2 * math.pi - temp_telegraph_angle
                        pygame.draw.line(screen, (255, 255, 255), (width // 2, height // 2), (
                            width // 2 + (radius_outside - 3) * math.cos(temp_telegraph_angle2),
                            height // 2 + (radius_outside - 3) * math.sin(temp_telegraph_angle2)), 5)

                        if temp_telegraph_angle > math.pi:
                            circle_rect_3_1.update(0, 0, radius_outside * 2 - i * 2, radius_outside * 2 - i * 2)
                            circle_rect_3_1.center = (width // 2, height // 2)
                            pygame.draw.arc(screen, (150, 150, 150), circle_rect_3_1, temp_telegraph_angle2,
                                            temp_telegraph_angle, 3)
                        for i in range(3):
                            temp_const_eqn = math.pi * (1 + 3 * i / 10)
                            if temp_telegraph_angle > temp_const_eqn:
                                temp_telegraph_angle3 = (math.pi / (2 * math.pi - temp_const_eqn)) * (
                                        temp_telegraph_angle - temp_const_eqn) + math.pi
                                pygame.draw.line(screen, (255, 255, 255), (width // 2, height // 2), (
                                    width // 2 + (radius_outside - 3) * math.cos(temp_telegraph_angle3),
                                    height // 2 + (radius_outside - 3) * math.sin(temp_telegraph_angle3)), 5)
                                temp_telegraph_angle4 = -temp_telegraph_angle3
                                pygame.draw.line(screen, (255, 255, 255), (width // 2, height // 2), (
                                    width // 2 + (radius_outside - 3) * math.cos(temp_telegraph_angle4),
                                    height // 2 + (radius_outside - 3) * math.sin(temp_telegraph_angle4)), 5)

                if len(projectile_object_homing.projectiles) > 0:
                    projectile_object_homing.update_all()

            player.update()
            player_temp = player.coords()

            if x == 1 or x == 0:
                player.keep_in_circle(radius + player.radius / 2, circle_center[0], circle_center[1], True)

            if x == 2 and time > 120:
                temp_radius = dist(circle_center[0], circle_center[1], player.pos[0], player.pos[1]) - 2
                if temp_radius < 200: temp_radius = 200
                player.keep_in_circle(temp_radius + player.radius / 2, circle_center[0], circle_center[1], True)

            if x == 0 or x == 1 or (x == 2 and time > 120):
                if (((player_temp[0] - circle_center[0]) ** 2 + (player_temp[1] - circle_center[1]) ** 2) > (
                        radius - 5) ** 2):
                    player.lose_health()
            if x == 3 and temp_choice == 2 and collide_border_circles:
                if (((player_temp[0] - width // 2) ** 2 + (player_temp[1] - height // 2) ** 2) > (
                        radius_outside - 6) ** 2):
                    player.lose_health()
                if (((player_temp[0] - width // 2) ** 2 + (player_temp[1] - height // 2) ** 2) < (
                        radius_inside + 4) ** 2):
                    player.lose_health()
            if (x == 2 and time <= 120) or (x == 0 or x == 1 or x == 4) or x == -1:
                player.collision(projectile_list)
                pass

            if not player.is_alive():
                return return_to_menu()
            if x == -1:
                pygame.mixer.stop()
                if not has_changed_music:
                    pygame.mixer.music.fadeout(music_change_time)
                    has_changed_music = True
                else:
                    music_time_frames -= 1
            if music_time_frames == -1:
                pygame.mixer.music.load(music_arr[2])
                pygame.mixer.music.play(-1, 0.0, 5 * music_change_time)
        else:
            return return_to_menu()
            # screen.fill((94, 129, 162))
            # screen.blit(title_surf,title_rect)
            # screen.blit(instr_surf,instr_rect)

        update_pygame()
