import math
from random import randint, random
import time
import numpy as np
import pygame as pg
import sys
import cv2
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt



LIFE = False
ROBOT = True
XENON_TILE = 0.01
ROD_HIGHT_COUNT = 32 #высота стрежня в клетках симуляции
HIGHT = 512
WIDGH = 1024
ROD_CELL_HIGHT = HIGHT/ROD_HIGHT_COUNT
ROD_SIZE = 10
DEBUG=False
origin = np.array((150,200))
ROD_COUNT = 16
CLOCK_TIME = 10
ROD_SPACE = int((1024-ROD_SIZE*ROD_COUNT)/(ROD_COUNT+1)) #расстояние между стрежнями
control_hight = 0.1
WATER_CELL_SIZE = 32

Uk = 40
Wk = 200

drawList = []


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
        self.X.resize(size,refcheck=False)
        self.Y.resize(size,refcheck=False)
        self.k.resize(size,refcheck=False)
        self.Alpha.resize(size,refcheck=False)
        self.Alpha[size-1] = angle
        self.Vy.resize(size,refcheck=False)
        self.Y[size-1] = y
        self.X[size-1] = x
        self.k = ROD_SPACE/np.cos(self.Alpha)
        self.Vy[size-1] = math.sin(angle)*math.fabs(self.k[size-1])/(HIGHT/ROD_HIGHT_COUNT)
        np.vectorize(self.add)

    def raycast(self, rods:np.ndarray, water:np.ndarray):
        
        self.start_pos =  np.vstack([self.X, self.Y])
        self.X+=(-1+2*(self.k>0))
        to_delete = np.where(self.X>ROD_COUNT-1)
        to_delete +=  np.where(self.X<0)
        self.Y+=self.Vy
        to_delete += np.where((self.Y+self.start_pos[1])/(2*ROD_HIGHT_COUNT)<control_hight)
        to_delete += np.where(self.Y>ROD_HIGHT_COUNT)
        to_delete += np.where(self.Y<0)
        self.delete(np.concatenate(to_delete))

        randA = np.random.sample(self.X.size)
        # to_water = np.where(2**(-(np.abs(self.k))/Wk)<randA)
        # randNum = random()
        # x_ = np.floor(((self.X[to_water]-self.start_pos[0,to_water])*randNum+self.start_pos[0,to_water])*(ROD_SPACE+ROD_SIZE)//WATER_CELL_SIZE).astype(int)
        # y_ = np.floor(((self.Y[to_water]-self.start_pos[1,to_water])*randNum+self.start_pos[1,to_water])*ROD_CELL_HIGHT//WATER_CELL_SIZE).astype(int)
        # water[x_,y_]+=1
        # self.delete(to_water)
        randA.resize(self.X.size,refcheck=False)
        to_rod = np.where(2**(-(np.abs(self.k))/Uk)<randA)
        reactedRods = rods[np.floor(self.X[to_rod]).astype(int),np.floor(self.Y[to_rod]).astype(int)]
        randA.resize(reactedRods.size, refcheck=False)
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
        self.k.resize(size,refcheck=False)
        self.Vy.resize(size,refcheck=False)
        self.k.resize(size,refcheck=False)
        self.Alpha += (np.random.sample(self.X.size)-0.5)*math.pi
        self.k = ROD_SPACE/np.cos(self.Alpha)
        self.Vy = np.sin(self.Alpha)*np.abs(self.k)/(HIGHT/ROD_HIGHT_COUNT)
        self.start_pos= self.start_pos.transpose()


    def draw(self):
        for i in range(min(self.start_pos.shape[0],10000)):
            pg.draw.line(screen,(255,255,255),
                         ((self.start_pos[i][0]+1)*(ROD_SPACE+ROD_SIZE)+origin[0],
                          self.start_pos[i][1]*ROD_CELL_HIGHT+origin[1]),
                         ((self.X[i]+1)*(ROD_SPACE+ROD_SIZE)+origin[0]
                          ,self.Y[i]*ROD_CELL_HIGHT+origin[1]))
            pg.draw.circle(screen,(255,0,0),((self.X[i]+1)*(ROD_SPACE+ROD_SIZE)+origin[0]
                          ,self.Y[i]*ROD_CELL_HIGHT+origin[1]),3)

    def tick(self, a, b):
        self.raycast(a.XenonField, b)
        self.draw()
    def PIL_tick(self, a, b, c:ImageDraw.ImageDraw):
        self.raycast(a.XenonField, b)
        self.PIL_draw(c)
    
    def PIL_draw(self, draw:ImageDraw.ImageDraw):
        for i in range(min(self.start_pos.shape[0],1000)):
            draw.line([((self.start_pos[i][0]+1)*(ROD_SPACE+ROD_SIZE),
                          self.start_pos[i][1]*ROD_CELL_HIGHT),
                         ((self.X[i]+1)*(ROD_SPACE+ROD_SIZE)
                          ,self.Y[i]*ROD_CELL_HIGHT)],fill=(255,255,255),width=1)
            draw.circle(((self.X[i]+1)*(ROD_SPACE+ROD_SIZE)
                          ,self.Y[i]*ROD_CELL_HIGHT),3,fill=(255,0,0))
    
    def delete(self,to_delete):
        self.X = np.delete(self.X,to_delete)
        self.Y = np.delete(self.Y,to_delete)
        self.k = np.delete(self.k,to_delete)
        self.Vy = np.delete(self.Vy,to_delete)
        self.Alpha = np.delete(self.Alpha, to_delete)
        self.start_pos = np.delete(self.start_pos.transpose(),to_delete,0).transpose()


    
class Urod():
    def __init__(self):
        self.XenonField:np.ndarray = np.full((ROD_COUNT,ROD_HIGHT_COUNT),0.1)
        drawList.append(self)
    def tick(self):
        self.XenonField+=XENON_TILE
        if random()<0.15:
            Nsys.add(randint(0,14),randint(0,14),random()*2*math.pi)
    def draw(self,screen:pg.surface.Surface):
        for ix, iy in np.ndindex(self.XenonField.shape):
            xcord = origin[0]+ix*ROD_SIZE+ix*ROD_SPACE+ROD_SPACE
            bColor = max(0,min(self.XenonField[ix,iy],255))
            pg.draw.rect(screen,(0,200,bColor),pg.Rect(xcord,origin[1]+iy*(int(ROD_CELL_HIGHT)),ROD_SIZE,int(ROD_CELL_HIGHT)))
    
    def draw_PIL(self, draw:ImageDraw.ImageDraw):
        for ix, iy in np.ndindex(self.XenonField.shape):
            xcord = ix*ROD_SIZE+ix*ROD_SPACE+ROD_SPACE
            bColor = int(max(0,min(self.XenonField[ix,iy]*255,255)))
            xy = (xcord,origin[1]+iy*(int(ROD_CELL_HIGHT)))
            draw.rectangle((xy,(xy[0]+ROD_SIZE,xy[1]+int(ROD_CELL_HIGHT))),(0,200,bColor))


class ControlRod():
    def draw_PIL(self, draw:ImageDraw.ImageDraw):
        for i in range(ROD_COUNT-1):
            xcord = i*(ROD_SPACE+ROD_SIZE)+1.5*ROD_SPACE+0.5*ROD_SIZE
            draw.rectangle((xcord, 0,ROD_SIZE+xcord, HIGHT*control_hight),(50,50,50))
    def draw(self, screen):
        for i in range(ROD_COUNT-1):
            xcord = i*(ROD_SPACE+ROD_SIZE)+1.5*ROD_SPACE+0.5*ROD_SIZE+origin[0]
            pg.draw.rect(screen, (50,50,50), pg.Rect(xcord, origin[1], ROD_SIZE, HIGHT*control_hight))

class WaterFiled():
    def __init__(self):
        self.field = np.ones((WIDGH//WATER_CELL_SIZE,HIGHT//WATER_CELL_SIZE))*20
    def tick(self):
        self.field *= 0.99 
    def draw(self, screen):
        for ix, iy in np.ndindex(self.field.shape):
            color = min(self.field[ix,iy],255)
            pg.draw.rect(screen, (color, color, 200), pg.Rect(ix*WATER_CELL_SIZE+origin[0]+10,iy*WATER_CELL_SIZE+origin[1]+10,WATER_CELL_SIZE,WATER_CELL_SIZE))
    def draw_PIL(self, draw:ImageDraw.ImageDraw):
        for ix, iy in np.ndindex(self.field.shape):
            color = int(min(self.field[ix,iy],255))
            x = ix*WATER_CELL_SIZE
            y = iy*WATER_CELL_SIZE
            draw.rectangle((x,y,x+WATER_CELL_SIZE,y+WATER_CELL_SIZE),(color, color, 200))

class Robot():
    def __init__(self):
        self.down_timer = 10
        self.activity:float
        self.prev_count:int = 1
        self.sum:int = 0
        self.target = 20_000
    def PID(self, error, a, b, y):
        return a*error + b*self.sum + y*(self.activity-1)
    def tick(self, ns:NeutronSystem, hight):
        count_n = ns.X.size
        self.sum += self.target - count_n
        self.activity = count_n/self.prev_count
        if self.down_timer == 0:
            hight -= self.PID(self.target - count_n, 0.0000003, 0.00000000001, -0.1)
        else:
            self.down_timer-=1
        # if count_n < 1500:
        #     hight = 0
        self.prev_count = max(count_n,1)
        return min(max(hight,0),1)
        

origin = (100,10)

wf = WaterFiled()
drawList.append(wf)
Nsys = NeutronSystem()
rods = Urod()
drawList.append(ControlRod())
rbt = Robot()
print("adding neutrons")
for i in range(1000):
    Nsys.add(randint(0,14),randint(0,14),random()*2*math.pi)
print("finish adding")


prev_count = 1
prev_k = 1
power = 1
PAUSE = True
dots = []
dots2 = []
if LIFE:
    pg.init()
    screen = pg.display.set_mode((1200, 700))
    pg.draw.rect(screen, (0,100,100), pg.Rect(origin, (1043,531)), 10)
    pg.draw.circle(screen,(255,0,0), (origin[0],origin[1]),20)
    pg.draw.circle(screen,(255,0,0), (((ROD_COUNT-1)*(ROD_SPACE+ROD_SIZE)+origin[0],
                            (ROD_HIGHT_COUNT-1)*ROD_CELL_HIGHT+origin[1])),20)
    pg.display.flip()
    while True:
        if not PAUSE:
            pg.time.Clock().tick(10)
            start_time = time.time()
            #рисуем drawlist
            if DEBUG:
                pg.draw.rect(screen,(0,0,0),pg.Rect(origin,(1043,531)))
            pg.draw.rect(screen,(0,0,0),pg.Rect(origin[0]+10,origin[1]+10,1024,HIGHT))
            for i in drawList:
                if DEBUG:
                    
                    i.debug_draw(screen)
                else:
                    i.draw(screen)
            Nsys.tick(rods,wf.field)
            
            rods.tick()
            wf.tick()
            if ROBOT:
                control_hight = rbt.tick(Nsys,control_hight)
            #рисуем fps и прочие
            pg.draw.rect(screen,(0,0,0),pg.Rect(100,600,400,40))
            screen.blit(pg.font.SysFont("monospace", 15).render(str(1/(time.time()-start_time))+
                                                                '  '+str(Nsys.X.size),
                        True,(255,255,255),(0,0,0)),(100,600))
            screen.blit(pg.font.SysFont("monospace", 15).render(str(Nsys.X.size/(prev_count+1)),
                        True,(255,255,255),(0,0,0)),(100,620))
            screen.blit(pg.font.SysFont("monospace", 15).render(str(np.sum(wf.field)),
                        True,(255,255,255),(0,0,0)),(100,640))
            prev_k = Nsys.X.size/(prev_count+1)
            prev_count = Nsys.X.size
            dots.append(prev_count)
            pg.display.flip()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                plt.plot(dots)
                plt.yscale("log")
                plt.show()
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONUP:
                control_hight = min((pg.mouse.get_pos()[1]-origin[1])/HIGHT,1)
                PAUSE= False
else:
    counter = 1
    change_counter = 0
    s_count = 0
    c_count = 0
    fourcc = cv2.VideoWriter.fourcc(*'mp4v')
    out = cv2.VideoWriter("out.mp4",fourcc,10,(WIDGH,HIGHT))
    fig, axN = plt.subplots()
    axN.set_ylabel("колличество нейтронов")
    axN.set_yscale('log')
    ax2 = axN.twinx()
    ax2.set_ylabel("высота стержней")
    ax2.set_ylim((0,1))
    ax2.axvline(800,color='r')
    while(Nsys.X.size < 10_000_000 and counter < 1500 and Nsys.X.size > 0):
        if Nsys.X.size < 20_000:
            change_counter+=1
            if change_counter>300 and rbt.target > 8_000:
                s_count = counter
                ax2.axvline(counter,color='r')
                rbt.target = 8_000
        if counter>800 and rbt.target != 4000:
            rbt.target =4000
        img = Image.new(mode="RGB",size=(WIDGH,HIGHT))
        draw = ImageDraw.Draw(img)
        for i in drawList:
            i.draw_PIL(draw)
        dots.append(Nsys.X.size)
        dots2.append(1-control_hight)
        Nsys.PIL_tick(rods,wf.field,draw)     
        rods.tick()
        wf.tick()
        control_hight = rbt.tick(Nsys,control_hight)
        # img.show()
        out.write(cv2.cvtColor(np.array(img),cv2.COLOR_RGB2BGR))
        counter+=1
        print(counter , Nsys.X.size)
    axN.axhline(y=20_000,xmin=0,xmax=s_count/counter, color='k')
    axN.axhline(y=8_000,xmin=s_count/counter,xmax=800/counter,color='k')
    axN.axhline(y=4_000,xmin=800/counter,xmax=1,color='k')
    out.release()
    axN.plot(dots,color='b',label="нейтроны")
    ax2.plot(dots2,color='g',label="высота стержней управления")
    fig.legend()
    fig.set_size_inches((15*(counter/1000),10))
    fig.savefig("fig.png")
    print("готово")


    