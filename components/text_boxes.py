import pygame
import pygame.math
import random
from random import uniform, randint, choice
import math
from sys import exit
from pygame.locals import *
from typing import List, Set, Tuple, Dict, Union
from dataclasses import dataclass

# calculations file
import components.calculations as calc
from components.calculations import *

screen: pygame.surface.Surface = None


def globals_initializer(global_screen) -> None:
    """" this is used to get the variables from the main file to be used inside here"""
    global screen
    screen = global_screen


def draw_text(text, font: pygame.font.Font, color, x, y, background_color=None, *, mid_bottom=False, mid_top=False,
              top_left=False, top_right=False, bottom_left=False, bottom_right=False, mid_right=False, mid_left=False,
              display_text=True) -> pygame.rect.Rect:
    """
    draws the text specified
    if no position argument, then text  is placed at the center
    """

    text = str(text)
    if background_color is None:
        text_obj = font.render(text, 1, color)
    else:
        text_obj = font.render(text, 1, color, background_color)
    text_rect = text_obj.get_rect()

    if sum([mid_bottom, mid_top, top_left, top_right, bottom_left, bottom_right, mid_right, mid_left]) > 1:
        print('inputted too many location values of text box to function - input exactly 1')
        raise
    if mid_bottom:
        text_rect.midbottom = (x, y)
    elif mid_top:
        text_rect.midtop = (x, y)
    elif top_left:
        text_rect.topleft = (x, y)
    elif top_right:
        text_rect.topright = (x, y)
    elif bottom_left:
        text_rect.bottomleft = (x, y)
    elif bottom_right:
        text_rect.bottomright = (x, y)
    elif mid_left:
        text_rect.midleft = (x, y)
    elif mid_right:
        text_rect.midright = (x, y)
    else:
        text_rect.center = (x, y)

    if display_text:
        screen.blit(text_obj, text_rect)
    return text_rect  # so that future code can take the positions of a text box, and base further positions on it


class BoxToGetInput:
    """Note: don't use this outside of menus"""

    def __init__(self, time_wait, rect, start_color, end_color):
        self.time_wait = time_wait
        self.rect: pygame.rect.Rect = rect

        # starts at 0, continuously increases toward time_wait until returning True, goes back down if pos not inside
        self.current_time_filled = 0 + 0

        self.start_color = start_color
        self.end_color = end_color

        # creates list current_color regardless of start color being 3 or 4 length and start color being tuple or list
        self.current_color = [self.start_color[i] for i in range(len(self.start_color))]

    def update_return_filled(self, pos: list[float] | tuple[float] | pygame.math.Vector2,
                             draw_box=True) -> pygame.math.Vector2:
        was_inside_rect = False

        # checks if the position is inside the rectangle
        if type(pos) is tuple or type(pos) is list:
            if self.rect.collidepoint(pos[0], pos[1]):
                was_inside_rect = True
        elif type(pos) is pygame.math.Vector2:
            if self.rect.collidepoint(pos.x, pos.y):
                was_inside_rect = True

        if was_inside_rect:
            # increment current filled time if pos inside rect, with it not exceeding the wait time
            self.current_time_filled = min(self.time_wait, self.current_time_filled + 1)
        else:
            # decrement current filled time if pos not inside rect, with it not going below 0
            self.current_time_filled = max(0, self.current_time_filled - 1)

        for i in range(len(self.current_color)):
            # temp_num manages the current part of RGB(A)
            temp_num = self.start_color[i] * (1 - self.current_time_filled / self.time_wait)
            temp_num += self.end_color[i] * self.current_time_filled / self.time_wait

            self.current_color[i] = max(0, min(255, temp_num))  # makes number be only from 0 to 255

        if draw_box:
            pygame.draw.rect(screen, self.current_color, self.rect)

        # returns True if current time exceeds the total time required
        return self.current_time_filled >= self.time_wait


class TextBoxToGetInput(BoxToGetInput):
    """only supports checking to start something based on time of a position (mouse,player position)
    inside the text
    """

    def __init__(self, time_wait, start_color, end_color, text, font, x, y, *,
                 mid_bottom=False, mid_top=False, top_left=False, top_right=False,
                 bottom_left=False, bottom_right=False, mid_right=False, mid_left=False):
        temp_rect = draw_text(text, font, start_color, x, y, mid_bottom=mid_bottom, mid_top=mid_top, top_left=top_left,
                              top_right=top_right, bottom_left=bottom_left, bottom_right=bottom_right,
                              mid_right=mid_right, mid_left=mid_left, display_text=False)
        super().__init__(time_wait, temp_rect, start_color, end_color)

        self.text = text
        self.font = font

        self.x = x
        self.y = y

        self.mid_bottom = mid_bottom
        self.mid_top = mid_top
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right
        self.mid_right = mid_right
        self.mid_left = mid_left

    def update_box_text(self, pos):
        return_val = self.update_return_filled(pos, False)

        draw_text(self.text, self.font, self.current_color, self.x, self.y, mid_bottom=self.mid_bottom,
                  mid_top=self.mid_top, top_left=self.top_left, top_right=self.top_right, bottom_left=self.bottom_left,
                  bottom_right=self.bottom_right, mid_right=self.mid_right, mid_left=self.mid_left)

        return return_val
#
#
# class TextBoxDisplay:
#     def __init__(self, text, font: pygame.font.Font, color, x, y, background_color=None, *, mid_bottom=False,
#                  mid_top=False, top_left=False, top_right=False, bottom_left=False, bottom_right=False, mid_right=False,
#                  mid_left=False):
#         self.text = text
#         self.font = font
#         self.color = color
#         self.x = x
#         self.y = y
#         self.background_color = background_color
#
#         self.mid_bottom = mid_bottom
#         self.mid_top = mid_top
#         self.top_left = top_left
#         self.top_right = top_right
#         self.bottom_left = bottom_left
#         self.bottom_right = bottom_right
#         self.mid_right = mid_right
#         self.mid_left = mid_left
#
#     def draw(self) -> pygame.Vector2:
#
#
#     text = str(text)
#     if background_color is None:
#         text_obj = font.render(text, 1, color)
#     else:
#         text_obj = font.render(text, 1, color, background_color)
#     text_rect = text_obj.get_rect()
#
#     if sum([mid_bottom, mid_top, top_left, top_right, bottom_left, bottom_right, mid_right, mid_left]) > 1:
#         print('inputted too many location values of text box to function - input exactly 1')
#         raise
#     if mid_bottom:
#         text_rect.midbottom = (x, y)
#     elif mid_top:
#         text_rect.midtop = (x, y)
#     elif top_left:
#         text_rect.topleft = (x, y)
#     elif top_right:
#         text_rect.topright = (x, y)
#     elif bottom_left:
#         text_rect.bottomleft = (x, y)
#     elif bottom_right:
#         text_rect.bottomright = (x, y)
#     elif mid_left:
#         text_rect.midleft = (x, y)
#     elif mid_right:
#         text_rect.midright = (x, y)
#     else:
#         text_rect.center = (x, y)
#
#     if display_text:
#         screen.blit(text_obj, text_rect)
#     return text_rect  # so that future code can take the positions of a text box, and base further positions on it
