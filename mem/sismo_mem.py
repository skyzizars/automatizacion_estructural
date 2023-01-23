from ipywidgets import widgets
import pandas as pd
from lib import sismo_utils as sis
from mem import latex_utils as ltx


def dropdown(op,desc,val=''):
    return widgets.Dropdown(options=op,description=desc,
            style={'description_width':'initial'},value=val)

def input_box(desc, val=''):
    return widgets.Text(description=desc,value = val,style={'description_width':'initial'})

def check_box(desc,val=False):
    return widgets.Checkbox(value=val, description=desc,style={'description_width':'initial'})


class sismo_e30():
    def __init__(self):
        self.data = {'Factor de Importancia': 'C',
            'Sistema Estructural': 'Dual de Concreto Armado',
            'Número de Pisos': '4',
            'Número de Sotanos': '0',
            'Número de Azoteas': '1',
            'Factor Zona': '2',
            'Factor Suelo': 'S2',
            'Piso Blando':'False',
            'Piso Blando Extremo':'False',
            'Irregularidad de Masa':'False',
            'Irregularidad Vertical':'False',
            'Dicontinuidad Vertical':'False',
            'Dicontinuidad Vertical Extrema':'False',
            'Irregularidad Torsional':'False',
            'Irregulariad Torsional Extrema':'False',
            'Esquinas Entrantes':'False',
            'Discontinuidad del diafragma':'False',
            'Sistemas no Paralelos':'False'}
        self.data.update(ltx.read_dict('..\datos\data.txt'))

        self.factor_zona = pd.DataFrame([[4, 0.45], [3, 0.35], [2, 0.25], [1, 0.1]], columns=['Zona', 'Z'])
        self.factor_suelo=pd.DataFrame(
            [[4,0.8,1,1.05,1.1],
            [3,0.8,1,1.15,1.20],
            [2,0.80,1,1.2,1.4],
            [1,0.8,1,1.6,2]],
            columns=['Z','S0','S1','S2','S3'])
        self.periodos_suelo=pd.DataFrame(
            [[0.3,0.4,0.6,1],
            [3,2.5,2,1.6]],
            columns=['S0','S1','S2','S3'],
            index=['Tp','Tl'])
        self.sist_estructural = pd.DataFrame(
            [['Pórticos Especiales de Acero Resistentes a Momentos',8,0.01],
            ['Pórticos Intermedios de Acero Resistentes a Momentos',5,0.01],
            ['Pórticos Ordinarios de Acero Resistentes a Momentos',4,0.01],
            ['Pórticos Especiales de Acero Concénticamente Arriostrados',7,0.01],
            ['Pórticos Ordinarios de Acero Concénticamente Arriostrados',4,0.1],
            ['Pórticos Acero Excéntricamente Arriostrados',8,0.01],
            ['Pórticos de Concreto Armado',8,0.007],
            ['Dual de Concreto Armado',7,0.007],
            ['De Muros Estructurales de Concreto Armado',6,0.007],
            ['Muros de Ductilidad Limita de Concreto Armado',4,0.005],
            ['Albañilería Armada o Confinada',3,0.005],
            ['Madera',7,0.01]],
            columns=['sistema','R_0','max_drift'])
        
        self.cat_edificacion = pd.DataFrame(
            [['A1 aislado',1],
            ['A1 no aislado', 1.5],
            ['A2',1.5],
            ['B',1.3],
            ['C',1]],
            columns=['categoria','U']
        )


        self.irreg_altura  = {
            'Piso Blando':0.75,
            'Piso Blando Extremo':0.50,
            'Irregularidad de Masa':0.90,
            'Irregularidad Vertical':0.90,
            'Dicontinuidad Vertical':0.80,
            'Dicontinuidad Vertical Extrema':0.60,
        }

        self.irreg_planta = {
            'Irregularidad Torsional':0.75,
            'Irregulariad Torsional Extrema':0.60,
            'Esquinas Entrantes':0.90,
            'Discontinuidad del diafragma':0.85,
            'Sistemas no Paralelos':0.90
        }

        self.set_data()

    def on_change(self,change,url='..\datos\data.txt'):
        if change['type'] == 'change' and change['name'] == 'value':
            ltx.save_var(change['owner'].description,change['new'],url)
            self.data.update(ltx.read_dict(url))
            self.set_data()


    def parametros_e30(self):
        zona = dropdown(['1','2','3','4'],'Factor Zona',val=self.data['Factor Zona'])
        uso = dropdown(self.cat_edificacion.categoria,'Factor de Importancia',val=self.data['Factor de Importancia'])
        suelo = dropdown(['S0','S1','S2','S3'],'Factor Suelo',val=self.data['Factor Suelo'])
        sistema = dropdown(self.sist_estructural.sistema,'Sistema Estructural',val=self.data['Sistema Estructural'])
        pisos = input_box('Número de Pisos', val=self.data['Número de Pisos'])
        sotanos = input_box('Número de Sotanos', val=self.data['Número de Sotanos'])
        azoteas = input_box('Número de Azoteas', val=self.data['Número de Azoteas'])
        zona.observe(self.on_change)
        uso.observe(self.on_change)
        suelo.observe(self.on_change) 
        sistema.observe(self.on_change)
        pisos.observe(self.on_change)
        sotanos.observe(self.on_change)
        azoteas.observe(self.on_change)
        return widgets.VBox([zona,uso,suelo,sistema,pisos,sotanos,azoteas])

    def irregularidades_e30(self):
        i_piso_b = check_box('Piso Blando', eval(self.data['Piso Blando']))
        i_piso_be = check_box('Piso Blando Extremo', eval(self.data['Piso Blando Extremo']))
        i_masa = check_box('Irregularidad de Masa', eval(self.data['Irregularidad de Masa']))
        i_vert = check_box('Irregularidad Vertical', eval(self.data['Irregularidad Vertical']))
        i_disc = check_box('Dicontinuidad Vertical', eval(self.data['Dicontinuidad Vertical']))
        i_disc_e = check_box('Dicontinuidad Vertical Extrema', eval(self.data['Dicontinuidad Vertical Extrema']))
        description_a = widgets.HTML(value='<b>Irregularidad en Altura</b>')
        i_altura = widgets.VBox([description_a,i_piso_b,i_piso_be,i_masa,i_vert,i_disc,i_disc_e])
        for i in [description_a,i_piso_b,i_piso_be,i_masa,i_vert,i_disc,i_disc_e]:
            i.observe(self.on_change)

        i_torsion = check_box('Irregularidad Torsional', eval(self.data['Irregularidad Torsional']))
        i_tosion_e = check_box('Irregulariad Torsional Extrema', eval(self.data['Irregulariad Torsional Extrema']))
        i_esquinas = check_box('Esquinas Entrantes', eval(self.data['Esquinas Entrantes']))
        i_disc_diaf = check_box('Discontinuidad del diafragma', eval(self.data['Discontinuidad del diafragma']))
        i_no_paral = check_box('Sistemas no Paralelos', eval(self.data['Sistemas no Paralelos']))
        description_p = widgets.HTML(value='<b>Irregularidad en Planta</b>')
        i_planta = widgets.VBox([description_p,i_torsion,i_tosion_e,i_esquinas,i_disc_diaf,i_no_paral])
        for i in [description_p,i_torsion,i_tosion_e,i_esquinas,i_disc_diaf,i_no_paral]:
            i.observe(self.on_change)
        return widgets.HBox([i_altura,i_planta])


    def set_data(self):
        zona = int(self.data['Factor Zona'])
        self.Z = float(self.factor_zona[self.factor_zona.Zona == zona].Z)
        categoria = self.data['Factor de Importancia']
        self.U = float(self.cat_edificacion[self.cat_edificacion.categoria==categoria].U)
        suelo = self.data['Factor Suelo']
        self.S = float(self.factor_suelo[self.factor_suelo.Z==zona][suelo])
        self.Tp = self.periodos_suelo[suelo].loc['Tp']
        self.Tl = self.periodos_suelo[suelo].loc['Tl']
        sistema = self.data['Sistema Estructural']
        self.R_0 = float(self.sist_estructural[self.sist_estructural.sistema==sistema]['R_0'])
        self.max_drift = float(self.sist_estructural[self.sist_estructural.sistema==sistema]['max_drift'])
        self.N = int(self.data['Número de Pisos'])
        self.n_sotanos = int(self.data['Número de Sotanos'])
        self.n_azoteas = int(self.data['Número de Azoteas'])
        self.Ip = min([j for i,j in self.irreg_planta.items() if eval(self.data[i])]+[1,])
        self.Ia = min([j for i,j in self.irreg_altura.items() if eval(self.data[i])]+[1,])

    def sismo_estatico(self,SapModel):
        N = self.N
        Z = self.Z
        U = self.U
        S = self.S
        Tp = self.Tp
        Tl = self.Tl
        Ip = self.Ip
        Ia = self.Ia
        R_o = self.R_0
        self.data_estatica = sis.sismo_estatico(SapModel,N,Z,U,S,Tp,Tl,Ip,Ia,R_o)

    def piso_blando(self,SapModel,loads=['Sx','Sy','SDx','SDy']):
        self.piso_blando_table =  sis.rev_piso_blando(SapModel,loads)

    def irregularidad_masa(self,SapModel):
        self.rev_masa_table = sis.rev_masa(SapModel,self.n_sotanos,self.n_azoteas)

    def centro_masa_inercia(self,SapModel):
        self.CM_CR_table = sis.get_CM_CR(SapModel)

    def irregularidad_torsion(self,SapModel,loads=['Sx','Sy','SDx','SDy']):
        self.R = self.R_0*self.Ia*self.Ip
        self.is_regular = self.Ip == 1 and self.Ia==1
        self.torsion_table = sis.create_rev_torsion_table(SapModel,loads,self.max_drift,self.R,is_regular=self.is_regular)

    def derivas(self):
        self.drift_table = sis.get_rev_drift(self.torsion_table, self.max_drift)
        
    def analisis_sismo(self,SapModel):
        self.sismo_estatico(SapModel)
        self.piso_blando(SapModel)
        self.irregularidad_masa(SapModel)
        self.centro_masa_inercia(SapModel)
        self.irregularidad_torsion(SapModel)
        self.derivas()