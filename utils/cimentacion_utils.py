import sys
import os
sys.path.append(os.getcwd())
import pandas as pd
from utils import etabs_utils as etb
# import matplotlib.pyplot as plt
import numpy as np
# from io import BytesIO
# from PIL import Image

def create_found_seism(SapModel):
    seism_cases = {'SDx':'x',
                    'SDx +eY':'x',
                    'SDx -eY':'x',
                    'SDy':'y',
                    'SDy +eX':'y',
                    'SDy -eX':'y'}
        
    set_load = list(seism_cases.keys())
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(set_load)
    SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay([]) 
    _,shear_table = etb.get_table(SapModel,'Story Forces')
    shear_table = shear_table.query('Location == "Top"')[['Story','OutputCase','VX','VY']]

    _,mass_center = etb.get_table(SapModel,'Centers Of Mass And Rigidity')
    mass_center = mass_center[['Story','Diaphragm','XCM','YCM']]

    shear_table = shear_table.merge(mass_center,on='Story')

    _,joint_table = etb.get_table(SapModel,'Joint Assignments - Diaphragms')
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





def create_found_seism_2(SapModel):
    seism_modal_cases = {'SDx':('Modal','x'),
                    'SDx +eY':('Modal +eY','x'),
                    'SDx -eY':('Modal -eY','x'),
                    'SDy':('Modal','y'),
                    'SDy +eX':('Modal +eX','y'),
                    'SDy -eX':('Modal -eX','y')}


    #Identificamos los modos principales
    _,modal = etb.get_table(SapModel,'Modal Participating Mass Ratios')
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
    _, table = etb.get_table(SapModel,'Base Reactions')
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
    _,SapModel = etb.connect_to_etabs()
    create_found_seism(SapModel)
    create_found_seism_2(SapModel)