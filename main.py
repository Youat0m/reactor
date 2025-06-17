from dataclasses import dataclass, field
from random import random
import numpy as np
import pygame as pg
from numba import jit
import sys

class MatObject():
    n:float 
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
@dataclass 
class Water(MatObject):
    n = 1
    temp:float
    def interact(self, ray:NeutronRay):
        if(ray.isFast):
            return ()
        else:
            pass

@dataclass
class Graphite(MatObject):
    def interact(self, ray:NeutronRay)->tuple:
        pass

@dataclass
class Rod(MatObject):
    pos:np.array
    radius:float

@dataclass
class ModeratorRod(Rod):
    def interact(self, ray:NeutronRay)->tuple:
        pass

@dataclass
class FuelRod(Rod):
    ksenon:float
    def interact(self, ray:NeutronRay)->tuple:
        pass

class GreateCalculator():
    def callenght(material, ray:NeutronRay)->bool:
        pass    



fild = np.full((16,32),Water(temp=0))
# @jit(nopython = True, parallel=True)
def randgen(array:np.ndarray):
    for iy, ix in np.ndindex(array.shape):
        array[iy,ix].temp = random()*255
        

pg.init()
screen = pg.display.set_mode((1200, 800))
origin = (100,150)
size = (1024,512)
pg.draw.rect(screen, (0,100,100), pg.Rect(origin, size), 10)
pg.display.flip()
while True:
    for iy, ix in np.ndindex(fild.shape):
        pg.draw.rect(screen, (fild[iy,ix].temp,50,200), pg.Rect((ix*32+110,iy*32+160),(31,31)))
    pg.display.flip()
    randgen(fild)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()