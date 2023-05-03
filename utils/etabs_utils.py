#from operator import index
#from re import S
import comtypes.client
import pandas as pd
import numpy as np


def connect_to_etabs():
    try:
        #create API helper object
        helper = comtypes.client.CreateObject('ETABSv1.Helper')
        helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
        #attach to a running instance of ETABS
        EtabsObject = helper.GetObject("CSI.ETABS.API.ETABSObject")
        #create SapModel object
        SapModel = EtabsObject.SapModel
        
        try:
            set_envelopes_for_dysplay(SapModel)
        except:
            EtabsObject=comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
            SapModel=EtabsObject.SapModel
            try:
                get_table(SapModel,'Modal Participating Mass Ratios')
            except:
                print('Lo sentimos no es posible concetarnos al API de ETABS')
                return None,None
        
        return EtabsObject, SapModel
        
    except:
        print('No es posible conectarse a ETABS')
        return None,None


    

def set_units(SapModel,unit):
    units = {'Ton_m_C' : 12, 'kgf_cm_C':14}
    SapModel.SetPresentUnits(units[unit])


def get_modal_data(SapModel,clean_data='true'):
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput("Modal")
    modal = SapModel.Results.ModalParticipatingMassRatios()
    modal = pd.DataFrame(modal[1:17],index= ['LoadCase', 'StepType', 'StepNum', 'Period', 'Ux', 'Uy', 'Uz', 'SumUx', 'SumUy', 'SumUz', 'Rx', 'Ry', 'Rz', 'SumRx', 'SumRy', 'SumRz']).transpose()
    if clean_data:
        modal = modal.drop(['LoadCase','StepType','StepNum','Rx', 'Ry', 'Rz', 'SumRx', 'SumRy', 'SumRz'],axis=1)

    #Masas Participativas 
    MP_x = max(modal.SumUx)

    MP_y = max(modal.SumUy)

    #Periodos Fundamentales
    mode_x = modal[modal.Ux == max(modal.Ux)].index
    period_x = modal.Period[mode_x[0]]
    Ux = modal.Ux[mode_x[0]]

    mode_y = modal[modal.Uy == max(modal.Uy)].index
    period_y = modal.Period[mode_y[0]]
    Uy = modal.Uy[mode_y[0]]

    return (modal,MP_x,MP_y,period_x,period_y,Ux,Uy)


def set_envelopes_for_dysplay(SapModel,set_envelopes=True):
    IsUserBaseReactionLocation=False
    UserBaseReactionX=0
    UserBaseReactionY=0
    UserBaseReactionZ=0
    IsAllModes=True
    StartMode=0
    EndMode=0
    IsAllBucklingModes=True
    StartBucklingMode=0
    EndBucklingMode=0
    MultistepStatic=1 if set_envelopes else 2
    NonlinearStatic=1 if set_envelopes else 2
    ModalHistory=1
    DirectHistory=1
    Combo=2
    SapModel.DataBaseTables.SetOutputOptionsForDisplay(IsUserBaseReactionLocation,UserBaseReactionX,
                                                        UserBaseReactionY,UserBaseReactionZ,IsAllModes,
                                                        StartMode,EndMode,IsAllBucklingModes,StartBucklingMode,
                                                        EndBucklingMode,MultistepStatic,NonlinearStatic,
                                                        ModalHistory,DirectHistory,Combo)

def get_table(SapModel,table_name,set_envelopes=True):
    set_envelopes_for_dysplay(SapModel,set_envelopes)
    data = SapModel.DatabaseTables.GetTableForDisplayArray(table_name,FieldKeyList='',GroupName='')
    
    if not data[2][0]:
        SapModel.Analyze.RunAnalysis()
        data = SapModel.DatabaseTables.GetTableForDisplayArray(table_name,FieldKeyList='',GroupName='')
        
    columns = data[2]
    data = [i if i else '' for i in data[4]] #reemplazando valores None por ''
    #reshape data
    data = pd.DataFrame(data)
    data = data.values.reshape(int(len(data)/len(columns)),len(columns))
    table = pd.DataFrame(data, columns=columns)
    return columns, table


def get_story_data(SapModel):
    _,story_data = get_table(SapModel,'Story Definitions')
    return story_data


def set_concrete(SapModel,fc=210):
    set_units(SapModel, 'kgf_cm_C')
    MATERIAL_CONCRETE = 2
    N_CONCRETO = "Concreto f'c =" + str(fc) + " kg/cm2"
    SapModel.PropMaterial.SetMaterial(N_CONCRETO, MATERIAL_CONCRETE)
    SapModel.PropMaterial.SetMPIsotropic(N_CONCRETO, 15000*fc**0.5 , 0.2, 0.0000055)
    IsLightweight = False
    FcsFactor = 1
    SSType = 2 #Mander
    SSHysType = 4 #Concrete
    StrainAtFc = 0.002219
    StrainUltimate = 0.005
    SapModel.PropMaterial.SetOConcrete(N_CONCRETO,fc,IsLightweight,FcsFactor,SSType,SSHysType,StrainAtFc,StrainUltimate)
    
def set_rebar(SapModel,fy=4200,fu=6300):
    set_units(SapModel, 'kgf_cm_C')
    MATERIAL_REBAR = 6
    N_REBAR = "Acero de Refuerzo f'c =" + str(fy) + " kg/cm2"
    SapModel.PropMaterial.SetMaterial(N_REBAR, MATERIAL_REBAR)
    SapModel.PropMaterial.SetMPIsotropic(N_REBAR, 2e6 , 0.2, 0.0000117)
    SSType = 1 #Simple
    SSHysType  = 1 #kinematic
    StrainAtHardening = 0.01
    StrainUltimate = 0.09
    UseCaltransSSDefaults = False
    SapModel.PropMaterial.SetORebar(N_REBAR,fy,fu,fy,fu,SSType,SSHysType,StrainAtHardening,StrainUltimate,UseCaltransSSDefaults)


def set_beam_sections(SapModel,b,h,r=5,fc=210,fy=4200):
    set_units(SapModel, 'kgf_cm_C')
    N_CONCRETO = "Concreto f'c =" + str(fc) + " kg/cm2"
    N_REBAR = "Acero de Refuerzo f'c =" + str(fy) + " kg/cm2"
    N_SECCION = f'Viga {b} x {h} cm'
    SapModel.PropFrame.SetRectangle(N_SECCION, N_CONCRETO, h, b)
    SapModel.PropFrame.SetRebarBeam(N_SECCION,N_REBAR,N_REBAR,r,r,0.0,0.0,0.0,0.0)
    
def set_column_sections(SapModel,b,h,r=5,fc=210,fy=4200):
    set_units(SapModel, 'kgf_cm_C')
    N_CONCRETO = "Concreto f'c =" + str(fc) + " kg/cm2"
    N_REBAR = "Acero de Refuerzo f'c =" + str(fy) + " kg/cm2"
    N_SECCION = f'Col {b} x {h} cm'
    SapModel.PropFrame.SetRectangle(N_SECCION, N_CONCRETO, b, h)
    Pattern = 1 #Rectangular
    ConfineType = 1 #Ties
    NumberCBars = 0 #Circular Bars
    NumberR3Bars = 3
    NumberR2Bars = 3
    RebarSize = SapModel.PropRebar.GetNameList()[1][3]
    TieSize = SapModel.PropRebar.GetNameList()[1][1]
    TieSpacingLongit = min(b,h)/2
    Number2DirTieBars = 2
    Number3DirTieBars = 2
    ToBeDesigned = False
    SapModel.PropFrame.SetRebarColumn(N_SECCION,N_REBAR,N_REBAR,Pattern,ConfineType,r,NumberCBars,NumberR3Bars,
                                      NumberR2Bars,RebarSize,TieSize,TieSpacingLongit,Number2DirTieBars,
                                      Number3DirTieBars,ToBeDesigned)

def set_shell_sections(SapModel,h,aligerado=True,fc=210):
    set_units(SapModel, 'kgf_cm_C')
    if aligerado:
        name = f'losa aligerada e= {h} cm'
        SlabType = 3
        ShellType = 3 #membrana
        MatProp = "Concreto f'c =" + str(fc) + " kg/cm2"
        Thickness = h
        SapModel.PropArea.SetSlab(name,SlabType,ShellType,MatProp,Thickness)
        SapModel.PropArea.SetSlabRibbed(name,OverallDepth=h,SlabThickness=5,StemWidthTop=10,StemWidthBot=10,
                                        RibSpacing=40,RibsParallelTo=1)

    else:
        name = f'losa llena e= {h} cm'
        SlabType = 0
        ShellType = 1 #shell thin
        MatProp = "Concreto f'c =" + str(fc) + " kg/cm2"
        Thickness = h
        SapModel.PropArea.SetSlab(name,SlabType,ShellType,MatProp,Thickness)
        

def set_wall_sections(SapModel,e,fc=210):
    set_units(SapModel, 'kgf_cm_C')
    name = f'Muro e= {e} cm'
    eWallPropType = 1
    ShellType = 1 #shell thin
    MatProp = "Concreto f'c =" + str(fc) + " kg/cm2"
    Thickness = e
    SapModel.PropArea.SetWall(name,eWallPropType,ShellType,MatProp,Thickness)


def draw_shell(SapModel,points,h,aligerado=True):
    if aligerado:
        prop_name = f'losa aligerada e= {h} cm'
    else:
        prop_name = f'losa llena e= {h} cm'
    X = points['X']
    Y = points['Y']
    Z = points['Z']
    area_obj = SapModel.AreaObj.AddByCoord(len(X),X,Y,Z)
    area_name = area_obj[3]
    SapModel.AreaObj.SetProperty(area_name,prop_name)


def draw_wall(SapModel,pi,pf,e,stories='all'):
    set_units(SapModel, 'kgf_cm_C')
    story_data = get_story_data(SapModel)
    story_data.Height = story_data.Height.astype('float64')
    story_data = story_data.sort_values(by=['Story'])
    story_data['t_height'] = story_data['Height'].cumsum()
    story_data.index = story_data.Story
    if stories == 'all':
        z1 = 0
        z2 = story_data['t_height'][-1]
    elif stories[0] not in story_data['Height']:
        z1 = 0
        z2 = story_data['t_height'][stories[1]]
    else:
        z1 = story_data['t_height'][stories[0]]
        z2 = story_data['t_height'][stories[1]]
        
    X = [pi[0],pf[0],pf[0],pi[0]]
    Y = [pi[1],pf[1],pf[1],pi[1]]    
    Z = [z1,z1,z2,z2]
    prop_name = f'Muro e= {e} cm'
    area_obj = SapModel.AreaObj.AddByCoord(len(X),X,Y,Z)
    area_name = area_obj[3]
    SapModel.AreaObj.SetProperty(area_name,prop_name)


def draw_beam(SapModel,pi,pf,b,h):
    set_units(SapModel, 'kgf_cm_C')
    Xi,Yi,Zi = pi
    Xj,Yj,Zj = pf
    propName = f'Viga {b} x {h} cm'
    SapModel.FrameObj.AddByCoord(Xi,Yi,Zi,Xj,Yj,Zj,PropName=propName)



# Generación de casos sismico
def create_seism_cases(SapModel,
                       mass_sources={'MsSrc':['x','y'],
                                     'MsSrc eX+':['x'],
                                     'MsSrc eX-':['x'],
                                     'MsSrc eY+':['y'],
                                     'MsSrc eY-':['y'],},
                       spectres={'Espectro XX':'x','Espectro YY':'y'}):
    '''
    Crea cases de sismo dinámico, 
    requiere:
    mass sources con excentricidad
    y espectros de respuestas definidos en el programa
    input: mass_sources = dict{name:[list_e_irections]}
           spectres = dict{name:direction}
    '''
    pass

# Generacion de cargas a exportar
def create_found_seism(SapModel,
                       seism_cases =   {'SDx':'x',
                                        'SDx +eY':'x',
                                        'SDx -eY':'x',
                                        'SDy':'y',
                                        'SDy +eX':'y',
                                        'SDy -eX':'y'}):
    '''
    crea cargas sísmicas equivalentes para análisis de la cimentación
    son asignadas al centro de masas (método 1)
    input:
    seism_cases: dict{case:direction}
    '''
    set_load = list(seism_cases.keys())
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_load)
    SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([]) 
    _,shear_table = get_table(SapModel,'Story Forces')
    shear_table = shear_table.query('Location == "Top"')[['Story','OutputCase','VX','VY']]

    _,mass_center = get_table(SapModel,'Centers Of Mass And Rigidity')
    mass_center = mass_center[['Story','Diaphragm','XCM','YCM']]

    shear_table = shear_table.merge(mass_center,on='Story')

    _,joint_table = get_table(SapModel,'Joint Assignments - Diaphragms')
    joint_table = mass_center.merge(joint_table,on=['Diaphragm','Story'])

    SapModel.SetModelIsLocked(False)

    #Creacion de CM
    CM_dict = {}
    for story in shear_table['Story'].unique():
        X = float(shear_table.query('Story==@story').iloc[0,5])
        Y = float(shear_table.query('Story==@story').iloc[0,6])
        Z = SapModel.PointObj.GetCoordCartesian(
            joint_table.query('Story == @story').iloc[0,5])[2]
        diaph = joint_table.query('Story == @story').iloc[0,1]
        CM_dict[story] = SapModel.PointObj.AddCartesian(X,Y,Z)[0]
        SapModel.PointObj.SetDiaphragm(CM_dict[story],3,diaph)

    #Creación de cargas
    for load in seism_cases.keys():
        data = shear_table.query('OutputCase==@load')
        data = data.assign(FX=data.loc[:,'VX'].astype(float) - data.loc[:,'VX'].astype(float).shift(1).fillna(0),
                           FY=data.loc[:,'VY'].astype(float) - data.loc[:,'VY'].astype(float).shift(1).fillna(0))
        
        SapModel.LoadPatterns.Add('f ' +load,5)
        
        for story, p_name in CM_dict.items():
            VX = data.query('Story==@story')['FX'].iloc[0]
            VY = data.query('Story==@story')['FY'].iloc[0]
            if seism_cases[load] == 'x':
                SapModel.PointObj.SetLoadForce(p_name,'f ' +load,[VX,0,0,0,0,0],Replace=True)
            elif seism_cases[load] == 'y':
                SapModel.PointObj.SetLoadForce(p_name,'f ' +load,[0,VY,0,0,0,0],Replace=True)



def create_found_seism_2(SapModel,
                         seism_modal_cases =   {'SDx':('Modal','x'),
                                                'SDx +eY':('Modal +eY','x'),
                                                'SDx -eY':('Modal -eY','x'),
                                                'SDy':('Modal','y'),
                                                'SDy +eX':('Modal +eX','y'),
                                                'SDy -eX':('Modal -eX','y')}):
    
    '''
    crea cargas sísmicas equivalentes para análisis de la cimentación
    combos equivalentes a partir del modo 1 (mérodo 2)
    input:
    seism_modal_cases: dict{case:(modal_name,direction)}
    '''

    #Identificamos los modos principales
    _,modal = get_table(SapModel,'Modal Participating Mass Ratios')
    modal = modal[['Case','Mode','UX','UY','RZ']]
    modal['Mode'] = modal.Mode.astype(int)
    modal['UX']=modal.UX.astype(float)
    mode_x = str(modal[modal.UX == max(modal.UX)].Mode.iloc[0])
    modal['UY']=modal.UY.astype(float)
    mode_y = str(modal[modal.UY == max(modal.UY)].Mode.iloc[0])

    #Cálculo de los momentos de volteo
    set_load = list(seism_modal_cases.keys()) + [i[0] for i in seism_modal_cases.values()]
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_load)
    SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([])                          
    _, table = get_table(SapModel,'Base Reactions')
    table = table[['OutputCase','StepNumber','MX','MY']].query('StepNumber==@mode_x or StepNumber==@mode_y or StepNumber==""')
    table['over_moment'] = np.maximum(abs(table['MX'].astype(float)), abs(table['MY'].astype(float)))
    table = table[['OutputCase','StepNumber','over_moment']]
    
    #Calculo del factor de amplificacion en tuplas
    eq_factor = pd.DataFrame([(load,
                            case:=seism_modal_cases[load][0],
                            mode:=mode_x if seism_modal_cases[load][1] == 'x' else mode_y,
                            (table.query('OutputCase==@load')['over_moment'].iloc[0] /
                            table.query('OutputCase==@case and StepNumber==@mode')['over_moment'].iloc[0]))  
                            for load in seism_modal_cases.keys()],
                            columns=['load','case','mode','factor'])
    
    SapModel.SetModelIsLocked(False)
    #Creación de combos
    for load in seism_modal_cases.keys():
        case = seism_modal_cases[load][0]
        mode = int(eq_factor.query('load==@load').iloc[0,2])
        factor = eq_factor.query('load==@load').iloc[0,3]
        SapModel.RespCombo.Add('found '+load,0)
        SapModel.RespCombo.SetCaseList_1('found '+load,0,case,mode,factor)


if __name__ == '__main__':
    _,SapModel = connect_to_etabs()
    #SapModel.SetModelIsLocked(False)
    #print(set_envelopes_for_dysplay(SapModel))
    #_,table = get_table(SapModel,'Story Forces')

    create_found_seism_2(SapModel,seism_modal_cases =   {'SDx':('Modal','x'),
                                                       'SDy':('Modal','y')})

