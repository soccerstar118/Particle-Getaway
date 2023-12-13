from dataclasses import dataclass
import pygame

pygame.init()


# so that typing out the names can be autocompleted by compiler
@dataclass
class Dif:
    past_game = 'Old Levels'

    extremely_easy = 'Extremely Easy'
    easy = 'Easy'
    normal = 'Normal'
    hard = 'Hard'


# difficulty dictionary
difficulty_dict = {Dif.extremely_easy: 8, Dif.easy: 4, Dif.normal: 2, Dif.hard: 1}

difficulty_dict2 = {}  # keeps difficulty_dict except key and value reversed
for key in difficulty_dict.keys():
    difficulty_dict2[difficulty_dict[key]] = key

# screen dimensions
width = 1536
height = 864

# music arr to play all music from
music_arr = ['Music/The Devourer of Gods.ogg',
             'Music/09. Treasures Within The Abomination.MP3',
             'Music/10. Pest of The Cosmos.MP3',
             'Music/DM DOKURO - Antarctic Reinforcement.MP3',
             'Music/08. The Heaven-Sent Abomination.MP3',
             "Music/23. Heaven's Hell-Sent Gift.MP3",
             'Music/00. The Tale of a Cruel World.MP3']

# font dictionary
font_dict = {}
for i in range(1, 300):
    font_dict[i] = pygame.font.SysFont(None, i)

__temp_num = 0
if __temp_num == 0:
    skip_intro = False
    start_game_instantly = False
    no_menu_or_pause_screen_exit_instantly = False
    default_difficulty_if_starting_instantly = Dif.hard
else:
    skip_intro = True
    start_game_instantly = True
    no_menu_or_pause_screen_exit_instantly = True
    default_difficulty_if_starting_instantly = Dif.hard
