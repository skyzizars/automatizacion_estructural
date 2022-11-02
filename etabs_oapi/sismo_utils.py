import pandas as pd
import etabs_utils as etb
import sys

#Programado para etabs 2019

#Cálculo del exponente de altura
def get_k(T):
    if T < 0.5:
        return 1
    elif 0.75+0.5*T < 2:
        return 0.75+0.5*T
    else:
        return 2

#Cálculo del Factor C
def get_C(T,Tp,Tl):
    if T < Tp:
        return 2.5
    elif T < Tl:
        return 2.5*Tp/T
    else:
        return 2.5*Tp*Tl/T**2

#Cálculo del coeficiente de sismo estático
def get_ZUCS_R(C,Z,U,S,R):
    if C/R>0.11:
        return Z*U*C*S/R
    else:
        return Z*U*S*0.11

#Sismo Estático
def ana_modal(SapModel):
    modal, MP_x,MP_y,T_x,T_y,Ux,Uy = etb.get_modal_data(SapModel)
    
    #Reporte
    print("\nAnálisis Modal:")
    print('Masa Paiticipativa X: {0:.2f}'.format(MP_x))
    if MP_x<0.9:
        print('---Aumentar Grados de Libertad: {0:.2f} < 0.9'.format(MP_x))
    print('Masa Paiticipativa Y: {0:.2f}'.format(MP_y))
    if MP_y<0.9:
        print('---Aumentar Grados de Libertad {0:.2f} < 0.9'.format(MP_y))
    print('Periodo y deformaxión X: Tx={0:.3f}'.format(T_x)+', Ux={0:.3f}'.format(Ux))
    print('Periodo y deformaxión Y: Ty={0:.3f}'.format(T_y)+', Uy={0:.3f}'.format(Uy))
    
    data = {'modal':modal,'T_x':T_x,'T_y':T_y}
    
    return data

def sismo_estatico(SapModel,N,Z,U,S,Tp,Tl,Ip,Ia,R_o):
    data = {}
    data['R'] = R_o*Ip*Ia
    data['modal'], data['T_x'], data['T_y'] = ana_modal(SapModel).values()
    data['k_x'] = get_k(data['T_x'])
    data['k_y'] = get_k(data['T_y'])
    data['C_x'] = get_C(data['T_x'],Tp,Tl)
    data['C_y']  = get_C(data['T_y'],Tp,Tl)
    data['ZUCS_Rx'] = get_ZUCS_R(data['C_x'],Z,U,S,data['R'])
    data['ZUCS_Ry'] = get_ZUCS_R(data['C_y'],Z,U,S,data['R'])

    #Resumen
    print('Factor de Reduccion con Irregularidades: R={}'.format(data['R']))
    print('C en X: {0:.2f}'.format(data['C_x']))
    print('C en Y: {0:.2f}'.format(data['C_y']))

    print('\nCoeficiente de sismo estático X: {0:.3f}'.format(data['ZUCS_Rx']))
    print('Coeficiente de sismo estático Y: {0:.3f}'.format(data['ZUCS_Ry']))
    print('Exponente de altura X: {0:.2f}'.format(data['k_x']))
    print('Exponente de altura Y: {0:.2f}'.format(data['k_y']))

    return data


#Revisión por Torsión

def get_max_over_avg_drifts(SapModel,loads):
    SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(loads)
    _ , table = etb.get_table(SapModel,'Story Max Over Avg Drifts')
    table = table[(table.StepType == 'Max') | (table.StepType.isnull())]
    table = table[['Story','OutputCase','Direction','Max Drift','Avg Drift','Ratio']]
    return table

def create_rev_torsion_table(SapModel,loads,max_drift,R,is_regular=True):
    table = get_max_over_avg_drifts(SapModel,loads)
    stories  = etb.get_story_data(SapModel)
    table = table.merge(stories[['Story','Height']], on = 'Story')
    if is_regular:
        table['Drifts']=table['Max Drift'].apply(lambda x:float(x))/table['Height'].apply(lambda x:float(x))*0.75*R
    else:
        table['Drifts']=table['Max Drift'].apply(lambda x:float(x))/table['Height'].apply(lambda x:float(x))*0.85*R
    table['Drift < Dmax/2'] = table['Drifts'] < max_drift/2
    tor_reg = (table['Drift < Dmax/2']) | (table['Ratio'].apply(lambda x: float(x)) < 1.3)
    table['tor_reg'] = tor_reg.apply(lambda x: 'Regular' if x else 'Irregular')

    return table

#Piso Blando

def obtener_despl_rel(data):
    data = data.reset_index(drop=True)
    data = data.apply(lambda x:float(x))
    despl = data.diff().apply(lambda x:-x)
    despl = despl.drop(0,axis=0)
    despl[len(despl)+1] = data[len(data)-1]
    despl = despl.reset_index(drop=True)
    return despl

def get_k_prom(data):
    k_prom = []
    s1 = 0
    s2 = 0
    s3 = 0
    for i,j in enumerate(data):
        s1 += j
        if i >= 1:
            s2 += j
        if i >= 2:
            s3 += j
        if i<2:
            k_prom.append(0)
        else:
            k_prom.append(s1/3)
            s1=s2
            s2=s3
            s3=0
    k_prom.pop()
    k_prom.insert(0,0)
    return k_prom

def down_1(data):
    data = data.drop(len(data)-1,axis=0)
    data = pd.concat([pd.DataFrame([0]),data],ignore_index=True)
    return data
      
def rev_piso_blando(SapModel,loads):
    _,data = etb.get_table(SapModel,'Diaphragm Center Of Mass Displacements')
    data = data[(data.StepType == 'Max') | (data.StepType.isnull())]
    data = data[['Story','OutputCase','UX','UY']]
    table = pd.DataFrame()

    _,data_forces = etb.get_table(SapModel,'Story Forces')
    data_forces = data_forces[((data_forces.StepType == 'Max') | (data_forces.StepType.isnull())) & (data_forces.Location=='Top')]
    data_forces = data_forces[['Story','OutputCase','VX','VY']]

    for load in loads:
        load_data = data[data.OutputCase == load]
        load_data = load_data.reset_index(drop=True)
        URX = obtener_despl_rel(load_data.UX)
        URY = obtener_despl_rel(load_data.UY)
        load_data['URX'] = URX
        load_data['URY'] = URY
        load_data = load_data.merge(data_forces)

        lat_rig_1 = abs(load_data.VX.apply(lambda x:float(x))/load_data.URX.apply(lambda x:float(x)))
        lat_rig_2 = abs(load_data.VY.apply(lambda x:float(x))/load_data.URY.apply(lambda x:float(x)))
        lat_rig = lat_rig_1 + lat_rig_2
        load_data['lat_rig(k)'] = lat_rig

        load_data['0.7_prev_k'] = down_1(load_data['lat_rig(k)'] *0.7)
        load_data['0.8k_prom'] = list(map(lambda x: 0.8*x ,get_k_prom(load_data['lat_rig(k)'])))

        table = pd.concat([table,load_data],ignore_index=True)


    is_reg = (table['lat_rig(k)'] > table['0.7_prev_k']) & (table['lat_rig(k)'] > table['0.8k_prom'])
    table['is_reg'] = is_reg.apply(lambda x: 'Regular' if x else 'Irregular')   

    return table

# Masa

def rev_masa(SapModel,n_sotanos,n_techos):
    _,masa = etb.get_table(SapModel,'Mass Summary by Story')
    masa['Mass'] = masa.UX
    masa = masa[['Story','Mass']]
    
    stories = masa.Story
    sotano = list(stories[-1-n_sotanos:])
    azotea = list(stories[0:n_techos+1])

    sup_mass = []
    aux = 0
    for i,j in enumerate(masa['Mass']):
        if i == 0:
            sup_mass.append('')
            aux = float(j)*1.5
        else:
            sup_mass.append(aux)
            aux = 0
        aux = float(j)*1.5

    inf_mass = []
    aux = 0
    for i,j in enumerate(masa['Mass']):
        aux = float(j)*1.5
        if i == 0:
            pass
        else:
            inf_mass.append(aux)
            aux = 0
    inf_mass.append('')

    masa['1.5_inf_mass'] = inf_mass
    masa['1.5_sup_mass'] = sup_mass

    mask = []
    j = False
    for i in masa.Story:
        if i in sotano:
            aux = mask.pop()
            if aux == 2:
                mask.append(1)
            else:
                mask.append(0)
            mask.append(0)
            continue
        if i in azotea:
            mask.append(4)
            j = True
            continue
        if j:
            j =False
            mask.append(3)
            continue
        mask.append(2)

    story_type = []
    for  i in masa.Story:
        if  i in azotea:
            story_type.append('Azotea')
        elif i in sotano:
            story_type.append('Sotano')
        else:
            story_type.append('Piso')

    masa['story_type'] = story_type

    reg = []
    for i,j in enumerate(mask):
        if j == 4:
            masa['1.5_inf_mass'][i] = ''
            reg.append(True)
        elif j == 3:
            masa['1.5_sup_mass'][i] = ''
            reg.append(float(masa.Mass[i]) < masa['1.5_inf_mass'][i])
        elif j==2:
            reg.append( (float(masa.Mass[i]) < masa['1.5_inf_mass'][i] ) & (float(masa.Mass[i]) < masa['1.5_sup_mass'][i]))
        elif j == 1:
            masa['1.5_inf_mass'][i] = ''
            reg.append(float(masa.Mass[i]) < masa['1.5_sup_mass'][i])
        else:
            masa['1.5_sup_mass'][i] = ''
            masa['1.5_inf_mass'][i] = ''
            reg.append(True)

    masa['is_reg'] = ['Regular' if i else 'Irregular' for i in reg]

    return masa

# Derivas
def get_rev_drift(rev_torsion, max_drift):
    rev_drift = rev_torsion[['Story','OutputCase','Direction','Drifts']]
    rev_drift['Drift<max_drift'] = rev_drift['Drifts'].apply(lambda x: 'Cumple' if x < max_drift else 'No Cumple')
    return rev_drift

# Centros de Masas y Rigideces

def get_CM_CR(SapModel):
    _,rev_CM_CR = etb.get_table(SapModel,'Centers Of Mass And Rigidity')
    rev_CM_CR = rev_CM_CR[['Story','XCCM','XCR','YCCM','YCR']]
    rev_CM_CR['DifX'] = rev_CM_CR.XCCM.apply(lambda x: float(x)) - rev_CM_CR.XCR.apply(lambda x: float(x))
    rev_CM_CR['DifY'] = rev_CM_CR.YCCM.apply(lambda x: float(x)) - rev_CM_CR.YCR.apply(lambda x: float(x))
    return rev_CM_CR

# Main
def rev_sismo(SapModel,Dt,T_analisis):
    
    loads = Dt['loads']
    model_loads = etb.get_table(SapModel, 'Load Case Definitions - Summary')[1].Name
    for load in loads:
        if load not in list(model_loads):
            sys.exit(f'El caso de carga "{load}" no está definido en el modelo \n')
            
    if T_analisis == 1:
        return ana_modal(SapModel)
    elif T_analisis == 2:
        return sismo_estatico(SapModel,N=Dt['N'],Z=Dt['Z'],U=Dt['U'],S=Dt['S'],Tp=Dt['Tp'],
                       Tl=Dt['Tl'],Ip=Dt['Ip'],Ia=Dt['Ia'],R_o=Dt['R_o'])
    elif T_analisis == 3:
        R = Dt['R_o']*Dt['Ia']*Dt['Ip']
        return create_rev_torsion_table(SapModel,Dt['loads'],Dt['max_drift'],R)
    elif T_analisis == 4:
        return rev_piso_blando(SapModel,Dt['loads'])
    elif T_analisis == 5:
        return rev_masa(SapModel,Dt['n_sotanos'],Dt['n_techos']) 
    elif T_analisis == 6:
        return get_CM_CR(SapModel)
    elif T_analisis == 7:
        R = Dt['R_o']*Dt['Ia']*Dt['Ip']
        rev_torsion = create_rev_torsion_table(SapModel,Dt['loads'],Dt['max_drift'],R)
        return get_rev_drift(rev_torsion, Dt['max_drift'])
    else:
        data = {}
        data['sismo_estatico'] = sismo_estatico(SapModel,N=Dt['N'],Z=Dt['Z'],U=Dt['U'],S=Dt['S'],Tp=Dt['Tp'],
                   Tl=Dt['Tl'],Ip=Dt['Ip'],Ia=Dt['Ia'],R_o=Dt['R_o'])
        R = Dt['R_o']*Dt['Ia']*Dt['Ip']
        data['torsion_table'] = create_rev_torsion_table(SapModel,Dt['loads'],Dt['max_drift'],R)
        data['piso_blando'] = rev_piso_blando(SapModel,Dt['loads'])
        data['rev_masa'] = rev_masa(SapModel,Dt['n_sotanos'],Dt['n_techos']) 
        data['CM_CR'] = get_CM_CR(SapModel)
        rev_torsion = data['torsion_table']
        data['drifts'] = get_rev_drift(rev_torsion, Dt['max_drift'])
        return data
        
        

        