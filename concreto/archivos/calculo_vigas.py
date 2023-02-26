#Unidades
m = 100
cm = 1
kg = 1
ton = 1000

# Dimensiones de Vigas
d_viga = {
    'b':20*cm,   #Ancho
    'h':70*cm,   #Peralte
    'ln':5.4*m}  #Luz Libre

#Materiales

#Concreto
conc = {
    'f_c' : 210 *kg/cm**2,      #Resistencia a compresión
    'eps_c' : 0.003,            #Deformación unitaria última
    'gamma_c' : 2.4 *ton/cm**3  #Peso especifico
    }

conc['E_c'] = 15000*(conc['f_c'])**0.5 #Módulo de elasticidad

#Acero
acero = {
    'E_s':2e6 kg/cm**2      #Módulo de elasticidad
    'fy': 4200 kg/cm**2     #Esfuerzo de fluencia
    'eps_y': 0.0021}        #Deformación unitaria de fluencia

#Factores de minoracion
phi_f = 0.9     #Flexión
phi_c = 0.85    #Corte

#Diseño por flexión


