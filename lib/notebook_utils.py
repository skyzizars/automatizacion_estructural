from ipywidgets import widgets
from IPython.display import clear_output, display
from lib import sismo_utils as sis
from lib import baseDatos_Zonificacion as BD
import numpy as np

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


class Sismo(sis.Sismo_e30):
    
    def __init__(self):
        sis.Sismo_e30.__init__(self)
        self.data.factor_zona(zona = 4)
        self.data.factor_suelo(suelo = 'S2')
        self.data.categoria_edificacion('C')
        self.data.sist_estructural('Dual de Concreto Armado','Dual de Concreto Armado')
        self.data.set_pisos(4,0,0)
        self.data.irreg_altura()
        self.data.irreg_planta()
        
    def ubicacion(self):
        #Creamos la base de datos de ciudades y su zonificación sismica
        BD_df= BD.BaseDatos_Zonas_Sismicas().BD_Zonas_Sismicas
        #Valores Iniciales
        departamentos = BD_df['DEPARTAMENTO'].unique()
        self.departamento = departamentos[0]
        provincias = BD_df.query('DEPARTAMENTO==@self.departamento')['PROVINCIA'].unique()
        self.provincia = provincias[0]
        distritos = (BD_df.query('DEPARTAMENTO==@self.departamento')
                    .query('PROVINCIA==@self.provincia')['DISTRITO'].unique())
        self.distrito = distritos[0]

        self.departamentos = dropdown(departamentos,'Departamento ',self.departamento)
        self.provincias = dropdown(provincias,'Provincia ',self.provincia)
        self.distritos = dropdown(distritos,'Distrito ',self.distrito)


        def change_cbx_ubicacion(change,departamento=None,provincia=None,distrito = None):
            if change['type'] == 'change' and change['name'] == 'value':
                clear_output(wait=False)
                self.departamento = departamento if departamento else self.departamento
                provincias = BD_df.query('DEPARTAMENTO==@self.departamento')['PROVINCIA'].unique()
                self.provincia = provincia if provincia else self.provincia if distrito else provincias[0]
                distritos = (BD_df.query('DEPARTAMENTO==@self.departamento')
                    .query('PROVINCIA==@self.provincia')['DISTRITO'].unique())
                self.distrito = distrito if distrito else distritos[0]

                self.provincias = dropdown(provincias,'Provincia ',self.provincia)
                self.distritos = dropdown(distritos,'Distrito ',self.distrito)

                self.provincias.observe(lambda change: change_cbx_ubicacion(change,provincia = self.provincias.value))
                self.distritos.observe(lambda change: change_cbx_ubicacion(change,distrito = self.distritos.value))

                self.data.zona = int((BD_df.query('DEPARTAMENTO==@self.departamento')
                                        .query('PROVINCIA==@self.provincia')
                                        .query('DISTRITO==@self.distrito')['ZONA(Z)']))
                return display(widgets.VBox([self.departamentos,self.provincias,self.distritos]))


        self.departamentos.observe(lambda change: change_cbx_ubicacion(change,departamento = self.departamentos.value))
        self.provincias.observe(lambda change: change_cbx_ubicacion(change,provincia = self.provincias.value))
        self.distritos.observe(lambda change: change_cbx_ubicacion(change,distrito = self.distritos.value))

        return(widgets.VBox([self.departamentos,self.provincias,self.distritos]))


    def parametros_e30(self):
        categorias= ['A1 aislado','A1 no aislado','A2','B','C']
        sistemas =['Pórticos Especiales de Acero Resistentes a Momentos',
                    'Pórticos Intermedios de Acero Resistentes a Momentos',
                    'Pórticos Ordinarios de Acero Resistentes a Momentos',
                    'Pórticos Especiales de Acero Concénticamente Arriostrados',
                    'Pórticos Ordinarios de Acero Concénticamente Arriostrados',
                    'Pórticos Acero Excéntricamente Arriostrados',
                    'Pórticos de Concreto Armado',
                    'Dual de Concreto Armado',
                    'De Muros Estructurales de Concreto Armado',
                    'Muros de Ductilidad Limita de Concreto Armado',
                    'Albañilería Armada o Confinada',
                    'Madera']


        zona = dropdown([1, 2, 3, 4], 'Factor Zona', val=self.data.zona)    
        uso = dropdown(categorias, 'Factor de Importancia', val=self.data.categoria)
        suelo = dropdown(['S0', 'S1', 'S2', 'S3'], 'Factor Suelo', val=self.data.suelo)
        sistema_x = dropdown(sistemas, 'Sistema Estructural X', val=self.data.sistema_x)
        sistema_y = dropdown(sistemas, 'Sistema Estructural Y', val=self.data.sistema_y)
        pisos = input_box('Número de Pisos', val=str(self.data.n_pisos))
        sotanos = input_box('Número de Sotanos', val=str(self.data.n_sotanos))
        azoteas = input_box('Número de Azoteas', val=str(self.data.n_azoteas))

        zona.observe(lambda _: self.data.factor_zona(zona.value))
        uso.observe(lambda _: self.data.categoria_edificacion(uso.value))
        suelo.observe(lambda _: self.data.factor_suelo(suelo.value))
        sistema_x.observe(lambda _: self.data.sist_estructural(sistema_x.value,self.data.sistema_y))
        sistema_y.observe(lambda _: self.data.sist_estructural(self.data.sistema_x,sistema_y.value))
        pisos.observe(lambda _: self.data.set_pisos(pisos.value,self.data.n_azoteas,self.data.n_sotanos))
        sotanos.observe(lambda _: self.data.set_pisos(self.data.n_pisos,sotanos.value,self.data.n_sotanos))
        azoteas.observe(lambda _: self.data.set_pisos(self.data.n_pisos,self.data.n_azoteas,azoteas.value))
        
        return display(widgets.VBox([zona, uso, suelo, sistema_x,sistema_y, pisos, sotanos, azoteas]))

        

    def irregularidades_e30(self):
        i_piso_b = check_box('Piso Blando', self.data.i_piso_blando)
        i_piso_b.observe(lambda _: self.data.irreg_altura(i_piso_blando=i_piso_b.value))
        i_piso_be = check_box('Piso Blando Extremo', self.data.i_piso_blando_e)
        i_piso_be.observe(lambda _: self.data.irreg_altura(i_piso_blando_e=i_piso_be.value))
        i_masa = check_box('Irregularidad de Masa', self.data.i_masa)
        i_masa.observe(lambda _: self.data.irreg_altura(i_masa=i_masa.value))
        i_vert = check_box('Irregularidad Vertical', self.data.i_vertical)
        i_vert.observe(lambda _: self.data.irreg_altura(i_vertical=i_vert.value))
        i_disc = check_box('Dicontinuidad Vertical', self.data.i_discontinuidad_vertical)
        i_disc.observe(lambda _: self.data.irreg_altura(i_discontinuidad_vertical=i_disc.value))
        i_disc_e = check_box('Dicontinuidad Vertical Extrema', self.data.i_discontinuidad_vertical_e)
        i_disc_e.observe(lambda _: self.data.irreg_altura(i_discontinuidad_vertical_e=i_disc_e.value))
        description_a = widgets.HTML(value='<b>Irregularidad en Altura</b>')
        i_altura = widgets.VBox([description_a, i_piso_b, i_piso_be, i_masa, i_vert, i_disc, i_disc_e])


        i_torsion = check_box('Irregularidad Torsional', self.data.i_torsional)
        i_torsion.observe(lambda _: self.data.irreg_planta(i_torsional=i_torsion.value))
        i_tosion_e = check_box('Irregulariad Torsional Extrema', self.data.i_torsional_e)
        i_tosion_e.observe(lambda _: self.data.irreg_planta(i_torsional_e=i_tosion_e.value))
        i_esquinas = check_box('Esquinas Entrantes', self.data.i_esquinas_entrantes)
        i_esquinas.observe(lambda _: self.data.irreg_planta(i_esquinas_entrantes=i_esquinas.value))
        i_disc_diaf = check_box('Discontinuidad del diafragma', self.data.i_discontinuidad_diafragma)
        i_disc_diaf.observe(lambda _: self.data.irreg_planta(i_discontinuidad_diafragma=i_disc_diaf.value))
        i_no_paral = check_box('Sistemas no Paralelos', self.data.i_sistemas_no_paralelos)
        i_no_paral.observe(lambda _: self.data.irreg_planta(i_sistemas_no_paralelos=i_no_paral.value))
        description_p = widgets.HTML(value='<b>Irregularidad en Planta</b>')
        i_planta = widgets.VBox([description_p, i_torsion, i_tosion_e, i_esquinas, i_disc_diaf, i_no_paral])

        return widgets.HBox([i_altura, i_planta])

    def show_params(self):
        self.data.periodos_suelo()
        self.data.factor_R()
        self.data.show_params()

    def select_loads(self,SapModel):
        #Guardamos la lista de los loadcases existentes
        _,load_cases,_ = SapModel.LoadCases.GetNameList()
        load_cases = [load for load in load_cases if load[0]!= '~' and load!= 'Modal']
        #inicializando valores
        try: 
            self.loads.seism_loads
        except:
            self.loads.seism_loads = {'Sismo_EstX':load_cases[-4],
                                    'Sismo_EstY':load_cases[-3],
                                    'Sismo_DinX':load_cases[-2],
                                    'Sismo_DinY':load_cases[-1]}
        if len (load_cases)>=1:
            self.Sismo_EstX = dropdown(load_cases,'Sismo Estatico en X',self.loads.seism_loads['Sismo_EstX'])
            self.Sismo_EstY = dropdown(load_cases,'Sismo Estatico en Y',self.loads.seism_loads['Sismo_EstY'])
            self.Sismo_DinX = dropdown(load_cases,'Sismo Dinámico en X',self.loads.seism_loads['Sismo_DinX'])
            self.Sismo_DinY = dropdown(load_cases,'Sismo Dinámico en Y',self.loads.seism_loads['Sismo_DinY'])
            Title_SismoX = widgets.HTML(value='<b>Dirección X</b>')
            Title_SismoY = widgets.HTML(value='<b>Dirección Y</b>')
            layout_X = widgets.VBox([Title_SismoX, self.Sismo_EstX, self.Sismo_DinX])
            layout_Y = widgets.VBox([Title_SismoY, self.Sismo_EstY, self.Sismo_DinY])
            # funcion de cambio   
            def change_s_load(change,s_load):
                if change['type'] == 'change' and change['name'] == 'value':
                        self.loads.seism_loads[s_load] = change['new']
            #Observacion en caso de cambio
            self.Sismo_EstX.observe(lambda change: change_s_load(change,'Sismo_EstX'))
            self.Sismo_EstY.observe(lambda change: change_s_load(change,'Sismo_EstY'))
            self.Sismo_DinX.observe(lambda change: change_s_load(change,'Sismo_DinX'))
            self.Sismo_DinY.observe(lambda change: change_s_load(change,'Sismo_DinY'))      

            return widgets.HBox([layout_X, layout_Y])
            
        else:
            print('NO HA INGRESADO NINGUN CASO DE CARGA EN EL MODELO')
            return None
        
    def select_base_story(self,SapModel):
        stories = SapModel.Story.GetStories_2()[2]
        self.stories_dropdown = dropdown(stories,'Piso Base',stories[0])
        self.base_story = stories[0]
        def change_base_load(change):
                if change['type'] == 'change' and change['name'] == 'value':
                        self.base_story = change['new']
        self.stories_dropdown.observe(lambda change: change_base_load(change))
                
        return self.stories_dropdown

    def show_table(self,table, column='OutputCase'):
        list_columns = tuple(table[column].unique())
        widget = dropdown(list_columns + ('sin filtro',), 'Filtro', val=list_columns[0])
        widget.observe(lambda change: change_filter(change, table, column, widget))
        f_table = table[table[column] == list_columns[0]]
        display(widget)
        display(f_table)

    def analisis_sismo(self,SapModel):
        try:
            super().analisis_sismo(SapModel)
        except:
            self.data.periodos_suelo(SapModel)
            self.data.factor_R(SapModel)
            super().analisis_sismo(SapModel)
