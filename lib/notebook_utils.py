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
        self.sec_change = {}
        self.openings = {}
        
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
    
    def discontinuidad_diafragma(self,sec_c=False,op=False,ap='1',sec_chang={},opns={}):
        clear_output(wait=False)
        d_diaf = []
        sec_change = check_box('cambios de sección',val=sec_c)
        openings = check_box('aperturas',val=op)
        sec_change.observe(lambda _:self.discontinuidad_diafragma(sec_change.value,openings.value,ap,self.sec_change,self.openings))
        openings.observe(lambda _:self.discontinuidad_diafragma(sec_change.value,openings.value,ap,self.sec_change,self.openings))
        d_diaf.append(sec_change)        
        
        if sec_change.value:
            des_change = widgets.HTML(value='<b>Cambios de Sección:</b>')
            val_l_a,val_e_a  = sec_chang.get('aligerado',('10','0.05'))
            val_l_m,val_e_m  = sec_chang.get('macisa',('1','0.2'))
            long_aligerado = input_box('Longitud del aligerado (m)',val=val_l_a)
            e_aligerado = input_box('Espesor del aligerado (m)',val=val_e_a)
            long_macisa = input_box('Longitud de la losa macisa (m)',val=val_l_m)
            e_macisa = input_box('Espesor de la losa macisa (m)',val=val_e_m)
            def assign_sec_change(change):
                # if change['type'] == 'change' and change['name'] == 'value':
                #     if type(change['new']) == str:
                #         try:
                #             float(change['new'])
                #         except:
                #             clear_output(wait=False)
                #             self.discontinuidad_diafragma(sec_change.value,openings.value)
                #             print('Ingrese datos numéricos')
                self.sec_change['aligerado'] = [long_aligerado.value,e_aligerado.value]
                self.sec_change['macisa'] = [long_macisa.value,e_macisa.value]
            long_aligerado.observe(lambda change:assign_sec_change(change))
            e_aligerado.observe(lambda change:assign_sec_change(change))
            long_macisa.observe(lambda change:assign_sec_change(change))
            e_macisa.observe(lambda change:assign_sec_change(change))
            assign_sec_change('')

            for i in [des_change,long_aligerado,e_aligerado,long_macisa,e_macisa]:
                d_diaf.append(i)

        d_diaf.append(openings)

        if openings.value:
            desc_openings = widgets.HTML(value='<b>Aperturas en losa:</b>')
            ap = ap if ap else '0'
            n_aperturas = input_box('Nro de aperturas (m)',val=ap)
            n_aperturas.observe(lambda _:self.discontinuidad_diafragma(sec_change.value,openings.value,n_aperturas.value,self.sec_change,self.openings))
            for i in [desc_openings,n_aperturas]:
                d_diaf.append(i)
            aperturas = []
            for i in range(int(n_aperturas.value)):
                try:
                    val_l_a,val_e_a  = opns['aperturas'][i]
                except:
                    val_l_a,val_e_a  = ['10','0.05']
                aperturas.append(input_box('Largo de apertura %i (m)'%(i+1),val=val_l_a))
                aperturas.append(input_box('Ancho de apertura %i (m)'%(i+1),val=val_e_a))
            val_a_p = opns.get('area_planta','12.5')
            area_planta = input_box('Area de la planta (m2)',val=val_a_p)
            def assign_openings():
                self.openings['area_planta'] = []
                self.openings['aperturas'] = []
                for i in range(int(n_aperturas.value)):
                    self.openings['aperturas'].append((aperturas[2*i].value,aperturas[2*i+1].value))
                self.openings['area_planta'] = area_planta.value
            
            for i in aperturas:
                i.observe(lambda _: assign_openings())
                d_diaf.append(i)
            area_planta.observe(lambda _: assign_openings())
            d_diaf.append(area_planta)
            assign_openings()
        
        display(widgets.VBox(d_diaf))

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
