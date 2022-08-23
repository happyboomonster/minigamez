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

#get a screen setup
screen = pygame.display.set_mode([400,400], pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("Bad Tetris")

#get ourself a font
pygame.font.init()
oxygene1 = pygame.font.Font("OXYGENE1.TTF",30)

oldpiece = [] #the "maps" for my piece which is currently falling onscreen
newpiece = [] #the map for my next piece

piecepos = [0,0] #the position of the piece I'm laying

#constants
TILECAP = 15 #how many tiles can be in one block?
TILESIZE = 5 #how large in XY can this tile be?

def blockgenerate(): #block generator function (warning, very loosely writen and chaos will ensue when using)
    tmppiece = [[0,0]]
    numtiles = random.randint(1,TILECAP)
    count = 0
    while (count != numtiles):
        x = random.randint(0,TILESIZE)
        y = random.randint(0,TILESIZE)
        tmppiece.append([x * 10,y * 10])
        count += 1
    return tmppiece

def drawpiece(piece,pos): #draws a tetris piece
    for pixels in range(0,len(piece)):
        pygame.draw.rect(screen,[255,0,0],[piece[pixels][0] + pos[0],piece[pixels][1] + pos[1],10,10],2)

def movepiece(piece,pos): #shifts a piece over by an offset
    for pixels in range(0,len(piece)):
        piece[0] += pos[0]
        piece[1] += pos[1]
    return piece

def flippiece(piece,horiz,vert):
    if(horiz):
        for pixels in range(0,len(piece)):
            piece[pixels][0] = (TILESIZE * 10) - piece[pixels][0]
    if(vert):
        for pixels in range(0,len(piece)):
            piece[pixels][1] = (TILESIZE * 10) - piece[pixels][1]
    return piece

rotatebookmark = 0 #needed for rotation
def rotatepiece(piece): #rotates a piece to the right
    global rotatebookmark
    if(rotatebookmark == 0):
        piece = flippiece(piece,False,True)
        rotatebookmark = 1
    else:
        rotatebookmark = 0
        piece = flippiece(piece,True,False)
    return piece

def piececollision(pieceA,pieceApos,pieceB,pieceBpos): #returns true if there's collision between pieces
    for pieceAiter in range(0,len(pieceA)):
        for pieceBiter in range(0,len(pieceB)):
            if(pieceA[pieceAiter][0] + pieceApos[0] == pieceB[pieceBiter][0] + pieceBpos[0]):
                if(pieceA[pieceAiter][1] + pieceApos[1] == pieceB[pieceBiter][1] + pieceBpos[1]):
                    return True
    return False

oldpiece = blockgenerate() #make some blocks in our block caches
newpiece = blockgenerate()

#make arena edges for pieces to fall/hit against
ground = []
for makeground in range(0,20):
    ground.append([makeground * 10,400])

edges = [] #make arena edges so we can't move blocks offscreen
for makeground in range(0,40):
    edges.append([-10,makeground * 10])
for makeground in range(0,40):
    edges.append([200,makeground * 10])

points = 500 #quick point counter - you lose points the longer it takes you to die!

placedblocks = [] #all the blocks we've already placed...

#create a clock for framecapping
clock = pygame.time.Clock()

#we're not dead yet, right?
alive = True

while alive:
    #decrement our points counter the longer you stay alive
    points -= 2
    
    #draw a green rectangle around the playing space
    pygame.draw.rect(screen,[0,255,0],[0,0,200,400],2)

    #draw our current piece
    drawpiece(oldpiece,piecepos)

    #draw our next piece
    drawpiece(newpiece,[250,50])

    #draw all the "placedblocks"
    for drawblocks in range(0,len(placedblocks)):
        drawpiece(placedblocks[drawblocks][0],placedblocks[drawblocks][1])

    #draw our score "points" variable
    screen.blit( oxygene1.render("SCORE: " + str(points),0,[150,150,150]) , [210,250] )

    #move our piece downward and check for ground/other blocks
    piecepos[1] += 10
    if(piececollision(oldpiece,piecepos,ground,[0,0])):
        points += 10
        piecepos[1] -= 10
        placedblocks.append([oldpiece,piecepos])
        piecepos = [100,0]
        oldpiece = newpiece[:]
        newpiece = blockgenerate()

    #check all the placed blocks now...
    for checkblocks in range(0,len(placedblocks)):
        if(piececollision(oldpiece,piecepos,placedblocks[checkblocks][0],placedblocks[checkblocks][1])):
            points += 10
            piecepos[1] -= 10
            placedblocks.append([oldpiece,piecepos])
            piecepos = [100,0]
            oldpiece = newpiece[:]
            newpiece = blockgenerate()
            for checkblocks in range(0,len(placedblocks)): #check if we're touching blocks from the moment we spawn a new block
                if(piececollision(oldpiece,piecepos,placedblocks[checkblocks][0],placedblocks[checkblocks][1])):
                    alive = False
            break

    #did we make a row?
    flag = 0
    mirow = 0
    fullcolumns = []
    for column in range(0,40):
        mirow = 0
        for row in range(0,20):
            flag = 0
            for findblock in range(0,len(placedblocks)): #placedblocks[findblock][0][pixel#][xy] #placedblocks[findblock][1][posxy]
                for findpixel in range(0,len(placedblocks[findblock][0])): #iterate through all pixels in a block
                    if((placedblocks[findblock][0][findpixel][0] + placedblocks[findblock][1][0]) == (row * 10)):
                        if((placedblocks[findblock][0][findpixel][1] + placedblocks[findblock][1][1]) == (column * 10)):
                            flag = 1
            if(flag == 1): #we did find something which fufilled the row/column requirements!
                mirow += 1
            else: #if not, well...NEXT.
                break
        if(mirow == 20): #we got a FULL ROW!!!!!!!!
            points += 150
            #now we have to delete the row so we don't keep giving that person points for a row which was there 10 minutes ago...
            fullcolumns.append(column) #we'll use this in a minute to delete all the shapes that make up that row...

    #now we delete any shape flaged within the "fullcolumns" list
    for columns in fullcolumns:
        for findblock in range(0,len(placedblocks)): #placedblocks[findblock][0][pixel#][xy] #placedblocks[findblock][1][posxy]
            for findpixel in range(0,len(placedblocks[findblock][0])):
                if((placedblocks[findblock][0][findpixel][1] + placedblocks[findblock][1][1]) == (columns * 10)):
                    placedblocks[findblock][0][findpixel][1] = -20 - placedblocks[findblock][1][1] #teleport all full-row blocks to -20 Y
                placedblocks[findblock][0][findpixel][1] += 10 #move all blocks down 10 to fill the empty space created
    fullcolumns = []
                
    for event in pygame.event.get():
        if(event.type == pygame.QUIT):
            alive = False
        elif(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_DOWN): #fast move the piece down
                piecepos[1] += 10
                if(piececollision(oldpiece,piecepos,ground,[0,0])):
                    points += 10
                    piecepos[1] -= 10
                    placedblocks.append([oldpiece,piecepos])
                    piecepos = [100,0]
                    oldpiece = newpiece[:]
                    newpiece = blockgenerate()
                    for checkblocks in range(0,len(placedblocks)): #check if we're touching blocks from the moment we spawn a new block
                        if(piececollision(oldpiece,piecepos,placedblocks[checkblocks][0],placedblocks[checkblocks][1])):
                            alive = False
            elif(event.key == pygame.K_UP): #rotate the piece
                oldpiece = rotatepiece(oldpiece)
            elif(event.key == pygame.K_LEFT): #move piece to left
                piecepos[0] -= 10
                if(piececollision(oldpiece,piecepos,edges,[0,0])):
                    piecepos[0] += 10
            elif(event.key == pygame.K_RIGHT): #move piece to right
                piecepos[0] += 10
                if(piececollision(oldpiece,piecepos,edges,[0,0])):
                    piecepos[0] -= 10
    
    pygame.display.flip() #my two sacred lines of code...
    screen.fill([0,0,0])

    #FPS throttle + gamespeed sanity cap
    clock.tick(5)
pygame.quit()

print("Score: " + str(points)) #print our our final score
