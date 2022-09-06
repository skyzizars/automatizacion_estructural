import numpy as np

import materiales as mat


class elemento_columna():
    def __init__(self,b,h,r,material=mat.concreto_210,rebar=mat.acero_4200):
        self.b = b
        self.h = h
        self.r = r
        self.mat = material
        self.rebar = rebar

    def matriz_acero(self, matriz):
        self.matriz = matriz
        self.m = len(matriz)
        self.n = len(matriz[0])
        