from pylatex import Document, Section, Subsection
from pylatex import Package
from pylatex.utils import NoEscape

import memoria_flexion as mem
import materiales as mat

class elemento_viga():
    def __init__(self,b,h,r,material = mat.concreto_210, rebar = mat.acero_4200 ,memoria=False):
        self.b = b
        self.d = h-r
        self.h = h
        self.mat = material
        self.reb = rebar

        self.memoria = memoria

        if self.memoria:
            self.mem_datos = mem.datos(b,h,r,self.mat.fc,self.mat.beta_1,self.reb.fy)


    def cuantia_acero(self,rho):
        return rho*self.b*self.d

    def cuantia_minima(self):
        fc = self.mat.fc
        fy = self.reb.fy
        rho_min = 0.7*(fc**0.5)/fy
        As_min = self.cuantia_acero(rho_min)

        if self.memoria:
            self.mem_cuantia_min = mem.acero_minimo(rho_min,As_min)

        return rho_min, As_min

    def cuantia_maxima(self, m = 0.75):
        fc = self.mat.fc
        fy = self.reb.fy
        beta_1 = self.mat.beta_1
        rho_b = 0.85*fc*beta_1/fy*6000/(6000+fy)
        rho_max = m*rho_b
        As_max = self.cuantia_acero(rho_max)

        if self.memoria:
            self.mem_cuantia_max = mem.acero_maximo(rho_b,As_max)

        return rho_b, rho_max, As_max


        
    def cuantia_flexion(self, Mu, phi=0.9):
            b = self.b
            d = self.d
            fc = self.mat.fc
            fy = self.reb.fy
            R_n = Mu*10**5/(phi*b*d**2)
            rho_dis = 0.85*fc/fy*(1-(1-2*R_n/(0.85*fc))**0.5)
            As_dis = self.cuantia_acero(rho_dis)

            if self.memoria:
                self.mem_cuantia_dis = mem.acero_dis(Mu,R_n,rho_dis,As_dis)

            return R_n, rho_dis, As_dis

    def diseño_corte(self,Vu,barra_acero=mat.b_1_2,barra_estribo=mat.b_3_8,sistema_dual=1,phi=0.85):
        b = self.b
        d = self.d
        fc = self.mat.fc
        fy = self.reb.fy
        #corte maximo
        V_max = phi*2.1*fc**0.5*b*d/1000
        #corte del concreto
        Vc = phi*0.53*fc**0.5*b*d/1000
        #corte del acero/ espaciamiento
        if Vu > Vc:
            Vs = Vu-Vc
            A_estribo = barra_estribo.A_b
            S_v = phi*A_estribo*fy*d/(Vs*1000)
        else:
            Vs = 0
            S_v =0
        
        #espaciamiento maximo
        Vp = 1.1*phi*fc**0.5*b*d/1000
        if Vs > Vp:
            S_max = [d/4,30]
        else:
            S_max = [d/2,60]
        #zona de confinamiento
        Lo = 2*self.h
        d_barra = barra_acero.d_b
        d_estribo = barra_estribo.d_b
        if sistema_dual == 1:
            So = [d/10,10*d_barra,24*d_estribo,30]
        elif sistema_dual == 2:
            So = [d/10,8*d_barra,24*d_estribo,30]
        else:
            print('Elegir sistema dual 1 o 2')

        n = int(input('Cantidad de espaciamientos'))
        espaciamiento = ((1,5),)
        for i in range(n):
            m = input(f'Nro de estribos {i+1}')
            e = float(input(f'Espaciamiento (cm) {i+1}'))
            if m != "R":
                m = int(m)
            espaciamiento += ((m,e),)

        if self.memoria:
            self.mem_corte = mem.corte(Vu,V_max,Vc,Vs,barra_estribo.name,barra_estribo.A_b,S_v,Vp,S_max,Lo,So,espaciamiento)

        return V_max, Vc, Vs, S_v, Vp, S_max, Lo, So


    def crear_memoria(self):
        self.doc = Document()
        self.doc.packages.append(Package('amssymb'))


    def memoria_flexion(self):
        doc = self.doc
        with doc.create(Section("Análisis de la Viga")):
            with doc.create(Subsection('Datos')):
                doc.append(NoEscape(self.mem_datos))
            with doc.create(Subsection('Acero mínimo')):
                doc.append(NoEscape(self.mem_cuantia_min))
            with doc.create(Subsection('Acero máximo')):
                doc.append(NoEscape(self.mem_cuantia_max))
            with doc.create(Subsection('Diseño por flexión')):
                doc.append(NoEscape(self.mem_cuantia_dis))

    def memoria_corte(self):
        doc = self.doc
        with doc.create(Section("Diseño por Corte")):
            doc.append(NoEscape(self.mem_corte))


    def generar_memoria(self):
        doc =self.doc
        doc.generate_pdf('Flexion',clean_tex=False)