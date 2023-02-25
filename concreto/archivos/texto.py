datos = r'''
\textbf{Dimensiones de la viga} \\
Ancho:              b = var_b cm\\
Peralte:            h = var_h cm\\
Recubrimiento:      r = var_r cm\\
Peralte efectivo:   d = var_d cm\\
Luz libre:          $l_{n}$ = var_ln cm\\
\\
\textbf{Materiales:}\\
\textbf{Concreto:}\\
Resistencia a compresión:       $f'_{c}$ = var_fc $kg/cm^{2}$ \\
Deformación unitaria última:    $\epsilon_{c}$ = var_eps_c \\
Peso específico del concreto:   $\gamma_{c}$ = var_gamma_c $kg/cm^{2}$\\
Módulo de elasticidad:          $E_{c}$ = var_Ec $kg/cm^{2}$\\
\\
\textbf{Acero de Refuerzo:}\\       
Módulo de elasticidad:      $E_{s}$ = var_Es $kg/cm^{2}$\\
Esfuerzo de fluencia:       $f'_{y}$ = var_fy $kg/cm^{2}$ \\
Deformación de fluencia:    $\epsilon_{s}$ = var_eps_s \\
'''

variables = {
    'b':25,
    'h':45,
    'r':5,
    'ln':540,
    'fc':210,
    'eps_c':0.003,
    'gamma_c':2400,
    'Es': 2e6,
    'fy': 4200,
    'eps_s':0.0021
    }

variables['d'] = variables['h']-variables['r']
variables['Ec'] = round(15000*variables['fc']**0.5,3)


# def datos(b,h,r,fc,beta_1,fy):
#     d = h-r
#     text = r'Geometría \\'
#     text += 'b = {} \\\  h = {} \\\ r = {} \\\  d = {} \\\ '.format(b,h,r,d)
#     text += r'\\Concreto \\'
#     text += r"$ f'_{c} = " + str(fc) + r"kg/cm^{2} \\"
#     text += r"E_{c} = " + '{:.2f}'.format(15000*fc**0.5) + r"kg/cm^{2} \\"
#     text += r"\beta_{1} = " + '{:.2f}'.format(beta_1) + r"\\ $"
#     text += r'\\Acero \\'
#     text += r" $ f_{y} = " + str(fy) + r"kg/cm^{2} \\"
#     text += r"E_{s} = " + '{}'.format(2000000) + r"kg/cm^{2} $ "
#     return text


def replace_variables(text,variables):
    for var, value in variables.items():
        var = 'var_' + var
        value = str(value)
        text = text.replace(var,value)
        
    return text