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

_sistemas = ['Pórticos de Concreto Armado',
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

_categorias = ['A1 aislado',
                  'A1 no aislado',
                  'A2',
                  'B',
                  'C']
    
_sis_loads = {'Sismo_EstX': 'SX',
                 'Sismo_EstY': 'SY',
                 'Sismo_DinX': 'SDX',
                 'Sismo_DinY': 'SDY'}

_sec_change = {}

_openings = {}

_datos_esquinas={}

_zona = 3
_suelo = 'S2'
_sist_x = _sistemas[2]
_sist_y = _sistemas[2]
_categoria = _categorias[4]
_n_pisos = 6
_n_sotanos = 0
_n_azoteas = 0
_story_base = 'Story1'

sismo = sis.Sismo_e30()
sismo.data.factor_zona(_zona)
sismo.data.factor_suelo(_suelo)
sismo.data.periodos_suelo()
sismo.data.sist_estructural(_sist_x,_sist_y)
sismo.data.categoria_edificacion(_categoria)
sismo.data.set_pisos(_n_pisos,_n_azoteas,_n_sotanos)
sismo.data.irreg_altura(i_vertical=False)
sismo.data.irreg_planta(i_torsional=False)
sismo.data.factor_R()
#sismo.data.show_params()
sismo.data.sec_change = _sec_change
sismo.data.openings = _openings
sismo.data.esquinas = _datos_esquinas
sismo.loads.set_seism_loads(_sis_loads)
sismo.set_base_story(_story_base)

sismo.ana_modal(_SapModel)
sismo.sismo_estatico(_SapModel,report=True)
sismo.dinamic_spectrum()
sismo.min_shear(_SapModel,story=sismo.base_story)
sismo.piso_blando(_SapModel)
sismo.irregularidad_masa(_SapModel)
sismo.irregularidad_torsion(_SapModel)
sismo.derivas(_SapModel)
sismo.desplazamientos(_SapModel)
sismo.centro_masa_inercia(_SapModel)

tables = sismo.tables
torsion = tables.torsion_table
drifts = tables.drift_table
centros_MR = tables.CM_CR_table
f_e = tables.shear_table


# sismo.generate_memoria()