import pygame
import pygame.math
import random
from random import uniform, randint, choice
import math
from sys import exit
from pygame.locals import *
from typing import List, Set, Tuple, Dict, Union
from dataclasses import dataclass

# importing self-made files with classes
import components.text_boxes
import components.old_game_code
from components.projectiles import *
from components import level_loader
from components import player_class
from components.text_boxes import *
from components.config import *

# calculations file
import components.calculations as calc
from components.calculations import *

pygame.init()

pygame.display.set_caption('Particle Getaway')

global_is_testing = True

# getting screen sizes
true_screen_width, true_screen_height = pygame.display.get_desktop_sizes()[0]
true_screen = pygame.display.set_mode((true_screen_width, true_screen_height))

# game works on same size for everyone essentially and is just scaled up for actual displaying
screen = pygame.Surface((width, height), pygame.SRCALPHA)
screen_scale_factor = min(true_screen_width / width, true_screen_height / height)

# don't use these values when coding other things - just for scaling the game surface up to display
screen_scaled_width = int(width * screen_scale_factor)
screen_scaled_height = int(height * screen_scale_factor)
screen_scaled = pygame.Surface((screen_scaled_width, screen_scaled_height))
screen_scaled_position_blit = ((true_screen_width - width * screen_scale_factor) / 2,
                               (true_screen_height - height * screen_scale_factor) / 2)

clock = pygame.time.Clock()  # use frame rate rather than precise time - only use this for setting frame rate
clock_frame_rate = 60  # change this to affect the frames per second - this will mess up almost all aspects of the game

# initializations so other files can use screen variable
components.text_boxes.globals_initializer(screen)  # makes text boxes work
player_class.globals_initializer(screen)  # makes player class work


# just updates the pygame screen, keeps the framerate, etc.
def update_pygame() -> None:
    pygame.display.update()  # update screen
    clock.tick(clock_frame_rate)  # delays time

    # scales, and transforms the game screen onto true screen
    pygame.transform.scale(screen, (screen_scaled_width, screen_scaled_height), screen_scaled)
    true_screen.blit(screen_scaled, screen_scaled_position_blit)


def main_menu(player_score=-1, difficulty: str = 'Invalid', player: player_class.Player = None, background_color=None):
    # initializes player to their previous position if they have died, and to the top otherwise
    if player is None:
        player = player_class.Player(width / 2, 200)
    else:
        player = player_class.Player(player.pos.x, player.pos.y)

    # initializes the text box inputs for different difficulty settings
    extremely_easy = TextBoxToGetInput(120, [30, 30, 30], [255, 255, 255], 'EXTREMELY EASY', font_dict[75], width / 2,
                                       350, mid_bottom=True)
    easy = TextBoxToGetInput(120, [0, 0, 50], [150, 150, 255], 'EASY', font_dict[75], width / 2,
                             extremely_easy.rect.bottom + 50, mid_top=True)
    normal = TextBoxToGetInput(120, [0, 50, 0], [150, 255, 0], 'NORMAL', font_dict[75], width / 2,
                               easy.rect.bottom + 50, mid_top=True)
    hard = TextBoxToGetInput(120, [50, 0, 0], [255, 150, 150], 'HARD', font_dict[75], width / 2,
                             normal.rect.bottom + 50, mid_top=True)

    past_game = TextBoxToGetInput(120, [0, 50, 0], [150, 255, 0], 'OLD (DIFFERENT) LEVELS', font_dict[50], width / 5,
                                  easy.rect.bottom + 50, mid_top=True)

    components.projectiles.globals_initializer(screen,
                                               player)  # makes it so projectiles can function

    main_menu_background_projectiles = ProjectileList()  # initializes a list of background shapes
    for i in range(300):
        temp_mov = MovementStandard(randint(0, width), randint(0, height), uniform(0, 5), uniform(0, 5))
        temp_shape = ShapeCircle(5, (randint(220, 255), randint(220, 255), randint(220, 255)),
                                 border_glow_func=lambda col: col_mult(col, 0.03), pulsate_mult=5)
        temp_proj = Projectile(temp_mov, temp_shape, bounce_back=True)
        main_menu_background_projectiles.add_projectile(temp_proj)

    # manages a background which can change color
    if background_color is None:
        background_color = ColorRainbow([255, 255, 255], [200, 200, 200], [255, 255, 255], [0.04, 0.04, 0.04],
                                        [0.08, 0.08, 0.08])
    else:
        background_color = ColorRainbow(background_color, [200, 200, 200], [255, 255, 255], [0.04, 0.04, 0.04],
                                        [0.08, 0.08, 0.08], [5, 5, 5])

    # gets rid of the music (if this function is called after a function which has music playing)
    pygame.mixer.music.fadeout(2000)

    while True:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(music_arr[6])  # only loading music once old music fades out
            pygame.mixer.music.play(-1, 0, 2000)

        screen.fill(background_color.get_new_color())

        # Background circles
        main_menu_background_projectiles.list_update(False)

        # instructions for playing game
        temp_rect = draw_text('Particle Getaway', font_dict[100], (0, 0, 0), width / 2, 100,
                              mid_bottom=True)
        temp_rect = draw_text('Use WASD or Arrow keys to move - Press ESC to leave', font_dict[30], (0, 0, 150),
                              width / 2, temp_rect.bottom + 10, mid_top=True)
        temp_rect = draw_text('Hold Left Shift to move slower, or H to move faster', font_dict[30], (0, 0, 150),
                              width / 2, temp_rect.bottom + 10, mid_top=True)
        temp_rect = draw_text('Your player trail length is your health!', font_dict[30], (0, 0, 150),
                              width / 2, temp_rect.bottom + 10, mid_top=True)
        draw_text('Stay in the designated difficulty text to start the game!', font_dict[50], (50, 0, 150), width / 2,
                  temp_rect.bottom + 10, mid_top=True)

        # This code only runs if player has been sent back after dying
        if player_score != -1:
            draw_text(f'Your Score Was: {int(player_score)} - on {difficulty}', font_dict[100],
                      (0, 0, 0),
                      width / 2, height - 100, mid_top=True)

        # checking if player is within the text boxes of the difficulty settings to start the game
        commence_extremely_easy = extremely_easy.update_box_text(player.pos)
        commence_easy = easy.update_box_text(player.pos)
        commence_normal = normal.update_box_text(player.pos)
        commence_hard = hard.update_box_text(player.pos)

        commence_past_game = past_game.update_box_text(player.pos)

        # starting game if player has stayed in a difficulty box for enough time
        if commence_extremely_easy:
            game_screen(Dif.extremely_easy, player, background_color.current_RGB)
        elif commence_easy:
            game_screen(Dif.easy, player, background_color.current_RGB)
        elif commence_normal:
            game_screen(Dif.normal, player, background_color.current_RGB)
        elif commence_hard:
            game_screen(Dif.hard, player, background_color.current_RGB)

        elif commence_past_game:
            game_screen_old()

        player.update()

        # quits game if X is hit, or if esc is hit
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
        update_pygame()


def game_screen(difficulty_name, player: player_class.Player = None, background_color=None):
    if player is None:
        player = player_class.Player(width / 4, height * 3 / 4)  # player creation
    else:
        player = player_class.Player(player.pos.x, player.pos.y)  # player creation

    # sending variables to other files so they work properly
    level_loader.globals_initializer(screen, player)
    components.projectiles.globals_initializer(screen, player)
    player_class.globals_initializer(screen)
    components.text_boxes.globals_initializer(screen)

    global_level_loader = level_loader.GalaxyLevel(difficulty_dict[difficulty_name])

    pygame.mixer.music.fadeout(2000)  # fades out whatever music was playing before the game

    if background_color is None:
        background_color = ColorRainbow([0, 0, 0], [0, 0, 0], [30, 30, 30], [0.005, 0.005, 0.005],
                                        [0.015, 0.015, 0.015])
    else:
        background_color = ColorRainbow(background_color, [0, 0, 0], [30, 30, 30], [0.005, 0.005, 0.005],
                                        [0.015, 0.015, 0.015], [1, 1, 1])

    go_to_main_menu = False
    while True:
        for event in pygame.event.get():  # check for input to close program
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if no_menu_or_pause_screen_exit_instantly:
                    pygame.quit()
                    exit()
                go_to_main_menu = pause_screen()

        screen.fill(background_color.get_new_color())  # don't put any drawing prior to this

        global_level_loader.main_update()

        # starts music once previous music ends
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(music_arr[0])  # only loading music once old music fades out
            pygame.mixer.music.play(-1, 0, 0)

        player.update(difficulty_dict[difficulty_name])
        update_pygame()
        # checks if player has died, and to move onto the menu
        if not player.is_alive() or go_to_main_menu:
            main_menu(player.score, difficulty_name, player, background_color.current_RGB)


# plays the old version of the game
def game_screen_old():
    player_score, background_color = components.old_game_code.run_game()
    return main_menu(player_score, Dif.past_game, None, background_color)


# not implemented fully yet
def pause_screen():
    # making it so that a previous copy of screen is kept to continue blitting
    past_screen = pygame.surface.Surface((width, height))
    past_screen.blit(screen, (0, 0))

    ESC = lambda: draw_text('ESC:  ', font_dict[150], 'Red',
                            50, 300, 'Green', mid_left=True)
    return_to_main_menu = lambda: draw_text('Exit to Main Menu', font_dict[150], 'White',
                                            ESC().right, 300, 'Green', mid_left=True)
    SPACEBAR = lambda: draw_text('SPACE:  ', font_dict[150], 'Red', 50,
                                 return_to_main_menu().bottom + 50, 'Green', top_left=True)
    resume_game = lambda: draw_text('Resume Game', font_dict[150], 'White', SPACEBAR().right,
                                    return_to_main_menu().bottom + 50, 'Green', top_left=True)

    while True:
        # copying over the saved old screen
        screen.blit(past_screen, (0, 0))
        for event in pygame.event.get():  # check for input to close program
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return False

        return_to_main_menu()
        ESC()
        resume_game()
        SPACEBAR()

        update_pygame()


# game_screen_old()
if start_game_instantly:
    game_screen(default_difficulty_if_starting_instantly)
else:
    main_menu()
