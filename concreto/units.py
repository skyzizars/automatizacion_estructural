import numpy as np
import math



class Unit():
    def __init__(self,value,unit):
        self.value = value
        self.unit = unit
    
    def conv_to(self,u_conv):
        unit = self.unit
        units = self.units
        f_conv = units[unit]/units[u_conv]
        self.value = self.value*f_conv
        
class Force(Unit):
    def __init__(self,value,unit):
        self.units = {'N'   : 1,
                      'kgf' : 9.81,
                      'tonf': 9.81*1000}
        super().__init__(value,unit)

class Long(Unit):
    def __init__(self,value,unit):
        self.units = {'m'   : 1,
                      'cm' : 1/100,
                      'pulg': 2.54/100}
        super().__init__(value,unit)

class Stress(Unit):
    def __init__(self,value,unit):
        self.units = {'Pa'   : 1,
                      'MPa' : 10**6,
                      'kgf/cm2': 9.81*10**4,
                      'kgf/cm': 9.81}
        super().__init__(value,unit)
        
class Rebar():
    def __init__(self):
        self.d_3 = Long(3/4,'pulg')
        self.d_4 = Long(1/2,'pulg')
        self. d_5 = Long(5/8,'pulg')
        self.d_6 = Long(3/4,'pulg')
        self.d_8 = Long(1,'pulg')
        
        self.A_3 = self.d_3.value ** 2 /4 * math.pi
        self.A_4 = self.d_4.value ** 2 /4 * math.pi
        self.A_5 = self.d_5.value ** 2 /4 * math.pi
        self.A_6 = self.d_6.value ** 2 /4 * math.pi
        self.A_8 = self.d_8.value ** 2 /4 * math.pi
        
if __name__ == '__main__':
    P = Force(5,'tonf')
    P.conv_to('N')