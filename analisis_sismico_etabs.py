#Programado para etabs 2019

import os
import sys
sys.path.append(os.getcwd()+'\\..')
import numpy as np
import pandas as pd
from lib import etabs_utils as etb
from lib import sismo_utils as sis
from lib import sismo_mem as smem


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
    
sis_loads = {'Sismo_EstX': 'Sx',
                 'Sismo_EstY': 'Sy',
                 'Sismo_DinX': 'SDx',
                 'Sismo_DinY': 'SDy'}

zona = 4
suelo = 'S2'
sist_x = sistemas[0]
sist_y = sistemas[1]
categoria = categorias[2]
n_pisos = 3
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

