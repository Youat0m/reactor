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
FUEL_ROD_SIZE = 10
XENON_CELL_SIZE = 10

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

@dataclass
class Rod(MatObject):
    pos:tuple
    n:int

class FuelRod(Rod):
    def __post_init__(self):
        self.xenonField = XsenonField(self.n, pos=self.pos)
    def draw(self,screen):
        self.xenonField.draw(screen=screen,fuelRod=self)
    def interact(self, ray:NeutronRay)->tuple:
        pass

class XsenonField():
    def __init__(self, n:int, pos:np.ndarray):
        self.xenonFields = [np.zeros((FUEL_ROD_SIZE//XENON_CELL_SIZE, zone[1]//XENON_CELL_SIZE)) for i in range(n)]
        self.n = n
        self.pos = pos
        drawList.append(self)
        self.randgen()
    def randgen(self):
        for i in self.xenonFields:
            _randgen(i)
    
    def draw(self, screen:pg.surface.Surface):
        space = int((zone[0]-FUEL_ROD_SIZE*self.n)/(self.n+1))
        for i in range(len(self.xenonFields)):
            xpos = self.pos[0]+(space + i*(space+FUEL_ROD_SIZE))
            for ix, iy in np.ndindex(self.xenonFields[i].shape):
                pg.draw.rect(screen, ((100,200,self.xenonFields[i][ix,iy])),pg.Rect((xpos+XENON_CELL_SIZE*ix,self.pos[1]+XENON_CELL_SIZE*iy),(XENON_CELL_SIZE,XENON_CELL_SIZE)))    
            

# @njit(parallel=True)
def _randgen(array):
    for iy, ix in np.ndindex(array.shape):
        array[iy,ix] = randint(0,255)

@dataclass
class Graphite(MatObject):
    def interact(self, ray:NeutronRay)->tuple:
        pass



class ModeratorRod(Rod):
    def interact(self, ray:NeutronRay)->tuple:
        pass

class GreateCalculator():
    def callenght(material, ray:NeutronRay)->bool:
        pass    



origin = (100,150)
size = (1043,531)

wf = WaterField(32,64)
frod = FuelRod((origin[0]+10,origin[1]+10),15)

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
    frod.xenonField.randgen()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()