import numpy as np
import math
import matplotlib as plt

def def_units():
    global N , m, cm, Pa, MPa, pulg
    N = 1
    m = 1
    cm = m/100
    Pa = 1
    MPa = 10**6*Pa
    pulg = 2.54 *m / 100


def def_rebar():
    global d_3,d_4,d_5,d_6,d_8,A_3,A_4,A_5,A_6,A_8
    d_3 = 3/8 * pulg
    d_4 = 1/4 * pulg
    d_5 = 5/8 * pulg
    d_6 = 3/4 * pulg
    d_8 = 1 * pulg
    
    A_3 = d_3 ** 2 /4 * math.pi
    A_4 = d_4 ** 2 /4 * math.pi
    A_5 = d_5 ** 2 /4 * math.pi
    A_6 = d_6 ** 2 /4 * math.pi
    A_8 = d_8 ** 2 /4 * math.pi
    
def_units()
def_rebar()

def create_rebar_matrix(d_p,d_s,n_f,n_c):
    reb_mat = [d_p] + [d_s]*(n_c-2) + [d_p]
    for i in range(n_f -2 ):
        fila = [d_s] + [0]*(n_c-2) + [d_s]
        reb_mat = np.vstack([reb_mat,fila])
    fila = [d_p] + [d_s]*(n_c-2) + [d_p]
    reb_mat = np.vstack([reb_mat,fila])
    return reb_mat

def dist_vector(b,r,d_p,d_st,n):
    sep = (b-2*(r+d_st)-d_p)/(n-1)
    reb_vect = [r+d_p/2+d_st+i*sep for i in range(n)]
    return np.array(reb_vect)

def def_betha(fc):
    if fc <= 28*MPa:
        return 0.85
    elif 28*MPa < fc & fc < 55 * MPa:
        return 0.85 - 0.05*(fc-28*MPa)/(7*MPa)
    else:
        return 0.65
    
def def_phi(c,d_t,eps_u,eps_y):
    if c==0:
        return 0.9
    eps_t = (c-d_t)/c*eps_u
    phi = 0.65+0.25*(abs(eps_t)-eps_y)/0.003
    if phi < 0.65:
        return 0.65
    elif phi > 0.9:
        return 0.9
    else:
        return phi
    
def vector_phi(C,d_t,eps_u,eps_y):
    vect_phi = [def_phi(c,d_t,eps_u,eps_y) for c in C]
    return np.array(vect_phi)

#esfuerzo en cada fila de acero:
def stress_f(x,c,eps_u,Es,fy):
    if c==0:
        return -fy
    fs = eps_u*(c-x)/c*Es
    if abs(fs) > fy:
        return math.copysign(fy, fs)
    else:
        return fs
    
def vect_stress_f(dist_vect,c,eps_u,Es,fy):
    fs_vect = [stress_f(x,c,eps_u,Es,fy) for x in dist_vect]
    return np.array(fs_vect)

def matrix_fs(C,dist_vect,eps_u,Es,fy):
    mat_fs = [vect_stress_f(dist_vect,c,eps_u,Es,fy) for c in C]
    return np.array(mat_fs)

def comp_area(b,h,a,theta):
    if theta == 0:
        return a*h,a/2,h/2
    elif theta == math.pi/2:
        return a*b,b/2,a/2
    cost = math.cos(theta)
    sint = math.sin(theta)
    tant = math.tan(theta)
    if (a<=b*cost) & (a<=h*sint):
        A_c = a**2/(2*sint*cost)
        x_c = a/(3*cost)
        y_c = a/(3*sint)
    elif (a<=h*sint) & ~(a<=b*cost):
        A_c = a*b/sint - b**2/(2*tant)
        x_c = (a*b**2/(2*sint)-b**3/(3*tant))/A_c
        y_c = (a**2*b/(2*sint**2)-b**2/(2*tant)*(a/sint-b/(3*tant)))/A_c
    elif ~(a<=h*sint) & (a<=b*cost):
        A_c = a*h/cost - h**2*tant/2
        y_c = (a*h**2/(2*cost)-h**3*tant/3)/A_c
        x_c = (a**2*h/(2*cost**2)-h**2*tant/2*(a/cost-h*tant/3))/A_c
    else:
        aux = h*sint+b*cost-a
        A_c = b*h - aux**2/(2*sint*cost)
        x_c = (b**2*h/2-aux**2/(2*sint*cost)*(b-aux/(3*cost)))/A_c
        y_c = (b*h**2/2-aux**2/(2*sint*cost)*(h-aux/(3*sint)))/A_c
    
    return A_c, x_c, y_c
    
def vect_comp_area(b,h,a,theta):
    vect_A_comp = []
    vect_c_x = []
    vect_c_y = []
    for a_i in a:
        A_c,x_c,y_c = comp_area(b,h,a_i,theta)
        vect_A_comp.append(A_c)
        vect_c_x.append(x_c)
        vect_c_y.append(y_c)
    return np.array(vect_A_comp),np.array(vect_c_x),np.array(vect_c_y)

def ax_force_n(A_comp,rsp,fc):
    return 0.85*fc*A_comp+rsp

def vect_ax_force_n(vect_A_comp,rsp,fc):
    vect_Pn = []
    for i,A_comp in enumerate(vect_A_comp):
        vect_Pn.append(ax_force_n(A_comp,rsp[i],fc))
    return np.array(vect_Pn)

def momemtum_n(A_comp,x_c,rsm,fc,b,theta):
    return 0.85*fc*A_comp*(b/2-x_c)+rsm

def vect_momentum_n(A_comp,x_c,rsm,fc,b,theta):
    vect_Mn = []
    for i,A_comp_i in enumerate(A_comp):
        vect_Mn.append(momemtum_n(A_comp_i,x_c[i],rsm[i],fc,b,theta))
    return np.array(vect_Mn)

def flex_comp_data(fc,eps_u,fy,Es,eps_y,b,h,r,d_p,d_s,d_st,n_f,n_c,phi,theta):
    Ag = b*h
    reb_matx = create_rebar_matrix(d_p,d_s,n_f,n_c)
    area_matx = reb_matx**2*math.pi/4
    area_vect = area_matx.flatten()
    Aref = area_matx.sum()
    dist_vect_x = dist_vector(b, r, d_p, d_st,n_c)
    dist_vect_y = dist_vector(h, r, d_p, d_st,n_f)
    P_n = 0.85*fc*(Ag-Aref)+Aref*fy
    phiP_n = phi*0.8*P_n
    betha = def_betha(fc)
    theta = math.radians(theta)
    l = b*math.cos(theta)+h*math.sin(theta)
    a = np.array([i/100*l for i in range(100)])
    c = a/betha
    dist_vect_x_rot = dist_vect_x*math.cos(theta)
    dist_vect_y_rot = dist_vect_y*math.sin(theta)
    dist_matx = np.array([i+dist_vect_x_rot for i in dist_vect_y_rot])
    dist_vect = dist_matx.flatten()
    matx_fs = matrix_fs(c,dist_vect,eps_u,Es,fy)
    d_t = dist_vect.max()
    vect_phi = vector_phi(c,d_t,eps_u,eps_y)
    rsp = np.dot(matx_fs,area_vect)
    dist_list_x = np.array([dist_vect_x for _ in dist_vect_y]).flatten()
    dist_list_y = np.array([i for i in dist_vect_y for _ in dist_vect_x])
    dist_CM_x = b/2-dist_list_x
    dist_CM_y = h/2-dist_list_y
    rsm_x = np.dot(matx_fs*area_vect,dist_CM_x)
    rsm_y = np.dot(matx_fs*area_vect,dist_CM_y)
    A_c,x_c,y_c = vect_comp_area(b,h,a,theta)
    vect_Pn = vect_ax_force_n(A_c,rsp,fc)
    vect_phi_Pn = vect_phi*vect_Pn
    vect_phi_Pn = np.array([i if i < phiP_n else phiP_n for i in vect_phi_Pn])
    vect_Mn_x = vect_momentum_n(A_c,x_c,rsm_x,fc,b,theta)
    vect_Mn_y = vect_momentum_n(A_c,y_c,rsm_y,fc,h,theta)
    vect_phi_Mn_x = vect_phi*vect_Mn_x
    vect_phi_Mn_y = vect_phi*vect_Mn_y
    
    return vect_Pn, vect_phi_Pn, vect_Mn_x, vect_Mn_y, vect_phi_Mn_x, vect_phi_Mn_y
  
def plot_flex_comp(vect_Pn,vect_Mn_x,vect_Mn_y,ax):
    ax.plot(vect_Mn_x/10**6,vect_Mn_y/10**6, vect_Pn/1000
            ,linestyle = ':',alpha=0.7,color='#23987C')
    ax.plot(-vect_Mn_x/10**6,-vect_Mn_y/10**6, vect_Pn/1000
            ,linestyle = ':',alpha=0.7,color='#23987C')
    ax.plot(-vect_Mn_x/10**6,vect_Mn_y/10**6, vect_Pn/1000
            ,linestyle = ':',alpha=0.7,color='#23987C')
    ax.plot(-vect_Mn_x/10**6,vect_Mn_y/10**6, vect_Pn/1000
            ,linestyle = ':',alpha=0.7,color='#23987C')
    
  
if __name__ == '__main__':
    def_units()
    def_rebar()
    fc=21*MPa
    d_p = 0.015875
    d_s = 0.015875
    d_st = 0.009525
    n_f = 6
    n_c = 3
    reb_mat = create_rebar_matrix(d_p,d_s,n_f,n_c)
    A_mat = reb_mat**2/4*math.pi
    A_ref = reb_mat.sum()
    b=0.35
    h=0.75
    r=0.04
    dist_vect_x = dist_vector(b, r, d_p, d_st,n_c)
    dist_vect_y = dist_vector(h, r, d_p, d_st,n_f)  
    betha = def_betha(fc)
    c = 0.35
    d_t = dist_vect_x[-1]
    eps_u = 0.003
    eps_y = 0.0021
    phi = def_phi(c,d_t,eps_u,eps_y)
    fy = 420*MPa
    Es = 200000*MPa
    x=0.2925375
    fs = stress_f(eps_u,c,x,Es,fy)
    fs_vect = vect_stress_f(dist_vect_y, c, eps_u, Es, fy)
    a = np.dot(fs_vect,A_mat).sum()
    a_x = np.array([i/100*b for i in range(101)])
    C_x = a_x/betha
    mat_fsx = matrix_fs(C_x,dist_vect_x,eps_u,Es,fy)/10**6
    theta = math.radians(10)
    c = 40*cm
    X = comp_area(b,h,c,theta)
    l = b*math.cos(theta)+h*math.sin(theta)
    #a = np.array([i/100*l for i in range(100)])
    a = np.array([0,5,10,15,20,25,30,40,45])*cm
    x_A_c,x_c,y_c = vect_comp_area(b,h,a,theta)
    
    

