from dataclasses import dataclass
import numpy as np

@dataclass
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
    yaw:float
    isFast:bool=False
    origin:np.array
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