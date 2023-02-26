#from operator import index
#from re import S
import comtypes.client
import pandas as pd



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
            get_table(SapModel,'Modal Participating Mass Ratios')
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


def get_table(SapModel,table_name):
    
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
    MultistepStatic=1
    NonlinearStatic=1
    ModalHistory=1
    DirectHistory=1
    Combo=2
    SapModel.DataBaseTables.SetOutputOptionsForDisplay(IsUserBaseReactionLocation,UserBaseReactionX,
                                                        UserBaseReactionY,UserBaseReactionZ,IsAllModes,
                                                        StartMode,EndMode,IsAllBucklingModes,StartBucklingMode,
                                                        EndBucklingMode,MultistepStatic,NonlinearStatic,
                                                        ModalHistory,DirectHistory,Combo)
    data = SapModel.DatabaseTables.GetTableForDisplayArray(table_name,FieldKeyList='',GroupName='')
    
    if not data[2][0]:
        SapModel.Analyze.RunAnalysis()
        data = SapModel.DatabaseTables.GetTableForDisplayArray(table_name,FieldKeyList='',GroupName='')
        
    columns = data[2]
    data = data[4]
    #reshape data
    j = 0
    fila = list()
    table = list()
    for i in data:
        fila.append(i)
        j += 1
        if j == len(columns):
            j = 0
            table.append(fila)
            fila = []
    #convert to dataframe
    table = pd.DataFrame(table, columns=columns)
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


if __name__ == '__main__':
    pass