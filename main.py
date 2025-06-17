from dataclasses import dataclass, field
import os
from random import randint
import time
import numpy as np
import pygame as pg
from numba import jit, njit
import sys


drawList = []
zone=(1024,512)

class MatObject():
    n:float 

    def __post_init__(self):
        drawList.append(self)
        return


    def interact(self,ray)->tuple:
        pass

#p=2**(-lambda/l)
#x=rnd()



@dataclass
class NeutronRay():
    originObj:MatObject
    pitc:float
    origin:np.ndarray
    isFast:bool
    def raycast(self):
        #raycast

        return ()
    def throw(self):
        is_interacte = False
        while(not isinstance):
            #matObj, lenght = raytrace()
            #if out of border:
            #   break
            #is_interacted = interact()
            pass

class WaterField():
    n = 1
    def __init__(self,xsize,ysize):
        self.temp = np.ones((xsize,ysize))
        drawList.append(self)


    def randgen(self):
        _randgen(self.temp)

    def interact(self, ray:NeutronRay):
        if(ray.isFast):
            return ()
        else:
            pass
    def draw(self, screen):
        for iy, ix in np.ndindex(self.temp.shape):
            pg.draw.rect(screen, (self.temp[iy,ix],50,200), pg.Rect((ix*zone[0]/self.temp.shape[1]+110,iy*zone[1]/self.temp.shape[0]+160),(16,16)))

class ksenonField():
    def __init__(self,xsize,ysize):
        self.temp = np.ones((xsize,ysize))
    def randgen(self):
        _randgen(self.temp)

# @njit(parallel=True)
def _randgen(array):
    for iy, ix in np.ndindex(array.shape):
        array[iy,ix] = randint(0,255)

@dataclass
class Graphite(MatObject):
    def interact(self, ray:NeutronRay)->tuple:
        pass

@dataclass
class Rod(MatObject):
    pos:tuple
    n:int

class ModeratorRod(Rod):
    def interact(self, ray:NeutronRay)->tuple:
        pass


class FuelRod(Rod):
    def draw(self,screen):
        space = int((zone[0]-10*self.n )/self.n)
        for i in range(self.n):
            xpos = self.pos[0]+(space + i*(space+5))
            pg.draw.line(screen,(0,100,50),(xpos,self.pos[1]),(xpos,self.pos[1]+zone[1]),10)
    
    def interact(self, ray:NeutronRay)->tuple:
        pass

class GreateCalculator():
    def callenght(material, ray:NeutronRay)->bool:
        pass    



origin = (100,150)
size = (1043,531)

wf = WaterField(32,64)
frod = FuelRod((origin[0]+10,origin[1]+10),10)

pg.init()
screen = pg.display.set_mode((1200, 800))
pg.display.set_caption('numba',str(os.getpid))
pg.draw.rect(screen, (0,100,100), pg.Rect(origin, size), 10)
pg.display.flip()

while True:
    start_time = time.time()
    #рисуем drawlist
    for i in drawList:
        i.draw(screen)
    
    #рисуем fps
    screen.blit(pg.font.SysFont("monospace", 15).render(str(1/(time.time()-start_time)),True,(255,255,255),(0,0,0)),(100,100))
    pg.display.flip()
    wf.randgen()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()