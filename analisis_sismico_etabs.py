#Programado para etabs 2019

import os
import sys
sys.path.append(os.getcwd()+'\\..')
import numpy as np
import pandas as pd
from utils import etabs_utils as etb
from utils import sismo_utils as sis
from utils import sismo_mem as smem


_, _SapModel = etb.connect_to_etabs()

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
    
sis_loads = {'Sismo_EstX': 'SEXX NEG',
                 'Sismo_EstY': 'SEYY NEG',
                 'Sismo_DinX': 'SDXX',
                 'Sismo_DinY': 'SDYY'}

sec_change = {'aligerado':[7.51,0.05],
            'macisa':[2.25,0.20]}

openings = {'aberturas':[(4.02,2.3),(1.1,2.3),(1.2,19)],
            'area_planta' : 120.41}

datos_esquinas={'esq_X':4.95,
            'esq_Y':2.30,
            'dim_X':7.51,
            'dim_Y':15.28}



zona = 4
suelo = 'S2'
sist_x = sistemas[0]
sist_y = sistemas[1]
categoria = categorias[2]
n_pisos = 6
n_sotanos = 0
n_azoteas = 0
story_base = 'Story1'

sismo = sis.Sismo_e30()
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
#sismo.data.show_params()


sismo.data.sec_change = sec_change
sismo.data.openings = openings
sismo.data.esquinas = datos_esquinas
sismo.data.sistema_x = sist_x
sismo.data.sistema_x = sist_y

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

sismo.generate_memoria()


# _,_SapModel= etb.connect_to_etabs()
# _,cortantes = etb.get_table(_SapModel,'Story Forces')

# df1 = cortantes[['Story','OutputCase','Location','VX']]
# shear_x=df1[(df1["OutputCase"]==sismo.loads.seism_loads['Sismo_DinX'])] #Filtro

# df2 = cortantes[['Story','OutputCase','Location','VY']]
# shear_y=df2[(df2["OutputCase"]==sismo.loads.seism_loads['Sismo_DinY'])] #Filtro

# shear_x=list(shear_x['VX'].astype(float))
# shear_x.insert(0,0)
# shear_y=list(shear_y['VY'].astype(float))
# shear_y.insert(0,0)
# max_shear_x = max(shear_x)
# max_shear_y = max(shear_y)

# heights = sismo.heights_drifts

# list_heights=list(reversed(heights)) #Convertir a lista e invertir posiciones
# heights_extended = []
# heights_extended.extend([i, i] for i in list_heights[:-1])
# heights_extended = [item for sublist in heights_extended for item in sublist] + [0]

# a = sismo.tables
# stories  = etb.get_story_data(_SapModel)


# set_loads = [load for load in sismo.loads.seism_loads.values()]
# _SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_loads)
# _SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([])

# _ , table = etb.get_table(_SapModel,'Story Max Over Avg Drifts')
# table['OutputCase'] = table.OutputCase+' '+table.StepType
# table = table[['Story','OutputCase','Direction','Max Drift','Avg Drift','Ratio']]
