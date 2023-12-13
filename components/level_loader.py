from dataclasses import dataclass

from components.projectiles import MovementRotate, MovementStandard, ShapePolygon, ShapeCircle, ShapeCircleBright, \
    Projectile, ProjectileList, ColorRainbow
import pygame
import pygame.math
import random
from random import uniform, randint, choice
import math
from sys import exit
from pygame.locals import *
from typing import List, Set, Tuple, Dict, Union

# self made inputs
import components.calculations as calc  # calculations file
import components.player_class  # player file
from components.text_boxes import *  # gets text box classes and functions
from components.config import *

screen: pygame.display.set_mode() = None
player: components.player_class.Player = None


# this is used to get the variables from the main file to be used inside here
def globals_initializer(global_screen, global_player) -> None:
    global screen, player
    screen = global_screen
    player = global_player


class AttackIndexError(Exception):
    def __init__(self):
        self.message = "Attack index given was not a valid input."

    def __str__(self):
        return self.message


class GalaxyLevel:
    def __init__(self, difficulty: int):
        """
        contains attacks for first level prior to the Square Boss fight
        difficulty must be an integer, hardest is 1, higher numbers are more difficult
        """
        self.level_name = "Galaxías Kýklos"
        self.looped_amount = 0  # keeps track of how many times player has looped through the level

        # timer to keep track of current frames, resets upon attack end
        # an increase of 60 by timer means 1 second has passed
        self.timer = 0

        # use to keep track of projectiles for attacks
        # if an attack requires projectiles to be separated differently,
        # then create more projectile lists for that attack
        self.projectiles = ProjectileList()

        self.attack_started = False  # use to check if an attack has happened

        self.ATTACK_INDEX_RETURN_TO = 0  # if the attacks loop, the attacks return to this attack

        # keeps track of all attacks and the order, make sure to update this when adding a new attack
        self.attack_arr = [
            self.intro,
            lambda: self.spiral_1(7), lambda: self.spiral_1(0), lambda: self.floor_1(2),
            lambda: self.floor_1(1), lambda: self.spiral_1(6), lambda: self.floor_1(3),
            lambda: self.spiral_1(5), lambda: self.floor_1(4), lambda: self.spiral_1(3),
            lambda: self.spiral_1(2), lambda: self.spiral_1(4), lambda: self.spiral_1(1),
            lambda: self.floor_1(0), lambda: self.spiral_1(8),
        ]
        if skip_intro: del self.attack_arr[0]

        # keeps track of current attack within the attack array
        self.attack_index = 0
        self.difficulty = difficulty  # hardest difficulty is 1, must be an integer,

    # I treat this intro as an attack, even though it doesn't have any threats
    def initialize_intro(self):
        self.attack_started = True

        self.intro_name = MovementStandard(width / 2, -100, acc_y=0.05)
        self.intro_name_font = font_dict[150]

        # amount below it should be from the name position
        self.intro_score = MovementStandard(width / 2, -100, acc_y=0.05)
        self.intro_score_font = font_dict[100]

        self.intro_player_score = int(player.score)
        if self.looped_amount == 0:
            self.intro_player_score = 0  # so that player score is 0 once level first played

    # I treat this intro as an attack, even though it doesn't have any threats
    def intro(self):
        if not self.attack_started:
            self.initialize_intro()

        intro_rect = draw_text(self.level_name, self.intro_name_font, (255, 255, 255), self.intro_name.pos.x,
                               self.intro_name.pos.y, mid_bottom=True)
        draw_text(f"Score: {self.intro_player_score} | Difficulty: {difficulty_dict2[self.difficulty]}",
                  self.intro_score_font,
                  (50, 100, 255), self.intro_score.pos.x, self.intro_score.pos.y, mid_top=True)

        self.intro_name.move()
        self.intro_score.move()

        self.projectiles.list_update()

        if intro_rect.top > height:
            return True
        return False

    def initialize_spiral_1(self, attack_type):
        self.attack_started = True  # necessary for attacks to function

        self.spiral_1_angle = random.uniform(0, math.tau)  # starting angle for attack

        # following if statements determine initial variables for the sub-attacks 0 through 5
        if attack_type == 0:
            self.spiral_1_radius = 1
            self.spiral_1_radius_incr = 0.2
            self.spiral_1_radius_max = 30

            self.spiral_1_arms = 2
            self.spiral_1_angle_incr = uniform(0.06, 0.08)
            self.spiral_1_speed = 1.3 / 2
            self.spiral_1_speed_acc = -0.08 / 2
            self.spiral_1_speed_jer = 0.002 / 3

            self.spiral_1_jer_offset = math.tau / 3.4

            self.spiral_1_wait_frames = 2

            self.spiral_1_time_end = 20 * 60  # attack ends after 20 seconds

            self.spiral_1_color = ColorRainbow([50, 35, 70, 200], [50, 35, 70], [70, 50, 255], [0.05, 0.1, 0.1],
                                               [0.1, 0.2, 0.3])

            self.spiral_1_border_length = 3

            self.spiral_1_special_counter = 0

        elif attack_type == 1:
            self.spiral_1_radius_max = 30
            self.spiral_1_radius_incr = 0.2

            self.spiral_1_radius = 1
            self.spiral_1_arms = 15
            self.spiral_1_angle_incr = 0.06
            self.spiral_1_speed = -1.5
            self.spiral_1_speed_acc = 0
            self.spiral_1_speed_jer = -0.001

            self.spiral_1_jer_offset = -math.tau / 3

            self.spiral_1_wait_frames = 20

            self.spiral_1_time_end = 20 * 60  # attack ends after 20 seconds

            self.spiral_1_color = ColorRainbow([255, 60, 0, 150], [255, 60, 0], [255, 150, 0], [0, 0.1, 0],
                                               [0, 0.2, 0])

            self.spiral_1_border_length = 7

            self.spiral_1_special_counter = 0

        elif attack_type == 2:
            self.spiral_1_radius_max = 20
            self.spiral_1_radius_incr = 0.2

            self.spiral_1_radius = 1
            self.spiral_1_arms = 15
            self.spiral_1_angle_incr = 0.06

            self.spiral_1_speed = 3
            self.spiral_1_speed_acc = -0.1
            self.spiral_1_speed_jer = 0.001

            self.spiral_1_unn_add = 0.00001

            self.spiral_1_jer_offset = math.tau / 7

            self.spiral_1_wait_frames = 4

            self.spiral_1_time_end = 15 * 60  # attack ends after 15 seconds

            self.spiral_1_color = ColorRainbow([255, 255, 255, 200], [0, 0, 50], [255, 0, 255], [0.1, 0, 0.1],
                                               [0.5, 0, 0.5], [1, 1, 1])

        elif attack_type == 3:
            self.spiral_1_radius = 10
            self.spiral_1_arms = 1
            self.spiral_1_angle_incr = 0.2

            self.spiral_1_speed = 1
            self.spiral_1_speed_acc = 0.03
            self.spiral_1_speed_jer = -0.001

            self.spiral_1_unn_add = 0.000003

            self.spiral_1_jer_offset = math.tau / 2.1

            self.spiral_1_wait_frames = 10

            self.spiral_1_time_end = 10 * 60  # attack ends after 10 seconds

            self.spiral_1_color = ColorRainbow(None, [50, 50, 50], [255, 255, 255], [0.1], [uniform(0.2, 0.5)])

        elif attack_type == 4:
            self.spiral_1_radius_max = 5
            self.spiral_1_radius_incr = 0.02

            self.spiral_1_radius = 1
            self.spiral_1_arms = 9
            self.spiral_1_angle_incr = 0.06

            self.spiral_1_speed = 3 / 2 / 2 * 2
            self.spiral_1_speed_acc = -0.1 / 2 / 2
            self.spiral_1_speed_jer = 0.001 / 3 / 2

            self.spiral_1_unn_add = 0.000005 / 3 / 2

            self.spiral_1_jer_offset = math.tau / 10.3

            self.spiral_1_wait_frames = 4

            self.spiral_1_time_end = 20 * 60  # attack ends after 20 seconds

            self.spiral_1_color = ColorRainbow(None, [150, 0, 150], [255, 50, 255], [0.1, 0.02, 0.1], [0.5, 0.05, 0.5])

        elif attack_type == 5:
            self.spiral_1_radius_max = 20
            self.spiral_1_radius_incr = 0.06  # original design for this was 0.03

            self.spiral_1_radius = 1
            self.spiral_1_arms = 19  # original was 9
            self.spiral_1_angle_incr = 0.06

            self.spiral_1_speed = 3 / 2 / 2 * 5
            self.spiral_1_speed_acc = -0.1 / 2 / 2
            self.spiral_1_speed_jer = 0.001 / 3 / 2

            self.spiral_1_unn_add = 0.000005 / 3 / 2

            self.spiral_1_jer_offset = math.tau / 10.3

            self.spiral_1_wait_frames = 7  # original design for this was 4

            self.spiral_1_time_end = 20 * 60  # attack ends after 20 seconds

            self.spiral_1_color = ColorRainbow(None, [150, 0, 150], [255, 50, 255], [0.1, 0.02, 0.1],
                                               [0.5, 0.05, 0.5])

        elif attack_type == 6:
            self.spiral_1_radius_max = 25
            self.spiral_1_radius_incr = 0.05

            self.spiral_1_radius = 1
            self.spiral_1_arms = 5
            self.spiral_1_angle_incr = 0.1
            self.spiral_1_speed = -1.67
            self.spiral_1_speed_acc = 0.005
            self.spiral_1_speed_jer = 0.0001

            self.spiral_1_unn_add_x = 0.000002
            self.spiral_1_unn_add_y = 0.000003

            self.spiral_1_angle_unn = uniform(0, math.tau)
            self.spiral_1_angle_unn_incr = 0.03

            self.spiral_1_jer_offset = -math.tau / 70.1

            self.spiral_1_wait_frames = 3

            self.spiral_1_time_end = 30 * 60  # attack ends after 30 seconds

            self.spiral_1_color = ColorRainbow([200, 60, 0], [200, 110, 0], [255, 255, 0], [0.05, 0.2, 0],
                                               [0.1, 0.4, 0])

        elif attack_type == 7:
            self.spiral_1_radius = 15
            self.spiral_1_arms = 15
            self.spiral_1_angle_incr = 0.06
            self.spiral_1_speed = 1.3
            self.spiral_1_speed_acc = -0.08
            self.spiral_1_speed_jer = 0.002

            self.spiral_1_unn_add = 0.000005

            self.spiral_1_jer_offset = math.tau / 3.4

            self.spiral_1_wait_frames = 4

            self.spiral_1_time_end = 10 * 60  # attack ends after 10 seconds

            self.spiral_1_color = ColorRainbow([255, 60, 0, 200], [255, 0, 0], [255, 255, 0], [0, 0.1, 0], [0, 0.2, 0])

        elif attack_type == 8:
            self.spiral_1_radius_max = 25
            self.spiral_1_radius_incr = 0.05

            self.spiral_1_radius = 1
            self.spiral_1_arms = 11
            self.spiral_1_angle_incr = 0.1
            self.spiral_1_speed = -1.67
            self.spiral_1_speed_acc = 0.005
            self.spiral_1_speed_jer = 0.0001

            self.spiral_1_unn_add_x = 0.000002
            self.spiral_1_unn_add_y = 0.000003

            self.spiral_1_angle_unn = uniform(0, math.tau)
            self.spiral_1_angle_unn_incr = 0.03

            self.spiral_1_jer_offset = -math.tau / 150.1

            self.spiral_1_wait_frames = 4

            self.spiral_1_time_end = 30 * 60  # attack ends after 30 seconds

            self.spiral_1_color = ColorRainbow([255, 255, 255], [0, 110, 200], [0, 255, 255], [0, 0.2, 0.05],
                                               [0, 0.4, 0.1], [1, 1, 1])
        # determines the center of the attack
        self.spiral_1_center = (width / 2, height / 2)

    def spiral_1(self, attack_type):
        if not self.attack_started:  # initializes attack
            self.initialize_spiral_1(attack_type)

        # only starts attack based on time criteria (higher the wait_frames the less often projectiles spawned)
        if self.timer % (self.difficulty * self.spiral_1_wait_frames) == 0 and self.timer < self.spiral_1_time_end:
            # updating arms - adds variety (to add variety to certain sub-attacks)
            if attack_type in [1, 7]:
                self.spiral_1_arms = 45 - self.spiral_1_arms
            elif attack_type == 3:
                self.spiral_1_arms = (6 + self.spiral_1_arms) % 37

            # loops through to create projectiles for each of the arms
            for i in range(self.spiral_1_arms):
                temp_angle = self.spiral_1_angle + i * math.tau / self.spiral_1_arms

                # black magic to assign the projectile movement system
                temp_mov = MovementStandard(self.spiral_1_center[0], self.spiral_1_center[1],
                                            self.spiral_1_speed * math.cos(temp_angle),
                                            self.spiral_1_speed * math.sin(temp_angle),

                                            self.spiral_1_speed_acc * math.cos(temp_angle),
                                            self.spiral_1_speed_acc * math.sin(temp_angle),

                                            self.spiral_1_speed_jer * math.cos(temp_angle + self.spiral_1_jer_offset),
                                            self.spiral_1_speed_jer * math.sin(temp_angle - self.spiral_1_jer_offset)
                                            )

                # determines shape based on sub-attack
                if attack_type == 0:
                    temp_shape = ShapePolygon(self.spiral_1_radius, self.spiral_1_color.get_new_color(), 5, 0.02,
                                              radius_incr=self.spiral_1_radius_incr,
                                              radius_max=self.spiral_1_radius_max,
                                              border_length=self.spiral_1_border_length)
                    temp_mov.acc.x *= [-0.2, 1, -0.4, 2][self.spiral_1_special_counter % 4]
                    temp_mov.acc.y *= [0.5, -1.5, 0.4, .72][self.spiral_1_special_counter % 4]

                elif attack_type == 1:
                    temp_shape = ShapePolygon(self.spiral_1_radius, self.spiral_1_color.get_new_color(), 3, 0.03,
                                              radius_incr=self.spiral_1_radius_incr,
                                              radius_max=self.spiral_1_radius_max,
                                              border_length=self.spiral_1_border_length)
                    temp_mov.jer.x *= [-1, 1][self.spiral_1_special_counter % 2]
                    temp_mov.jer.y *= [-1, 1, 1, -1][self.spiral_1_special_counter % 4]

                elif attack_type == 2:
                    temp_shape = ShapeCircle(self.spiral_1_radius, self.spiral_1_color.get_new_color(),
                                             radius_incr=self.spiral_1_radius_incr,
                                             radius_max=self.spiral_1_radius_max, should_glow=True, pulsate_mult=2)
                    temp_mov.unn.x = [-1, 1][i % 2] * self.spiral_1_unn_add

                elif attack_type == 3:
                    temp_shape = ShapePolygon(self.spiral_1_radius, self.spiral_1_color.get_new_color(), 7, -0.05)
                    temp_mov.unn.x = uniform(-1, 1) * self.spiral_1_unn_add
                    temp_mov.unn.y = uniform(-1, 1) * self.spiral_1_unn_add

                elif attack_type == 4:
                    temp_shape = ShapePolygon(self.spiral_1_radius, self.spiral_1_color.get_new_color(), 5, 0.1,
                                              radius_incr=self.spiral_1_radius_incr,
                                              radius_max=self.spiral_1_radius_max, fast_collision=True)
                    temp_mov.unn.x = [-1, 1, 0, 0][i % 4] * self.spiral_1_unn_add

                elif attack_type == 5:
                    temp_shape = ShapePolygon(self.spiral_1_radius, self.spiral_1_color.get_new_color(), 6, 0.1,
                                              radius_incr=self.spiral_1_radius_incr,
                                              radius_max=self.spiral_1_radius_max, fast_collision=True)
                    temp_mov.unn.x = [-1, 1, 0, 0][i % 4] * self.spiral_1_unn_add

                elif attack_type == 6:
                    temp_shape = ShapePolygon(self.spiral_1_radius, self.spiral_1_color.get_new_color(), 4, -0.07,
                                              fast_collision=True, radius_max=self.spiral_1_radius_max,
                                              radius_incr=self.spiral_1_radius_incr, should_glow=True)
                    temp_unn_x = self.spiral_1_unn_add_x * (1 - 2 * i / self.spiral_1_arms)
                    temp_unn_y = self.spiral_1_unn_add_y * (1 - 2 * i / self.spiral_1_arms)

                    temp_mov.unn.x = math.cos(self.spiral_1_angle_unn) * temp_unn_x \
                                     + math.sin(self.spiral_1_angle_unn) * temp_unn_y
                    temp_mov.unn.y = math.sin(self.spiral_1_angle_unn) * temp_unn_x \
                                     + math.cos(self.spiral_1_angle_unn) * temp_unn_y

                elif attack_type == 7:
                    temp_shape = ShapePolygon(self.spiral_1_radius, self.spiral_1_color.get_new_color(), 4, 0.00)
                    temp_mov.unn.x = uniform(-1, 1) * self.spiral_1_unn_add
                    temp_mov.unn.y = uniform(-1, 1) * self.spiral_1_unn_add

                elif attack_type == 8:
                    temp_shape = ShapePolygon(self.spiral_1_radius, self.spiral_1_color.get_new_color(), 2, 0,
                                              fast_collision=True, radius_max=self.spiral_1_radius_max,
                                              radius_incr=self.spiral_1_radius_incr, should_glow=True,
                                              border_length=3, pulsate_mult=3, border_length_glow=3,
                                              point_at_vel=True)
                    temp_unn_x = self.spiral_1_unn_add_x * (1 - 3 * i / self.spiral_1_arms)
                    temp_unn_y = self.spiral_1_unn_add_y * (1 - 2 * i / self.spiral_1_arms)

                    temp_mov.unn.x = math.cos(self.spiral_1_angle_unn) * temp_unn_x \
                                     + math.sin(self.spiral_1_angle_unn) * temp_unn_y
                    temp_mov.unn.y = math.sin(self.spiral_1_angle_unn) * temp_unn_x \
                                     + math.cos(self.spiral_1_angle_unn) * temp_unn_y
                else:
                    raise AttackIndexError

                temp_proj = Projectile(temp_mov, temp_shape)  # create projectile

                if attack_type != 2:
                    self.projectiles.add_projectile(temp_proj)  # append proj to proj list

                elif (self.timer // 60) % 5 not in [3, 4]:  # for sub-attack 2 it has moments of attack pausing
                    self.projectiles.add_projectile(temp_proj)

            if attack_type in [0, 1]:
                self.spiral_1_special_counter += 1

        if attack_type in [6, 8]:
            self.spiral_1_angle_unn += self.spiral_1_angle_unn_incr

        self.spiral_1_angle += self.spiral_1_angle_incr  # increments the primary angle for attack

        self.projectiles.list_update()

        # ends attack once time reaches the end time and the projectile list has only 30 or less proj
        if self.timer > self.spiral_1_time_end and (len(self.projectiles) < 30):
            return True
        return False

    def initialize_floor_1(self, attack_type):
        self.attack_started = True

        if attack_type == 0:
            self.floor_1_color = ColorRainbow(None, [90, 50, 150], [255, 60, 200], [0.1, 0.1, 0.02], [0.2, 2, 0.05])

            temp_mov = MovementStandard(0, 0, uniform(15, 20), uniform(10, 15))
            temp_circ = ShapeCircle(75, self.floor_1_color.current_RGB)
            self.floor_1_pos_proj = Projectile(temp_mov, temp_circ, bounce_back=True, min_y=height * 0.45)

            self.floor_1_arms = 4

            self.floor_1_angle = 0
            self.floor_1_angle_incr = math.pi / 3

            self.floor_1_angle_acc = 0
            self.floor_1_angle_incr_acc = math.pi / 3

            self.floor_1_wait_frames = 1

            self.floor_1_time_end = 60 * 23

            self.floor_1_speed = 5
            self.floor_1_speed_acc = 0.1
            self.floor_1_jer_add = 0.003

            # proj info
            self.floor_1_radius = 35
            self.floor_1_radius_min = 1
            self.floor_1_radius_incr = -0.2

            self.floor_1_time_start = 60 * 3
        elif attack_type == 1:
            self.floor_1_color = ColorRainbow(None, [150, 255, 50], [250, 255, 255], [0.2, 0.1, 0.5], [0.6, 2, 0.9])

            temp_mov = MovementStandard(0, 0, uniform(2.5, 3.5), uniform(.7, 1.3))
            temp_circ = ShapePolygon(75, self.floor_1_color.current_RGB, 13, 0.01)
            self.floor_1_pos_proj = Projectile(temp_mov, temp_circ, bounce_back=True)

            self.floor_1_arms = 8

            self.floor_1_angle = 0
            self.floor_1_angle_incr = .3

            self.floor_1_angle_acc = choice([-1, 1]) * -0.05 / self.difficulty
            self.floor_1_angle_incr_acc = 0.3

            self.floor_1_wait_frames = 11

            self.floor_1_time_end = 60 * 20

            self.floor_1_speed = 5
            self.floor_1_speed_acc = -0.05
            self.floor_1_jer_add = 0

            # proj info
            self.floor_1_radius = 1
            self.floor_1_radius_incr = 0.04
            self.floor_1_radius_min = 1
            self.floor_1_radius_max = 10

            self.floor_1_time_start = 60 * 1
        elif attack_type == 2:  # WORK IN PROGRESS ATTACK - NOT FINISHED YET
            self.floor_1_color = ColorRainbow([255, 255, 255], [0, 0, 255], [255, 255, 255], [1, 1, 1],
                                              [3, 3, 3])

            temp_mov = MovementStandard(0, 0, 4.5 * uniform(2.5, 3.5), 1)
            temp_circ = ShapePolygon(130, self.floor_1_color.current_RGB, 4, 0.2, border_length=5)
            self.floor_1_pos_proj = Projectile(temp_mov, temp_circ, bounce_back=True)

            self.floor_1_arms = 3

            self.floor_1_angle = 0
            self.floor_1_angle_incr = .03

            self.floor_1_angle_acc = -0.05 / self.difficulty * 4
            self.floor_1_angle_incr_acc = 0.03

            self.floor_1_wait_frames = 9

            self.floor_1_time_end = 60 * 12

            self.floor_1_speed = 5
            self.floor_1_speed_acc = -0.05
            self.floor_1_jer_add = 0

            # proj info
            self.floor_1_radius = 1
            self.floor_1_radius_min = 1
            self.floor_1_radius_max = 30
            self.floor_1_radius_incr = 0.1

            self.floor_1_time_start = 60 * 1
        elif attack_type == 3:  # WORK IN PROGRESS ATTACK - NOT FINISHED YET
            self.floor_1_color = ColorRainbow([200, 100, 50, 200], [200, 100, 50], [255, 150, 255], [0.2, 0.1, 0.5],
                                              [0.4, 0.2, 2])

            temp_mov = MovementStandard(0, 0, 3.0 * uniform(4.8, 5.2), 1)
            temp_circ = ShapePolygon(130 / 4, self.floor_1_color.current_RGB, 6, -0.2, border_length=5)
            self.floor_1_pos_proj = Projectile(temp_mov, temp_circ, bounce_back=True, max_y=100,
                                               min_y=0)

            self.floor_1_arms = 7

            self.floor_1_angle = 0
            self.floor_1_angle_incr = .03

            self.floor_1_angle_acc = choice([1]) * -0.05 / self.difficulty * 2
            self.floor_1_angle_incr_acc = 0.03

            self.floor_1_wait_frames = 6

            self.floor_1_time_end = 60 * 30

            self.floor_1_speed = 5
            self.floor_1_speed_acc = -0.05
            self.floor_1_jer_add = 0

            # proj info
            self.floor_1_radius = 1
            self.floor_1_radius_incr = 0.06
            self.floor_1_radius_min = 1
            self.floor_1_radius_max = 25

            self.floor_1_time_start = 60 * 1
        elif attack_type == 4:  # WORK IN PROGRESS ATTACK - NOT FINISHED YET
            self.floor_1_color = ColorRainbow([200, 100, 50], [200, 100, 50], [255, 150, 255], [0.2, 0.1, 0.5],
                                              [0.4, 0.2, 2])

            temp_mov = MovementStandard(0, 0, 3.0 * uniform(4.8, 5.2), 1)
            temp_circ = ShapeCircle(130 / 4, self.floor_1_color.current_RGB, border_length=5)
            self.floor_1_pos_proj = Projectile(temp_mov, temp_circ, bounce_back=True, max_y=100,
                                               min_y=0)

            self.floor_1_arms = 12

            self.floor_1_angle = 0
            self.floor_1_angle_incr = .03

            self.floor_1_angle_acc = choice([1]) * -0.05 / self.difficulty * 2
            self.floor_1_angle_incr_acc = 0.03

            self.floor_1_wait_frames = 60

            self.floor_1_time_end = 60 * 30

            self.floor_1_speed = 5
            self.floor_1_speed_acc = -0.05
            self.floor_1_jer_add = 0

            # proj info
            self.floor_1_radius = 1
            self.floor_1_radius_incr = 0.06
            self.floor_1_radius_min = 1
            self.floor_1_radius_max = 25

            self.floor_1_border_len = 5

            self.floor_1_time_start = 60 * 1

    def floor_1(self, attack_type):
        if not self.attack_started:
            self.initialize_floor_1(attack_type)

        if self.timer % (self.difficulty * self.floor_1_wait_frames) == 0 and \
                self.floor_1_time_end > self.timer > self.floor_1_time_start:
            for i in range(self.floor_1_arms):
                temp_angle = self.floor_1_angle + i * math.tau / self.floor_1_arms
                temp_angle_acc = self.floor_1_angle_acc + i * math.tau / self.floor_1_arms

                if attack_type in [0, 1, 2, 3, 4]:
                    temp_mov = MovementStandard(self.floor_1_pos_proj.pos.x, self.floor_1_pos_proj.pos.y,
                                                self.floor_1_speed * math.cos(temp_angle),
                                                self.floor_1_speed * math.sin(temp_angle),
                                                self.floor_1_speed_acc * math.cos(temp_angle_acc),
                                                self.floor_1_speed_acc * math.sin(temp_angle_acc),
                                                0, self.floor_1_jer_add)
                if attack_type == 0:
                    temp_shape = ShapePolygon(self.floor_1_radius, self.floor_1_color.get_new_color(), 8, 0.03,
                                              radius_min=self.floor_1_radius_min, fast_collision=True,
                                              radius_incr=self.floor_1_radius_incr)
                    temp_proj = Projectile(temp_mov, temp_shape, min_y=-100)
                elif attack_type == 1:
                    temp_shape = ShapeCircle(self.floor_1_radius, self.floor_1_color.get_new_color(),
                                             radius_min=self.floor_1_radius_min, radius_incr=self.floor_1_radius_incr,
                                             radius_max=self.floor_1_radius_max)
                    temp_proj = Projectile(temp_mov, temp_shape, max_y=height + 200, min_y=-200, max_x=width + 200,
                                           min_x=-200)
                elif attack_type == 2:
                    temp_shape = ShapeCircle(self.floor_1_radius, self.floor_1_color.get_new_color(), should_glow=True,
                                             border_glow_func=lambda col: [col[0] * 0.5, col[1] * 0.5, col[2] * 0.5],
                                             radius_incr=self.floor_1_radius_incr, radius_min=self.floor_1_radius_min,
                                             radius_max=self.floor_1_radius_max)
                    temp_proj = Projectile(temp_mov, temp_shape)
                elif attack_type == 3:
                    temp_mov.vel.y += self.floor_1_pos_proj.pos.y / 50
                    temp_shape = ShapePolygon(self.floor_1_radius, self.floor_1_color.get_new_color(), 4,
                                              choice([-1, 1]) * -0.02,
                                              radius_min=self.floor_1_radius_min, radius_incr=self.floor_1_radius_incr,
                                              radius_max=self.floor_1_radius_max, fast_collision=True)
                    temp_proj = Projectile(temp_mov, temp_shape, min_y=-100)
                elif attack_type == 4:
                    temp_mov.vel.y += self.floor_1_pos_proj.pos.y / 10
                    temp_shape = ShapePolygon(self.floor_1_radius, self.floor_1_color.get_new_color(), 3,
                                              choice([-1, 1]) * -0.02,
                                              radius_min=self.floor_1_radius_min, radius_incr=self.floor_1_radius_incr,
                                              radius_max=self.floor_1_radius_max, border_length=self.floor_1_border_len)
                    temp_proj = Projectile(temp_mov, temp_shape, max_y=height + 600, min_y=-800, max_x=width + 200,
                                           min_x=-200)
                self.projectiles.add_projectile(temp_proj)

        self.floor_1_angle += self.floor_1_angle_incr  # incrementing angle
        self.floor_1_angle_acc += self.floor_1_angle_incr_acc  # incrementing angle_acc

        self.projectiles.list_update()
        self.floor_1_pos_proj.update()
        if self.floor_1_pos_proj.collide():
            player.lose_health()

        # making the position no longer bounce so it leaves screen
        if self.timer >= self.floor_1_time_end:
            self.floor_1_pos_proj.bounce_back = False

        # makes the primary 'moon' position projectile shrink once attack ends
        if attack_type == 0:
            if self.timer > self.floor_1_time_end and len(self.projectiles) < 30:
                return True
            elif self.timer > self.floor_1_time_end and self.timer % 5 == 0:
                self.floor_1_pos_proj.movement.vel.x *= 0.9
                self.floor_1_pos_proj.movement.vel.y *= 0.9
                self.floor_1_pos_proj.radius *= 0.9
        elif attack_type in [2]:
            if self.timer > self.floor_1_time_end and len(self.projectiles) < 50:
                return True
        elif attack_type in [1, 3]:
            if self.timer > self.floor_1_time_end and len(self.projectiles) < 100:
                return True
        elif attack_type in [4]:
            if self.timer > self.floor_1_time_end and len(self.projectiles) < 40:
                return True
        else:
            if self.timer > self.floor_1_time_end:
                return True
        return False

    def initialize_spiral_2(self, attack_type):
        self.attack_started = True
        if attack_type == 0:
            self.spiral_2_arms = 1
            self.spiral_2_angle = uniform(0, math.tau)
            self.spiral_2_angle_incr = 3

            self.spiral_2_radius = 17

            self.spiral_2_speed = 10

            self.spiral_2_color = ColorRainbow([255, 64, 100], [255, 64, 100], [255, 255, 255], [1, 1, 1], [2, 2, 2])

            self.spiral_2_center = [width / 2, height / 2]

            self.spiral_2_wait_frames = 1
            self.spiral_2_time_end = 10 * 60 * 100
        elif attack_type == 1:
            self.spiral_2_arms = 13

            self.spiral_2_angle = uniform(0, math.tau)
            self.spiral_2_angle_incr = 0.07

            self.spiral_2_radius = 17
            self.spiral_2_proj_angle_incr = 0.01

            self.spiral_2_speed = 3

            self.spiral_2_color = ColorRainbow([255, 64, 100], [255, 64, 100], [255, 255, 255], [1, 1, 1], [2, 2, 2])

            self.spiral_2_center = [width / 2, height / 2]

            self.spiral_2_wait_frames = 27
            self.spiral_2_time_end = 10 * 60 * 100

    def spiral_2(self, attack_type):
        if not self.attack_started:
            self.initialize_spiral_2(attack_type)

        if self.timer % self.spiral_2_wait_frames == 0 and self.timer < self.spiral_2_time_end:
            for i in range(self.spiral_2_arms):
                temp_angle = i * math.tau / self.spiral_2_arms + self.spiral_2_angle
                if attack_type in [0]:
                    temp_mov = MovementStandard(self.spiral_2_center[0], self.spiral_2_center[1],
                                                math.cos(temp_angle) * self.spiral_2_speed,
                                                math.sin(temp_angle) * self.spiral_2_speed,
                                                )
                if attack_type == 0:
                    temp_shape = ShapeCircle(self.spiral_2_radius, self.spiral_2_color.get_new_color(),
                                             should_glow=True,
                                             pulsate_mult=1.5)
                    temp_proj = Projectile(temp_mov, temp_shape)

                elif attack_type == 1:
                    temp_mov = MovementRotate.from_center(50, temp_angle, self.spiral_2_center,
                                                          self.spiral_2_proj_angle_incr * [-1, 1, -0.5, 0.5][i % 4],
                                                          self.spiral_2_speed)

                    temp_shape = ShapeCircle(self.spiral_2_radius, self.spiral_2_color.get_new_color(),
                                             should_glow=True,
                                             border_glow_func=lambda col: [col[0] / 2, col[1] / 2, col[2] / 2])
                    temp_proj = Projectile(temp_mov, temp_shape)

                self.projectiles.add_projectile(temp_proj)

        self.spiral_2_angle += self.spiral_2_angle_incr
        self.projectiles.list_update()

        if self.timer > self.spiral_2_time_end and len(self.projectiles) < 30:
            return True
        return False

    def main_update(self):
        self.timer += 1  # increments timer

        current_attack = self.attack_arr[self.attack_index]

        finish_attack = current_attack()  # executes the attack

        # once an attack finishes this runs
        if finish_attack:
            print(self.attack_index)
            self.looped_amount += 1

            self.attack_index += 1

            # returns the attacks back to the start
            if self.attack_index >= len(self.attack_arr):
                self.attack_index = self.ATTACK_INDEX_RETURN_TO

            self.timer = 0
            self.attack_started = False
