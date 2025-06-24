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
ROD_HIGHT = 32 #высота стрежня 
ROD_SIZE = 10
DEBUG=False
origin = np.array((150,200))
ROD_COUNT = 16
CLOCK_TIME = 10
ROD_SPACE = (1024-ROD_SIZE*ROD_COUNT)/(ROD_COUNT+1) #расстояние между стрежнями

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
        self.Vy[size-1] = math.sin(angle)*math.fabs(self.k[size-1])/ROD_HIGHT
        np.vectorize(self.add)
    def raycast(self, rods:np.ndarray):
        X_ = self.X.copy()
        Y_ = self.Y.copy()
        self.X+=(-1+2*(self.k>0))
        border = 1 #границы реактора
        to_delete:tuple = np.where(self.X>ROD_COUNT-1)
        to_delete +=  np.where(self.X<0)
        self.Y+=self.Vy
        to_delete += np.where(self.Y>ROD_HIGHT+1)
        to_delete += np.where(self.Y<0)
        self.delete(to_delete)
        randA = np.random.sample(self.X.size)
        to_rod = np.where(2**(-(self.k*(ROD_SPACE/ROD_SIZE)/Uk)))>randA
        reactedRods = rods[self.X[to_rod],self.Y[to_rod]]
        reactedXe = reactedRods>randA
        self.results[to_rod] = 1+(reactedXe)
        rods[self.X[to_rod],self.Y[to_rod]] += (1-2*(self.results[to_rod]))*XENON_TILE

        to_u_rod = np.where(self.results==1)
        np.concatenate([self.X, np.repeat(self.X[to_u_rod],3)])
        np.concatenate([self.Y, np.repeat(self.Y[to_u_rod],3)])
        self.delete(to_rod)
        size = self.X
        self.k.resize(size)
        self.Vy.resize(size)
        self.k.resize(size)
        self.Alpha.resize(size)        
        self.Alpha = np.random.sample(self.X.size)
        self.k = ROD_SPACE/np.cos(self.Alpha)
        self.Vy = np.sin(self.Alpha)*np.abs(self.k)/ROD_HIGHT
        self.draw(X_, Y_)


    def draw(self, x:np.ndarray, y:np.ndarray):
        for i in range(x.size):
            pg.draw.line(screen,(255,255,255),x[i],y[i])

    def tick(self, a):
        self.raycast(a.XenonField)

    def delete(self,to_delete):
        np.delete(self.X,to_delete)
        np.delete(self.Y,to_delete)
        np.delete(self.k,to_delete)
        np.delete(self.Vy,to_delete)
    
class Urod():
    def __init__(self):
        self.XenonField:np.ndarray = np.full((ROD_COUNT,ROD_HIGHT),0.1)
        drawList.append(self)
    def tick(self):
        self.XenonField+=0.05
    def draw(self,screen:pg.surface.Surface):
        for ix, iy in np.ndindex(self.XenonField.shape):
            xcord = origin[0]+ix*ROD_SIZE+ix*ROD_SPACE+ROD_SPACE
            pg.draw.rect(screen,(0,200,50),pg.Rect(xcord,origin[1]+iy*ROD_HIGHT,ROD_SIZE,ROD_HIGHT))

origin = (100,150)

Nsys = NeutronSystem()
rods = Urod()

print("adding neutrons")
for i in range(100):
    Nsys.add(randint(0,14),randint(0,14),random()*2*math.pi)
print("finish adding")

pg.init()
screen = pg.display.set_mode((1200, 800))
pg.draw.rect(screen, (0,100,100), pg.Rect(origin, (1043,531)), 10)
pg.display.flip()


while True:
    pg.time.Clock().tick(1)
    start_time = time.time()
    #рисуем drawlist
    if DEBUG:
        pg.draw.rect(screen,(0,0,0),pg.Rect(origin,(1043,531)))
    for i in drawList:
        if DEBUG:
            
            i.debug_draw(screen)
        else:
            i.draw(screen)

    Nsys.tick(rods)
    rods.tick()
    #рисуем fps
    screen.blit(pg.font.SysFont("monospace", 15).render(str(1/(time.time()-start_time))+'  '+str(Nsys.X.size),
                True,(255,255,255),(0,0,0)),(100,100))
    pg.display.flip()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    