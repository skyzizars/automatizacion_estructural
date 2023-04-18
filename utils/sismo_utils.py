import sys
import os
sys.path.append(os.getcwd())
import pandas as pd
from IPython.display import display
from utils import etabs_utils as etb
import matplotlib.pyplot as plt
import numpy as np


#Programado para etabs 2019
   

#Funciones básicas
class Sismo_e30():
    def __init__(self): 
        self.data = self.Data()
        self.loads = self.Loads()
        self.tables = self.Tables()
        
    class Loads():
        def __init__(self):
            pass
        def set_seism_loads(self,seism_loads):
            self.seism_loads = seism_loads

    class Data():
        def __init__(self):
            pass

        def factor_zona(self,zona):
            table = pd.DataFrame([[4, 0.45], [3, 0.35], [2, 0.25], [1, 0.1]], columns=['Zona', 'Z'])
            self.zona = int(zona)
            self.Z = float(table.query('Zona == @zona')['Z'])

        def factor_suelo(self,suelo,zona=None):
            table = pd.DataFrame(
                [[4, 0.8, 1, 1.05, 1.1],
                [3, 0.8, 1, 1.15, 1.20],
                [2, 0.80, 1, 1.2, 1.4],
                [1, 0.8, 1, 1.6, 2]],
                columns=['Z', 'S0', 'S1', 'S2', 'S3'])
            if zona:
                self.factor_zona(zona)
            zona = self.zona
            self.suelo = suelo
            self.S = float(table.query('Z == @zona')[suelo])
        
        def periodos_suelo(self,suelo=None,zona=None):
            table = pd.DataFrame(
                [[0.3, 0.4, 0.6, 1],
                [3, 2.5, 2, 1.6]],
                columns=['S0', 'S1', 'S2', 'S3'],
                index=['Tp', 'Tl'])
            if suelo:
                self.factor_suelo(suelo,zona)
            suelo = self.suelo
            self.Tp = table[suelo].loc['Tp']
            self.Tl = table[suelo].loc['Tl']

        def sist_estructural(self,sistema_x,sistema_y):
            table = pd.DataFrame(
                [['Pórticos Especiales de Acero Resistentes a Momentos', 8, 0.01],
                ['Pórticos Intermedios de Acero Resistentes a Momentos', 5, 0.01],
                ['Pórticos Ordinarios de Acero Resistentes a Momentos', 4, 0.01],
                ['Pórticos Especiales de Acero Concénticamente Arriostrados', 7, 0.01],
                ['Pórticos Ordinarios de Acero Concénticamente Arriostrados', 4, 0.1],
                ['Pórticos Acero Excéntricamente Arriostrados', 8, 0.01],
                ['Pórticos de Concreto Armado', 8, 0.007],
                ['Dual de Concreto Armado', 7, 0.007],
                ['De Muros Estructurales de Concreto Armado', 6, 0.007],
                ['Muros de Ductilidad Limita de Concreto Armado', 4, 0.005],
                ['Albañilería Armada o Confinada', 3, 0.005],
                ['Madera', 7, 0.01]],
                columns=['sistema', 'R_0', 'max_drift'])
            self.sistema_x = sistema_x
            self.sistema_y = sistema_y
            self.Rox = float(table.query('sistema == @sistema_x')['R_0'])
            self.Roy = float(table.query('sistema == @sistema_y')['R_0'])
            self.max_drift_x = float(table.query('sistema == @sistema_x')['max_drift'])
            self.max_drift_y = float(table.query('sistema == @sistema_y')['max_drift'])

        def categoria_edificacion(self,categoria):
            table = pd.DataFrame(
                [['A1 aislado', 1],
                ['A1 no aislado', 1.5],
                ['A2', 1.5],
                ['B', 1.3],
                ['C', 1]],
                columns=['categoria', 'U']
            )
            self.categoria = categoria
            self.U = float(table.query('categoria == @categoria')['U'])


        def set_pisos(self,n_pisos,n_azoteas,n_sotanos):
            self.n_pisos, self.n_azoteas, self.n_sotanos = int(n_pisos),int(n_azoteas),int(n_sotanos)

        def irreg_planta(self,i_torsional=False,i_torsional_e=False,i_esquinas_entrantes=False,
                        i_discontinuidad_diafragma=False,i_sistemas_no_paralelos=False):
            self.i_torsional,self.i_torsional_e,self.i_esquinas_entrantes = i_torsional,i_torsional_e,i_esquinas_entrantes
            self.i_discontinuidad_diafragma,self.i_sistemas_no_paralelos = i_discontinuidad_diafragma,i_sistemas_no_paralelos
            self.Ip = 1
            if i_torsional:
                self.Ip = min(self.Ip,0.75)
            elif i_torsional_e:
                self.Ip = min(self.Ip,0.60)
            elif i_esquinas_entrantes:
                self.Ip = min(self.Ip,0.90)
            elif i_discontinuidad_diafragma:
                self.Ip = min(self.Ip,0.85)
            elif i_sistemas_no_paralelos:
                self.Ip = min(self.Ip,0.90)

        def irreg_altura(self,i_piso_blando=False,i_piso_blando_e=False,i_masa=False,i_vertical=False,
                        i_discontinuidad_vertical=False,i_discontinuidad_vertical_e=False):
            self.i_piso_blando,self.i_piso_blando_e,self.i_masa,self.i_vertical = i_piso_blando,i_piso_blando_e,i_masa,i_vertical
            self.i_discontinuidad_vertical,self.i_discontinuidad_vertical_e = i_discontinuidad_vertical,i_discontinuidad_vertical_e
            self.Ia = 1
            if i_piso_blando:
                self.Ia = min(self.Ia,0.75)
            elif i_piso_blando_e:
                self.Ia = min(self.Ia,0.50)
            elif i_masa:
                self.Ia = min(self.Ia,0.90)
            elif i_vertical:
                self.Ia = min(self.Ia,0.90)
            elif i_discontinuidad_vertical:
                self.Ia = min(self.Ia,0.80)
            elif i_discontinuidad_vertical_e:
                self.Ia = min(self.Ia,0.60)

        def factor_R(self):
            self.Rx = self.Rox * self.Ia * self.Ip
            self.Ry = self.Roy * self.Ia * self.Ip
            self.is_regular = self.Ip == 1 and self.Ia == 1

        def show_params(self):
            print('''
\033[1m Parámetros de sitio:\033[0m
Factor de zona: 
    Z={:.2f}
Factor de Importancia: 
    U={:.2f}
Factor de Suelo: 
    S={:.2f}
Periodos del Suelo: 
    Tp={:.2f}
    Tl={:.2f}
Factor Básico de Reducción:
    Rox={:.2f}
    Roy={:.2f}
Irregularidad en planta:
    Ip={:.2f}
Irregularidad en altura:
    Ia={:.2f}
Factor de Reducción:
    Rx={:.2f}
    Ry={:.2f}
'''.format(self.Z, self.U, self.S, self.Tp, self.Tl, self.Rox, self.Roy, self.Ip, self.Ia, self.Rx, self.Ry))
            
        
    class Tables():
        def __init__(self):
            pass

    def set_base_story(self,base_story):
        self.base_story = base_story
        
    #Sismo Estático
    def ana_modal(self,SapModel,report=False):
        '''Devuelve datos del analisis modal, y los periodos fundamentales
        para cada dirección de análisis si la masa participativa es mayor al
        90%. Revise 29.1.2 NTE 030 2020
    
        Parámetros
        ----------
        SapModel: objeto propio del ETABS
        
        Returns
        -------
        mensaje: ----Aumentar grados de libertad, si MP_y o MP_x<0.9
        modal=tabla "Modal Participating Mass Ratios"
        T_x=Periodo fundamental en la dirección x
        T_y=Periodo fundamental en la dirección y
        '''
        _,modal = etb.get_table(SapModel,'Modal Participating Mass Ratios')
        modal = modal[['Mode','Period','UX','UY','RZ','SumUX','SumUY','SumRZ']]
        modal['UX']=modal.UX.astype(float)
        modal['UY']=modal.UY.astype(float)
        #Masas Participativas 
        MP_x = float(max(modal.SumUX))

        MP_y = float(max(modal.SumUY))

        #Periodos Fundamentales
        mode_x = modal[modal.UX == max(modal.UX)].index
        Tx = float(modal.Period[mode_x[0]])
        Ux = float(modal.UX[mode_x[0]])

        mode_y = modal[modal.UY == max(modal.UY)].index
        Ty = float(modal.Period[mode_y[0]])
        Uy = float(modal.UY[mode_y[0]])

        self.tables.modal = modal
        self.data.Tx = Tx
        self.data.Ty = Ty
        
        #Reporte
        if report:
            print("\nAnálisis Modal:")
            print('Masa Participativa X: {0:.2f}'.format(MP_x))
            if MP_x<0.9:
                print('---Aumentar Grados de Libertad: {0:.2f} < 0.9'.format(MP_x))
            print('Masa Participativa Y: {0:.2f}'.format(MP_y))
            if MP_y<0.9:
                print('---Aumentar Grados de Libertad {0:.2f} < 0.9'.format(MP_y))
            print('Periodo y Masa Participativa X: Tx={0:.3f}'.format(Tx)+', Ux={0:.3f}'.format(Ux))
            print('Periodo y Masa Participativa Y: Ty={0:.3f}'.format(Ty)+', Uy={0:.3f}'.format(Uy))

            display(modal)
        
    #Cálculo del exponente de altura
    def get_k(self,T):
        """Devuelve el exponente relacionado con el periodo (T). Revise
        28.3.2 NTE 030 2020
        
        Parámetros
        ----------
        T : Periodo fundamental de vibración de la estructura (seg)
        
        Returns
        -------
        k=1, si T<=0.5 seg.
        k=0.75+0.5*T, si T>=0.5
        k=2, si 0.75+0.5*T>2
        """
        if T < 0.5:
            return 1
        elif 0.75+0.5*T < 2:
            return 0.75+0.5*T
        else:
            return 2
        
    #Cálculo del Factor C
    def get_C(self,T):
        """Devuelve el factor de amplificacion sismica (C).Revise
        Articulo 14 NTE 030 2020
        
        Parámetros
        ----------
        T : Periodo fundamental de vibración de la estructura (seg)
        Tp: Periodo del suelo
        Tl: Periodo del suelo
        
        Returns
        -------
        C=2.5, si T<Tp
        C=2.5*Tp/T, si Tp<T<Tl
        C=2.5*(Tp*Tl/T**2), si T>Tl
        """
        if T < self.data.Tp:
            return 2.5
        elif T < self.data.Tl:
            return 2.5*self.data.Tp/T
        else:
            return 2.5*self.data.Tp*self.data.Tl/T**2
        
    def get_ZUCS_R(self,C,R):
            ZUS = self.data.Z*self.data.U*self.data.S
            if C/R>0.11:
                return C/R*ZUS
            else:
                return 0.11*ZUS
    

    def sismo_estatico(self,SapModel,report=False):
        '''Registra en un diccionario: el factor de Reduccion total R, los factores de 
        amplificacion sísmica en ambas direcciones de analisis, los exponentes de altura 
        relacionados con los periodos fundamentales en cada direccion de analisis y los 
        coeficientes de sismo estatico para cada direccion de analisis.
        
        Parámetros
        ----------
        SapModel: objeto propio del ETABS
        N: Numero de pisos
        Z: Factor de zona
        U: Factor de uso
        S: Factor de amplificacion del suelo
        Tp: Periodo del suelo para C=cte
        Tl: Periodo del suelo para desplazamientos constantes
        Ip: Factor de irregularidad en planta
        Ia: Factor de irregularidad en altura
        R_o: Coeficiente basico de reduccion

        Returns
        -------
        Imprime los valores de 
        data: Diccionario que contiene la tabla "Modal Participating Mass Ratios", k_x,
        k_y, C_x, C_y, ZUCS_Rx y ZUCS_Ry
        '''
        self.data.factor_R()
        self.ana_modal(SapModel)
        self.data.kx = self.get_k(self.data.Tx)
        self.data.ky = self.get_k(self.data.Ty)
        self.data.Cx = self.get_C(self.data.Tx)
        self.data.Cy = self.get_C(self.data.Ty)
        self.data.ZUCS_Rx = self.get_ZUCS_R(self.data.Cx,self.data.Rx)
        self.data.ZUCS_Ry = self.get_ZUCS_R(self.data.Cy,self.data.Ry)

        #Análisis Sísmico Manual
        static_seism = etb.get_table(SapModel,'Mass Summary by Story')[1][['Story','UX']]
        static_seism['UX'] = static_seism['UX'].astype(float)*9.806
        stories = etb.get_table(SapModel,'Story Definitions')[1][['Story','Height']]
        static_seism = static_seism.merge(stories,left_on='Story',right_on='Story')
        static_seism['Height'] = static_seism.loc[::-1,'Height'].astype(float).cumsum()[::-1]
        static_seism['H^kx'] = static_seism['Height']**self.data.kx
        static_seism['H^ky'] = static_seism['Height']**self.data.ky
        static_seism['PxHx'] = static_seism['H^kx'] * static_seism['UX']
        static_seism['PxHy'] = static_seism['H^ky'] * static_seism['UX']
        static_seism['ax'] = static_seism['PxHx']/sum(static_seism['PxHx'])
        static_seism['ay'] = static_seism['PxHx']/sum(static_seism['PxHy'])
        self.data.Vx = self.data.ZUCS_Rx*sum(static_seism['UX'])
        self.data.Vy = self.data.ZUCS_Ry*sum(static_seism['UX'])
        static_seism['vx'] = static_seism['ax']*self.data.Vx
        static_seism['vy'] = static_seism['ay']*self.data.Vy
        static_seism = static_seism.rename(columns={'UX':'Weight'})
        static_seism = static_seism.round({'Weight':3,'Height':2,'H^kx':2,'H^ky':2,'PxHx':3,'PxHy':3,'ax':3,'ay':3,'vx':3,'vy':3})

        self.tables.static_seism = static_seism

        if report:
            #Resumen
            print('Factor de Reduccion con Irregularidades en X: R={}'.format(self.data.Rx))
            print('Factor de Reduccion con Irregularidades en Y: R={}'.format(self.data.Ry))
            print('C en X: {0:.2f}'.format(self.data.Cx))
            print('C en Y: {0:.2f}'.format(self.data.Cy))

            print('\nCoeficiente de sismo estático X: {0:.3f}'.format(self.data.ZUCS_Rx))
            print('Coeficiente de sismo estático Y: {0:.3f}'.format(self.data.ZUCS_Ry))
            print('Exponente de altura X: {0:.2f}'.format(self.data.kx))
            print('Exponente de altura Y: {0:.2f}'.format(self.data.ky))
            print('Fuerza Cortante en X: {0:.2f}'.format(self.data.Vx))
            print('Fuerza Cortante en Y: {0:.2f}'.format(self.data.Vy))

            display(self.tables.static_seism)
            
    #Espectro Dinamico
    def dinamic_spectrum(self,report=False):
        self.data.factor_R()
        self.T = np.arange(0,4.1,0.1)
        self.Sax = np.round(np.vectorize(self.get_C)(self.T)*self.get_ZUCS_R(1,self.data.Rx),decimals=3)
        self.Say = np.round(np.vectorize(self.get_C)(self.T)*self.get_ZUCS_R(1,self.data.Ry),decimals=3)

        if report:
            y_max = max(max(self.Sax),max(self.Say))
            plt.ylim(0,y_max+0.02)
            plt.xlim(0,4)
            plt.plot(self.T,self.Sax,'r',label='X (R=%.2f)'%self.data.Rx)
            plt.plot(self.T,self.Say,'b',label='Y (R=%.2f)'%self.data.Ry)
            plt.axvline(x = self.data.Tl, color = 'g',linestyle='dotted')
            plt.text(self.data.Tp,y_max+0.005, 'Tp', fontsize=12, color='k')
            plt.text(self.data.Tl,y_max+0.005, 'Tl', fontsize=12, color='k')
            plt.axvline(x = self.data.Tp, color = 'g',linestyle='dotted')
            plt.xlabel('T (s)')
            plt.ylabel('Sa $(m/s^2)$')
            plt.grid(linestyle='dotted', linewidth=1)
            plt.legend()
            plt.show()


    #Revisión por Torsión      
    def irregularidad_torsion(self,SapModel,report=False):
        '''Registra en un DataFrame la tabla de derivas maximas de entrepiso, 
        deriva promedio y la razon de derivas maximas sobre derivas promedios

        Parámetros
        ----------
        SapModel: objeto propio del ETABS
        loads: Casos de carga
        max_drift: deriva máxima
        R: coeficiente de reduccion sismica
        is_regular: boleano, true si es regular, false si es irregular

        Returns
        -------
        table: DataFrame que contiene la tabla "Story Max Over Avg Drifts", Max Drift,
        Avg Drift y Ratio
        '''
        set_loads = [load for load in self.loads.seism_loads.values()]
        SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_loads)
        SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([])

        _ , table = etb.get_table(SapModel,'Story Max Over Avg Drifts')
        table['OutputCase'] = table.OutputCase+' '+table.StepType
        table = table[['Story','OutputCase','Direction','Max Drift','Avg Drift','Ratio']]


        stories  = etb.get_story_data(SapModel)
        table = table.merge(stories[['Story','Height']], on = 'Story')
        if self.data.is_regular:
            table['Drifts']=table['Max Drift'].apply(lambda x:float(x))/table['Height'].apply(lambda x:float(x))*0.75
        else:
            table['Drifts']=table['Max Drift'].apply(lambda x:float(x))/table['Height'].apply(lambda x:float(x))*0.85

        table['Drifts'] = table.apply((lambda row: float(row['Drifts'])*self.data.Rx if 'x' in row['OutputCase'] else float(row['Drifts'])*self.data.Ry),axis=1)

        table['Drift < Dmax/2'] = table['Drifts'] < self.data.max_drift_x/2
        tor_reg = (table['Drift < Dmax/2']) | (table['Ratio'].apply(lambda x: float(x)) < 1.3)
        table['tor_reg'] = tor_reg.apply(lambda x: 'Regular' if x else 'Irregular')

        self.tables.torsion_table = table

        if report:
            self.show_table(table)

    #Piso Blando
        
    def piso_blando(self,SapModel,report=False):
        set_loads = [load for load in self.loads.seism_loads.values()]
        SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_loads)
        SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([])

        _,data = etb.get_table(SapModel,'Diaphragm Center Of Mass Displacements')
        data['OutputCase'] = data.OutputCase+ ' ' +data.StepType.fillna('')
        data['OutputCase'] = data['OutputCase'].apply(lambda x:x.rstrip())
        data = data[['Story','OutputCase','UX','UY']]


        _,data_forces = etb.get_table(SapModel,'Story Forces')
        data_forces['OutputCase'] = data_forces.OutputCase+ ' ' +data_forces.StepType.fillna('')
        data_forces['OutputCase'] = data_forces['OutputCase'].apply(lambda x:x.rstrip())
        data_forces = data_forces[ data_forces.Location=='Top']
        data_forces = data_forces[['Story','OutputCase','VX','VY']]

        table = pd.DataFrame()

        for load in set(data_forces.OutputCase):
            load_data = data[data.OutputCase == load].reset_index(drop=True)
            UX_0 = load_data.UX.astype(float) #desplazamiento del piso
            UX_1 = UX_0.shift(-1).fillna(0) #desplazamiento del piso inferior
            UY_0 = load_data.UY.astype(float) #desplazamiento del piso
            UY_1 = UY_0.shift(-1).fillna(0) #desplazamiento del piso inferior
            load_data['ΔUX'] = UX_0 - UX_1 #desplazamiento relativo X
            load_data['ΔUY'] = UY_0 - UY_1 #desplazamieto relativo Y
            load_data = load_data.merge(data_forces)
            lat_rig_1 = abs(load_data.VX.apply(lambda x:float(x))/load_data.ΔUX.apply(lambda x:float(x))) #rigidez calculada en X
            lat_rig_2 = abs(load_data.VY.apply(lambda x:float(x))/load_data.ΔUY.apply(lambda x:float(x))) #rigidez calculada en Y
            load_data['lat_rig(k)'] = lat_rig_1 if lat_rig_1.mean() > lat_rig_2.mean() else lat_rig_2 #La rigidez en el sentido correcto será la mayor

            load_data['0.7_prev_k'] = load_data['lat_rig(k)'].shift(1).fillna(0)*0.7 #70% de la rigidez del piso superior
            
            k_3 = load_data['lat_rig(k)'].shift(3).fillna(0) #rigidez del tercer piso superior
            k_2 = load_data['lat_rig(k)'].shift(-1).shift(3).fillna(0) #rigidez del segundo piso superior
            k_1 = load_data['lat_rig(k)'].shift(-2).shift(3).fillna(0) #rigidez del piso superior
            
            load_data['0.8k_prom'] = 0.8*(k_1+k_2+k_3)/3 #80% del promedio de tres pisos superiores

            table = pd.concat([table,load_data],ignore_index=True)


        is_reg = (table['lat_rig(k)'] > table['0.7_prev_k']) & (table['lat_rig(k)'] > table['0.8k_prom'])
        table['is_reg'] = is_reg.apply(lambda x: 'Regular' if x else 'Irregular')   

        self.tables.piso_blando_table = table

        if report:
            self.show_table(table)

    # Masa

    def irregularidad_masa(self,SapModel,report=False):
        _,masa = etb.get_table(SapModel,'Mass Summary by Story')
        masa['Mass'] = masa.UX
        masa = masa[['Story','Mass']]
        
        stories = masa.Story
        sotanos = list(stories[-1-self.data.n_sotanos:])
        azoteas = list(stories[0:self.data.n_azoteas+1])
            
        def set_story(story):
            if story in sotanos:
                return 'Sotano'
            elif story in azoteas:
                return 'Azotea'
            else:
                return 'Piso'
        
        masa['story_type'] = masa.Story.apply(set_story)
        masa.Mass = masa.Mass.astype(float)
        masa['1.5 Mass'] = masa.apply(lambda x: 1.5 * x['Mass'] if x['story_type'] == 'Piso' else None,axis=1)
        masa['inf_mass'] = masa['1.5 Mass'].shift(-1).fillna(float('inf'))
        masa['sup_mass'] = masa['1.5 Mass'].shift(1).fillna(float('inf'))
        
        def is_reg(row):
            if row['story_type'] in ['Sotano','Azotea']:
                return 'Regular'
            elif (row['Mass'] < row['inf_mass']) and (row['Mass'] < row['sup_mass']):
                return 'Regular'
            else:
                return 'Irregular'
        
        masa['is_regular'] = masa.apply(is_reg, axis = 1)
        
        masa = masa[['Story','Mass','1.5 Mass','story_type','is_regular']].fillna('')
        self.tables.rev_masa_table = masa

        if report:
            display(masa)

    # Derivas
    def derivas(self,SapModel,report=False):
        import numpy as np
        self.irregularidad_torsion(SapModel)
        rev_drift = self.tables.torsion_table[['Story','OutputCase','Direction','Height','Drifts',]]
        rev_drift = rev_drift.assign(Drift_Check = (rev_drift['Drifts'] < self.data.max_drift_x).apply(lambda x: 'Cumple' if x else 'No Cumple'))
        self.tables.drift_table = rev_drift

        cases_x = list(rev_drift.query('Direction=="X"')['OutputCase'].unique())
        max_drift_x = rev_drift[rev_drift['OutputCase'].isin(cases_x)].query('Direction=="X"')['Drifts'].max()
        force_x = list(rev_drift.query('Direction=="X"').query('Drifts==@max_drift_x')['OutputCase'])[0]
        self.drifts_x = np.array(rev_drift.query('Direction=="X"').query('OutputCase==@force_x')['Drifts'])[::-1]
        self.drifts_x  = np.append([0.],self.drifts_x)
        self.heights_drifts = np.array(rev_drift.query('Direction=="X"').query('OutputCase==@force_x')['Height']).astype(float)[::-1].cumsum()
        self.heights_drifts  = np.append([0.],self.heights_drifts)

        cases_y = list(rev_drift.query('Direction=="Y"')['OutputCase'].unique())
        max_drift_y = rev_drift[rev_drift['OutputCase'].isin(cases_y)].query('Direction=="Y"')['Drifts'].max()
        force_y = list(rev_drift.query('Direction=="Y"').query('Drifts==@max_drift_y')['OutputCase'])[0]
        self.drifts_y = np.array(rev_drift.query('Direction=="Y"').query('OutputCase==@force_y')['Drifts'])[::-1]
        self.drifts_y  = np.append([0.],self.drifts_y)

        if report:
            self.show_table(rev_drift)

            plt.ylim(0,max(self.heights_drifts)*1.05)
            plt.xlim(0,max(max_drift_x,max_drift_y,self.data.max_drift_x)+0.003)
            plt.plot(self.drifts_x,self.heights_drifts,'r',label='X (R=%.2f)'%self.data.Rx)
            plt.plot(self.drifts_y,self.heights_drifts,'b',label='Y (R=%.2f)'%self.data.Ry)
            plt.scatter(self.drifts_x,self.heights_drifts,color='r',marker='x')
            plt.scatter(self.drifts_y,self.heights_drifts,color='b',marker='x')
            plt.axvline(x = self.data.max_drift_x/2, color = 'c',linestyle='dotted')
            plt.axvline(x = self.data.max_drift_x, color = 'g',linestyle='dotted')
            plt.text(self.data.max_drift_x-0.001,max(self.heights_drifts),self.data.max_drift_x , fontsize=10, color='k')
            plt.text(self.data.max_drift_x/2-0.001,max(self.heights_drifts),self.data.max_drift_x/2, fontsize=10, color='k')
            plt.xlabel('Derivas')
            plt.ylabel('h (m)')
            plt.grid(linestyle='dotted', linewidth=1)
            plt.legend()
            plt.show()


    def desplazamientos(self,SapModel,report=False):
        set_loads = [load for load in self.loads.seism_loads.values()]
        SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_loads)
        SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([])

        _ , table = etb.get_table(SapModel,'Story Max Over Avg Displacements')
        table['OutputCase'] = table.OutputCase+' '+table.StepType
        table = table[['Story','OutputCase','Direction','Maximum']]

        stories  = etb.get_story_data(SapModel)
        table = table.merge(stories[['Story','Height']], on = 'Story')
        
        self.tables.displacements = table

        table['Maximum'] = table['Maximum'].astype(float)

        cases_x = list(table.query('Direction=="X"')['OutputCase'].unique())
        max_disp_x = table[table['OutputCase'].isin(cases_x)].query('Direction=="X"')['Maximum'].max()
        force_x = list(table.query('Direction=="X"').query('Maximum==@max_disp_x')['OutputCase'])[0]
        self.disp_x = np.array(table.query('Direction=="X"').query('OutputCase==@force_x')['Maximum'])[::-1]
        self.disp_x  = np.append([0.],self.disp_x)
        self.heights = np.array(table.query('Direction=="X"').query('OutputCase==@force_x')['Height']).astype(float)[::-1].cumsum()
        self.heights  = np.append([0.],self.heights)

        cases_y = list(table.query('Direction=="Y"')['OutputCase'].unique())
        max_disp_y = table[table['OutputCase'].isin(cases_y)].query('Direction=="Y"')['Maximum'].max()
        force_y = list(table.query('Direction=="Y"').query('Maximum==@max_disp_y')['OutputCase'])[0]
        self.disp_y = np.array(table.query('Direction=="Y"').query('OutputCase==@force_y')['Maximum'])[::-1]
        self.disp_y  = np.append([0.],self.disp_y)

        if report:
            self.show_table(table)

            plt.ylim(0,max(self.heights)*1.05)
            plt.xlim(0,float(max(max_disp_x,max_disp_y))+0.003)
            plt.plot(self.disp_x,self.heights,'r',label='X (R=%.2f)'%self.data.Rx)
            plt.plot(self.disp_y,self.heights,'b',label='Y (R=%.2f)'%self.data.Ry)
            plt.scatter(self.disp_x,self.heights,color='r',marker='x')
            plt.scatter(self.disp_y,self.heights,color='b',marker='x')
            plt.xlabel('Desplazamientos (m)')
            plt.ylabel('h (m)')
            plt.grid(linestyle='dotted', linewidth=1)
            plt.legend()
            plt.show()



    # Centros de Masas y Rigideces

    def centro_masa_inercia(self,SapModel,report=False):
        try:
            _,rev_CM_CR = etb.get_table(SapModel,'Centers Of Mass And Rigidity')
            rev_CM_CR = rev_CM_CR[['Story','XCCM','XCR','YCCM','YCR']]
            rev_CM_CR['DifX'] = rev_CM_CR.XCCM.apply(lambda x: float(x)) - rev_CM_CR.XCR.apply(lambda x: float(x))
            rev_CM_CR['DifY'] = rev_CM_CR.YCCM.apply(lambda x: float(x)) - rev_CM_CR.YCR.apply(lambda x: float(x))
            self.tables.CM_CR_table = rev_CM_CR
        except:
            print('Por favor active el cálculo del centro de Rigidez')

        if report:
            display(rev_CM_CR)

    def min_shear(self,SapModel,story='Story1',report=False):
        etb.set_units(SapModel,'Ton_m_C')
        seism_loads = self.loads.seism_loads
        set_loads = [load for load in seism_loads.values()]
        SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_loads)
        SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([])
        _,base_shear=etb.get_table(SapModel,'Story Forces')
        base_shear = base_shear[base_shear['Story']==story]
        base_shear = base_shear[base_shear['Location']=='Bottom']
        base_shear['StepType'] = base_shear['StepType'].replace('','Max')
        base_shear = base_shear[base_shear['StepType']=='Max']
        base_shear = base_shear[['OutputCase','VX','VY']]
        #Extraemos los datos necesatios
        Sx = float(base_shear[base_shear['OutputCase'] == seism_loads['Sismo_EstX']]['VX'])
        SDx = float(base_shear[base_shear['OutputCase'] == seism_loads['Sismo_DinX']]['VX'])
        Sy = float(base_shear[base_shear['OutputCase'] == seism_loads['Sismo_EstY']]['VY'])
        SDy = float(base_shear[base_shear['OutputCase'] == seism_loads['Sismo_DinY']]['VY'])
        per_min = 80 if self.data.is_regular else 90 #porcentaje mínimo 80% o 90% si es regular o no
        per_x = abs(round(SDx/Sx*100,2)) #relacion entre sismo en x
        per_y = abs(round(SDy/Sy*100,2)) #relacion entre sismo en y
        fex = 1 if per_x > per_min else round(per_min/per_x,2) #relacion entre sismo en x
        fey = 1 if per_y > per_min else round(per_min/per_y,2) #relacion entre sismo en y
        table = pd.DataFrame(
            [['','X','Y'],
            ['V din (Ton)',SDx,SDy],
            ['V est (Ton)',Sx,Sy],
            ['% min',per_min,per_min],
            ['%',per_x,per_y],
            ['F.E.',fex,fey]])
        self.tables.shear_table = table

        if report:  
            display(table.style.hide(axis='index').hide(axis='columns'))
        
    def analisis_sismo(self, SapModel):
        self.sismo_estatico(SapModel)
        self.piso_blando(SapModel)
        self.irregularidad_masa(SapModel)
        #self.centro_masa_inercia(SapModel)
        self.irregularidad_torsion(SapModel)
        self.derivas(SapModel)
        self.min_shear(SapModel,self.base_story)

    def generate_memoria(self):
        from pylatex import Document, Section
        from pylatex.utils import NoEscape
        from pylatex.package import Package
        from utils import sismo_mem as smem
        seism_x = self.loads.seism_loads['Sismo_DinX'] + ' Max'
        seism_y = self.loads.seism_loads['Sismo_DinY'] + ' Max'
        zona = self.data.zona
        suelo = self.data.suelo
        categoria = self.data.categoria
        Z,U,S,Tp,Tl = self.data.Z,self.data.U,self.data.S,self.data.Tp,self.data.Tl
        Rox,Roy,Ia,Ip = self.data.Rox,self.data.Roy,self.data.Ia,self.data.Ip
        Tx,Ty,Cx,Cy = self.data.Tx,self.data.Ty,self.data.Cx,self.data.Cy
        kx,ky = self.data.kx,self.data.ky

        p_blando_x = self.tables.piso_blando_table.query('OutputCase == @seism_x')
        p_blando_y = self.tables.piso_blando_table.query('OutputCase == @seism_y')
        torsion_x = self.tables.torsion_table.query('OutputCase == @seism_x')
        torsion_y = self.tables.torsion_table.query('OutputCase == @seism_y')

        sist_x = self.data.sistema_x
        sist_y = self.data.sistema_y

        #Espectro de Respuestas
        T = self.T
        Sax = self.Sax
        Say = self.Say
        Rx = self.data.Rx
        Ry = self.data.Ry

        #Desplazamientos
        disp_x = self.disp_x
        disp_y = self.disp_y
        heights = self.heights

        #Derivas
        drifts_x = self.drifts_x
        drifts_y = self.drifts_y
        max_drift =self.data.max_drift_x
        heights_drifts = self.heights_drifts

        #datos discontinuidad de diafragma
        sec_change = self.data.sec_change
        openings = self.data.openings
        
        #datos de esquinas entrantes
        datos_esquinas = self.data.esquinas
        
        #Cargas sismicas
        sis_estatico = self.tables.static_seism

        # Datos separacion
        datos_sep={'altura_edificio':max(heights)*100,
               'despl_max_X':max(disp_x)*100,
               'despl_max_Y':max(disp_y)*100}
        
        #datos cortantes por piso
        _,_SapModel= etb.connect_to_etabs()
        _,cortantes = etb.get_table(_SapModel,'Story Forces')

        df1 = cortantes[['Story','OutputCase','Location','VX']]
        shear_x=df1[(df1["OutputCase"]==self.loads.seism_loads['Sismo_DinX'])] #Filtro
        
        df2 = cortantes[['Story','OutputCase','Location','VY']]
        shear_y=df2[(df2["OutputCase"]==self.loads.seism_loads['Sismo_DinY'])] #Filtro

        geometry_options = { "left": "2.5cm", "top": "1.5cm" }
        doc = Document(geometry_options=geometry_options)
        doc.packages.append(Package('xcolor', options=['dvipsnames']))
        doc.preamble.append(NoEscape(r'\graphicspath{ {%s/} }'%os.getcwd().replace('\\','/')))

        sec = Section('Análisis Sísmico')
        p_sitio = smem.parametros_sitio()
        f_zona = smem.factor_zona(zona)
        f_suelo = smem.factor_suelo(zona, suelo)
        p_suelo = smem.periodos_suelo(suelo)   
        s_est = smem.sist_estructural(sist_x,sist_y)
        f_amp = smem.factor_amplificacion()
        f_imp = smem.factor_importancia(categoria)
        t_resumen = smem.tabla_resumen(Z,U,S,Tp,Tl,Rox,Roy,Ia,Ip)
        e_resp = smem.espectro_respuesta(T,Sax,Say,Tp,Tl,Rx,Ry)
        p_sis = smem.peso_sismico()
        e_accidental = smem.excentricidad_accidental()
        a_modal = smem.ana_modal(self.tables.modal)
        a_irreg = smem.analisis_irregularidades()          
        i_rig = smem.irreg_rigidez(p_blando_x,p_blando_y)
        i_masa = smem.irreg_masa(self.tables.rev_masa_table)        
        i_torsion = smem.irreg_torsion(torsion_x,torsion_y)
        i_discontinuidad = smem.irreg_discontinuidad_diaf(sec_change=sec_change, openings=openings)
        i_esquinas = smem.irreg_esquinas_entrantes(datos_esquinas)
        analisis_din = smem.analisis_dinamico()
        criterios_comb= smem.criterios_combinacion()
        desplaz_lat= smem.desplazamientos_laterales(heights,disp_x,disp_y,Rx,Ry)
        verif_derivas= smem.verificacion_derivas(sist_x,sist_y,heights_drifts,drifts_x,drifts_y,max_drift,Rx,Ry)
        verif_sist_est = smem.verificacion_sist_est()
        analisis_est = smem.analisis_estatico()
        corte_basal= smem.cortante_basal(Z,U,Tx,Ty,Cx,Cy,kx,ky,S,Rox,Roy,Ia,Ip,sis_estatico)
        corte_basal_min = smem.fuerza_cortante_min(self.tables.shear_table,heights_drifts,shear_x,shear_y,Rx,Ry)
        sep_edificios= smem.separacion_edificios(datos_sep)

        obj_list = [p_sitio,f_zona,f_suelo,p_suelo,s_est,f_amp,f_imp,t_resumen,
            e_resp,p_sis,e_accidental,a_modal,
            a_irreg,i_rig,i_masa,i_torsion,i_discontinuidad,i_esquinas,
            analisis_din,criterios_comb,
            desplaz_lat,verif_derivas,verif_sist_est,
            analisis_est,corte_basal,corte_basal_min,sep_edificios]

        for i in obj_list:
            sec.append(i)
        
        doc.append(sec)
        print("\n")
        print("Iniciando la generación del documento en formato .pdf y .tex...")
        doc.generate_pdf('out/Memoria Sismo2')
        doc.generate_tex('out/Memoria Sismo2')
        print("El documento ha sido generado con éxito")
        


if __name__ == '__main__':

    _,_SapModel= etb.connect_to_etabs()


    #Definir variables de salida 'Ton_m_C' o 'kgf_cm_C'
    etb.set_units(_SapModel,'Ton_m_C')

    sistemas = ['Pórticos de Concreto Armado',
                'Dual de Concreto Armado',
                'De Muros Estructurales de Concreto Armado',
                'Pórticos Especiales de Acero Resistentes a Momentos',
                'Pórticos Intermedios de Acero Resistentes a Momentos',
                'Pórticos Ordinarios de Acero Resistentes a Momentos',
                'Pórticos Especiales de Acero Concénticamente Arriostrados',
                'Pórticos Ordinarios de Acero Concénticamente Arriostrados',
                'Pórticos Acero Excéntricamente Arriostrados',
                'Muros de Ductilidad Limita de Concreto Armado',
                'Albañilería Armada o Confinada',
                'Madera']

    categorias = ['A1 aislado',
                  'A1 no aislado',
                  'A2',
                  'B',
                  'C']
    
    sis_loads = {'Sismo_EstX': 'Sx',
                 'Sismo_EstY': 'Sy',
                 'Sismo_DinX': 'SDx',
                 'Sismo_DinY': 'SDy'}
    
    sec_change = {'aligerado':[7.51,0.05],
                'macisa':[2.25,0.20]}
    
    openings = {'aberturas':[(4.02,2.3),(1.1,2.3),(1.2,19)],
                'area_planta' : 120.41}
    
    datos_esquinas={'esq_X':4.95,
                'esq_Y':2.30,
                'dim_X':7.51,
                'dim_Y':15.28}
    zona = 4
    suelo = 'S1'
    sist_x = sistemas[0]
    sist_y = sistemas[1]
    categoria = categorias[4]
    n_pisos = 4
    n_sotanos = 0
    n_azoteas = 0
    story_base = 'Story1'

    sismo = Sismo_e30()
    sismo.data.factor_zona(zona)
    sismo.data.factor_suelo(suelo)
    sismo.data.periodos_suelo()
    sismo.data.sist_estructural(sist_x,sist_y)
    sismo.data.categoria_edificacion(categoria)
    sismo.data.set_pisos(n_pisos,n_azoteas,n_sotanos)
    sismo.data.irreg_altura(i_vertical=False)
    sismo.data.irreg_planta(i_torsional=False)
    sismo.data.factor_R()
    sismo.data.set_pisos(n_pisos, n_azoteas, n_sotanos)
    
    sismo.loads.set_seism_loads(sis_loads)
    sismo.set_base_story(story_base)
    
    sismo.ana_modal(_SapModel)
    sismo.sismo_estatico(_SapModel)
    sismo.dinamic_spectrum()
    sismo.min_shear(_SapModel,story=sismo.base_story)
    sismo.piso_blando(_SapModel)
    sismo.irregularidad_masa(_SapModel)
    sismo.irregularidad_torsion(_SapModel)
    sismo.derivas(_SapModel)
    sismo.desplazamientos(_SapModel)
    sismo.centro_masa_inercia(_SapModel)
    
    sismo.data.sec_change = sec_change
    sismo.data.openings = openings
    sismo.data.esquinas = datos_esquinas
    sismo.data.sistema_x = sist_x
    sismo.data.sistema_x = sist_y
    
    sismo.generate_memoria()

    
