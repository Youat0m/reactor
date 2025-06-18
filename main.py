from dataclasses import dataclass, field
import math
import os
from random import randint, random
import time
from types import NoneType
import numpy as np
import pygame as pg
from numba import jit, njit
import sys


drawList = []
Neutron_list=[]
zone=(1024,512)
FUEL_ROD_SIZE = 10
XENON_CELL_SIZE = 10
STEP = 1/4
ROD_COUNT = 15
CLOCK_TIME = 10
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
    originObjcolor:int
    pitc:float
    origin:np.ndarray
    isFast:bool

   

    def __post_init__(self):
        self.originVec = np.array((math.cos(self.pitc),math.sin(self.pitc)))*STEP
        self.pos = origin
        Neutron_list.append(self)
    def raycast(self, screen:pg.surface.Surface):
        # print("a")
        color = screen.get_at((int(self.pos[0]),int(self.pos[1]))).g 
        while color == self.originObjcolor:
            self.pos += self.originVev
            color = screen.get_at((int(self.pos[0])),int(self.pos[1])).g 
        lenght = np.linalg.norm(self.pos-self.origin)
        matObj = findObj(color)
        self.originObjcolor = color 
        pg.draw.circle(screen,(250,0,0),(int(self.pos[0]),int(self.pos[1])),10)
        
        return matObj, lenght
    def throw(self, screen:pg.surface.Surface):
        is_interacte = False
        while(not is_interacte):
            matObj, lenght = self.raycast(screen)
            if type(matObj) == NoneType:
                break 
            is_interacted = matObj.interact(self, lenght,(self.pos-self.origin)/2)
            print(type(matObj))
        drawList.append(self)
        Neutron_list.remove(self)
    def draw(self,screen):
        pg.draw.line(screen, (255,255,255),(int(self.origin[0]), int(self.origin[1])),(int(self.pos[0]),int(self.pos[1])))
        drawList.remove(self)

class WaterField():
    n = 1
    def __init__(self,xsize,ysize):
        self.temp = np.full((xsize,ysize),200.0)
        drawList.append(self)


    def randgen(self):
        _randgen(self.temp)

    def substract(self):
        self.temp = self.temp - np.full_like(self.temp,1/CLOCK_TIME)
        self.temp[np.where(self.temp<0)]=1
        pass

    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray):
        pos = pos//16
        pos = (pos[0],pos[1])
        
        if(not ray.isFast):
            if self.temp[pos] >= 100:
                if(random() < 2**-(lenght/3000)):
                    ray.isFast = False
                    self.temp[pos] += 10    
            else:
                if(random() < 2**-(lenght/60)):
                    ray.isFast = False
                    self.temp[pos] += 10
        return False
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
        self.space = int((zone[0]-FUEL_ROD_SIZE*self.n)/(self.n+1))
    
    
    def draw(self,screen):
        self.xenonField.draw(screen=screen,fuelRod=self)
    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray)->bool:
        xefield:np.ndarray = self.xenonField.xenonFields[pos[0]//self.space]
        cord = (int(pos[0]),int(pos[1])) 
        
        if(random()<=xefield[cord]/255):
            return True
        if(random() < 2**-(lenght/200)):
            for i in range(-1,2,2):
                NeutronRay(200,ray.pitc+(math.pi/3)*i,pos,True)
            xefield[cord] = math.abs(xefield[cord]-5)
            return True
        return False 

class XsenonField():
    def __init__(self, n:int, pos:np.ndarray):
        self.xenonFields = [np.zeros((FUEL_ROD_SIZE//XENON_CELL_SIZE, zone[1]//XENON_CELL_SIZE)) for i in range(n)]
        self.n = n
        self.pos = pos
        drawList.append(self)
    
    def sum(self):
        for i in self.xenonFields:
            i += np.full_like(i,1/CLOCK_TIME)
            i[np.where(i>255)]=255

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


@dataclass
class ControlRod(Rod):
    hight:float
    
    def draw(self,screen):
        space = int((zone[0]-FUEL_ROD_SIZE*self.n)/(self.n+1)) 
        for i in range(self.n-1):
            xpos = self.pos[0]+(1.5*space + i*(space+FUEL_ROD_SIZE))
            pg.draw.rect(screen,(100,100,100),pg.Rect((xpos,self.pos[1]),(FUEL_ROD_SIZE,int(zone[1]*(1-self.hight)))))
    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray)->tuple:
        if(random()<0.95):
            return True
        return False


def findObj(color:int)->MatObject:
    if color == 50:
        return wf
    if color == 100:
        return crod
    if color == 200:
        return frod
    if color == 0:
        return 


origin = (100,150)
size = (1043,531)

wf = WaterField(32,64)
frod = FuelRod((origin[0]+10,origin[1]+10),ROD_COUNT)
crod = ControlRod((origin[0]+10,origin[1]+10),ROD_COUNT,1)

for i in range(10):
    NeutronRay(50,random()*2*math.pi,np.array((600,400)),True)

pg.init()
screen = pg.display.set_mode((1200, 800))
pg.display.set_caption('numba',str(os.getpid))
pg.draw.rect(screen, (0,100,100), pg.Rect(origin, size), 10)
pg.display.flip()


while True:
    pg.time.Clock().tick(1)
    start_time = time.time()
    #рисуем drawlist
    for i in drawList:
        i.draw(screen)
    for i in Neutron_list:
        i.throw(screen)
    #рисуем fps
    screen.blit(pg.font.SysFont("monospace", 15).render(str(1/(time.time()-start_time))+'  '+str(len(Neutron_list)),True,(255,255,255),(0,0,0)),(100,100))
    pg.display.flip()
    wf.substract()
    frod.xenonField.sum()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    