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


ROD_SPACE = 1 #расстояние между стрежнями
ROD_HIGHT = 1 #высота стрежня 
DEBUG=True
zone=(1024,512)
FUEL_ROD_SIZE = 10
# WATER_CHANNEL_RADIUS = 5
STEP = 1/4
ROD_COUNT = 16
CLOCK_TIME = 10
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
        self.results:np.ndarray
    def add(self,x:float,y:float,angle:float):
        size = self.X.size + 1
        self.X.resize(size)
        self.X.resize(size)
        self.k.resize(size)
        self.Vy.resize(size)
        self.Y[size-1] = x
        self.X[size-1] = y
        self.k[size-1] = ROD_SPACE/math.cos(angle)
        self.Vy[size-1] = math.sin(angle)*math.fabs(self.k[size-1])/ROD_HIGHT
    
    def raycast(self, rods:np.ndarray):
        self.X+=(-1+2*(self.k>0))
        border = 1 #границы реактора
        n = 1 #пробег в водичке
        n2 = 1.0
        to_delete:tuple = np.where(self.X>border or self.X<border)
        self.Y+=self.Vy
        to_delete += (np.where(self.Y>border or self.Y<border))
        self.delete(to_delete)
        randA = np.random.sample(self.X.size)
        self.results=np.zeros_like(self.X)
        to_rod = np.where(2**-(self.k*(ROD_SPACE/FUEL_ROD_SIZE)/n2))>randA
        reactedRods = rods[self.X[to_rod],self.Y[to_rod]]
        reactedXe = reactedRods>randA
        self.results[to_rod] = 1+(reactedXe)
        rods[self.X[to_rod],self.Y[to_rod]] += (1-2*(self.results[to_rod]))*XENON

    def delete(self,to_delete):
        np.delete(self.X,to_delete)
        np.delete(self.Y,to_delete)
        np.delete(self.k,to_delete)
        np.delete(self.Vy,to_delete)
    

def calculator(a,b):
    n2 = 1 #пробег в уране
    return (2**-(a*(ROD_SPACE/FUEL_ROD_SIZE)/n2))>b
        

class WaterField():
    n = 1
    def __init__(self,xsize,ysize):
        self.temp = np.full((xsize,ysize),50.0)
        drawList.append(self)
        self.pos = np.array(origin)+np.array((10,10))

    def randgen(self):
        _randgen(self.temp)

    def substract(self):
        
        self.temp = self.temp - np.full_like(self.temp,1/CLOCK_TIME)
        self.temp[np.where(self.temp<0)]=1
        pass

    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray):
        q = pos.copy()
        pos -= self.pos
        pos = pos//16
        pos = (int(pos[0]),int(pos[1])) # type: ignore
        
        if(not ray.isFast):
            try:
                if self.temp[pos] >= 100:
                    if(random() < 2**-(lenght/3000)):
                        #ray.isFast = False
                        self.temp[pos] += 10

                else:
                    if(random() < 2**-(lenght/60)):
                        #ray.isFast = False
                        self.temp[pos] += 10
            except:
                s = pg.surface.Surface((20,20))
                s.set_alpha(128)
                pg.draw.circle(s,(255,255,255),(5,5),10)
                screen.blit(s,(q[0],q[1]))
                pg.display.flip()
        return False
    def debug_draw(self,screen:pg.surface.Surface):
        pass
    def draw(self, screen):
        for iy, ix in np.ndindex(self.temp.shape):
            pg.draw.rect(screen, (min(self.temp[iy,ix],255),50,200), pg.Rect((ix*zone[0]/self.temp.shape[1]+110,iy*zone[1]/self.temp.shape[0]+160),(16,16)))


class Border():
    def __init__(self):
        Collision_objects[origin[0]] = self
        Collision_objects[origin[0]+size[0]] = self
    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray):
        return True
    def debug_draw(self,screen):
        pg.draw.line(screen,(255,0,0),(origin[0],0),(origin[0],2000))
        pg.draw.line(screen,(255,0,0),(origin[0]+size[0],0),(origin[0]+size[0],2000))
    def draw(self,scree):
        pass

@dataclass
class Rod(MatObject):
    pos:tuple
    k:int
    def __post_init__(self):
        super().__post_init__()
        self.water_channel = WaterChannel(self.pos)

class FuelRod(Rod):
    def __post_init__(self):
        super().__post_init__()
        self.lvl = 0
        self.xenon_field = XsenonField(pos=self.pos)
        Collision_objects[self.pos[0]] = self
        Collision_objects[self.pos[0]+FUEL_ROD_SIZE] = self
    def draw(self,screen):
        self.xenon_field.draw(screen=screen)
    def debug_draw(self,screen:pg.surface.Surface):
        pg.draw.line(screen,(0,255,0),(self.pos[0],0),(self.pos[0],2000))
        pg.draw.line(screen,(0,255,0),(self.pos[0]+FUEL_ROD_SIZE,0),(self.pos[0]+FUEL_ROD_SIZE,2000))
    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray)->bool:
        q = pos.copy()
        pos -= self.pos
        cord = (int(pos[0]//XENON_CELL_SIZE),int(pos[1]//XENON_CELL_SIZE))
        if(random()<=self.xenon_field.xenon_field[cord]/255):
            return True
        if(random() > 2**-(lenght/self.k)):
            for i in range(-1,2,2):
                NeutronRay(self,ray.pitc+(math.pi/3)*i,q,True)
            self.xenon_field.xenon_field[cord] = math.fabs(self.xenon_field.xenon_field[cord]-5)
            return True
        return False 

class XsenonField():
    def __init__(self, pos:tuple):
        self.xenon_field = np.zeros((FUEL_ROD_SIZE//XENON_CELL_SIZE, zone[1]//XENON_CELL_SIZE+1))
        self.pos = pos
        drawList.append(self)
        self.sum_matrix = np.full_like(self.xenon_field,1/CLOCK_TIME)
    
    def sum(self):
        self.xenon_field += self.sum_matrix
        self.xenon_field[np.where(self.xenon_field>255)]=255
    
    def randgen(self):
        _randgen(self.xenon_field)
    def debug_draw(self,screen:pg.surface.Surface):
        pass
    def draw(self, screen:pg.surface.Surface):
        for ix, iy in np.ndindex(self.xenon_field.shape):
            pg.draw.rect(screen, ((100,200,self.xenon_field[ix,iy])),pg.Rect((self.pos[0]+XENON_CELL_SIZE*ix,self.pos[1]+XENON_CELL_SIZE*iy),(XENON_CELL_SIZE,XENON_CELL_SIZE)))    
    

# @njit(parallel=True)
def _randgen(array):
    for iy, ix in np.ndindex(array.shape):
        array[iy,ix] = randint(0,255)


class WaterChannel():
    
    def __init__(self,pos):
        Collision_objects[pos[0]-WATER_CHANNEL_RADIUS]=self
        Collision_objects[pos[0]+WATER_CHANNEL_RADIUS+FUEL_ROD_SIZE] = self
        self.lvl = 1
        self.pos = pos
        drawList.append(self)
    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray)->bool:
        return wf.interact(ray,lenght,pos)
    def draw(self, screen:pg.surface.Surface):
        s = pg.Surface((WATER_CHANNEL_RADIUS*2+FUEL_ROD_SIZE, zone[1]))
        s.set_alpha(128)
        s.fill((0,0,255))
        screen.blit(s,(self.pos[0]-WATER_CHANNEL_RADIUS,self.pos[1]))
    def debug_draw(self,screen:pg.surface.Surface):
        pg.draw.line(screen,(0,0,255),(self.pos[0]-WATER_CHANNEL_RADIUS,0),(self.pos[0]-WATER_CHANNEL_RADIUS,2000))
        pg.draw.line(screen,(0,0,255),(self.pos[0]+WATER_CHANNEL_RADIUS+FUEL_ROD_SIZE,0),(self.pos[0]+WATER_CHANNEL_RADIUS+FUEL_ROD_SIZE,2000))

class Graphite():
    def __init__(self, k:int):
        self.k = k
        self.lvl = 2
    def interact(self, ray:NeutronRay,lenght, pos:np.ndarray)->bool:
        if(random() > 2**-(lenght/self.k)):
            ray.isFast=False
        return False
@dataclass
class ControlRod(Rod):
    hight:float
    def __post_init__(self):
        super().__post_init__()
        self.lvl = 0
        Collision_objects[self.pos[0]] = self
        Collision_objects[self.pos[0]+FUEL_ROD_SIZE] = self
    def draw(self,screen):
        pg.draw.rect(screen,(100,100,100),pg.Rect((self.pos[0],self.pos[1]),(FUEL_ROD_SIZE,int(zone[1]*(1-self.hight)))))
    def debug_draw(self,screen):
        pg.draw.line(screen,(200,255,200),(self.pos[0],0),(self.pos[0],2000))
        pg.draw.line(screen,(200,255,200),(self.pos[0]+FUEL_ROD_SIZE,0),(self.pos[0]+FUEL_ROD_SIZE,2000))
    def interact(self, ray:NeutronRay, lenght, pos:np.ndarray)->bool:
        if(random()<0.95):
            return True
        return False




origin = (100,150)
size = (1043,531)

wf = WaterField(32,64)
g = Graphite(600)

frods = []
crods = [] 

#генерируем стержни
interspace = math.ceil((zone[0]-FUEL_ROD_SIZE*ROD_COUNT)/(ROD_COUNT+1))
for i in range(ROD_COUNT):
    frods.append(FuelRod((origin[0]+i*(FUEL_ROD_SIZE+interspace)+interspace,origin[1]+10),100))
for i in range(ROD_COUNT-1):
    crods.append(ControlRod((origin[0]+i*(FUEL_ROD_SIZE+interspace)+interspace+(interspace+FUEL_ROD_SIZE)/2,origin[1]+10),1,1))

# NeutronRay(g,random()*2*math.pi,np.array((600.0,400.0)),True)
for i in range(1000):
    NeutronRay(g,math.pi*0.002*i,np.array((597.0,400.0)),True)

if DEBUG:
    drawList.append(Border())

pg.init()
screen = pg.display.set_mode((1200, 800))
pg.draw.rect(screen, (0,100,100), pg.Rect(origin, size), 10)
pg.display.flip()


while True:
    pg.time.Clock().tick(1)
    start_time = time.time()
    #рисуем drawlist
    if DEBUG:
        pg.draw.rect(screen,(0,0,0),pg.Rect(origin,(size)))
    for i in drawList:
        if DEBUG:
            
            i.debug_draw(screen)
        else:
            i.draw(screen)

    for i in Neutron_list:
        i.throw(screen)
    #рисуем fps
    print(len(Neutron_list))
    screen.blit(pg.font.SysFont("monospace", 15).render(str(1/(time.time()-start_time))+'  '+str(len(Neutron_list)),True,(255,255,255),(0,0,0)),(100,100))
    pg.display.flip()
    wf.substract()
    for i in frods:
        i.xenon_field.sum()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    