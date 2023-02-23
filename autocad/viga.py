from pyautocad import Autocad, APoint, aDouble
import math
acad = Autocad()

class Viga():
    def __init__(self,index,desc, length,h,r):
        self.index = index
        self.desc = desc
        self.length = length
        self.h = h
        self.r=r

    def draw_beam(self,i_point):
        layer = acad.doc.Layers.Add('vigas')
        layer.color = 2
        p1 = i_point
        for i,j in enumerate(self.desc):
            if i == 0:
                if j == 0:
                    p2 = p1 + (0,self.h[i]+0.8,0)
                    acad.model.AddLine(p1,p2).Layer = layer.name
                    p3 = APoint(p1[0]+self.length[i],p1[1])
                    acad.model.AddLine(p1,p3).Layer = layer.name
                    p1 = APoint(p2[0]+self.length[i],p2[1])
                    acad.model.AddLine(p2,p1).Layer = layer.name
                    p2 = APoint(p3[0], p3[1] + .4)
                    acad.model.AddLine(p3,p2).Layer = layer.name
                    p3 = APoint(p1[0], p1[1] - .4)
                    acad.model.AddLine(p3,p1).Layer = layer.name
                    p1 = p3

                    dim = acad.model.AddDimAligned(p2-(self.length[i],0.4,0),
                            p2-(0,0.4,0),p2-(self.length[i]/2,0.5,0))
                    set_dim_style(dim,layer.name)

                else:
                    p2 = APoint(p1[0], p1[1] + self.h[i])
                    acad.model.AddLine(p1,p2).Layer = layer.name
                    p3 = APoint(p1[0]+self.length[i],p1[1])
                    acad.model.AddLine(p1,p3).Layer = layer.name
                    p1 = APoint(p2[0]+self.length[i],p2[1])
                    acad.model.AddLine(p2,p1).Layer = layer.name
                    p2 = p3

                    dim = acad.model.AddDimAligned(p2-(self.length[i],0.4,0),
                            p2-(0,0.4,0),p2-(self.length[i]/2,0.5,0))
                    set_dim_style(dim,layer.name)
            
            else:
                if j == 0:
                    p3 = APoint(p1[0], p1[1] + 0.4)
                    acad.model.AddLine(p1,p3).Layer = layer.name
                    p1 = APoint(p3[0]+self.length[i],p3[1])
                    acad.model.AddLine(p1,p3).Layer = layer.name
                    p3 = APoint(p1[0],p1[1]- 0.4)
                    acad.model.AddLine(p1,p3).Layer = layer.name
                    p1 =p3
                    p3 = APoint(p2[0],p2[1]-.4)
                    acad.model.AddLine(p2,p3).Layer = layer.name
                    p2 = APoint(p3[0]+self.length[i],p3[1])
                    acad.model.AddLine(p2,p3).Layer = layer.name
                    p3 = APoint(p2[0],p2[1]+.4)
                    acad.model.AddLine(p2,p3).Layer = layer.name
                    p2 = p3

                    dim = acad.model.AddDimAligned(p2-(self.length[i],0.4,0),
                            p2-(0,0.4,0),p2-(self.length[i]/2,0.5,0))
                    set_dim_style(dim,layer.name)
                else:
                    p3 = APoint(p1[0]+self.length[i],p1[1])
                    acad.model.AddLine(p1,p3).Layer = layer.name
                    p1 = p3
                    p3 = APoint(p2[0]+self.length[i],p2[1])
                    acad.model.AddLine(p3,p2).Layer = layer.name
                    p2 = p3

                    dim = acad.model.AddDimAligned(p2-(self.length[i],0.4,0),
                            p2-(0,0.4,0),p2-(self.length[i]/2,0.5,0))
                    set_dim_style(dim,layer.name)
        
        acad.model.AddLine(p1,p2).Layer = layer.name
        p1 = APoint(p1[0]-sum(self.length),p1[1]-0.04)
        p2 = APoint(p2[0]-sum(self.length),p2[1]+0.04)
        return (p1,p2)

    def draw_stirrup(self,p1,p2):
        layer = acad.doc.Layers.Add('estribos')
        layer.color = 6
        layer.Lineweight = 40
        for i,j in enumerate(self.desc):
            if j == 0:
                p1 = APoint(p1[0]+self.length[i],p1[1])
                p2 = APoint(p2[0]+self.length[i],p2[1])
                
            else:
                p3 = APoint(p1[0]+self.length[i],p1[1])
                p4 = APoint(p2[0]+self.length[i],p2[1])
                p5, p6 = p3, p4
                distance = self.length[i]

                acad.model.Addtext(f'EST.{2}',
                    p2+(0.05,-0.3,0),0.07).Layer = layer.name
                acad.model.Addtext(f'EST.{2}',
                    p2+(distance-0.3,-0.3,0),0.07).Layer = layer.name
 
                for m in stirrup:
                    if m[0]=='r':
                        n_stir = math.ceil(distance/m[1])
                        d_stir = distance/n_stir
                        
                        for k in range(1,n_stir):
                            p1 = APoint(p1[0]+d_stir,p1[1])
                            p2 = APoint(p2[0]+d_stir,p2[1])
                            acad.model.AddLine(p1,p2).Layer = layer.name

                    else:
                        if m[0]*m[1]*2 > distance:
                            n_stir = math.ceil(distance/m[1])
                            d_stir = distance/n_stir
                            for k in range(1,n_stir):
                                p1 = APoint(p1[0]+d_stir,p1[1])
                                p2 = APoint(p2[0]+d_stir,p2[1])
                                acad.model.AddLine(p1,p2).Layer = layer.name
                            break

                        else:
                            n_stir = m[0]
                            d_stir = m[1]
                            for k in range(1,n_stir+1):
                                p1 = APoint(p1[0]+d_stir,p1[1])
                                p2 = APoint(p2[0]+d_stir,p2[1])
                                acad.model.AddLine(p1,p2).Layer = layer.name
                                p5 = APoint(p5[0]-d_stir,p5[1])
                                p6 = APoint(p6[0]-d_stir,p6[1])
                                acad.model.AddLine(p5,p6).Layer = layer.name

                            distance -= n_stir*d_stir*2
                p1 = p3
                p2 = p4


    def draw_ref(self,p1,p2):
        layer = acad.doc.Layers.Add('refuerzo')
        layer.color = 1
        layer.Lineweight = 50

        if ref[0] == 'a':
            p3 = p1 + (self.r,0,0)
            p4 = p2 + (self.r,0,0)
            acad.model.AddLine(p3,p3+(0,-0.10,0)).Layer = layer.name
            acad.model.AddLine(p4,p4+(0,0.10,0)).Layer = layer.name
            p5 = p3 + (sum(self.length)-2*self.r,0,0)
            p6 = p4 + (sum(self.length)-2*self.r,0,0)
            acad.model.AddLine(p3,p5).Layer = layer.name
            acad.model.AddLine(p4,p6).Layer = layer.name
            acad.model.AddLine(p5,p5+(0,-0.10,0)).Layer = layer.name
            acad.model.AddLine(p6,p6+(0,0.10,0)).Layer = layer.name


        

    def add_text(self,p2,h_text):
        layer = acad.doc.Layers.Add('cotas')
        layer.color = 6
        acad.model.Addtext(f'VIGA  V.{self.index}',
                    p2+(sum(self.length)-h_text*5,-0.8-h_text,0),h_text).Layer = layer.name
        acad.model.Addtext('ESC: 1/50',
                    p2+(sum(self.length)-h_text*3,-0.8-2*h_text,0),h_text-0.05).Layer = layer.name

def set_dim_style(dim,l_name):
    dim.TextHeight = 0.05
    dim.PrimaryUnitsPrecision = 2
    dim.ArrowheadSize = 0.05
    dim.ExtensionLineExtend = 0.05
    dim.TextInside = 1
    dim.Layer = l_name

if __name__ == '__main__':
    index = '1'
    desc = (0,1)*3+(0,)
    length = (0.50,3.30,3.73,2.16,0.5,5.23,4.21)
    h = (0.50,)*3+(0.50,)
    r = 0.04
    viga_1 = Viga(index,desc,length,h,r)
    p1,p2 = viga_1.draw_beam(APoint(1,1))
    stirrup = ((1,0.05),(10,0.10),('r',0.2))
    viga_1.draw_stirrup(p1,p2)
    ref = ('a',(3,('1/2')))
    viga_1.draw_ref(p1,p2)
    viga_1.add_text(p2,0.1)