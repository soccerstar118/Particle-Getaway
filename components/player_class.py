import pygame
import pygame.math
import random
from random import uniform, randint, choice
import math
from sys import exit
from pygame.locals import *
from typing import List, Set, Tuple, Dict, Union

# calculations file
import components.calculations as calc

# necessary for managing projectiles collision and losing health
from components import projectiles

# brings in difficult width and height among other things
from components.config import *

screen: pygame.surface.Surface = None


def globals_initializer(global_screen) -> None:
    global screen
    screen = global_screen


class Player:
    def __init__(self, pos_x, pos_y, max_health=15,
                 particles_decay_mult=0.95):
        """allows changing the player initial position, health, trail particle size"""
        self.pos = pygame.math.Vector2(pos_x, pos_y)
        self.radius = 15

        # not quite speed as player goes faster moving diagonally
        self.pos_incr_slow = 2
        self.pos_incr_normal = 5
        self.pos_incr_fast = 11

        # moving slow takes priority over fast movement when checking inputs if 2 keys are pressed
        self.slow_key = K_LSHIFT
        self.fast_key = K_h

        # color of player is white - do not change this
        # changing the trail color will break code
        self.color_trail = (0, 0, 255)
        self.max_health = max_health
        self.health = self.max_health

        # manages the trail of circles behind the player
        self.amount_particles = self.health + 1  # Health is correlational to particle amount
        self.particles_decay_mult = particles_decay_mult  # affects the particle size of the trail

        # creates the particle lists
        self.particles_past_circ: list[pygame.math.Vector2] = [None] * self.amount_particles
        self.particles_past_circ_color = [self.color_trail] * self.amount_particles
        for i in range(self.amount_particles):
            self.particles_past_circ[i] = pygame.math.Vector2((self.pos.x, self.pos.y))

        # deals with immunity in terms of frames (60 per second)
        self.immunity_timer = 0
        self.immunity_frames = 120

        self.score = 0  # keeps track of score within player

    def update(self, difficulty=-1) -> None:  # moves (takes keyboard input) and draws player
        self.immunity_timer += 1

        self.update_trail()
        self.draw_trail()

        self.move()
        self.draw()

        self.increment_score(difficulty)

    def update_trail(self) -> None:
        """updates the player trail to match up with past player positions"""
        temp_color = self.color_trail
        if self.is_in_immunity():  # calculates new color so it fades from red to blue
            temp_color = (255 * (1 - self.immunity_timer / self.immunity_frames), 0,
                          255 * self.immunity_timer / self.immunity_frames)

        temp_circ = pygame.math.Vector2((self.pos.x, self.pos.y))

        # removes the farthest away circle and then appends on a circle at player position
        self.particles_past_circ.pop()
        self.particles_past_circ.insert(0, temp_circ)
        self.particles_past_circ_color.pop()
        self.particles_past_circ_color.insert(0, temp_color)

    def draw_trail(self) -> None:
        """draws the player trail"""

        # draws the circles for each proj, with decreasing size
        # first circle is most recently added, and drawn the largest
        for i, circ in enumerate(self.particles_past_circ):
            temp_radius = self.radius * self.particles_decay_mult ** (i + 1)

            # draws an intermediary screen first so that transparency can be rendered
            screen_mid = pygame.surface.Surface((temp_radius * 2, temp_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(screen_mid, self.particles_past_circ_color[i][:3] + (temp_radius / self.radius * 255,),
                               (temp_radius, temp_radius),
                               temp_radius)
            screen.blit(screen_mid, (circ.x - temp_radius, circ.y - temp_radius))

    def move(self) -> None:
        """takes player input and moves accordingly"""

        # returns all keys pressed (True/False value depending on if pressed or not)
        keys = pygame.key.get_pressed()

        # determines the direction of movement - if two things override each other nothing happens
        is_up = (keys[pygame.K_w] or keys[pygame.K_UP])
        is_down = (keys[pygame.K_s] or keys[pygame.K_DOWN])
        is_left = (keys[pygame.K_a] or keys[pygame.K_LEFT])
        is_right = (keys[pygame.K_d] or keys[pygame.K_RIGHT])

        # temp vars used to multiply the movement based on fast, slow, or medium later
        temp_incr_x = 0
        temp_incr_y = 0

        # doesn't move if 2 contradicting movements are being instructed to occur (up and down, right and left)
        if is_up and not is_down:
            temp_incr_y -= 1
        elif is_down and not is_up:
            temp_incr_y += 1

        if is_left and not is_right:
            temp_incr_x -= 1
        elif is_right and not is_left:
            temp_incr_x += 1

        # updates player position, adding different amounts based on the speed to use
        # the slow key is prioritized over fast key -- > if neither are pressed normal movement is used
        if keys[self.slow_key]:
            self.pos.x += temp_incr_x * self.pos_incr_slow
            self.pos.y += temp_incr_y * self.pos_incr_slow
        elif keys[self.fast_key]:
            self.pos.x += temp_incr_x * self.pos_incr_fast
            self.pos.y += temp_incr_y * self.pos_incr_fast
        else:
            self.pos.x += temp_incr_x * self.pos_incr_normal
            self.pos.y += temp_incr_y * self.pos_incr_normal

        # making sure to not let player go out of bounds
        if self.pos.x > width:
            self.pos.x = width
        if self.pos.y > height:
            self.pos.y = height
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = 0

    def draw(self) -> None:
        """draws white circle for player when not immune, draws red(ish) circle while immune"""
        if not self.is_in_immunity():  # draws white circ if it hasn't been hit recently
            pygame.draw.circle(screen, (255, 255, 255), self.pos, self.radius)
        else:  # draws red circ if is currently in immunity time
            pygame.draw.circle(screen, (255, 254 * self.immunity_timer / self.immunity_frames,
                                        254 * self.immunity_timer / self.immunity_frames), self.pos, self.radius)

    def increment_score(self, difficulty) -> None:
        """Increments Score
        you get more score longer since last hit, increasingly so if on more difficult settings
        (lower difficulty number = more difficult)"""
        self.score += self.immunity_timer ** (0.5 / difficulty)

    def is_alive(self) -> bool:
        if self.health <= 0:
            return False
        return True

    def lose_health(self) -> None:
        """makes player lose health if they aren't in immunity
         also decreasing the corresponding circle in trail so that player trail is correlational to health"""

        if not self.is_in_immunity():
            self.immunity_timer = 0
            self.health -= 1

            self.amount_particles -= 1  # reducing particles so player trail is correlational w health
            self.particles_past_circ.pop()
            self.particles_past_circ_color.pop()

    def is_in_immunity(self) -> bool:
        """returns True if player was hit/spawned recently and cannot take damage, False otherwise"""
        if self.immunity_timer < self.immunity_frames:
            return True
        return False
