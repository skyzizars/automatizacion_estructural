#Programado para etabs 2019

import os
import sys
sys.path.append(os.getcwd()+'\\..')
import numpy as np
import pandas as pd
from lib import etabs_utils as etb
from lib import sismo_utils as sis
from lib import sismo_mem as smem


_SapModel, _EtabsObject = etb.connect_to_etabs()

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

datos = {'Factor de Importancia': 'C',
        'Sistema Estructural': sistemas[0],
        'Número de Pisos': '4',
        'Número de Sotanos': '0',
        'Número de Azoteas': '1',
        'Factor Zona': '2',
        'Factor Suelo': 'S2',
        'Piso Blando': 'False',
        'Piso Blando Extremo': 'False',
        'Irregularidad de Masa': 'False',
        'Irregularidad Vertical': 'False',
        'Dicontinuidad Vertical': 'False',
        'Dicontinuidad Vertical Extrema': 'False',
        'Irregularidad Torsional': 'False',
        'Irregulariad Torsional Extrema': 'False',
        'Esquinas Entrantes': 'False',
        'Discontinuidad del diafragma': 'False',
        'Sistemas no Paralelos': 'False'}




sismo = sis.sismo_e30(data=datos)
self.zona = int(self.data['Factor Zona'])
self.Z = float(self.factor_zona[self.factor_zona.Zona == zona].Z)
categoria = self.data['Factor de Importancia']
self.U = float(self.cat_edificacion[self.cat_edificacion.categoria == categoria].U)
suelo = self.data['Factor Suelo']
self.S = float(self.factor_suelo[self.factor_suelo.Z == zona][suelo])
self.Tp = self.periodos_suelo[suelo].loc['Tp']
self.Tl = self.periodos_suelo[suelo].loc['Tl']
sistema_x = self.data['Sistema Estructural X']
sistema_y = self.data['Sistema Estructural X']
self.Rox = float(self.sist_estructural[self.sist_estructural.sistema == sistema_x]['R_0'])
self.Roy = float(self.sist_estructural[self.sist_estructural.sistema == sistema_y]['R_0'])
self.max_drift_x = float(self.sist_estructural[self.sist_estructural.sistema == sistema_x]['max_drift'])
self.max_drift_y = float(self.sist_estructural[self.sist_estructural.sistema == sistema_y]['max_drift'])
self.N = int(self.data['Número de Pisos'])
self.n_sotanos = int(self.data['Número de Sotanos'])
self.n_azoteas = int(self.data['Número de Azoteas'])
self.Ip = min([j for i, j in self.irreg_planta.items() if eval(self.data[i])] + [1, ])
self.Ia = min([j for i, j in self.irreg_altura.items() if eval(self.data[i])] + [1, ])

sismo.show_params()
sismo.analisis_sismo(_SapModel)

zona = 2
suelo = 'S1'
categoria = 'A2'

geometry_options = { "left": "2.5cm", "top": "1.5cm" }
doc = smem.Document(geometry_options=geometry_options)
doc.packages.append(smem.Package('xcolor', options=['dvipsnames']))
s1 = smem.Section('Análisis Sísmico')
s1.packages.append(smem.Package('tcolorbox'))
s1.packages.append(smem.Package('booktabs'))
# s1 = smem.params_sitio(zona,suelo,categoria,s1)
# s1 = smem.ana_modal(sismo.modal, s1)
tabla = sismo.piso_blando_table
sis_x = tabla[tabla['OutputCase']=='SDX Max']
sis_y = tabla[tabla['OutputCase']=='SDY Max']
s1 = smem.irreg_rigidez(s1,sis_x,sis_y)

doc.append(s1)
doc.generate_pdf('Memoria Sismo2')
doc.generate_tex('Memoria Sismo2')


