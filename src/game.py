from random import choice, randint, shuffle, random
from dataclasses import dataclass
import pgzrun
import pygame
import random
from pgzero.actor import Actor
from src.input import InputState
from pgzero.builtins import sounds
from enum import Enum

# Constants
WIDTH = 800
HEIGHT = 480
NUM_ROWS = 18
NUM_COLUMNS = 28
LEVEL_X_OFFSET = 50
GRID_BLOCK_SIZE = 25
ANCHOR_CENTRE = ("center", "center")
ANCHOR_CENTRE_BOTTOM = ("center", "bottom")

LEVELS = [ ["XXXXX     XXXXXXXX     XXXXX",
            "","","","",
            "   XXXXXXX        XXXXXXX   ",
            "","","",
            "   XXXXXXXXXXXXXXXXXXXXXX   ",
            "","","",
            "XXXXXXXXX          XXXXXXXXX",
            "","",""],

           ["XXXX    XXXXXXXXXXXX    XXXX",
            "","","","",
            "    XXXXXXXXXXXXXXXXXXXX    ",
            "","","",
            "XXXXXX                XXXXXX",
            "      X              X      ",
            "       X            X       ",
            "        X          X        ",
            "         X        X         ",
            "","",""],

           ["XXXX    XXXX    XXXX    XXXX",
            "","","","",
            "  XXXXXXXX        XXXXXXXX  ",
            "","","",
            "XXXX      XXXXXXXX      XXXX",
            "","","",
            "    XXXXXX        XXXXXX    ",
            "","",""]]

# Helper functions
def sign(x): return -1 if x < 0 else 1

def block(x, y, game):
    grid_x = (x - LEVEL_X_OFFSET) // GRID_BLOCK_SIZE
    grid_y = y // GRID_BLOCK_SIZE
    if 0 < grid_y < NUM_ROWS:
        row = game.grid[grid_y]
        return grid_x >= 0 and grid_x < NUM_COLUMNS and len(row) > 0 and row[grid_x] != " "
    return False

space_down = False
def space_pressed(keyboard):
    global space_down
    if keyboard.space:
        if space_down:
            return False
        else:
            space_down = True
            return True
    else:
        space_down = False
        return False

# Base collision actor
class CollideActor(Actor):
    def __init__(self, pos, anchor=ANCHOR_CENTRE):
        super().__init__("blank", pos, anchor)

    def move(self, dx, dy, speed, game=None):
        new_x, new_y = int(self.x), int(self.y)
        for _ in range(speed):
            new_x += dx
            new_y += dy

            if new_x < 70 or new_x > 730:  # Borders
                return True

            if ((dy > 0 and new_y % GRID_BLOCK_SIZE == 0 or
                 dx > 0 and new_x % GRID_BLOCK_SIZE == 0 or
                 dx < 0 and new_x % GRID_BLOCK_SIZE == GRID_BLOCK_SIZE-1)
                and block(new_x, new_y, game)):
                    return True

            self.pos = new_x, new_y
        return False

# Gravity actor
class GravityActor(CollideActor):
    MAX_FALL_SPEED = 10

    def __init__(self, pos):
        super().__init__(pos, ANCHOR_CENTRE_BOTTOM)
        self.vel_y = 0
        self.landed = False

    def update(self, game, detect=True):
        self.vel_y = min(self.vel_y + 1, GravityActor.MAX_FALL_SPEED)
        if detect:
            if self.move(0, sign(self.vel_y), abs(self.vel_y), game):
                self.vel_y = 0
                self.landed = True
            if self.top >= HEIGHT:
                self.y = 1
        else:
            self.y += self.vel_y

# Entities
class Orb(CollideActor):
    MAX_TIMER = 250

    def __init__(self, pos, dir_x):
        super().__init__(pos)
        self.direction_x = dir_x
        self.floating = False
        self.trapped_enemy_type = None
        self.timer = -1
        self.blown_frames = 6

    def update(self, game):
        self.timer += 1
        if self.floating:
            self.move(0, -1, randint(1,2), game)
        else:
            if self.move(self.direction_x, 0, 4, game):
                self.floating = True
        if self.timer == self.blown_frames: self.floating = True
        if self.timer >= Orb.MAX_TIMER or self.y <= -40:
            game.pops.append(Pop(self.pos, 1))
            if self.trapped_enemy_type is not None:
                game.fruits.append(Fruit(self.pos, self.trapped_enemy_type))
            game.play_sound("pop", 4)

class Bolt(CollideActor):
    SPEED = 7
    def __init__(self, pos, dir_x):
        super().__init__(pos)
        self.direction_x = dir_x
        self.active = True

    def update(self, game):
        if self.move(self.direction_x, 0, Bolt.SPEED, game):
            self.active = False
        else:
            for obj in game.orbs + [game.player]:
                if obj and obj.hit_test(self, game):
                    self.active = False
                    break
        dir_idx = "1" if self.direction_x>0 else "0"
        anim_frame = str((game.timer//4)%2)
        self.image = "bolt"+dir_idx+anim_frame

class Pop(Actor):
    def __init__(self, pos, type):
        super().__init__("blank", pos)
        self.type = type
        self.timer = -1

    def update(self):
        self.timer += 1
        self.image = "pop" + str(self.type) + str(self.timer//2)

class Fruit(GravityActor):
    APPLE = 0
    RASPBERRY = 1
    LEMON = 2
    EXTRA_HEALTH = 3
    EXTRA_LIFE = 4

    def __init__(self, pos, trapped_enemy_type=0):
        super().__init__(pos)
        self.type = choice([Fruit.APPLE, Fruit.RASPBERRY, Fruit.LEMON])
        self.time_to_live = 500

    def update(self, game):
        super().update(game)
        if game.player and game.player.collidepoint(self.center):
            game.player.score += (self.type + 1) * 100
            game.play_sound("score")
            self.time_to_live = 0
        self.time_to_live -= 1

# Player using InputState only
class Player(GravityActor):
    def __init__(self):
        super().__init__((WIDTH//2, 100))
        self.lives = 2
        self.score = 0
        self.health = 3
        self.direction_x = 1
        self.fire_timer = 0
        self.hurt_timer = 100
        self.blowing_orb = None

    def reset(self):
        self.pos = (WIDTH/2, 100)
        self.vel_y = 0
        self.direction_x = 1
        self.fire_timer = 0
        self.hurt_timer = 100
        self.health = 3
        self.blowing_orb = None

    def update(self, input_state, game):
        super().update(game, self.health > 0)

        self.fire_timer -= 1
        self.hurt_timer -= 1

        # Horizontal movement
        dx = 0
        if input_state.left: dx = -1
        elif input_state.right: dx = 1
        if dx != 0: self.direction_x = dx
        if dx != 0 and self.fire_timer <= 0: self.move(dx, 0, 4, game)

        # Jump
        if input_state.jump_pressed and self.vel_y == 0 and self.landed:
            self.vel_y = -16
            self.landed = False
            game.play_sound("jump")

        # Orb firing
        if input_state.fire and self.fire_timer <= 0 and len(game.orbs) < 5:
            x = min(730, max(70, self.x + self.direction_x*38))
            y = self.y - 35
            orb = Orb((x, y), self.direction_x)
            game.orbs.append(orb)
            self.blowing_orb = orb
            self.fire_timer = 20
            game.play_sound("blow", 4)

        # Blow current orb further
        if input_state.fire and self.blowing_orb:
            self.blowing_orb.blown_frames += 4
            if self.blowing_orb.blown_frames >= 120:
                self.blowing_orb = None
        else:
            self.blowing_orb = None

    def hit_test(self, obj, game):
        return False

# Robot class
class Robot(GravityActor):
    TYPE_NORMAL = 0
    TYPE_AGGRESSIVE = 1

    def __init__(self, pos, type):
        super().__init__(pos)
        self.type = type
        self.speed = randint(1,3)
        self.direction_x = 1
        self.alive = True
        self.change_dir_timer = 0
        self.fire_timer = 100

    def update(self, game):
        super().update(game)
        self.change_dir_timer -= 1
        self.fire_timer += 1

        if self.move(self.direction_x, 0, self.speed, game):
            self.change_dir_timer = 0

        if self.change_dir_timer <= 0:
            directions = [-1,1]
            if game.player: directions.append(sign(game.player.x - self.x))
            self.direction_x = choice(directions)
            self.change_dir_timer = randint(100, 250)

    def hit_test(self, orb, game):
        # simple rectangle collision
        if self.alive and self.x-20 < orb.x < self.x+20 and self.y-20 < orb.y < self.y+20:
            self.alive = False
            orb.trapped_enemy_type = 0  # any fruit type
            return True
        return False



# Game class with pause support
class Game:
    def __init__(self):
        self.level = -1
        self.level_colour = -1
        self.player = Player()
        self.fruits = []
        self.orbs = []
        self.enemies = []
        self.pops = []
        self.next_level()
        self.timer = -1

    def next_level(self):
        self.level += 1
        self.level_colour = (self.level_colour + 1) % 4
        self.grid = LEVELS[self.level % len(LEVELS)] + [LEVELS[self.level % len(LEVELS)][0]]

    def update(self, input_state: InputState):
        self.timer += 1
        self.player.update(input_state, self)
        for obj in self.fruits + self.orbs + self.enemies + self.pops:
            obj.update(self)
        # Clean up expired objects
        self.fruits = [f for f in self.fruits if f.time_to_live > 0]
        self.orbs = [o for o in self.orbs if o.timer < 250 and o.y > -40]

    def draw(self, screen):
        screen.blit("bg" + str(self.level_colour), (0,0))
        # Draw blocks
        block_sprite = "block" + str(self.level % 4)
        for row_y, row in enumerate(self.grid):
            if row:
                x = LEVEL_X_OFFSET
                for block_char in row:
                    if block_char != " ":
                        screen.blit(block_sprite, (x, row_y*GRID_BLOCK_SIZE))
                    x += GRID_BLOCK_SIZE
        # Draw all objects
        for obj in self.fruits + self.orbs + self.enemies + self.pops + [self.player]:
            obj.draw()

        for i in range(self.player.health):
            screen.blit("health", (10 + i*35, 10))

        # draw score
        score_text = str(self.player.score).rjust(6, "0")
        screen.draw.text(score_text, (WIDTH-120, 10), fontsize=32, color="white")
        
    def play_sound(self, name, count=1):
        try:
            getattr(sounds, name).play()
        except:
            pass

def next_level(self):
    self.level += 1
    self.level_colour = (self.level_colour + 1) % 4
    self.grid = LEVELS[self.level % len(LEVELS)] + [LEVELS[self.level % len(LEVELS)][0]]
    
    # Spawn some enemies
    self.enemies = []
    for i in range(3):  # spawn 3 robots
        x = 100 + i*200
        y = 100
        robot = Robot((x, y), Robot.TYPE_NORMAL)
        self.enemies.append(robot)