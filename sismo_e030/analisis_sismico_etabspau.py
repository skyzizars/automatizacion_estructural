#Programado para etabs 2019

import numpy as np
import pandas as pd
import os
import sys
sys.path.append(os.getcwd())
from lib import etabs_utils as etb
from lib import sismo_utils as sis



_SapModel, _EtabsObject = etb.connect_to_etabs()

#Definir variables de salida 'Ton_m_C' o 'kgf_cm_C'
etb.set_units(_SapModel,'Ton_m_C')

# Datos:
Datos = {
'N': 3,
'Z': 0.25,
'U': 1,
'S': 1.2,
'Tp': 0.6,
'Tl': 2,
'Ip': 1,
'Ia': 1,
'R_o': 8,
'max_drift': 0.007,
'loads': ['Sx','Sy','SDx','SDy'],
'n_sotanos': 0 ,
'n_techos': 0}

'''
1 → Análisis Modal
2 → Sismo Estático
3 → Revisar Torsión
4 → Revisar Piso Blando
5 → Revisar Irregularidad de masa
6 → Obtener Centros de Masa y Rigidez
7 → Análisis de Derivas
8 → Análisis Completo
'''

data = sis.rev_sismo(_SapModel,Datos,T_analisis = 8)



derivas = data['drifts']
derivas_x  = derivas[derivas.Direction == 'X']
derivas_y  = derivas[derivas.Direction == 'Y']


torsion = data['torsion_table']
torsion_x  = torsion[torsion.Direction == 'X']
torsion_y  = torsion[torsion.Direction == 'Y']


CM_CR = data['CM_CR']
