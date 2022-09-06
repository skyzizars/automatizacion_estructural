from cmath import sqrt

class barra_acero():
    def __init__(self,name,d_b,A_b):
        self.name = name
        self.d_b = d_b
        self.A_b = A_b

# barras de acero
b_3_8 = barra_acero('3/8',3/8*2.54,0.71)
b_1_2 = barra_acero('1/2',1/2*2.54,1.29)
b_5_8 = barra_acero('5/8',5/8*2.54,1.99)
b_3_4 = barra_acero('3/4',3/4*2.54,2.84)
b_1 = barra_acero('1',2.54,5.10)

class acero():
    def __init__(self,fy,E,def_u):
        self.fy = fy
        self.E = E
        self.def_u = def_u

#acero fy=4200
acero_4200 = acero(4200,6*10^6,0.003)

class concreto():
    def __init__(self,fc,def_u):
        self.fc = fc
        self.E = 15000*sqrt(fc)
        self.def_u = def_u
        if fc > 280:
            self.beta_1 = (0.85-0.05*(fc-280)/70)
        else:
            self.beta_1 = 0.85

#concreto fc=210
concreto_210 = concreto(210,0.002)