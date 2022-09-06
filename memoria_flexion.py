from pylatex import Document, Section, Subsection
from pylatex.utils import NoEscape, bold

def datos(b,h,r,fc,beta_1,fy):
    d = h-r
    text = r'Geometría \\'
    text += 'b = {} \\\  h = {} \\\ r = {} \\\  d = {} \\\ '.format(b,h,r,d)
    text += r'\\Concreto \\'
    text += r"$ f'_{c} = " + str(fc) + r"kg/cm^{2} \\"
    text += r"E_{c} = " + '{:.2f}'.format(15000*fc**0.5) + r"kg/cm^{2} \\"
    text += r"\beta_{1} = " + '{:.2f}'.format(beta_1) + r"\\ $"
    text += r'\\Acero \\'
    text += r" $ f_{y} = " + str(fy) + r"kg/cm^{2} \\"
    text += r"E_{s} = " + '{}'.format(2000000) + r"kg/cm^{2} $ "
    return text
            
def acero_minimo(rho_min, As_min):
    text = r'$ \rho_{min} = \frac{0.70 \sqrt{fc}}{fy} = ' + '{:.4f}'.format(rho_min) + r'\\'
    text += r'As_{min} = \frac{0.70 \sqrt{fc}}{fy}*b*d = ' + '{:.2f}'.format(As_min) + r'cm^{2} $ \\'
    return text

def acero_maximo(rho_b, As_max):
    text = r'$ \rho_{b} = \frac{0.85 * fc * \beta_{1}} {fy} * \frac{6000}{6000+fy} = ' + '{:.4f}'.format(rho_b) + r'\\'
    text += r'\rho_{max} = 0.75*\rho_{b} = ' + '{:.4f}'.format(rho_b*0.75) + r'\\'
    text += r'As_{max} = \rho_{b}*b*d = ' + '{:.2f}'.format(As_max) + r'cm^{2} $ \\'
    return text

def acero_dis(Mu,R_n,rho_dis,As_dis):
    text = r'$ Mu = ' + '{:.2f}'.format(Mu/10**5) + r'ton-m \\ '
    text += r'R_{n} = \frac{Mu}{\phi*b*d^{2}} = ' + '{:.4f}'.format(R_n) + r'\\ '
    text += r"\rho_{dis} = \frac {0.85*f_{c}}{fy} \left( 1 - \sqrt{1- \frac{2*R_{n}}{0.85*f'_{c}}}  \right) = " + "{:.4f} ".format(rho_dis) + r" \\ "
    text += r"As_{dis} = \rho_{dis}*b*d = " + '{:.2f}'.format(As_dis) + r"cm^{2} \\ $"
    return text

def corte(Vu,V_max, V_c,Vs,estribo, A_estribo, S, Vp,S_max,Lo,So, espaciamiento):
    text = r'Cortante máximo: \\'
    text += r"$ V_{max} = \phi=2.1*\sqrt{f'_{c}}*b*d = " + '{:.2f}'.format(Vu) +r'(Ton) \\ $'
    text += r"$ V_{u} = " + '{:.2f}'.format(Vu) + r" (Ton) < V_{max} = " +'{:.2f}'.format(V_max) + r' (Ton) ... Ok \\$'

    text += r'\\ Cortante que absorbe el Concreto: \\'
    text += r"$ V_{c}=\phi*0.53*\sqrt{f'_{c}}*b*d = " + '{:.2f}'.format(V_c) +r'(Ton) \\$'

    if Vs == 0:
        text += r"\\$ V_{u} = " + '{:.2f}'.format(Vu) + r" (Ton) < V_{c} = " +'{:.2f}'.format(V_c) + r' (Ton) \\$'
        text += r'El concreto es capaz de absorber todo el corte. \\'
    else:
        text += r'\\Cortante que absorbe el acero:'
        text += r'\\ $ V_{s} = V_{u} - V_{c} = '+ '{:.2f}'.format(Vs) +r'(Ton) \\$'
        text += r'\\ Espaciamiento de estribos: \\'
        text += r' Usando acero de $\phi = ' + estribo + r'$  $(A_{v} = ' + '{:.2f}'.format(A_estribo) + r' cm^{2}) $\\'
        text += r'$ S = \frac{\phi*A_{v}*f_{y}*d}{V_{s}} = ' +'{:.2f}'.format(S) + r' cm \\$'
    

    text += r'\\ Espaciamiento máximo: \\'
    text += r"$ V_p = 1.1*\phi*\sqrt{f'_{c}}*b*d $ = " +'{:.2f}'.format(Vp) + r' Ton\\'

    if Vs > Vp:
        text += r"$ V_{s} = " + '{:.2f}'.format(Vs) + r" (Ton) > V_{p} = " +'{:.2f}'.format(Vp) + r' (Ton) \\$'
        text += r'\therefore Corte Alto \\'
        text += r'$ S_{max} $ = min(d/4, 30 cm) = min(' + '{:.2f} cm, {:.2f} cm'.format(S_max[0],S_max[1]) + r') = ' + '{:.2f} cm'.format(min(S_max)) + r'$'
    else:
        text += r"$ V_{s} = " + '{:.2f}'.format(Vs) + r" (Ton) < V_{p} = " +'{:.2f}'.format(Vp) + r' (Ton) \\$'
        text += r'$\therefore$ Corte Bajo \\'
        text += r'$ S_{max} $ = min(d/2, 60 cm) = min(' + '{:.2f} cm, {:.2f} cm'.format(S_max[0],S_max[1]) + r') = ' + '{:.2f} cm \\\ '.format(min(S_max))

    text += r'\\ Zona de confinamiento: \\'
    text += r'$L_{o}$ = 2d =' + '{:.2f}'.format(Lo) + r' cm \\'
    text += r'Espaciamiento en Zona de Confinamiento: \\'
    text += r'$S_{o}$ = min(d/4, $8d_{varilla}, 24d_{estribo}$, 30 cm) \\'
    text += r'$S_{o}$ = min(' +'{:.2f} cm,{:.2f} cm, {:.2f} cm, {:.2f} cm) = '.format(So[0],So[1],So[2],So[3]) + '{:.2f} cm \\\ '.format(min(So))

    text += r'\\ Armado de Estribos: \\'
    text += r'$\phi$' + estribo + '\": '
    for i in espaciamiento:
        text += '{} @ {}cm '.format(i[0],i[1])

    return text


if __name__ == '__main__':
    doc = Document()
    text = corte(6.77,23.28,5.88,6.77-5.88,'3/8',1.42,15.2,1.5,[35,60],40,[9,15,17,30],((1,5),(10,10),('R',20)))
    doc.append(NoEscape(text))
    doc.generate_pdf('Prueba corte')
