from dataclasses import dataclass, field
import math
from random import randint, random
import time
from types import NoneType
import numpy as np
import pygame as pg
from numba import jit, njit
import sys


drawList = []
rod_list = []

# Collision_objects = {}

XENON_TILE = 0.1
ROD_HIGHT_COUNT = 32 #высота стрежня в клетках симуляции
ROD_CELL_HIGHT = 512/32
ROD_SIZE = 10
DEBUG=False
origin = np.array((150,200))
ROD_COUNT = 16
CLOCK_TIME = 10
ROD_SPACE = int((1024-ROD_SIZE*ROD_COUNT)/(ROD_COUNT+1)) #расстояние между стрежнями

Uk = 20
class MatObject():
    lvl:int
    n:float 

    def __post_init__(self):
        drawList.append(self)
        return


    def interact(self, ray, lenght, pos:np.ndarray):
        pass




class NeutronSystem():
    def __init__(self):
        self.X:np.ndarray = np.zeros(0)
        self.Y:np.ndarray = np.zeros(0)
        self.k:np.ndarray = np.zeros(0) # длина вектора перемещения (знак проекции на ось x)
        self.Vy:np.ndarray = np.zeros(0)
        self.Alpha:np.ndarray = np.zeros(0)
        self.results:np.ndarray
    def add(self,x:float,y:float,angle:float):
        size = self.X.size + 1
        self.X.resize(size)
        self.Y.resize(size)
        self.k.resize(size)
        self.Alpha.resize(size)
        self.Alpha[size-1] = angle
        self.Vy.resize(size)
        self.Y[size-1] = y
        self.X[size-1] = x
        self.k = ROD_SPACE/np.cos(self.Alpha)
        self.Vy[size-1] = math.sin(angle)*math.fabs(self.k[size-1])/(512/ROD_HIGHT_COUNT)
        np.vectorize(self.add)
    # @njit(parallel =True)
    def raycast(self, rods:np.ndarray):
        
        self.start_pos =  np.vstack([self.X, self.Y])
        self.start_pos= self.start_pos.transpose()
        self.X+=(-1+2*(self.k>0))
        to_delete = np.where(self.X>ROD_COUNT-1)
        to_delete +=  np.where(self.X<0)
        self.Y+=self.Vy
        to_delete += np.where(self.Y>ROD_HIGHT_COUNT-1)
        to_delete += np.where(self.Y<0)
        self.delete(np.concatenate(to_delete))
        randA = np.random.sample(self.X.size)
        to_rod = np.where(2**(-(np.abs(self.k))/Uk)<randA)
        reactedRods = rods[np.floor(self.X[to_rod]).astype(int),np.floor(self.Y[to_rod]).astype(int)]
        randA.resize(reactedRods.size)
        reactedXe = reactedRods>randA
        self.results=np.zeros_like(self.X)
        self.results[to_rod] = 1+(reactedXe)
        rods[np.floor(self.X[to_rod]).astype(int),np.floor(self.Y[to_rod]).astype(int)] += (1-2*(self.results[to_rod]))*XENON_TILE

        to_u_rod = np.where(self.results==1)

        self.X = np.concatenate([self.X, np.repeat(self.X[to_u_rod],3)])
        self.Y = np.concatenate([self.Y, np.repeat(self.Y[to_u_rod],3)])
        self.Alpha = np.concatenate([self.Alpha, np.repeat(self.Alpha[to_u_rod],3)])
        self.delete(to_rod)
        size = self.X.size
        self.k.resize(size)
        self.Vy.resize(size)
        self.k.resize(size)
        self.Alpha += (np.random.sample(self.X.size)-0.5)*math.pi
        self.k = ROD_SPACE/np.cos(self.Alpha)
        self.Vy = np.sin(self.Alpha)*np.abs(self.k)/(512/ROD_HIGHT_COUNT)


    def draw(self):
        for i in range(self.start_pos.shape[0]):
            pg.draw.line(screen,(255,255,255),
                         (self.start_pos[i][0]*(ROD_SPACE+ROD_SIZE)+origin[0],
                          self.start_pos[i][1]*ROD_CELL_HIGHT+origin[1]),
                         (self.X[i]*(ROD_SPACE+ROD_SIZE)+origin[0]
                          ,self.Y[i]*ROD_CELL_HIGHT+origin[1]))
            pg.draw.circle(screen,(255,0,0),(self.X[i]*(ROD_SPACE+ROD_SIZE)+origin[0]
                          ,self.Y[i]*ROD_CELL_HIGHT+origin[1]),3)

    def tick(self, a):
        self.raycast(a.XenonField)
        self.draw()

    def delete(self,to_delete):
        self.X = np.delete(self.X,to_delete)
        self.Y = np.delete(self.Y,to_delete)
        self.k = np.delete(self.k,to_delete)
        self.Vy = np.delete(self.Vy,to_delete)
        self.Alpha = np.delete(self.Alpha, to_delete)
        self.start_pos = np.delete(self.start_pos,to_delete,0)


    
class Urod():
    def __init__(self):
        self.XenonField:np.ndarray = np.full((ROD_COUNT,ROD_HIGHT_COUNT),0.1)
        drawList.append(self)
    def tick(self):
        self.XenonField+=0.05
    def draw(self,screen:pg.surface.Surface):
        for ix, iy in np.ndindex(self.XenonField.shape):
            xcord = origin[0]+ix*ROD_SIZE+ix*ROD_SPACE+ROD_SPACE
            bColor = max(0,min(self.XenonField[ix,iy],255))
            pg.draw.rect(screen,(0,200,bColor),pg.Rect(xcord,origin[1]+iy*(512//ROD_HIGHT_COUNT),ROD_SIZE,512//ROD_HIGHT_COUNT))

origin = (100,150)

Nsys = NeutronSystem()
rods = Urod()

print("adding neutrons")
for i in range(1000):
    Nsys.add(randint(0,14),randint(0,14),random()*2*math.pi)
print("finish adding")

pg.init()
screen = pg.display.set_mode((1200, 800))
pg.draw.rect(screen, (0,100,100), pg.Rect(origin, (1043,531)), 10)
pg.draw.circle(screen,(255,0,0), (origin[0],origin[1]),20)
pg.draw.circle(screen,(255,0,0), (((ROD_COUNT-1)*(ROD_SPACE+ROD_SIZE)+origin[0],
                          (ROD_HIGHT_COUNT-1)*ROD_CELL_HIGHT+origin[1])),20)
pg.display.flip()


while True:
    # pg.time.Clock().tick(1)
    start_time = time.time()
    #рисуем drawlist
    if DEBUG:
        pg.draw.rect(screen,(0,0,0),pg.Rect(origin,(1043,531)))
    pg.draw.rect(screen,(0,0,0),pg.Rect(origin[0]+10,origin[1]+10,1024,512))
    for i in drawList:
        if DEBUG:
            
            i.debug_draw(screen)
        else:
            i.draw(screen)
    
    Nsys.tick(rods)
    rods.tick()
    #рисуем fps
    pg.draw.rect(screen,(10,10,10),pg.Rect(100,100,400,15))
    screen.blit(pg.font.SysFont("monospace", 15).render(str(1/(time.time()-start_time))+'  '+str(Nsys.X.size),
                True,(255,255,255),(0,0,0)),(100,100))
    pg.display.flip()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    