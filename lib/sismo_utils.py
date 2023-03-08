import sys
import os
sys.path.append(os.getcwd())
import pandas as pd
from lib import etabs_utils as etb


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
            self.n_pisos, self.n_azoteas, self.n_sotanos = n_pisos,n_azoteas,n_sotanos

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
        
        self.tables.modal = modal
        self.data.Tx = Tx
        self.data.Ty = Ty

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

        #Cálculo del exponente de altura
        def get_k(T):
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
        def get_C(T):
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
            
        def get_ZUCS_R(C,R):
            ZUS = self.data.Z*self.data.U*self.data.S
            if C/R>0.11:
                return C/R*ZUS
            else:
                return 0.11*ZUS


        self.ana_modal(SapModel)
        self.data.kx = get_k(self.data.Tx)
        self.data.ky = get_k(self.data.Ty)
        self.data.Cx = get_C(self.data.Tx)
        self.data.Cy = get_C(self.data.Ty)
        self.data.ZUCS_Rx = get_ZUCS_R(self.data.Cx,self.data.Rx)
        self.data.ZUCS_Ry = get_ZUCS_R(self.data.Cy,self.data.Ry)

        if report:
            #Resumen
            print('Factor de Reduccion con Irregularidades en X: R={}'.format(self.data.Rx))
            print('Factor de Reduccion con Irregularidades en Y: R={}'.format(self.data.Ry))
            print('C en X: {0:.2f}'.format(self.data.Cx))
            print('C en Y: {0:.2f}'.format(self.data.Cy))

            print('\nCoeficiente de sismo estático X: {0:.3f}'.format(self.data.ZUCS_Rx))
            print('Coeficiente de sismo estático Y: {0:.3f}'.format(self.data.ZUCS_Rx))
            print('Exponente de altura X: {0:.2f}'.format(self.data.kx))
            print('Exponente de altura Y: {0:.2f}'.format(self.data.kx))

    #Revisión por Torsión      
    def irregularidad_torsion(self,SapModel):
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

        table['Drifts'] = table.apply((lambda row: float(row['Max Drift'])*self.data.Rx if 'x' in row['OutputCase'] else float(row['Max Drift'])*self.data.Ry),axis=1)

        table['Drift < Dmax/2'] = table['Drifts'] < self.data.max_drift_x/2
        tor_reg = (table['Drift < Dmax/2']) | (table['Ratio'].apply(lambda x: float(x)) < 1.3)
        table['tor_reg'] = tor_reg.apply(lambda x: 'Regular' if x else 'Irregular')

        self.tables.torsion_table = table

    #Piso Blando
        
    def piso_blando(self,SapModel):
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

    # Masa

    def irregularidad_masa(self,SapModel):
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

    # Derivas
    def derivas(self):
        rev_drift = self.tables.torsion_table[['Story','OutputCase','Direction','Drifts']]
        rev_drift = rev_drift.assign(Drift_Check = (rev_drift['Drifts'] < self.data.max_drift_x).apply(lambda x: 'Cumple' if x else 'No Cumple'))
        self.tables.drift_table = rev_drift

    # Centros de Masas y Rigideces

    def centro_masa_inercia(self,SapModel):
        _,rev_CM_CR = etb.get_table(SapModel,'Centers Of Mass And Rigidity')
        rev_CM_CR = rev_CM_CR[['Story','XCCM','XCR','YCCM','YCR']]
        rev_CM_CR['DifX'] = rev_CM_CR.XCCM.apply(lambda x: float(x)) - rev_CM_CR.XCR.apply(lambda x: float(x))
        rev_CM_CR['DifY'] = rev_CM_CR.YCCM.apply(lambda x: float(x)) - rev_CM_CR.YCR.apply(lambda x: float(x))
        self.tables.CM_CR_table = rev_CM_CR

    def min_shear(self,SapModel,story='Story1'):
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
        
    def analisis_sismo(self, SapModel):
        self.sismo_estatico(SapModel)
        self.piso_blando(SapModel)
        self.irregularidad_masa(SapModel)
        #self.centro_masa_inercia(SapModel)
        self.irregularidad_torsion(SapModel)
        self.derivas()
        self.min_shear(SapModel,self.base_story)

    def generate_memoria(self):
        from pylatex import Document, Section, Subsection,Subsubsection
        from pylatex.utils import NoEscape
        from pylatex.package import Package
        from lib import sismo_mem as smem
        seism_x = self.loads.seism_loads['Sismo_DinX'] + ' Max'
        seism_y = self.loads.seism_loads['Sismo_DinY'] + ' Max'
        zona = self.data.zona
        suelo = self.data.suelo
        categoria = self.data.categoria
        geometry_options = { "left": "2.5cm", "top": "1.5cm" }
        doc = Document(geometry_options=geometry_options)
        doc.packages.append(Package('xcolor', options=['dvipsnames']))
        doc.preamble.append(NoEscape(r'\graphicspath{ {%s/} }'%os.getcwd().replace('\\','/')))
        sec = Section('Análisis Sísmico')
        f_zona = smem.factor_zona(zona, o_type=Subsection)
        f_suelo = smem.factor_suelo(zona, suelo)
        p_suelo = smem.periodos_suelo(suelo)   
        s_est = smem.sist_estructural()
        f_amp = smem.factor_amplificacion()
        f_imp = smem.factor_importancia(categoria)
        a_modal = smem.ana_modal(self.tables.modal)             
        sis_x = self.tables.piso_blando_table.query('OutputCase == @seism_x')
        sis_y = self.tables.piso_blando_table.query('OutputCase == @seism_y')
        i_rig = smem.irreg_rigidez(sis_x,sis_y)
        i_masa = smem.irreg_masa(self.tables.rev_masa_table)
        sis_x = self.tables.torsion_table.query('OutputCase == @seism_x')
        sis_y = self.tables.torsion_table.query('OutputCase == @seism_y')
        i_torsion = smem.irreg_torsion(sis_x, sis_y)
        sec_change = {'aligerado':[7.51,0.05],
                    'macisa':[2.25,0.20]}
        openings = {'aberturas':[(4.02,2.3),(1.1,2.3),(1.2,19)],
                    'area_planta' : 120.41}
        i_esquinas = smem.irreg_esquinas(sec_change=sec_change, openings=openings)
        for i in [f_zona,f_suelo,p_suelo,s_est,f_amp,f_imp,a_modal,i_rig,i_masa,i_torsion]:
            sec.append(i)
        
        doc.append(sec)
        doc.generate_pdf('out/Memoria Sismo2')
        doc.generate_tex('out/Memoria Sismo2')
    


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
    sismo.data.irreg_altura(i_vertical=True)
    sismo.data.irreg_planta(i_torsional=True)
    sismo.data.factor_R()
    sismo.data.set_pisos(n_pisos, n_azoteas, n_sotanos)
    sismo.data.show_params()
    
    sismo.loads.set_seism_loads(sis_loads)
    sismo.set_base_story(story_base)
    
    sismo.analisis_sismo(_SapModel)
    
    tablas = sismo.tables
    sismo.generate_memoria()

    
