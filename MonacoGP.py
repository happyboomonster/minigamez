## - MonacoGP: A simple 2D top-view racing game designed to appear very similar to an arcade game -
##Copyright (C) 2023 Lincoln V.
##
##This program is free software: you can redistribute it and/or modify
##it under the terms of the GNU General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.
##
##You should have received a copy of the GNU General Public License
##along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pygame
import time
import random
import math

#IMPORTANT: Tiles are 8x8 px.

class Car():
    def __init__(self, arena, screen, AI=False, player=None):
        # - Physics constants -
        self.accelerate_const = random.randint(5,7) * 10
        self.decelerate_const = random.randint(3,5) * 10
        self.min_speed = 102
        self.max_speed = 300
        self.brake_heat_gen = random.randint(45,65) * 10
        self.brake_heat_release = random.randint(35,55) * 10

        # - Other setup -
        self.AI = AI
        self.alive = True #This changes to a number which counts down to 0 when the player dies. The reason for doing this is to the explosion frames have time to display themselves.
        self.pos = [arena.screen_size[0] * 4,arena.screen_size[1] * 7] #This value CAN be a float
        if(player != None and AI): #we need to set the AI to position itself either after or before the player
            if(random.randint(0,1) == 0): #before player (speed should be greater than player)
                self.max_speed = random.randint(225,265)
                self.pos[1] = player.pos[1] + screen.get_height() * 2.5
            else: #after player (speed should be slower than player)
                self.max_speed = random.randint(135,175)
                self.pos[1] = player.pos[1] - screen.get_height() - 8
        elif(player == None and AI):
            self.pos[1] -= arena.screen_size[1] * 8 #Spawned above the player if this is the start of the game. This is done so that the player does not get immediately slammed from behind.
            self.max_speed = random.randint(102,150) #Set the max speed to a low number, so that the player does have to pass the cars at the start of the game.
        pos = self.find_open_space(arena, screen)
        if(self.AI):
            self.position_bias = 1.0 + random.randint(-45,45) / 100
            random.shuffle(pos)
            if(player == None):
                decrement = 0 #delete any positions which conflict with the player's starting position
                for x in range(0,len(pos)):
                    if(pos[x - decrement] > arena.screen_size[0] * 4 - 16 and pos[x - decrement] < arena.screen_size[0] * 4 + 16):
                        del(pos[x - decrement])
                        decrement += 1
            self.pos[0] = pos[0]
        else:
            self.pos[0] = pos[math.floor(len(pos) / 2)]
        self.speed = self.min_speed #this is a variable controlling how fast self.pos[1] is decremented.
        self.last_tick = time.time()
        self.brake_heat = 0

        self.colors = [
            None,
            [random.randint(50,255),random.randint(50,255),random.randint(50,255)],
            [random.randint(50,255),random.randint(50,255),random.randint(50,255)],
            [random.randint(50,255),random.randint(50,255),random.randint(50,255)]
            ]


        self.image = [
            [ #car 1
            [ 0, 0, 0, 1, 1, 0, 0, 0],
            [ 0, 0, 1, 3, 3, 1, 0, 0],
            [ 0, 2, 1, 3, 3, 1, 2, 0],
            [ 0, 2, 1, 1, 1, 1, 2, 0],
            [ 0, 0, 1, 1, 1, 1, 0, 0],
            [ 0, 2, 1, 1, 1, 1, 2, 0],
            [ 0, 2, 1, 1, 1, 1, 2, 0],
            [ 0, 0, 0, 1, 1, 0, 0, 0]
            ],

            [ #car 2
            [ 0, 0, 0, 1, 1, 0, 0, 0],
            [ 0, 0, 0, 3, 3, 0, 0, 0],
            [ 0, 0, 2, 1, 1, 2, 0, 0],
            [ 0, 0, 2, 1, 1, 2, 0, 0],
            [ 0, 0, 0, 1, 1, 0, 0, 0],
            [ 0, 0, 1, 1, 1, 1, 0, 0],
            [ 0, 2, 1, 1, 1, 1, 2, 0],
            [ 0, 2, 1, 3, 3, 1, 2, 0]
            ],

            [ #explosion frame 1
            [ 0, 0, 0, 1, 1, 0, 0, 0],
            [ 0, 1, 1, 2, 2, 1, 1, 0],
            [ 0, 1, 2, 3, 1, 2, 1, 0],
            [ 1, 2, 3, 1, 3, 1, 2, 1],
            [ 1, 2, 1, 3, 1, 3, 2, 1],
            [ 0, 1, 2, 1, 3, 2, 1, 0],
            [ 0, 1, 1, 2, 2, 1, 1, 0],
            [ 0, 0, 0, 1, 1, 0, 0, 0]
            ],

            [ #explosion frame 2
            [ 0, 0, 0, 2, 2, 0, 0, 0],
            [ 0, 2, 2, 3, 1, 2, 2, 0],
            [ 0, 2, 2, 1, 3, 1, 2, 0],
            [ 2, 1, 1, 3, 1, 3, 1, 2],
            [ 2, 1, 3, 1, 3, 1, 1, 2],
            [ 0, 2, 1, 3, 1, 1, 2, 0],
            [ 0, 2, 2, 1, 1, 2, 2, 0],
            [ 0, 0, 0, 2, 2, 0, 0, 0]
            ]
            ]

        self.appearance = random.randint(0,len(self.image) - 3)

    # - Self explanatory: Accelerates the car (dependent on move() being called once per game loop) -
    def accelerate(self):
        if(self.alive == True):
            if(self.speed == 0):
                self.speed = 1
            elif(self.speed < self.max_speed):
                self.speed *= 1 + self.accelerate_const * (time.time() - self.last_tick)

    # - Self explanatory: Declerates the car (backwards not allowed, dependent on move() being called once per game loop) -
    def decelerate(self):
        if(self.speed > self.min_speed and self.alive == True):
            self.speed *= 1 - self.decelerate_const * (time.time() - self.last_tick)

    # - Moves the car forward by self.speed (frametime is taken into account) -
    def move(self, arena=None, screen=None, player=None):
        self.pos[1] -= self.speed * (time.time() - self.last_tick)
        if(self.alive == True):
            # - Check if self.speed is smaller than self.min_speed (accelerate if it isn't) -
            if(self.speed < self.min_speed):
                self.speed *= 1.025 #slow accelerate
            # - Decrease the player's brake heat -
            if(self.brake_heat > 0):
                self.brake_heat -= self.brake_heat_release * (time.time() - self.last_tick)
            # - Manage the player's movement (if AI) -
            if(self.AI):
                # - Always accelerate until self.speed reaches its max -
                if(self.speed < self.max_speed):
                    self.accelerate()
                # - Move left/right based on whether there is a block in our way ahead -
                self.pos[1] -= 8 * 4 #look 4 blocks ahead of current location
                positions = self.find_open_space(arena, screen)
                self.pos[1] += 8 * 4 #revert our position
                goal_pos = sum(positions) / len(positions) * self.position_bias #average the X pos of open positions, and attempt to go there
                if(goal_pos - 3 >= self.pos[0]):
                    direction = 64 * (time.time() - self.last_tick)
                elif(goal_pos + 3 <= self.pos[0]):
                    direction = -64 * (time.time() - self.last_tick)
                else:
                    direction = 0
                self.pos[0] += direction
        # - Force decelerate the player if they are dead -
        else:
            if(self.speed > self.min_speed):
                self.speed -= 102 * (time.time() - self.last_tick)
        # - Update the movement timer -
        self.last_tick = time.time()

    # - Similar to decelerate, but more aggressive (dependent on move() being called once per game loop) -
    def brake(self):
        if(self.speed > self.min_speed and self.alive == True):
            if(self.brake_heat < 10):
                self.speed *= 1 - self.decelerate_const * 3 * (time.time() - self.last_tick)
                self.brake_heat += self.brake_heat_gen * (time.time() - self.last_tick)

    # - Draws the player onscreen taking into account the offset given. Everything's units are in pixels. This function also returns True when the arena should be reset -
    def draw_self(self, screen, arena, player=None):
        offset = arena.offset[:]
        if(self.alive == True):
            pass
        elif(time.time() - self.alive < 3): #we died and need to display the explosion?
            self.appearance = (len(self.image) - 1) - int((time.time() - self.alive) * 8) % 2
        else: #Time to reset...
            self.__init__(arena, screen, self.AI, player)
            return True
        for y in range(0,len(self.image[self.appearance])):
            for x in range(0,len(self.image[self.appearance][y])):
                if(self.colors[self.image[self.appearance][y][x]] != None):
                    screen.set_at([int(x + self.pos[0] - offset[0]), int(y + self.pos[1] + offset[1])], self.colors[self.image[self.appearance][y][x]])
        return False

    # - Finds a open spaces to spawn on at the Y coordinate the player is currently at -
    def find_open_space(self, arena, screen):
        old_pos = self.pos[:]
        self.pos[0] = 0
        safe = []
        for x in range(0,arena.screen_size[0]):
            if(self.check_arena_collision(arena, screen, True)):
                pass
            else:
                safe.append(self.pos[0])
            self.pos[0] += 8
        self.pos = old_pos[:]
        return safe

    # - Returns True when touching another Car() entity -
    def check_car_collision(self, entity): #Check collision with another Car() entity
        if(self.alive == True):
            my_collision = [self.pos[0], self.pos[1], self.pos[0] + 8, self.pos[1] + 8] #get collision boxes
            other_collision = [entity.pos[0], entity.pos[1], entity.pos[0] + 8, entity.pos[1] + 8]
            if(my_collision[0] < other_collision[2]):
                if(my_collision[2] > other_collision[0]):
                    if(my_collision[1] < other_collision[3]):
                        if(my_collision[3] > other_collision[1]):
                            # - COLLISION! -
                            self.alive = time.time()

    # - Checks if the player hit something. If so, returns True. Else, False -
    def check_arena_collision(self, arena, screen, probe=False):
        # - Readjust our collision boxes so they can be used well with the map (the map is drawn backwards, down-up, not up-down, so the player's collision has to be tweaked a bit to compensate) -
        if(self.alive == True):
            my_collision = [self.pos[0], self.pos[1] * -1 + screen.get_height(), self.pos[0] + 8, self.pos[1] * -1 + screen.get_height() - 8]
            my_collision = [my_collision[0] / 8, my_collision[1] / 8, my_collision[2] / 8, my_collision[3] / 8]
            for y in range(math.floor(my_collision[3]), math.ceil(my_collision[1])):
                for x in range(math.floor(my_collision[0]),math.ceil(my_collision[2])):
                    if(y < len(arena.arena) and x < len(arena.arena[0]) and x >= 0 and y >= 0):
                        if(arena.arena[y][x] == 1 or arena.arena[y][x] == 0 or arena.arena[y][x] == 2): #Hit a tree/driving on grass (lost control)? CRASH!
                            if(not probe):
                                self.alive = time.time()
                            else:
                                return True
                        elif(arena.arena[y][x] == 6): #Level end?
                            if(not probe):
                                return True #level finished! (only returns this when NOT in probe mode)
        return False
                    

class Arena():
    def __init__(self):
        self.tiles = [
            [ #grass
            [ 2, 2, 2, 2, 2, 2, 2, 2],
            [ 2, 2, 2, 2, 5, 2, 2, 2],
            [ 2, 2, 2, 2, 3, 2, 2, 2],
            [ 2, 5, 2, 2, 5, 2, 3, 2],
            [ 2, 3, 2, 2, 3, 2, 5, 2],
            [ 2, 5, 2, 2, 2, 2, 3, 2],
            [ 2, 2, 3, 2, 2, 5, 2, 2],
            [ 2, 2, 2, 2, 2, 2, 2, 2]
            ],

            [ #tree
            [ 2, 2, 2, 2, 0, 2, 2, 2],
            [ 2, 2, 2, 5, 0, 2, 2, 2],
            [ 2, 2, 2, 0, 5, 0, 2, 2],
            [ 2, 2, 0, 5, 2, 0, 2, 2],
            [ 2, 0, 5, 0, 5, 2, 0, 2],
            [ 2, 0, 2, 5, 2, 5, 0, 2],
            [ 2, 2, 5, 0, 5, 2, 2, 2],
            [ 2, 2, 2, 5, 2, 2, 2, 2]
            ],

            [ #house
            [ 2, 2, 2, 0, 2, 2, 2, 2],
            [ 2, 2, 0, 1, 0, 2, 2, 2],
            [ 2, 0, 1, 1, 1, 0, 2, 2],
            [ 0, 0, 1, 1, 1, 0, 0, 2],
            [ 2, 0, 1, 1, 1, 0, 2, 2],
            [ 2, 0, 1, 1, 3, 0, 2, 2],
            [ 2, 0, 1, 1, 3, 0, 2, 2],
            [ 2, 0, 0, 0, 0, 0, 2, 2]
            ],

            [ #road (middle)
            [ 0, 0, 0, 0, 4, 0, 0, 0],
            [ 0, 0, 0, 4, 0, 0, 0, 0],
            [ 0, 0, 0, 0, 4, 0, 0, 0],
            [ 0, 0, 0, 0, 0, 0, 0, 0],
            [ 0, 0, 0, 4, 0, 0, 0, 0],
            [ 0, 0, 0, 0, 4, 0, 0, 0],
            [ 0, 0, 0, 4, 0, 0, 0, 0],
            [ 0, 0, 0, 0, 0, 0, 0, 0]
            ],

            [ #road (left side)
            [ 2, 0, 0, 0, 4, 0, 0, 0],
            [ 2, 0, 0, 4, 0, 0, 0, 0],
            [ 2, 0, 0, 0, 4, 0, 0, 0],
            [ 2, 0, 0, 0, 0, 0, 0, 0],
            [ 2, 0, 0, 4, 0, 0, 0, 0],
            [ 2, 0, 0, 0, 4, 0, 0, 0],
            [ 2, 0, 0, 4, 0, 0, 0, 0],
            [ 2, 0, 0, 0, 0, 0, 0, 0]
            ],

            [ #road (right side)
            [ 0, 0, 0, 0, 4, 0, 0, 2],
            [ 0, 0, 0, 4, 0, 0, 0, 2],
            [ 0, 0, 0, 0, 4, 0, 0, 2],
            [ 0, 0, 0, 0, 0, 0, 0, 2],
            [ 0, 0, 0, 4, 0, 0, 0, 2],
            [ 0, 0, 0, 0, 4, 0, 0, 2],
            [ 0, 0, 0, 4, 0, 0, 0, 2],
            [ 0, 0, 0, 0, 0, 0, 0, 2]
            ],

            [ #finish!
            [ 4, 4, 0, 0, 4, 4, 0, 0],
            [ 4, 4, 0, 0, 4, 4, 0, 0],
            [ 0, 0, 4, 4, 0, 0, 4, 4],
            [ 0, 0, 4, 4, 0, 0, 4, 4],
            [ 4, 4, 0, 0, 4, 4, 0, 0],
            [ 4, 4, 0, 0, 4, 4, 0, 0],
            [ 0, 0, 4, 4, 0, 0, 4, 4],
            [ 0, 0, 4, 4, 0, 0, 4, 4]
            ]
            
            ]

        self.colors = [
            [0,0,0], #black - 0
            [255,0,0], #red
            [0,255,0], #green - 2
            [0,0,255], #blue
            [255,255,0], #yellow - 4
            [0,255,255], #turquoise
            [255,0,255], #pink - 6
            [255,255,255] #white
            ]

        self.offset = [0,0] #offset in tiles where the arena is currently being drawn
        self.screen_size = [24,24] #tile count - how many tiles in X and Y fill the screen?

        self.arena = [ #This list continually grows...This arena can SELF-GENERATE!
            ]

        # - Arena generator variables -
        self.current_road_pos = self.screen_size[0] / 2
        self.current_road_width = self.screen_size[0] - 2
        self.generate_count = 0 #how many times generate_road_row() has been run
        self.difficulty = 1 #valid values: anything above 0...1 is best left as the maximum difficulty.
        self.made_finish = False

    # - Configures a screen size and loads a new level -
    def new_level(self,screen_size,difficulty=1):
        # - Reset arena attributes -
        self.screen_size = screen_size[:]
        self.offset = [0,0]
        # - Reset level generator attributes -
        self.current_road_pos = self.screen_size[0] / 2
        self.current_road_width = self.screen_size[0] - 2
        self.generate_count = 0
        self.made_finish = False
        self.difficulty = difficulty
        # - Begin a new level -
        for y in range(0,self.screen_size[1] + 1):
            arena.generate_road_row()

    # - Based on offset[1], this checks whether more level should be generated -
    def handle_generation(self):
        finished = False
        while not finished:
            if(self.offset[1] + self.screen_size[1] * 2 > len(self.arena)): #new territory should be generated if we are 1 screen away from the end of what has been generated already
                self.generate_road_row()
            else:
                finished = True

    # - Generates a new row of tiles for the arena/track -
    def generate_road_row(self):
        # - Readjust the road's width with a SMALL chance -
        if(random.randint(0,7) == 0):
            self.current_road_width += random.randint(-math.ceil(self.screen_size[0] / (8 / self.difficulty)),math.ceil(self.screen_size[0] / (8 / self.difficulty)))
            if(self.current_road_width < math.ceil(self.screen_size[0] / 3)): #road too thin?
                self.current_road_width = math.ceil(self.screen_size[0] / 3)
            elif(self.current_road_width > self.screen_size[0] - 3): #this road is too wide for the screen?
                self.current_road_width = self.screen_size[0] - 3
            # - Does this road connect to the last one? It'd better... -
            if(math.floor(self.current_road_pos - self.current_road_width / 2) < 1): #road too far off to the left?
                self.current_road_pos = math.ceil(self.current_road_width / 2 + 1)
            elif(math.ceil(self.current_road_pos + self.current_road_width / 2) > self.screen_size[0] - 1): #road too far to the right?
                self.current_road_pos = math.floor(self.screen_size[0] - self.current_road_width / 2 - 1)
        # - Reposition the center of the road -
        elif(random.randint(0,7) == 0):
            self.current_road_pos += random.randint(max([-math.ceil(self.screen_size[0] / (8 / self.difficulty)), -math.floor(self.current_road_width / (4 / self.difficulty))]),min([math.ceil(self.current_road_width / (4 / self.difficulty)), math.ceil(self.screen_size[0] / (8 / self.difficulty))]))
            if(math.floor(self.current_road_pos - self.current_road_width / 2) < 1): #road too far off to the left?
                self.current_road_pos = math.ceil(self.current_road_width / 2 + 1)
            elif(math.ceil(self.current_road_pos + self.current_road_width / 2) >= self.screen_size[0] - 1): #road too far to the right?
                self.current_road_pos = math.floor(self.screen_size[0] - self.current_road_width / 2 - 1)
        # - Generate the new tiles! -
        tile_row = [] #Begin with trees and grass
        offset = random.randint(0,10)
        for x in range(0,self.screen_size[0]):
            if(self.generate_count % 8 > 6): #houses and trees and grass?
                if((x + offset) % 4 > 2): #houses?
                    tile_row.append(2)
                elif((x + offset) % 4 > 1): #trees?
                    tile_row.append(1)
                else: #grass
                    tile_row.append(0)
            elif(self.generate_count % 8 > 4): #trees and grass?
                if((x + offset) % 3 > 1):
                    tile_row.append(1)
                else:
                    tile_row.append(0)
            else: #grass?
                tile_row.append(0) #all grass
        # - Add the road in overtop -
        for x in range(math.ceil(self.current_road_pos - self.current_road_width / 2), math.floor(self.current_road_pos + self.current_road_width / 2)):
            if(x == round(self.current_road_pos - self.current_road_width / 2)): #tile furthest to the left?
                tile_row[x] = 4 #left road side
            elif(x == round(self.current_road_pos + self.current_road_width / 2) - 1): #tile furthest to the left?
                tile_row[x] = 5 #right road side
            else: #road middle tile
                tile_row[x] = 3
        # - Check if this should be the finish -
        if(len(self.arena) > 5000 * self.difficulty):
            if(random.randint(0,math.ceil(10 * self.difficulty)) == 0 and self.made_finish == False):
                self.made_finish = True
                # - Level should end here -
                for x in range(0,len(tile_row)):
                    tile_row[x] = 6 #end tile
        # - Move the tiles to the arena! -
        self.arena.append(tile_row)
        # - Update the run counter -
        self.generate_count += 1

    def draw_self(self, screen):
        pixel_offset = [self.offset[0] % 8, self.offset[1] % 8]
        onscreen_pos = [-1,self.screen_size[1] + 1]
        for y in range(int(self.offset[1] / 8) - 1, int(self.offset[1] / 8) + self.screen_size[1] + 1):
            onscreen_pos[1] -= 1
            for x in range(int(self.offset[0] / 8), int(self.offset[0] / 8) + self.screen_size[0]):
                onscreen_pos[0] += 1
                # - Draw a tile IF the requested index is in arena's range -
                if(y >= 0 and y < len(self.arena)):
                    if(x >= 0 and x < self.screen_size[0]):
                        for draw_tiley in range(0,len(self.tiles[self.arena[y][x]])):
                            for draw_tilex in range(0,len(self.tiles[self.arena[y][x]][draw_tiley])):
                                screen.set_at([int(draw_tilex + onscreen_pos[0] * 8 + pixel_offset[0]), int(draw_tiley + onscreen_pos[1] * 8 + pixel_offset[1])], self.colors[self.tiles[self.arena[y][x]][draw_tiley][draw_tilex]])
            onscreen_pos[0] = -1

### - Arena test code [works] -
##arena = Arena()
##screen = pygame.display.set_mode([128,128],pygame.SCALED | pygame.RESIZABLE | pygame.HWACCEL)
##arena.new_level([int(screen.get_width() / 8), int(screen.get_height() / 8)])
##running = True
##while running:
##    arena.handle_generation()
##    arena.offset[1] += 5
##    screen.fill([0,0,0])
##    arena.draw_self(screen)
##    pygame.display.flip()
##    for event in pygame.event.get():
##        if(event.type == pygame.QUIT):
##            running = False
##pygame.quit()

### - Car test code -
##screen = pygame.display.set_mode([128,128],pygame.SCALED | pygame.RESIZABLE | pygame.HWACCEL)
##arena = Arena()
##arena.new_level([int(screen.get_width() / 8), int(screen.get_height() / 8)])
##running = True
##car = Car(arena, screen)
##enemy_cars = [ Car(arena, screen, True), Car(arena, screen, True), Car(arena, screen, True), Car(arena, screen, True) ]
##car_directions = [0,0]
##brake = False
##last_loop = time.time()
##while running:
##    screen.fill([0,0,0])
##    arena.draw_self(screen)
##    arena.offset[1] += math.sqrt(abs(screen.get_height() - (arena.offset[1] + car.pos[1]))) / 3
##    car.move()
##    if(car.draw_self(screen, arena, car)):
##        arena.__init__()
##        arena.new_level([int(screen.get_width() / 8), int(screen.get_height() / 8)])
##    for x in range(0,len(enemy_cars)):
##        enemy_cars[x].draw_self(screen, arena, car)
##    pygame.display.flip()
##
##    arena.handle_generation()
##    car.check_arena_collision(arena, screen)
##    for x in range(0,len(enemy_cars)):
##        car.check_car_collision(enemy_cars[x])
##        enemy_cars[x].check_car_collision(car)
##
##        enemy_cars[x].move(arena, screen, car)
##        enemy_cars[x].check_arena_collision(arena, screen)
##
##        for y in range(0,len(enemy_cars)):
##            if(y == x):
##                continue
##            enemy_cars[x].check_car_collision(enemy_cars[y])
##
##    for event in pygame.event.get():
##        if(event.type == pygame.QUIT):
##            running = False
##        if(event.type == pygame.KEYDOWN):
##            if(event.key == pygame.K_UP):
##                car_directions[1] = 1
##            elif(event.key == pygame.K_DOWN):
##                car_directions[1] = -1
##            elif(event.key == pygame.K_LEFT):
##                car_directions[0] = -64
##            elif(event.key == pygame.K_RIGHT):
##                car_directions[0] = 64
##            elif(event.key == pygame.K_SPACE):
##                brake = True
##        elif(event.type == pygame.KEYUP):
##            if(event.key == pygame.K_UP):
##                car_directions[1] = 0
##            elif(event.key == pygame.K_DOWN):
##                car_directions[1] = 0
##            elif(event.key == pygame.K_LEFT):
##                car_directions[0] = 0
##            elif(event.key == pygame.K_RIGHT):
##                car_directions[0] = 0
##            elif(event.key == pygame.K_SPACE):
##                brake = False
##
##    if(car.alive == True):
##        car.pos[0] += car_directions[0] * (time.time() - last_loop)
##    if(car_directions[1] > 0):
##        car.accelerate()
##    elif(car_directions[1] < 0):
##        car.decelerate()
##    if(brake):
##        car.brake()
##    last_loop = time.time()
##pygame.quit()

# - Close/open scene effects (similar to fade in/out) -
close_timer = False
def close(screen):
    global close_timer
    if(close_timer != False):
        if(time.time() - close_timer > 1): #fade done?
            close_timer = False
            return True
        else: #fade not done.
            move = screen.get_width() * (time.time() - close_timer)
            pygame.draw.rect(screen, [0,0,0], [0, 0, move, screen.get_height()], 0)
            pygame.draw.rect(screen, [0,0,0], [screen.get_width() - move, 0, move + 1, screen.get_height()], 0)
            return False
    else:
        close_timer = time.time()
        return False

open_timer = False
def open(screen):
    global open_timer
    if(open_timer != False):
        if(time.time() - open_timer > 1): #fade done?
            open_timer = False
            return True
        else: #fade not done.
            move = int(screen.get_width() * (time.time() - open_timer))
            pygame.draw.rect(screen, [0,0,0], [0, 0, screen.get_width() - move, screen.get_height()], 0)
            pygame.draw.rect(screen, [0,0,0], [move, 0, screen.get_width() - move, screen.get_height()], 0)
            return False
    else:
        open_timer = time.time()
        return False

# - Game Loop -
pygame.font.init()
screen = pygame.display.set_mode([128,128],pygame.SCALED | pygame.RESIZABLE | pygame.HWACCEL)
pygame.display.set_caption("Monaco GP")
loop_continue = True
font = pygame.font.Font(None, 100)
while loop_continue:
    # - Front Screen -
    running = True
    arena = Arena() #arena used for scrolling background
    arena.new_level([int(screen.get_width() / 8), int(screen.get_height() / 8)])
    last_tick = time.time() #timing variable
    car = Car(arena, screen, True) #car used to drive on the arena (adds interest to the title screen)
    car.pos[1] = screen.get_height() / 2
    car.pos[0] = sum(car.find_open_space(arena, screen)) / len(car.find_open_space(arena, screen))
    while running:
        # - Event Loop -
        for event in pygame.event.get():
            if(event.type == pygame.QUIT): #exit game
                running = False
                loop_continue = False
            elif(event.type == pygame.KEYDOWN): #game start
                running = False

        # - Draw everything (title screen, "press any key to play", scrolling arena) -
        screen.fill([0,0,0]) #clear display
        arena.draw_self(screen) #draw arena
        car.draw_self(screen, arena) #draw car
        # - Handling the car is part of the draw routine -
        if(car.alive != True): #If the car is dead, reset it. NOTE: the 2.5s wait for the explosion will need to be changed if the explosion time in the Car() class is changed.
            closed = close(screen)
            if(time.time() - car.alive > 2.5 or closed):
                arena.__init__()
                arena.new_level([int(screen.get_width() / 8), int(screen.get_height() / 8)])
                car = Car(arena, screen, True)
                car.pos[1] = screen.get_height() / 2
                car.pos[0] = sum(car.find_open_space(arena, screen)) / len(car.find_open_space(arena, screen))
        if(car.check_arena_collision(arena, screen)): #car completed the level? Make a new one!
            if(close(screen)): #close the viewport, and reset the demo screen
                arena.__init__()
                arena.new_level([int(screen.get_width() / 8), int(screen.get_height() / 8)])
                car = Car(arena, screen, True)
                car.pos[1] = screen.get_height() / 2
                car.pos[0] = sum(car.find_open_space(arena, screen)) / len(car.find_open_space(arena, screen))
        else: #if the car ISN'T finished the level...
            car.move(arena, screen)
        # - Draw font-based things onscreen -
        screen.blit( pygame.transform.scale( font.render("MONACO GP",False,[255,255,255]), [screen.get_width(), int(screen.get_height() / 8)]), [0,0]) #title
        if(int(last_tick * 2) % 2 == 0): #blink the "press any key" words
            pak_title = pygame.transform.scale( font.render("Press Any Key To Play...",False,[255,255,255]), [screen.get_width(), int(screen.get_height() / 16)]) #press any key caption
            screen.blit( pak_title, [0, screen.get_height() / 2 - pak_title.get_height()] )
        pygame.display.flip()

        # - Update timing counter -
        last_tick = time.time()

        # - Generate new terrain -
        arena.handle_generation()
        arena.offset[1] = -car.pos[1] + screen.get_height() - (car.speed / 4.1) #move arena at the same pace as the car
        
    # - Game -
    if(loop_continue == False): #triggered if the player asked to exit
        continue
    else:
        while not close(screen): #close the frontscreen
            pygame.display.flip()
        # - Draw "Game Start!" on the screen, and wait for N seconds -
        start_surf = pygame.transform.scale(font.render("Game Start!",False,[255,255,255]), [screen.get_width() / 1.5, screen.get_height() / 6])
        screen.blit(start_surf, [screen.get_width() / 2 - start_surf.get_width() / 2, screen.get_height() / 2 - start_surf.get_height() / 2])
        pygame.display.flip()
        time.sleep(1.25)
    # - Player game state variables -
    level = 1 #when level reaches 11, the game is complete.
    lives = 5 #when this reaches -1, the game is over.
    # - Draw the level the player will begin on onscreen (1) -
    screen.fill([0,0,0])
    next_surf = pygame.transform.scale(font.render("Level " + str(level),False,[255,255,255]), [screen.get_width() / 1.75, screen.get_height() / 6])
    screen.blit(next_surf, [screen.get_width() / 2 - next_surf.get_width() / 2, screen.get_height() / 2 - next_surf.get_height() / 2])
    pygame.display.flip()
    time.sleep(1.25)
    # - Arena -
    arena = Arena()
    arena.new_level([int(screen.get_width() / 8), int(screen.get_height() / 8)], level / 11)
    running = True #whether the game should be exited
    # - Player car and AI car setup -
    car = Car(arena, screen)
    enemy_cars = [ Car(arena, screen, True), Car(arena, screen, True) ]
    car_directions = [0,0] #used for handling keypresses and converting them into car motion
    brake = False
    last_loop = time.time() #timing counter
    while running:
        # - Event loop -
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                running = False
                loop_continue = False
            if(event.type == pygame.KEYDOWN):
                if(event.key == pygame.K_UP):
                    car_directions[1] = 1
                elif(event.key == pygame.K_DOWN):
                    car_directions[1] = -1
                elif(event.key == pygame.K_LEFT):
                    car_directions[0] = -64
                elif(event.key == pygame.K_RIGHT):
                    car_directions[0] = 64
                elif(event.key == pygame.K_SPACE):
                    brake = True
            elif(event.type == pygame.KEYUP):
                if(event.key == pygame.K_UP):
                    car_directions[1] = 0
                elif(event.key == pygame.K_DOWN):
                    car_directions[1] = 0
                elif(event.key == pygame.K_LEFT):
                    car_directions[0] = 0
                elif(event.key == pygame.K_RIGHT):
                    car_directions[0] = 0
                elif(event.key == pygame.K_SPACE):
                    brake = False
        
        # - Draw everything -
        screen.fill([0,0,0]) #clear screen
        arena.draw_self(screen) #draw arena
        if(car.draw_self(screen, arena, car)):
            while not close(screen): #close the level
                pygame.display.flip()
            lives -= 1
            if(lives < 0): #game over?
                # - Draw the words "GAME OVER" onscreen for 2.5s before returning to the frontscreen -
                game_over_surf = pygame.transform.scale(font.render("GAME OVER",False,[255,255,255]), [screen.get_width() / 1.25, screen.get_height() / 6])
                screen.blit(game_over_surf, [screen.get_width() / 2 - game_over_surf.get_width() / 2, screen.get_height() / 2 - game_over_surf.get_height() / 2])
                pygame.display.flip()
                time.sleep(2.5)
                running = False
            else: #restart the level otherwise
                arena.__init__()
                arena.new_level([int(screen.get_width() / 8), int(screen.get_height() / 8)], level / 11)
                car.last_tick = time.time() #reset the car timing counter so that it doesn't go flying at the start of the next level
                enemy_cars = []
                for x in range(0, level * 2):
                    enemy_cars.append(Car(arena, screen, True))
                last_loop = time.time()
        for x in range(0,len(enemy_cars)):
            enemy_cars[x].draw_self(screen, arena, car)
        # - Draw the player's life counter, speed, level, and distance travelled -
        distance = str(int(abs(car.pos[1] - screen.get_height()) / 8)) + " KM Travelled"
        distance_surf = pygame.transform.scale(font.render(distance, False, [255,255,255]), [len(distance) * 5, 8])
        speed = str(int(car.speed / 8)) + " KM/S"
        speed_surf = pygame.transform.scale(font.render(speed, False, [255,255,255]), [len(speed) * 5, 8])
        lives_left = str(lives) + " Crashes Left"
        lives_surf = pygame.transform.scale(font.render(lives_left, False, [255,255,255]), [len(lives_left) * 5, 8])
        level_str = "Level " + str(level)
        level_surf = pygame.transform.scale(font.render(level_str, False, [255,255,255]), [len(level_str) * 5, 8])
        # - Draw the text onscreen -
        screen.blit(distance_surf, [screen.get_width() - distance_surf.get_width(), screen.get_height() - speed_surf.get_height() - distance_surf.get_height()])
        screen.blit(speed_surf, [screen.get_width() - speed_surf.get_width(), screen.get_height() - speed_surf.get_height()])
        screen.blit(lives_surf, [0, screen.get_height() - lives_surf.get_height()])
        screen.blit(level_surf, [screen.get_width() / 2 - level_surf.get_width() / 2, 0])
        pygame.display.flip()

        # - Move the arena and the player's car -
        car.move()
        arena.offset[1] = -car.pos[1] + screen.get_height() - (car.speed / 4.1)

        # - Generate new arena space -
        arena.handle_generation()

        # - Handle car collision -
        if(car.check_arena_collision(arena, screen)): #the car completed a level (returned True)?
            level += 1 #increase the level counter by one
            lives += 1 #add another life to the player's counter
            arena.__init__() #reset arena with harder level
            arena.new_level([int(screen.get_width() / 8), int(screen.get_height() / 8)], level / 11)
            car = Car(arena, screen) #reset player car
            enemy_cars = [] #add AI cars
            for x in range(0, level * 2):
                enemy_cars.append(Car(arena, screen, True))
            while not close(screen): #close the old level
                pygame.display.flip()
            # - Draw words telling which level is next -
            next_surf = pygame.transform.scale(font.render("Level " + str(level),False,[255,255,255]), [screen.get_width() / 1.75, screen.get_height() / 6])
            screen.blit(next_surf, [screen.get_width() / 2 - next_surf.get_width() / 2, screen.get_height() / 2 - next_surf.get_height() / 2])
            pygame.display.flip()
            time.sleep(1.25)
            car_directions = [0,0] #reset the keypress list so that the car doesn't move funny when the level starts
            car.last_tick = time.time() #reset the car timing counter so that it doesn't go flying when the level starts
            last_loop = time.time()
            
        for x in range(0,len(enemy_cars)):
            car.check_car_collision(enemy_cars[x])
            enemy_cars[x].check_car_collision(car)

            enemy_cars[x].move(arena, screen, car)
            enemy_cars[x].check_arena_collision(arena, screen)

            for y in range(0,len(enemy_cars)):
                if(y == x):
                    continue
                enemy_cars[x].check_car_collision(enemy_cars[y])

        # - Car movements corresponding to keypresses -
        if(car.alive == True):
            car.pos[0] += car_directions[0] * (time.time() - last_loop)
        if(car_directions[1] > 0):
            car.accelerate()
        elif(car_directions[1] < 0):
            car.decelerate()
        if(brake):
            car.brake()

        # - Update timing counter -
        last_loop = time.time()

        # - If level reaches 11, the game has been completed -
        if(level > 10):
            while not close(screen): #close the old level
                pygame.display.flip()
            # - Draw the words "Game Complete!" onscreen for 2.5s before returning to the frontscreen -
            complete_surf = pygame.transform.scale(font.render("Game Complete!",False,[255,255,255]), [screen.get_width() / 1.25, screen.get_height() / 6])
            screen.blit(complete_surf, [screen.get_width() / 2 - complete_surf.get_width() / 2, screen.get_height() / 2 - complete_surf.get_height() / 2])
            pygame.display.flip()
            time.sleep(2.5)
            running = False
# - Close the window -
pygame.quit()
