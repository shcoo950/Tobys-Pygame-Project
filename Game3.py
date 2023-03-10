from __future__ import annotations
from importlib.resources import path
#from concurrent.futures import ThreadPoolExecutor

from lib2to3.pygram import python_grammar
from operator import setitem, truediv
from socket import fromshare
from turtle import Vec2D, clear

from typing import List, Tuple
from pathlib import Path

#import numpy as np
#from numba import jit, njit, vectorize
import math
import os
from xmlrpc.client import Boolean
import pygame as pg
from pygame.locals import *
from pytmx.util_pygame import load_pygame

import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

from PIL import Image
import random


MAINDIR = os.path.split(os.path.abspath(__file__))[0]
DATADIR = os.path.join(MAINDIR, "Data")
MAINFONT = os.path.join(DATADIR, "rainyhearts.ttf")



def initScreen(width, height):

    screen = pg.display.set_mode((width, height), pg.RESIZABLE)
    screen.blit
    return screen

def loadImage(name, colorKey=None, scale=1):

    fullName = os.path.join(DATADIR, name)
    image = pg.image.load(fullName)
    image = image.convert()

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    if colorKey is not None:
        if colorKey == -1:
            colorKey = image.get_at((0, 0))
        image.set_colorkey(colorKey, pg.RLEACCEL)
    return image.convert_alpha()

def gifToImages(name, numberOfFrames):

    filename = os.path.join(DATADIR, name + ".gif")
    with Image.open(filename) as im:
        for i in range(numberOfFrames):
            im.seek(im.n_frames // numberOfFrames * i )
            im.save(os.path.join(DATADIR, name +'-{}.png'.format(i)))

def getListOfImages(name, numberOfImages) -> List[pg.image()]:

    gifToImages(name, numberOfImages)
    files = os.listdir(DATADIR)
    listOfImages = []
    for file in files:
        if file.rsplit("-")[0] == name:
            listOfImages.append(loadImage(file, -1))

    return listOfImages

def properListInsert(list, element, index, blankValue):

    leftIndex = -9000
    rightIndex = 9000

    for i in range(index, 0, -1):
        if list[i] == blankValue:
            leftIndex = i
            break
    for i in range(index, len(list)):
        if list[i] == blankValue:
            rightIndex = i
            break
    
    if index - leftIndex <= rightIndex - index:
        subList = list[leftIndex + 1:index + 1]
        for i,value in enumerate(subList):
            list[leftIndex + i] = value
    else:
        subList = list[index:rightIndex]
        for i,value in enumerate(subList):
            list[index + i +1] = value   

    list[index] = element
    return list

def checkLineRectCollision(line:Tuple[(int,int), (int,int)], rect:pg.Rect) -> Boolean:

    for extrem1, extrem2 in [(rect.topleft, rect.bottomleft), (rect.bottomleft, rect.bottomright), (rect.bottomright, rect.topright), (rect.topright, rect.topleft)]:
        if line[0] != extrem1 and line[0] != extrem2:
            deno = (line[0][0] - line[1][0]) * (extrem1[1] - extrem2[1]) - (line[0][1] - line[1][1]) * (extrem1[0] - extrem2[0])
            if deno != 0:
                param1 = ((extrem2[0] - line[0][0]) * (line[0][1] - line[1][1]) - (extrem2[1] - line[0][1]) * (line[0][0] - line[1][0]))/deno
                param2 = ((extrem2[0] - line[0][0]) * (extrem2[1] - extrem1[1]) - (extrem2[1] - line[0][1]) * (extrem2[0] - extrem1[0]))/deno

                if 0 <= param1 <= 1 and 0 <= param2 <= 1:
                    return True   
        else:
            return False
    return False

def AStarAlgorithm(adjacencyList, startNode, endNode) -> List:

    visitedList = set([startNode])
    fullyVisitedList = set([])

    g = {}
    g[startNode] = 0

    parents = {}
    parents[startNode] = startNode

    while len(visitedList) > 0:
        n = None

        for v in visitedList:
            if n == None or g[v] < g[n]:
                n = v

        if n == None:
            print("Path does not exist")
            return None

        if n == endNode:
            path = []

            while parents[n] != n:
                path.append(n)
                n = parents[n]

            path.append(startNode)
            path.reverse()

            return path
        
        for (m, weight) in adjacencyList[n]:
            if m not in visitedList and m not in fullyVisitedList:
                visitedList.add(m)
                parents[m] = n
                g[m] = g[n] + weight

            else:
                if g[m] > g[n] + weight:
                    g[m] = g[n] + weight
                    parents[m] = n

                    if m in fullyVisitedList:
                        fullyVisitedList.remove(m)
                        visitedList.add(m)

        visitedList.remove(n)
        fullyVisitedList.add(n)



def avoidSprites(targetSprite, spriteGroup):

    for sprite in spriteGroup:
        if targetSprite != sprite:

            distance = targetSprite.pos - sprite.pos
            distance = pg.math.Vector2(distance)

            if distance.magnitude < 50 and distance.magnitude > 0:
                targetSprite.angle += distance.normalize()



class Player(pg.sprite.Sprite):

    def __init__(self):

        super().__init__()
        pg.sprite.Sprite.__init__(self, self.containers)

        self.downSprites = getListOfImages("MumpsDown", 8)
        self.upSprites = getListOfImages("MumpsUp", 8)
        self.rightSprites = getListOfImages("MumpsRight", 8)
        self.leftSprites = getListOfImages("MumpsLeft", 8)

        self.image = self.downSprites[0]
        self.rect = self.image.get_rect()

        self.velocity = [0, 0]
        self._position = [0.00, 0.00]
        self._oldPosition = self._position
        self.feet = pg.Rect(0, 0, self.rect.width * 0.5, 8)
        self.speed = 200

        self.facing = "down"
        self.currentSprite = 0
        self.sumdt = 0
    
    @property
    def position(self):
        return list(self._position)
        
    @position.setter
    def position(self, value: List[float]):
        self._position = list(value)

    def update(self, dt: float):

        self._oldPosition = self._position[:]
        self._position[0] += self.velocity[0] * dt
        self._position[1] += self.velocity[1] * dt
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom

        if self.velocity[0] > 0:
            self.facing = "right"
        if self.velocity[0] < 0:
            self.facing = "left"
        if self.velocity[1] > 0:
            self.facing = "down"
        if self.velocity[1] < 0:
            self.facing = "up"

        if self.velocity[0] != 0 or self.velocity[1] != 0:
            self._animate(dt)

        if self.velocity[0] == 0 and self.velocity[1] == 0:
            self.currentSprite = 0
            if self.facing == "down":
                self.image = self.downSprites[self.currentSprite]
            if self.facing == "up":
                self.image = self.upSprites[self.currentSprite]
            if self.facing == "right":
                self.image = self.rightSprites[self.currentSprite]
            if self.facing == "left":
                self.image = self.leftSprites[self.currentSprite]

    def moveBack(self, direction):

        if direction == "x":
            self._position[0] = self._oldPosition[0]
            self.rect.topleft = self._position
            self.feet.midbottom = self.rect.midbottom
        if direction == "y":
            self._position[1] = self._oldPosition[1]
            self.rect.topleft = self._position
            self.feet.midbottom = self.rect.midbottom 

    def _animate(self, dt):

        if self.sumdt >= 0.1:
            self.currentSprite += 1
            if self.facing == "down":                
                if self.currentSprite >= len(self.downSprites):
                    self.currentSprite = 0
                self.image = self.downSprites[self.currentSprite]
            if self.facing == "up":
                if self.currentSprite >= len(self.upSprites):
                    self.currentSprite = 0
                self.image = self.upSprites[self.currentSprite]
            if self.facing == "right":
                if self.currentSprite >= len(self.rightSprites):
                    self.currentSprite = 0
                self.image = self.rightSprites[self.currentSprite]
            if self.facing == "left":
                if self.currentSprite >= len(self.leftSprites):
                    self.currentSprite = 0
                self.image = self.leftSprites[self.currentSprite]
            self.sumdt = 0

        self.sumdt += dt

class Map():

    def __init__(self, mapname):

        filepath = os.path.join(DATADIR, mapname + ".tmx")
        self.tmxData = load_pygame(filepath)
        self.walls, self.thingamabobs, self.NPCs, self.otherObjects = self._getObjects()
        txtfile = os.path.join(DATADIR, mapname + ".txt")

        self.width = self.tmxData.width * 16
        self.height = self.tmxData.height * 16
        
        try:
            txtfile = open(txtfile, "r")
            self.containedSprites = []
            self.startPos = [0,0]
            self.connected = ["L","U","R","D"]
            self.pathResolution = 320

            for line in txtfile:
                if line.split(":")[0] == "StartPos":
                    pos = line.split(":")[1].strip("\n")
                    if pos != "":
                        self.startPos = (int(pos.split(",")[0]), int(pos.split(",")[1]))
                elif line.split(":")[0] == "Sprites":
                    sprites = line.split(":")[1].strip("\n")
                    if sprites != "":
                        self.containedSprites = sprites.split(",")
                elif line.split(":")[0] == "PathResolution":
                    self.pathResolution = int(line.split(":")[1].strip("\n"))
                else:
                    pos = line.split(":")[0]
                    map = line.split(":")[1].strip("\n")
                    if map != "":
                        if pos == "Left":
                            self.connected[0] = map
                        elif pos == "Up":
                            self.connected[1] = map
                        elif pos == "Right":
                            self.connected[2] = map
                        elif pos == "Down":
                            self.connected[3] = map
            txtfile.close()
        except:
            pass
        self.graph = self.createMapGraph()
            
    def _getObjects(self):

        walls = []
        thingamabobs = []
        NPCs = []
        otherObjects = []
        for obj in self.tmxData.objects:
            if obj.type == "Collision":
                walls.append(pg.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == "Thingamabob":
                thingamabobs.append([obj.name,(obj.x, obj.y, obj.width, obj.height)])
            elif obj.type == "NPC":
                NPCs.append([obj.name, pg.Rect(obj.x, obj.y, obj.width, obj.height)])
            else:
                otherObjects.append([obj, pg.Rect(obj.x, obj.y, obj.width, obj.height)])

        return walls, thingamabobs, NPCs, otherObjects

    def createMapGraph(self):

        self.createVerticesGrid()
        adjacencyDict = {}
        for vertex in self.mapVertices:
            path = self.checkForPaths(vertex)
            if path != []:
                adjacencyDict[vertex] = path

        return adjacencyDict

    def createVerticesGrid(self):

        self.mapVertices = []
        for x in range(0,self.width,self.pathResolution):
            for y in range(0,self.height,self.pathResolution):
                vertex = (x,y)
                collided = False
                for wall in self.walls:
                    if wall.collidepoint(vertex):
                        collided = True
                if not collided:
                    self.mapVertices.append(vertex)

    def checkForPaths(self, node):

        neighbours = [None,None,None,None]
        paths = []
        for vertex in self.mapVertices:
            if vertex != node:
                add = True
                if vertex[0] == node[0]:
                    if vertex[1] == node[1] - self.pathResolution:
                        neighbours[1] = vertex
                        add = True
                    elif vertex[1] == node[1] + self.pathResolution:
                        neighbours[3] = vertex
                        add = True
                    else:
                        add = False
                elif vertex[1] == node[1]:
                    if vertex[0] == node[0] - self.pathResolution:
                        neighbours[0] = vertex
                        add = True
                    elif vertex[0] == node[0] + self.pathResolution:
                        neighbours[2] = vertex
                        add = True
                    else:
                        add = False
                if add:
                    collided = False
                    line  = (node, vertex)
                    for wall in self.walls:
                        if checkLineRectCollision(line, wall):
                            collided = True
                    if not collided:
                        vector = pg.Vector2()
                        vector.x = node[0] - vertex[0]
                        vector.y = node[1] - vertex[1]
                        paths.append((vertex, int(vector.magnitude())))
        return paths

class UserInterface():

    def __init__(self, screen):

        self.screenResize(screen)

        self.oldItem = ""
        self.invScreenRect = ""
        self.hotScreenRect = ""
        self.hunScreenRect = ""

        self.inventoryBgnd = loadImage("InventoryBackground.png")

        self.descShow = False
        self.itemDesc = ""
        self.itemName = ""

        self.drawInventory([])
        self.drawHotbar()

    def drawHunger(self, hunger):
        pass

    def drawHotbar(self, hotbar=[]):
        
        if self.hotScreenRect == self.screen.get_rect():
            self.screen.blit(self.hotbarSurf, self.hotTopLeft) 

        else:
            self.hotScreenRect = self.screen.get_rect()
            
            rectSize = (self.itemWidth * 16, self.itemWidth * 1.5)
            self.hotTopLeft = (int(self.screen.get_width() * 0.1), int(self.screen.get_height() * 0.85))

            self.hotItemStartPos = (0.2 * self.itemWidth, 0.2 * rectSize[1])
            self.realItemStartPos = [self.hotTopLeft[0] + self.hotItemStartPos[0], self.hotTopLeft[1] + self.hotItemStartPos[1]]

            self.hotbarSurf = pg.Surface(rectSize).convert_alpha()

            self.hotbarSurf.fill("#DBD9B7")

            realItemPos = [0,0]
            itemPos = [0,0]
            realItemPos[1] = self.realItemStartPos[1]
            itemPos[1] = self.hotItemStartPos[1]

            for i, item in enumerate(hotbar):
                if item != "":
                    quantity = self.mainFont.render(str(item.quantity), 1, "oldlace")

                    itemPos[0] = self.hotItemStartPos[0] + i * self.itemWidth * 1.2
                    realItemPos[0] = self.realItemStartPos[0] + i * self.itemWidth * 1.2
                    item.image = pg.transform.scale(item.image, (self.itemWidth, self.itemWidth))
  
                    item.pos = realItemPos
                    
                    self.hotbarSurf.blit(item.image, itemPos)
                    self.hotbarSurf.blit(quantity, (itemPos[0], itemPos[1] + self.itemWidth * 0.8))
                else:
                    itemPos[0] = self.hotItemStartPos[0] + i * self.itemWidth
                    realItemPos[0] = self.realItemStartPos[0] + i * self.itemWidth

            self.screen.blit(self.hotbarSurf, self.hotTopLeft)
        
    def drawInventory(self, inventory):

        if self.invScreenRect == self.screen.get_rect():
                           
            self.screen.blit(self.inventorySurf, self.invTopLeft)

            for item in inventory:
                    if item == self.descShow:
                        self.showItemDesc(item)
                        self.screen.blit(self.titleText, item.rect.topright)   
                        self.screen.blit(self.descText, item.rect.midright)
        else:
            self.invScreenRect = self.screen.get_rect()
            
            size = (int(self.screen.get_width() * 0.8), int(self.screen.get_height() * 0.7))
            self.invTopLeft = (int(self.screen.get_width() * 0.1), int(self.screen.get_height() * 0.1))

            self.realInvItemStartPos = (int(self.screen.get_width() * 0.52), int(self.screen.get_height() * 0.15))
            self.invItemStartPos = (int(self.screen.get_width() * 0.42), int(self.screen.get_height() * 0.05))
            
            self.inventorySurf = pg.transform.scale(self.inventoryBgnd, size) 
            self.screen.blit(self.inventorySurf, self.invTopLeft)

            itemPos = [0,0]
            realItemPos = [0,0]

            for row in range(1):
                itemPos[1] = self.invItemStartPos[1] + row * self.itemWidth * 1.2
                realItemPos[1] = self.realInvItemStartPos[1] + row * self.itemWidth * 1.2

                for column, item in zip(range(6), inventory):

                    if item == None:
                        break

                    quantity = self.mainFont.render(str(item.quantity), 1, "oldlace")

                    itemPos[0] = self.invItemStartPos[0] + column * self.itemWidth * 1.2
                    realItemPos[0] = self.realInvItemStartPos[0] + column * self.itemWidth * 1.2

                    item.image = pg.transform.scale(item.image, (self.itemWidth, self.itemWidth))
                    item.pos = realItemPos

                    self.inventorySurf.blit(item.image, itemPos)
                    self.inventorySurf.blit(quantity, (itemPos[0], itemPos[1] + self.itemWidth * 0.8))

    def drawGeneralUI(self, UI, UIImage = None, items = []):

        if UI[0] == 0:
            self.screen.blit(self.generalUI, self.generalUITopLeft)

        elif UI[0] == 1:
            UI[0] = 0
            self.generalUITopLeft = (int(self.screen.get_width() * UI[1][0]), int(self.screen.get_height() * UI[1][1]))
            generalUISize = (int(self.screen.get_width() * UI[1][2]), int(self.screen.get_height() * UI[1][3]))

            if UI[2] != None:
                self.generalItemRectTopLeft = (int(generalUISize[0] * UI[2][0]), int(generalUISize[1] * UI[2][1]))
                self.generalItemRectSize = (int(generalUISize[0] * UI[2][2]), int(generalUISize[1] * UI[2][3]))
                self.generalMaxItems = (int(self.generalItemRectSize[0] / (self.itemWidth * 1.2)), int(self.generalItemRectSize[1] / (self.itemWidth * 1.2)))

            if UIImage != None:
                self.generalUI = UIImage
            self.generalUI = pg.transform.scale(self.generalUI, generalUISize)
            
            if len(UI) >= 4:
                for textRects in UI[3:]:

                    text = textRects[0].split(",")
                    textRectTopLeft = (int(generalUISize[0] * textRects[1]), int(generalUISize * textRects[2]))
                    textRectSize = (int(generalUISize[0] * textRects[3]), int(generalUISize * textRects[4]))
                    textSurface = self.drawText(text[0], text[1], text[2], textRectSize[0], textRectSize[1])

                    self.generalUI.blit(textSurface, textRectTopLeft)

            if items !=[]:       
                if items[0] == 1:
                    itemPos = [0,0]
                    for row in range(self.generalMaxItems[1]):
                        itemPos[1] = self.generalItemRectTopLeft[1] + row * self.itemWidth * 1.2
                        for column, item in zip(range(self.generalMaxItems[0], items)):
                            itemPos[0] = self.generalItemRectTopLeft[0] + column * self.itemWidth * 1.2
                            if item == None:
                                break 
                            else:
                                self.generalUI.blit(item.image, itemPos)
            
            self.screen.blit(self.generalUI, self.generalUITopLeft)

    def screenResize(self, screen):
        self.screen = screen

        self.itemWidth = int(self.screen.get_width() * 0.05)

        fontSize = int(self.itemWidth / 2)
        self.mainFont = pg.font.SysFont(MAINFONT, fontSize)
        self.titleFont = pg.font.SysFont(MAINFONT, int(fontSize * 1.2), True)
            
    def collide(self, item):
        self.descShow = item

    def showItemDesc(self, item):

        if item != self.oldItem:
            self.oldItem = item

            rectSize = (self.itemWidth * 3, self.itemWidth)
            textRect = pg.Rect(item.rect.topright,rectSize)

            pg.draw.rect(self.screen, item.desc[1], textRect)
            self.titleText = self.titleFont.render(type(item).__name__, 1, item.desc[2])
            self.descText = self.drawText(item.desc[3], item.desc[2], self.mainFont, rectSize[0], rectSize[1], item.desc[1], True, item)

    def drawText(self, text, textColor,font, rectWidth = None, rectHeight = None, bckColor = None, aa = True, item = ""):
        
        lineSpacing = -2
        imageList = []

        spaceWidth, fontHeight = font.size(" ")[0], font.size("Tg")[1]

        listOfWords = text.strip('\n').split(" ")

        align = listOfWords[0][1]
        listOfWords.remove(listOfWords[0])

        for i, word in enumerate(listOfWords): 
            if word == "{Value}":
                try:
                    word = "£" + item.value
                    imageList.append(font.render(word, aa, textColor))
                except:
                    print("No item class was input")
            elif word[0] != "<":
                imageList.append(font.render(word, aa, textColor))

        maxLen = rectWidth
        lineLenList = [0]
        lineList = [[]]

        currentAlign = align
        lineList[-1].append(int(currentAlign))
        wordIndex = 0
        currentLine = True
        for word in listOfWords:
            
            if word[0] == "<":
                    currentAlign = word[1]
                    currentLine = False
            else:
                width = imageList[wordIndex].get_width()
                lineLen = lineLenList[-1] + (len(lineList[-1]) -1) * spaceWidth + width

                if (len(lineList[-1]) == 1 or lineLen <= maxLen) and currentLine:
                    currentLine = True
                    lineLenList[-1] += width
                    lineList[-1].append(imageList[wordIndex])
                else:
                    currentLine = True
                    lineLenList.append(width)
                    lineList.append([int(currentAlign)])
                    lineList[-1].append(imageList[wordIndex])

                wordIndex += 1

        if rectHeight != None and rectWidth != None:
            textSurface = pg.Surface((rectWidth, rectHeight))
        elif rectWidth != None and rectHeight == None:
            textSurface = pg.Surface((rectWidth, len(lineList) * fontHeight))
        elif rectWidth == None:
            textSurface = pg.Surface((int((len(text) / 2.2) * fontHeight), fontHeight))
        textSurface.convert_alpha()
        if bckColor == None:
            bckColor = pg.Color(0,0,0, 0)
        textSurface.fill(bckColor)

        lineBottom = 0
        lastLine = 0


        for lineLen, lineImages in zip(lineLenList, lineList):
            lineSpaceWidth = spaceWidth
            lineLeft = 0
            align = lineImages[0]
            lineImages.remove(align)
            if align == 1:
                lineLeft += + rectWidth -lineLen - spaceWidth * (len(lineImages) - 1)
            elif align == 2:
                lineLeft += (rectWidth - lineLen - spaceWidth * (len(lineImages)-1)) // 2
            elif align == 3:
                lineSpaceWidth = (rectWidth - lineLen) // (len(lineImages)-1)

            if lineBottom + fontHeight > rectHeight:
                break
            lastLine += 1

            for i, image in enumerate(lineImages):
                x,y = lineLeft + i * lineSpaceWidth, lineBottom
                textSurface.blit(image, (round(x), y))
                lineLeft += image.get_width()
            lineBottom += fontHeight + lineSpacing

        if lastLine < len(lineList):
            drawWords = sum([len(lineList[i]) for i in range(lastLine)])
            remainingText = ""
            for text in listOfWords[drawWords:]: remainingText += text + " "

        return textSurface

    def takeItem(self, item):

        self.holdItem = item
        self.holdItem.image.set_alpha(128)

    def dragItem(self, mousePos):
        self.screen.blit(self.holdItem.image, mousePos)

    def dropItem(self, mousePos, showingInventory):

        hotbarRect = self.hotbarSurf.get_rect()
        hotbarRect.topleft = self.hotTopLeft
        if hotbarRect.collidepoint(mousePos):
            index = mousePos[0] - self.hotItemStartPos[0]
            index = round(index / (self.itemWidth  * 1.2))
            return (index - 2)

        if showingInventory:
            if self.inventorySurf.get_rect().collidepoint(mousePos):
                return -1
                
class Time():

    def __init__(self, time:List[str]):
        self.currentTime = time

    def update(self):

        if self.currentTime[1] < 60:
            self.currentTime[1] = self.currentTime[1] + 10
        else:
            if self.currentTime[0] < 23:
                self.currentTime[0] =  self.currentTime[0] + 1
                self.currentTime[1] = "00"
            else:
                self.currentTime[0] = "00"
                self.currentTime[1] = "00"

class CutScene():

    def __init__(self):
        pass

    def playCutScene(self, cutscene):

        filepath = os.path.join(DATADIR, cutscene + ".txt")
        file = open(filepath)
        gifs = []
        for line in file:
            gifs.append(line)

        return gifs

class Dialogue():

    def __init__(self, screen):
        self.screen = screen

    def drawDialogueBox(self):

        rectWidth = int(self.screen.get_width * 0.2) 
        rectHeight = int(self.screen.get_height * 0.125)
        xpos = int(self.screen.get_width * 0.1)
        ypos = self.screen.get_height - rectHeight
        self.rect = pg.Rect(xpos, ypos, rectWidth, rectHeight)

        return self.rect

    def __init__(self):
        super().__init__()

class BaseNPC(pg.sprite.Sprite):

    def __init__(self, xpos, ypos):

        pg.sprite.Sprite.__init__(self, self.containers)

        self._loadImages()

        self.image = self.downSprites[0]
        self.rect = self.image.get_rect()

        self.pos = [xpos, ypos]
        self.rect.topleft = self.pos
        self.feet = pg.Rect(xpos,ypos, self.rect.width, 8)
        self.feetOffset = 40

        self.oldPosition = self.pos
        self.velocity = [0,0]
        self.speed = 100

        self.currentNode = (0,0)
        self.reachedNode = True
        self.currentPath = []
        self.visitedNode = 0
        self.finishedPath = True
        
        self.facing = "down"
        self.currentSpirte = 0
        self.sumdt = [0,0]

        self.suspicion = 20
        self.state = "neutral"
        self.targetNode = []

    def update(self, dt):

        if self.finishedPath and self.reachedNode:
            self.state = ""

        if self.state == "followingPath":
            self.followPath(dt=dt)
        else:
            if self.suspicion >= 80:
                #Tase.suspicion
                pass
            elif self.suspicion >= 70:
                self.state = "detain"
            elif self.suspicion >= 50:
                if self.sumdt[1] >= 2:
                    self.state = "follow"
                    self.sumdt[1] = 0
                else:
                        self.sumdt[1] += dt  
            elif self.suspicion >= 30:
                self.state = "suspicious"
            elif self.suspicion == 20:
                if self.sumdt[1] >= 5:
                    self.state = "wandering"
                    self.sumdt[1] = 0
                else:
                        self.sumdt[1] += dt

                   
        if self.velocity[0] == 0 and self.velocity[1] == 0:
            self.currentSprite = 0
            if self.facing == "down":
                self.image = self.downSprites[self.currentSprite]
            if self.facing == "up":
                self.image = self.upSprites[self.currentSprite]
            if self.facing == "right":
                self.image = self.rightSprites[self.currentSprite]
            if self.facing == "left":
                self.image = self.leftSprites[self.currentSprite]

        self.sumdt[0] += dt

    def lookAtPos(self, pos) -> pg.Vector2:

        directionVector = [0,0]
        directionVector[0] = pos[0] - self.pos[0]
        directionVector[1] = pos[1] - self.pos[1]

        directionVector = pg.math.Vector2(directionVector)
        self.angle = directionVector.angle_to(Vec2D(1,0))
        if self.angle < 0:
            self.angle = 360 + self.angle
        if self.angle < 45 or self.angle >= 315:
            self.facing = "right"
        if self.angle >= 225 and self.angle < 315:
            self.facing = "down"
        if self.angle >= 135 and self.angle < 225:
            self.facing = "left"
        if self.angle >= 45 and self.angle < 135:
            self.facing = "up"

        self.angle = math.radians(self.angle)
        return directionVector

    def _advance(self, dt):

        self.oldPosition = self.pos[:]

        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt
        self.feet.topleft = self.pos
        self.rect.topleft = [self.feet.topleft[0], self.feet.topleft[1] - self.feetOffset]

        if self.velocity[0] != 0 or self.velocity[1] != 0:
            self._animate(dt)

    def moveBack(self, direction):

        if direction == "x":
            self.pos[0] = self.oldPosition[0]
        if direction == "y":
            self.pos[1] = self.oldPosition[1]

        self.rect.topleft = self.pos
        self.feet.midbottom = self.rect.midbottom
    
    def goToPos(self, position:List, dt):

        if position != self.targetNode:
            self.reachedNode = False
            self.targetNode = position
            self.lookAtPos(position)
            self.velocity[0] = self.speed * math.cos(self.angle)
            self.velocity[1] = -self.speed * math.sin(self.angle)

        self._advance(dt)
        if self.feet.collidepoint(position):
            self.velocity = [0,0]
            self.reachedNode = True

    def followPath(self,path=None, dt = 0):

        if path != None:
            self.finishedPath = False
            self.currentNode = 0
            self.currentPath = path
            self.state = "followingPath"
        else:
            if self.reachedNode:
                if self.currentNode < len(self.currentPath) -1:
                    self.currentNode += 1
                    self.reachedNode = False
                else:
                    self.finishedPath = True
            else:
                self.goToPos(self.currentPath[self.currentNode], dt)

    def _animate(self, dt):
    
        if self.sumdt[0] >= 0.1:
            self.currentSprite += 1
            if self.facing == "down":                
                if self.currentSprite >= len(self.downSprites):
                    self.currentSprite = 0
                self.image = self.downSprites[self.currentSprite]
            if self.facing == "up":
                if self.currentSprite >= len(self.upSprites):
                    self.currentSprite = 0
                self.image = self.upSprites[self.currentSprite]
            if self.facing == "right":
                if self.currentSprite >= len(self.rightSprites):
                    self.currentSprite = 0
                self.image = self.rightSprites[self.currentSprite]
            if self.facing == "left":
                if self.currentSprite >= len(self.leftSprites):
                    self.currentSprite = 0
                self.image = self.leftSprites[self.currentSprite]
            self.sumdt[0] = 0
        self.sumdt[0] += dt

    def _loadImages(self):
        pass

class BaseItem(pg.sprite.Sprite):
    
    def __init__(self, quantity):
        
        pg.sprite.Sprite.__init__(self, self.containers)

        self._setItemType()
        self.rect = pg.Rect(0,0,48,48)
        self.quantity = quantity
        self.desc = self._setDescription()
        self.value = self.desc[0]

    def _setItemType(self):
        pass

    def _setDescription(self):

        filepath = os.path.join(DATADIR, "itemDesc.txt")
        file = open(filepath, "r")
        for line in file:
            if line.split(";")[0] == type(self).__name__:
                return line.split(";")[1:]
        file.close()

    def __del__(self):
        pass

    @property
    def pos(self):
        return list(self.pos)
        
    @pos.setter
    def pos(self, value: List[float]):
        self.rect = self.image.get_rect()
        self.rect.topleft = value
        
class BaseThingamabob():
    
    def __init__(self, rect):
        self.rect = pg.Rect(rect)

        self.UIImage = ""
        self.UI = [2]
        self.approachText = ""
        
        self.interactText = ""
        self.setThingamabobType()

    def setThingamabobType(self):
        pass
    
    def loadUI(self):

        self.UIImage = loadImage(type(self).__name__ + "UI.png")
        filePath = os.path.join(DATADIR, type(self).__name__ + "UI.txt")

        try:
            file = open(filePath)
            for lineNumber, line in enumerate(file):
                if lineNumber == 0:
                    UIRect = line.split(",")
                    UIRect  = [float(x) for x in UIRect]
                    self.UI.append(UIRect)
                if lineNumber == 1:
                    itemRect = line.split(",")
                    self.UI.append(itemRect)
                if lineNumber > 1:
                    text = line.split(";")[0]
                    self.UI.append(text)
                    textRect = line.split(";")[1:]
                    self.UI[-1].append(textRect.split(","))
            file.close()
            if len(self.UI) == 2:
                self.UI.append(None)
        except:
            self.UI = []

class Police1(BaseNPC):

    def _loadImages(self):

        rnd = random.randint(0,1)
        if rnd == 1:
            self.downSprites = getListOfImages("Police1FemaleDown", 8)
            self.upSprites = getListOfImages("Police1FemaleUp", 8)
            self.rightSprites = getListOfImages("Police1FemaleRight", 8)
            self.leftSprites = getListOfImages("Police1FemaleLeft", 8)
        else:
            self.downSprites = getListOfImages("Police1MaleDown", 8)
            self.upSprites = getListOfImages("Police1MaleUp", 8)
            self.leftSprites = getListOfImages("Police1MaleLeft", 8)
            self.rightSprites = getListOfImages("Police1MaleRight", 8)

class Wallet(BaseItem):

    def _setItemType(self):
        self.image = loadImage("Wallet.png", -1)

    def updateMoney(self, value):
        self.value = value

class Phone(BaseItem):

    def _setItemType(self):
        self.image = loadImage("Phone.png", -1)

class VendingMachine(BaseThingamabob):

    def setThingamabobType(self):
        self.loadUI()
        pass

class PhoneBox(BaseThingamabob):
    pass

class GarbageCan(BaseThingamabob):
    pass

class Game():

    def __init__(self, screen, saveFile):

        self.screen = screen
        self.saveFilePath = os.path.join(DATADIR, saveFile)
        self.running = False
        self.paused = False
        self.nightOn = False
        self.showGraph = False

        self.interface = UserInterface(self.screen)
        self.fontSize = int(self.screen.get_width() / 30)

        self.cutscene = CutScene()
        self.playingCutScene = False

        self.genericUIShow = False
        self.openInventory = False
        self.hotbarShow = True
        self.holdingItem = False
        self.holdItem = [0,0,0,0]
        self.holdIndex = 0

        self.loadMap()
        self.createGroups()             
        self.loadNPCs()
        self.loadThingamabobs()
        self.loadInventory()
        self.loadMoney()      

    def loadMap(self, mapName = "fromSave"):

        if mapName == "fromSave":
            saveFile = open(self.saveFilePath, "r")
            for line in saveFile:
                if line.split(":")[0] == "Map":
                    self.map = Map(line.split(":")[1].strip("\n"))
                    saveFile.close()
                    break
        else:
            self.map = Map(mapName)
            self.player.position = self.map.startPos

        self.mapLayer = pyscroll.BufferedRenderer(
            data=pyscroll.data.TiledMapData(self.map.tmxData),
            size=self.screen.get_size(),
            clamp_camera=True,
        )

        self.mapLayer.zoom = 3

        if mapName != "fromSave":
            self.all._map_layer = self.mapLayer

    def createGroups(self):

        self.all = PyscrollGroup(map_layer=self.mapLayer, default_layer=0)
        self.npc = pg.sprite.Group()
        self.item = pg.sprite.Group()

        Player.containers = self.all
        BaseNPC.containers = self.all, self.npc
        BaseItem.containers = self.item
        
        self.player = Player()
        saveFile = open(self.saveFilePath, "r")
        for line in saveFile:
            if line.split(":")[0] == "Pos":
                pos = line.split(":")[1].strip("\n")
                self.player.position = (int(pos.split(",")[0]), int(pos.split(",")[1]))
                saveFile.close()
                break

    def loadNPCs(self):

        for object in self.map.NPCs:
            objectName = object[0]
            objectRect = object[1]
            statement = ("{}({}, {})".format(objectName, objectRect.x, objectRect.y))
            eval(statement)       
    
    def loadThingamabobs(self):

        self.thingamabobs = []
        for thingamabob in self.map.thingamabobs:
            statement = "self.thingamabobs.append({}({}))".format(thingamabob[0], thingamabob[1])
            eval(statement)

    def loadInventory(self):

        self.playerInventory = []
        self.playerHotbar = []
        saveFile = open(self.saveFilePath, "r")
        for line in saveFile:
            if line.split(":")[0] == "Inventory":
                items = line.split(":")[1].strip("\n")
                for item in items.split(","):
                        name = item.split(";")[0]
                        quantity = item.split(";")[1]
                        eval("self.playerInventory.append({}({}))".format(name, quantity))
            if line.split(":")[0] == "Hotbar":
                items = line.split(":")[1].strip("\n")
                for item in items.split(","):
                    name = item.split(";")[0]
                    quantity = item.split(";")[1]
                    eval("self.playerHotbar.append({}({}))". format(name, quantity))
                for i in range(13 - len(items.split(","))):
                    self.playerHotbar.append("")
                break
        saveFile.close()
        self.interface.hotScreenRect = ""
        self.interface.invScreenRect = ""

    def loadMoney(self):

        saveFile = open(self.saveFilePath, "r")
        for line in saveFile:
            if line.split(":")[0] == "Money":
                self.walletMoney = line.split(":")[1]
                self.atmMoney = line.split(":")[2]
        saveFile.close()

    def draw(self):

        self.all.center(self.player.rect.center)
        self.all.draw(self.screen)
        if self.showGraph:
            self.drawGraph()
        #pg.draw.aaline(self.screen, "green", (0,0), self.targetNode)
        if self.nightOn:
            self.drawOverlay()
        self.drawInterface()

    def handleInput(self):

        direction = [0,0]
        for event in pg.event.get():
            if event.type == QUIT:
                self.running = False
                break

            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    self.running = False
                    break

                elif event.key == K_r:
                    self.mapLayer.reload()

                elif event.key == K_EQUALS:
                    self.mapLayer.zoom += 0.25

                elif event.key == K_MINUS:
                    value = self.mapLayer.zoom - 0.25
                    if value > 0:
                        self.mapLayer.zoom = value
                
                elif event.key == K_TAB:
                    if not self.openInventory:
                        self.hotbarShow = not self.hotbarShow
                        self.holdingItem = False

                elif event.key == K_e:
                    self.interactKey()

                elif event.key == K_n:
                    self.nightOn = not self.nightOn

                elif event.key == K_p:
                    for sprite in self.npc:
                        print(f"{sprite.angle = }")
                        print(f"{sprite.velocity = }")
                        print(f"{sprite.facing = }")
                        print(f"{sprite.rect.height = }")

                elif event.key == K_o:
                    print(f"{self.map.graph = }")
                
                elif event.key == K_l:
                    self.showGraph = not self.showGraph

            elif event.type == pg.MOUSEMOTION:

                if self.openInventory:
                    self.interactWithInventory(pg.mouse.get_pos())

            elif event.type == pg.MOUSEBUTTONDOWN:

                if not self.holdingItem:
                    self.interactWithInventory(pg.mouse.get_pos(), event.button)
                else:
                    if self.hotbarShow:
                        if event.button == 4:
                            self.holdIndex -= 1
                        elif event.button == 5:
                            self.holdIndex += 1
                    pass
                    #interact with item

            elif event.type == pg.MOUSEBUTTONUP:
        
                if self.holdingItem:
                    self.holdingItem = False

                    newPos = self.interface.dropItem(pg.mouse.get_pos(), self.openInventory)
                    self.interface.hotScreenRect = ""
                    self.interface.invScreenRect = ""

                    if newPos != None:

                        if self.holdItem[2] == -1 and not self.holdItem[3]:
                            self.playerInventory.remove(self.holdItem[1])
                        else:
                            if not self.holdItem[3] or self.holdItem[1].quantity == 0:
                                self.playerHotbar[self.holdItem[2]] = ""

                        self.holdItem[0].image.set_alpha(255)
                        if newPos != -1:
                            if self.playerHotbar[newPos] != "":
                                if type(self.playerHotbar[newPos]).__name__ == type(self.holdItem[0]).__name__:
                                    self.playerHotbar[newPos].quantity += self.holdItem[0].quantity
                                else:
                                    self.playerHotbar = properListInsert(self.playerHotbar, self.holdItem[0], newPos, "")
                            else:
                                self.playerHotbar[newPos] = self.holdItem[0]
                        else:
                            inInv = False

                            for item in self.playerInventory:
                                if type(item).__name__ == type(self.holdItem[0]).__name__:
                                    inInv = True
                                    item.quantity = item.quantity + self.holdItem[0].quantity
                                    item.image.set_alpha(255)

                            if not inInv:
                                self.playerInventory.append(self.holdItem[0])
                    else:
                        self.holdItem[1].image.set_alpha(255)
                        if self.holdItem[3]:
                            self.holdItem[1].quantity += self.holdItem[0].quantity


            elif event.type == pg.VIDEORESIZE:
                self.screen = initScreen(event.w, event.h)
                self.fontSize = int(self.screen.get_width() / 30)
                self.interface.screenResize(self.screen)

        keys = pg.key.get_pressed()
        direction[0] = keys[K_d] - keys[K_a]
        direction[1] = keys[K_s] - keys[K_w]
        self.player.velocity[0] = direction[0] * self.player.speed
        self.player.velocity[1] = direction[1] * self.player.speed

        if self.player.velocity[0] != 0 and self.player.velocity[1] != 0:
            self.player.velocity[0] * 0.7071
            self.player.velocity[1] * 0.7071
        
    def update(self, dt):
        self.thingabobNameText = ""
        self.all.update(dt)
        
        self.collideWithWalls()
        self.handleNpcStates(dt)
        
    def collideWithWalls(self):

        if self.player.feet.collidelist(self.map.walls) > -1:
            self.player.moveBack("x")
            self.player.moveBack("y")
    
        for object in self.map.otherObjects:
            if self.player.feet.colliderect(object[1]):
                if object[0].type == "Map":
                    for sprite in self.npc.sprites():
                        sprite.kill()
                        del sprite
                    self.loadMap(object[0].name)
                elif object[0].type == "Cutscene":
                    self.paused = True
                    cutsceneGifs = self.cutscene.playCutScene(object[0].name)
                    self.playCutscenes(cutsceneGifs)

    def handleNpcStates(self, dt):

        for sprite in self.npc:
            
            if sprite.state == "suspicious":
                sprite.lookAtPos(self.player.position)
            elif sprite.state == "follow":
                path = AStarAlgorithm(self.map.graph, self.findValidNode(sprite), self.findValidNode(self.player))
                print(f"{path = }")
                sprite.followPath(path)
            elif sprite.state == "wandering":
                path = AStarAlgorithm(self.map.graph, self.findValidNode(sprite), self.chooseRandomNode())
                print(f"{path = }")
                sprite.followPath(path)

    def drawInterface(self):

        if self.openInventory:
            self.interface.drawInventory(self.playerInventory)
        if self.hotbarShow:
            self.interface.drawHotbar(self.playerHotbar)
        if self.holdingItem:
            self.interface.dragItem(pg.mouse.get_pos())
        if self.genericUIShow:
            self.screen.blit(self.thingabobNameText, self.screen.get_rect().topleft)
            self.interface.drawGeneralUI(self.collideThingamabob.UI, self.collideThingamabob.UIImage)

    def interactKey(self):

        interacted = False
        for thingamabob in self.thingamabobs:
            if self.player.feet.colliderect(thingamabob.rect):
                self.paused = not self.paused
                self.genericUIShow = not self.genericUIShow
                self.collideThingamabob = thingamabob
                interacted = True
                if self.collideThingamabob.UI[0] == 2:
                    self.collideThingamabob.UI[0] = 1
                    self.thingabobNameText = self.interface.drawText("<0 " + type(self.collideThingamabob).__name__, "oldlace", pg.font.SysFont(MAINFONT, self.fontSize), rectHeight = self.fontSize)
        
        if interacted == False:
            self.openInventory = not self.openInventory
            self.paused = not self.paused
            if self.openInventory:
                self.hotbarShow = True

    def interactWithInventory(self, mousePos, clickKey = False):
        
        if not clickKey:

            collided = False
            for item in self.playerInventory:
                if item.rect.collidepoint(mousePos):
                    if not self.holdingItem:
                        self.interface.collide(item)
                        collided = True
            if not collided:
                self.interface.collide(False)
        else:
            
            for item in self.item:         
                if item.rect.collidepoint(mousePos):
                    self.holdItem[1] = item
                    self.holdItem[3] = False
                    if self.openInventory:
                        self.holdItem[0] = eval("{}({})".format(type(item).__name__, item.quantity))

                        if item in self.playerHotbar:
                            index = self.playerHotbar.index(item)
                            self.holdItem[2] = index
                            if clickKey == 1:
                                item.image.set_alpha(128)
                                self.holdItem[1] = item
                            if clickKey == 3:
                                self.holdItem[3] = True
                                self.holdItem[0].quantity = math.ceil(item.quantity / 2)
                                self.holdItem[1].quantity = math.floor(item.quantity / 2)
                                if math.floor(item.quantity / 2) == 0:
                                    self.holdItem[1].image.set_alpha(128)

                            self.interface.hotScreenRect = ""
                        else:
                            self.holdItem[2] = -1
                            if clickKey == 1:
                                item.image.set_alpha(128)
                            if clickKey == 3:
                                self.holdItem[3] = True
                                self.holdItem[0].quantity = math.ceil(item.quantity / 2)
                                self.holdItem[1].quantity = math.floor(item.quantity / 2)
                                if self.holdItem[1].quantity == 0:
                                    item.image.set_alpha(128)

                            self.interface.invScreenRect = ""

                        self.holdingItem = True
                        self.interface.takeItem(self.holdItem[0])
                    else:
                       if item in self.playerHotbar:
                            self.holdItem[0] = eval("{}({})".format(type(item).__name__, item.quantity))
                            index = self.playerHotbar.index(item)
                            self.holdItem[2] = index

                            if clickKey == 1:
                                item.image.set_alpha(128) 
                            if clickKey == 3:
                                self.holdItem[3] = True
                                self.holdItem[0].quantity = math.ceil(item.quantity / 2)
                                self.holdItem[1].quantity = math.floor(item.quantity / 2)
                                if self.holdItem[1].quantity == 0:
                                    item.image.set_alpha(128)

                            self.interface.hotScreenRect = ""
                            self.holdingItem = True
                            self.interface.takeItem(self.holdItem[0])

    def run(self):

        clock = pg.time.Clock()
        self.running = True

        try:
            while self.running:
                dt = clock.tick() / 1000.0
                self.handleInput()
                if not self.paused:
                    self.update(dt)
                if not self.playingCutScene:
                    self.draw()
                pg.display.flip()
                pg.display.set_caption("{:.2f} fps".format(clock.get_fps()))

        except KeyboardInterrupt:
            self.running = False

    def drawOverlay(self):
        alpha = 0
        overlayColor = pg.Color(128,128,128, alpha)

        overlaySurf = pg.Surface(self.screen.get_size())
        overlaySurf.fill(overlayColor)

        self.screen.blit(overlaySurf, (0,0), special_flags= BLEND_RGB_MULT)

    def playCutscenes(self, cutscenegGifs):

        timer = pg.time.Clock()
        tempSurf = pg.Surface(self.screen.get_size())
        tempSurf.fill((0,0,0))
        playing = True

        while playing:
            for gif in cutscenegGifs:
                gifFile = os.path.join(DATADIR, gif + ".gif")
                with Image.open(gifFile) as im:
                    numberOfFrames = im.n_frames
                frames = getListOfImages(gif, numberOfFrames)
                for image in frames:
                    self.screen.blit(tempSurf, (0,0))
                    self.screen.blit(image, (0,0))
                    pg.display.flip()
                    timer.tick(12)
            playing = False

        self.paused = False

    def findValidNode(self, sprite):

        pathResolution = self.map.pathResolution
        tryNode  = [int(sprite.feet.center[0] / pathResolution) * pathResolution, int(sprite.feet.center[1] / pathResolution) * pathResolution]
        if tryNode in self.map.mapVertices:
            return tryNode
        else:
            tryNodes = self.findClosestNodes(tryNode)
            for node in tryNodes:
                collided = False
                for wall in self.map.walls:
                    if checkLineRectCollision((sprite.feet.center,node), wall):
                        collided = True
                if collided:
                    tryNodes.remove(node)
            return tryNodes[0]

    def findClosestNodes(self, tryNode):

        nodeNotFound = True
        neighbours = [tryNode]
        closeNodes = []
        pathResolution = self.map.pathResolution
        while nodeNotFound:
            for node in neighbours:
                if node in self.map.mapVertices:
                    closeNodes.append(node)
                    nodeNotFound = False
                else:
                    if nodeNotFound:
                        n = [(node[0] - pathResolution, node[1]), (node[0], node[1] - pathResolution), (node[0] + pathResolution, node[1]), (node[0],node[1] + pathResolution)]
                        for i in n:
                            if i not in neighbours:
                                neighbours.append(i)
        return closeNodes
                
    def chooseRandomNode(self):

        rnd = random.randint(0,len(self.map.graph) - 1)
        return self.map.mapVertices[rnd]

    def drawGraph(self):

        for vertex in list(self.map.graph):
            for connection in self.map.graph[vertex]:
                pg.draw.aaline(self.screen, "green", vertex, connection[0])

        for sprite in self.npc:
            if sprite.currentPath != None:
                if not(sprite.finishedPath and sprite.reachedNode):
                    for i, node in enumerate(sprite.currentPath[sprite.currentNode:len(sprite.currentPath) - 1:2]):
                        pg.draw.aaline(self.screen, "red", node, sprite.currentPath[i + 1])




def main():

    pg.init()
    pg.font.init()
    screen = initScreen(960, 720)
    #pg.display.set_caption("Make It Or Break It")

    try:
        game = Game(screen, "save.txt")
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        pg.quit()

if __name__ == "__main__":
    main() 