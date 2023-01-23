#Programado para etabs 2019

import numpy as np
import pandas as pd
from lib import etabs_utils as etb
from lib import sismo_utils as sis


_SapModel, _EtabsObject = etb.connect_to_etabs()

#Definir variables de salida 'Ton_m_C' o 'kgf_cm_C'
etb.set_units(_SapModel,'Ton_m_C')

# Datos:
Datos = {
'N': 6,
'Z': 0.25,
'U': 1,
'S': 1.2,
'Tp': 0.6,
'Tl': 2,
'Ip': 1,
'Ia': 0.75,
'R_o': 6,
'max_drift': 0.007,
'loads': ['Sx','Sy','SDx','SDy'],
'n_sotanos': 1 ,
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

data = sis.rev_sismo(_SapModel,Datos,T_analisis = 4)


derivas = data['drifts']
derivas_sx  = derivas[derivas.OutputCase == 'Sx']
derivas_sy  = derivas[derivas.OutputCase == 'Sy']
derivas_sdx = derivas[derivas.OutputCase == 'SDx']
derivas_sdy = derivas[derivas.OutputCase == 'SDy']

torsion = data['torsion_table']
torsion_sx  = torsion[torsion.OutputCase == 'Sx']
torsion_sy  = torsion[torsion.OutputCase == 'Sy']
torsion_sdx = torsion[torsion.OutputCase == 'SDx']  
torsion_sdy = torsion[torsion.OutputCase == 'SDy']

CM_CR = data['CM_CR']
