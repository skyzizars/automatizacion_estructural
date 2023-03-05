from ipywidgets import widgets
from IPython.display import clear_output, display
from lib import sismo_utils as sis
from lib import latex_utils as ltx

#widgets
def dropdown(op, desc, val=''):
    return widgets.Dropdown(options=op, description=desc,
                            style={'description_width': 'initial'}, value=val)


def input_box(desc, val=''):
    return widgets.Text(description=desc, value=val, style={'description_width': 'initial'})


def check_box(desc, val=False):
    return widgets.Checkbox(value=val, description=desc, style={'description_width': 'initial'})


def change_filter(change, table, column, widget):
    if change['type'] == 'change' and change['name'] == 'value':
        clear_output(wait=False)
        display(widget)
        if change['new'] == 'sin filtro':
            display(table)
        else:
            display(table[table[column] == change['new']])


class Sismo(sis.sismo_e30):
    
    def __init__(self):
        sis.sismo_e30.__init__(self,data=False,seism_loads=False)

    def parametros_e30(self):
        zona = dropdown(['1', '2', '3', '4'], 'Factor Zona', val=self.data['Factor Zona'])
        uso = dropdown(self.cat_edificacion.categoria, 'Factor de Importancia', val=self.data['Factor de Importancia'])
        suelo = dropdown(['S0', 'S1', 'S2', 'S3'], 'Factor Suelo', val=self.data['Factor Suelo'])
        sistema = dropdown(self.sist_estructural.sistema, 'Sistema Estructural X', val=self.data['Sistema Estructural X'])
        pisos = input_box('Número de Pisos', val=self.data['Número de Pisos'])
        sotanos = input_box('Número de Sotanos', val=self.data['Número de Sotanos'])
        azoteas = input_box('Número de Azoteas', val=self.data['Número de Azoteas'])
        zona.observe(self.w_change)
        uso.observe(self.w_change)
        suelo.observe(self.w_change)
        sistema.observe(self.w_change)
        pisos.observe(self.w_change)
        sotanos.observe(self.w_change)
        azoteas.observe(self.w_change)
        return display(widgets.VBox([zona, uso, suelo, sistema, pisos, sotanos, azoteas]))
    
    def irregularidades_e30(self):
        i_piso_b = check_box('Piso Blando', eval(self.data['Piso Blando']))
        i_piso_be = check_box('Piso Blando Extremo', eval(self.data['Piso Blando Extremo']))
        i_masa = check_box('Irregularidad de Masa', eval(self.data['Irregularidad de Masa']))
        i_vert = check_box('Irregularidad Vertical', eval(self.data['Irregularidad Vertical']))
        i_disc = check_box('Dicontinuidad Vertical', eval(self.data['Dicontinuidad Vertical']))
        i_disc_e = check_box('Dicontinuidad Vertical Extrema', eval(self.data['Dicontinuidad Vertical Extrema']))
        description_a = widgets.HTML(value='<b>Irregularidad en Altura</b>')
        i_altura = widgets.VBox([description_a, i_piso_b, i_piso_be, i_masa, i_vert, i_disc, i_disc_e])
        for i in [description_a, i_piso_b, i_piso_be, i_masa, i_vert, i_disc, i_disc_e]:
            i.observe(self.w_change)

        i_torsion = check_box('Irregularidad Torsional', eval(self.data['Irregularidad Torsional']))
        i_tosion_e = check_box('Irregulariad Torsional Extrema', eval(self.data['Irregulariad Torsional Extrema']))
        i_esquinas = check_box('Esquinas Entrantes', eval(self.data['Esquinas Entrantes']))
        i_disc_diaf = check_box('Discontinuidad del diafragma', eval(self.data['Discontinuidad del diafragma']))
        i_no_paral = check_box('Sistemas no Paralelos', eval(self.data['Sistemas no Paralelos']))
        description_p = widgets.HTML(value='<b>Irregularidad en Planta</b>')
        i_planta = widgets.VBox([description_p, i_torsion, i_tosion_e, i_esquinas, i_disc_diaf, i_no_paral])
        for i in [description_p, i_torsion, i_tosion_e, i_esquinas, i_disc_diaf, i_no_paral]:
            i.observe(self.w_change)
        return widgets.HBox([i_altura, i_planta])
    
    def w_change(self, change, url='data\data.txt'):
        if change['type'] == 'change' and change['name'] == 'value':
            ltx.save_var(change['owner'].description, change['new'], url)
            self.data.update(ltx.read_dict(url))
            self.set_data()


    def select_load(self,SapModel):
        #Guardamos la lista de los loadcases existentes
        _,load_cases,_ = SapModel.LoadCases.GetNameList()
        load_cases = [load for load in load_cases if load[0]!= '~' and load!= 'Modal']
        if len (load_cases)>=1:
            self.Sismo_EstX = dropdown(load_cases,'Sismo Estatico en X',load_cases[0])
            self.Sismo_EstY = dropdown(load_cases,'Sismo Estatico en Y',load_cases[0])
            self.Sismo_DinX = dropdown(load_cases,'Sismo Dinámico en X',load_cases[0])
            self.Sismo_DinY = dropdown(load_cases,'Sismo Dinámico en Y',load_cases[0])
            Title_SismoX = widgets.HTML(value='<b>Dirección X</b>')
            Title_SismoY = widgets.HTML(value='<b>Dirección Y</b>')
            layout_X = widgets.VBox([Title_SismoX, self.Sismo_EstX, self.Sismo_DinX])
            layout_Y = widgets.VBox([Title_SismoY, self.Sismo_EstY, self.Sismo_DinY])
            
            #inicializando valores
            self.seism_loads = {'Sismo_EstX' : load_cases[0],
                                'Sismo_EstY' : load_cases[0],
                                'Sismo_DinX' : load_cases[0],
                                'Sismo_DinY' : load_cases[0] }

            #Observacion en caso de cambio
            self.Sismo_EstX.observe(self.change_cbx_Sx)
            self.Sismo_EstY.observe(self.change_cbx_Sy)
            self.Sismo_DinX.observe(self.change_cbx_SDx)
            self.Sismo_DinY.observe(self.change_cbx_SDy)      

            return widgets.HBox([layout_X, layout_Y])
            
        else:
            print('NO HA INGRESADO NINGUN CASO DE CARGA EN EL MODELO')
            return None
    
    def change_cbx_Sx(self,change):
        if change['type'] == 'change' and change['name'] == 'value':
            self.seism_loads['Sismo_EstX'] = change['new']
    def change_cbx_Sy(self,change):
        if change['type'] == 'change' and change['name'] == 'value':
            self.seism_loads['Sismo_EstY']= change['new']
    def change_cbx_SDx(self,change):
        if change['type'] == 'change' and change['name'] == 'value':
            self.seism_loads['Sismo_DinX']= change['new']
    def change_cbx_SDy(self,change):
        if change['type'] == 'change' and change['name'] == 'value':
            self.seism_loads['Sismo_DinY']= change['new']

    def show_table(self,table, column='OutputCase'):
        list_columns = tuple(table[column].unique())
        widget = dropdown(list_columns + ('sin filtro',), 'Filtro', val='sin filtro')
        widget.observe(lambda change: change_filter(change, table, column, widget))
        display(widget)
        display(table)
