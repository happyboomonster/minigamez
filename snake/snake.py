##Copyright (C) 2022 Lincoln V.
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
import random

#set up pygame
screen = pygame.display.set_mode([500,500], pygame.RESIZABLE | pygame.SCALED)
clock = pygame.time.Clock()
pygame.display.set_caption("Snake")

#define our snake's attributes
snake = [[0,0],[0,1],[0,2],[0,3]] #define our snake's positions
snakedirection = "right" #define our direction
alive = True

#create the fruit/food/whatever which the snake needs to eat
foodpos = [random.randint(0,49),random.randint(0,49)]

#miscellanous variable I need
insert = False

while alive:
    #handle moving the snake around
    if(insert == False):
        snake.pop(0)
    insert = False
    if(snakedirection == "right"):
        snake.append([snake[len(snake) - 1][0] + 10,snake[len(snake) - 1][1]])
    elif(snakedirection == "left"):
        snake.append([snake[len(snake) - 1][0] - 10,snake[len(snake) - 1][1]])
    elif(snakedirection == "down"):
        snake.append([snake[len(snake) - 1][0],snake[len(snake) - 1][1] + 10])
    elif(snakedirection == "up"):
        snake.append([snake[len(snake) - 1][0],snake[len(snake) - 1][1] - 10])

    #are we still alive or did we slam a wall?
    if(snake[len(snake) - 1][0] > 490 or snake[len(snake) - 1][0] < 0):
        alive = False
    elif(snake[len(snake) - 1][1] > 490 or snake[len(snake) - 1][1] < 0):
        alive = False

    #did we eat?
    if(int(snake[len(snake) - 1][0] / 10) == int(foodpos[0])):
        if(int(snake[len(snake) - 1][1] / 10) == int(foodpos[1])):
            foodpos = [random.randint(0,49),random.randint(0,49)]
            insert = True

    #did we hit ourselves?
    if(len(snake) > 1):
        front_square = snake[len(snake) - 1]
        for x in range(0,len(snake)):
            if(x == len(snake) - 1):
                continue
            if(front_square[0] < snake[x][0] + 10):
                if(front_square[0] + 10 > snake[x][0]): #we're colliding with ourselves on the X axis?
                    if(front_square[1] < snake[x][1] + 10):
                        if(front_square[1] + 10 > snake[x][1]): #we're colliding with ourselves on the Y axis?
                            alive = False #we cut ourselves! We died.

    #draw a rectangle around our playing border
    pygame.draw.rect(screen,[255,0,0],[0,0,500,500],5)

    #draw the snake onscreen
    for x in range(0,len(snake)):
        pygame.draw.rect(screen,[170,50,50],[snake[x][0],snake[x][1],10,10],0)

    #draw the snake's food
    pygame.draw.rect(screen,[0,255,0],[foodpos[0] * 10,foodpos[1] * 10,10,10],0)

    #input loop
    for event in pygame.event.get():
        if(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_DOWN): #move our direction down
                snakedirection = "down"
            elif(event.key == pygame.K_UP): #move our direction up
                snakedirection = "up"
            elif(event.key == pygame.K_RIGHT): #move our direction right
                snakedirection = "right"
            elif(event.key == pygame.K_LEFT): #move our direction left
                snakedirection = "left"

    #flip the screen and framecap + screen clear
    pygame.display.flip()
    screen.fill([0,0,0])
    clock.tick(15)

print(len(snake))
pygame.quit()
