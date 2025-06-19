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

Collision_objects = {}

zone=(1024,512)
FUEL_ROD_SIZE = 10
XENON_CELL_SIZE = 5
STEP = 1/4
ROD_COUNT = 16
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
    ORIGIN:np.ndarray
    isFast:bool

   

    def __post_init__(self):
        self.originVec = np.array((math.cos(self.pitc),math.sin(self.pitc)))*STEP
        self.pos = self.ORIGIN.copy()
        
        Neutron_list.append(self)
    def raycast(self, screen:pg.surface.Surface):
        # print("a")
        color = screen.get_at((int(self.pos[0]),int(self.pos[1]))).g 
        while color == self.originObjcolor:
            self.pos += self.originVec
            color = screen.get_at((int(self.pos[0]),int(self.pos[1]))).g 
            
        lenght = np.linalg.norm(self.pos-self.ORIGIN)
        matObj = findObj(color)
        self.originObjcolor = color 
        
        
        return matObj, lenght
    def throw(self, screen:pg.surface.Surface):
        print(int(self.pos[0]),int(self.pos[1]))
        is_interacted = False
        while(not is_interacted):
            matObj, lenght = self.raycast(screen)
            if type(matObj) == NoneType:
                break
            # pg.draw.circle(screen,(50,0,123),(((self.pos-self.origin)/2)[0],((self.pos-self.origin)/2)[1]),5)
            is_interacted = matObj.interact(self, lenght,(self.pos+self.ORIGIN)/2)
        self.draw(screen)
        Neutron_list.remove(self)
    def draw(self,screen):
        pg.draw.line(screen, (255,255,255),(int(self.ORIGIN[0]), int(self.ORIGIN[1])),(int(self.pos[0]),int(self.pos[1])))
        

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
        
        if(ray.isFast):
            if self.temp[pos] >= 100:
                if(random() < 2**-(lenght/3000)):
                    #ray.isFast = False
                    self.temp[pos] += 10    
            else:
                if(random() < 2**-(lenght/60)):
                    #ray.isFast = False
                    self.temp[pos] += 10
        return False
    def draw(self, screen):
        for iy, ix in np.ndindex(self.temp.shape):
            pg.draw.rect(screen, (self.temp[iy,ix],50,200), pg.Rect((ix*zone[0]/self.temp.shape[1]+110,iy*zone[1]/self.temp.shape[0]+160),(16,16)))


class Border():
    def __init__(self):
        Collision_objects[origin[0]] = self
        Collision_objects[origin[0]+size[0]] = self
    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray):
        return True

@dataclass
class Rod(MatObject):
    pos:tuple
    k:int

class FuelRod(Rod):
    def __post_init__(self):
        self.xenon_field = XsenonField(pos=self.pos)
        Collision_objects[self.pos[0]] = self
        Collision_objects[self.pos[0]+FUEL_ROD_SIZE] = self
    def draw(self,screen):
        self.xenon_field.draw(screen=screen)
    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray)->bool:
        pos -= self.pos
        con = int(pos[0]//self.space)
        xefield:np.ndarray = self.xenon_field.xenon_fields[con]
        cord = ((int((pos[0])-self.space*con+self.space-FUEL_ROD_SIZE)//XENON_CELL_SIZE),int(pos[1]//XENON_CELL_SIZE))
        
        if(random()<=xefield[cord]/255):
            return True
        if(random() < 2**-(lenght/200)):
            for i in range(-1,2,2):
                NeutronRay(200,ray.pitc+(math.pi/3)*i,pos,True)
            xefield[cord] = math.fabs(xefield[cord]-5)
            return True
        return False 

class XsenonField():
    def __init__(self, pos:np.ndarray):
        self.xenon_field = np.zeros((FUEL_ROD_SIZE//XENON_CELL_SIZE, zone[1]//XENON_CELL_SIZE))
        self.pos = pos
        drawList.append(self)
        self.sum_matrix = np.full_like(self.xenon_field,1/CLOCK_TIME)
    
    def sum(self):
        self.xenon_field += self.sum_matrix
        self.xenon_field[np.where(self.xenon_field>255)]=255
    
    def randgen(self):
        _randgen(self.xenon_field)

    def draw(self, screen:pg.surface.Surface):
        for ix, iy in np.ndindex(self.xenon_field.shape):
            pg.draw.rect(screen, ((100,200,self.xenon_field[ix,iy])),pg.Rect((self.pos[0]+XENON_CELL_SIZE*ix,self.pos[1]+XENON_CELL_SIZE*iy),(XENON_CELL_SIZE,XENON_CELL_SIZE)))    
            

# @njit(parallel=True)
def _randgen(array):
    for iy, ix in np.ndindex(array.shape):
        array[iy,ix] = randint(0,255)


class WaterChannel():
    def __init__(self):
        Collision_objects
    def interact(self, ray:NeutronRay)->tuple:
        pass
@dataclass
class Graphite():
    k:float
    def interact(self, ray:NeutronRay)->tuple:
        pass

@dataclass
class ControlRod(Rod):
    hight:float

    def __post_init__(self):
        super().__post_init__()


    def draw(self,screen):
        pg.draw.rect(screen,(100,100,100),pg.Rect((self.pos[0],self.pos[1]),(FUEL_ROD_SIZE,int(zone[1]*(1-self.hight)))))
    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray)->tuple:
        if(random()<0.95):
            return True
        return False




origin = (100,150)
size = (1043,531)

wf = WaterField(32,64)


frods = []
crods = [] 

#генерируем стержни
interspace = math.ceil((zone[0]-FUEL_ROD_SIZE*ROD_COUNT)/(ROD_COUNT+1))
for i in range(ROD_COUNT):
    frods.append(FuelRod((origin[0]+i*(FUEL_ROD_SIZE+interspace)+interspace,origin[1]+10),1))
for i in range(ROD_COUNT-1):
    crods.append(ControlRod((origin[0]+i*(FUEL_ROD_SIZE+interspace)+interspace+(interspace+FUEL_ROD_SIZE)/2,origin[1]+10),1,0.5))

# NeutronRay(50,random()*2*math.pi,np.array((600.0,400.0)),False)
# for i in range(10):
#     NeutronRay(50,random()*2*math.pi,np.array((600,400)),True)


pg.init()
screen = pg.display.set_mode((1200, 800))
pg.display.set_caption('numba',str(os.getpid))
pg.draw.rect(screen, (0,100,100), pg.Rect(origin, size), 10)
pg.display.flip()


while True:
    # pg.time.Clock().tick(1)
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
    for i in frods:
        i:FuelRod
        i.xenon_field.randgen()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    