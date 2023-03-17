import sys
import os
sys.path.append(os.getcwd())

from lib import latex_utils as ltx
from pylatex import Document, Section, Subsection,Subsubsection, Tabular, NoEscape, MiniPage, Center, MultiColumn, Table, Figure,MultiRow
from pylatex.utils import NoEscape, bold
from pylatex.package import Package
from pylatex.base_classes import Environment
from pylatex.math import Alignat
from math import ceil
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter('ignore', category=Warning)


def def_obj(o_type,*args):
    """
    Añade el método add a un objeto pylatex (o_type)
    """
    class Object(o_type):
  
        def add(self,insertion):
            self.insert(self.index('%insertion'),NoEscape(insertion+r'\\'))

    obj = Object(*args)
    obj._latex_name = str(o_type).split('.')[-1][:-2].lower()
    return obj

def mybox3(title):
    mbox = Environment()
    mbox._latex_name = 'tcolorbox'
    mbox.options = NoEscape(r'colback=gray!5!white,colframe=Maroon!75!black,fonttitle=\bfseries,title=%s'%title)
    return mbox

def mybox2(title):
    mbox = Environment()
    mbox._latex_name = 'tcolorbox'
    mbox.options = NoEscape(r'colback=gray!5!white,colframe=cyan!75!black,fonttitle=\bfseries,title=%s'%title)
    return mbox

def parametros_sitio(o_type=Subsection):
    obj = def_obj(o_type,NoEscape(r'Parámetros de sitio')) 
    obj.append(NoEscape('%insertion'))

    return obj

def factor_zona(zona,o_type=Subsubsection):
    obj = def_obj(o_type,'Factor zona')
    obj.packages.append(Package('array'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('caption'))
    
    
    df = [['4','0.45'],['3','0.35'],['2','0.25'],['1','0.10']]
    df[4-zona][1] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+df[4-zona][1]+r'}}'
    df[4-zona] = [i+r'\cellcolor[rgb]{ .949,  .949,  .949} ' for i in df[4-zona]]

    obj.append(NoEscape(r'Este factor se interpreta como la aceleración máxima horizontal en el suelo rígido con una probabilidad de 10 \% de ser excedida en 50 años'))
    obj.append(NoEscape('%insertion'))

    with obj.create(Table(position='ht!')) as tab:
        with obj.create(MiniPage(width='0.55\\textwidth')) as mp:
                mp.append(NoEscape(r'\caption{Factor de zona}'))
                with obj.create(Tabular(r'|>{\centering\arraybackslash}m{3.75cm}|>{\centering\arraybackslash}m{3.75cm}|')) as table:
                    table.add_hline()
                    table.add_row((MultiColumn(2, align='|c|', data=bold('FACTOR DE ZONA SEGÚN E-030')),))
                    table.add_hline()
                    table.add_row((NoEscape('\\textbf{ZONA}'), NoEscape('\\textbf{Z}')))
                    table.add_hline()
                    for row in df:
                            table.add_row((NoEscape(row[0]), NoEscape(row[1])))
                            table.add_hline()
        with obj.create(MiniPage(width='0.35\\textwidth')):
            with obj.create(Center()):
                obj.append(NoEscape('\\includegraphics[width=4cm]{images/mapa_zona}'))
        tab.append(NoEscape(r'\caption*{Fuente: E-030 (2018)}'))

    return obj
        

def factor_suelo(zona,suelo,o_type=Subsubsection):
    obj = def_obj(o_type,'Factor de suelo')
    obj.packages.append(Package('array'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('caption'))
    obj.packages.append(Package('slashbox'))
    
    suelo_ind = {'S0':1,'S1':2,'S2':3,'S3':4}
    data = [['4','0.80','1.00','1.05','1.10'],
            ['3','0.80','1.00','1.15','1.20'],
            ['2','0.80','1.00','1.20','1.40'],
            ['1','0.80','1.00','1.60','2.00']]
    data[4-zona][suelo_ind[suelo]] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+data[4-zona][suelo_ind[suelo]] +r'}}'
    data[4-zona] = [i+r'\cellcolor[rgb]{ .949,  .949,  .949} ' for i in data[4-zona]]
    data = [[j+r'\cellcolor[rgb]{ .949,  .949,  .949} ' if i ==suelo_ind[suelo] else j for i,j in enumerate(row)]  for row in data]
    
    obj.append(NoEscape(r'Este factor se interpreta como  un factor de modificación de la aceleración pico del suelo para un perfil determinado respecto al pefil tipo S1'))
    obj.append(NoEscape('%insertion'))

    with obj.create(Table(position='ht!')) as tab:
        tab.append(NoEscape(r'\centering'))
        tab.append(NoEscape(r'\caption{Factor de suelo}'))
        with obj.create(Tabular(r'|>{\centering\arraybackslash}m{3.75cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|')) as table:
            table.add_hline()
            table.add_row((MultiColumn(5, align='|c|', data=bold('FACTOR DE SUELO SEGÚN E-030')),))
            table.add_hline()
            table.add_row(NoEscape(r'\backslashbox{\textit{\textbf{ZONA}}}{\textit{\textbf{SUELO}}}'),bold('S0'),bold('S1'),bold('S2'),bold('S3'))
            table.add_hline()
            for row in data:
                table.add_row([NoEscape(i) for i in row])
                table.add_hline()
        tab.append(NoEscape(r'\caption*{Fuente: E-030 (2018)}'))
    
    return obj
    

def periodos_suelo(suelo,o_type=Subsubsection):
    suelo_ind = {'S0':1,'S1':2,'S2':3,'S3':4}
    
    data = [['Tp','0.30','0.40','0.60','1.00'],
            ['Tl','3.00','2.50','2.00','1.60']]
    data[0][suelo_ind[suelo]] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+data[0][suelo_ind[suelo]]+r'}}'+r'\cellcolor[rgb]{ .949,  .949,  .949} '
    data[1][suelo_ind[suelo]] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+data[1][suelo_ind[suelo]]+r'}}'+r'\cellcolor[rgb]{ .949,  .949,  .949} '
    
    obj = def_obj(o_type,'Periodos de suelo')
    obj.packages.append(Package('array'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('caption'))
    obj.packages.append(Package('float'))

    obj.append(NoEscape('%insertion'))
        
    with obj.create(Table(position='H')) as tab:
        tab.append(NoEscape(r'\centering'))
        tab.append(NoEscape(r'\caption{Periodos de suelo}'))
        with obj.create(Tabular(r'|>{\centering\arraybackslash} m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|')) as table:
            table.append(NoEscape(r'\cline{2-5}'))
            table.add_row((MultiColumn(1,align='r|',data=''),MultiColumn(4,align='c|',data=NoEscape('\\textbf{PERIODO "Tp" y "Tl" SEGÚN E-030}'))))
            table.append(NoEscape(r'\cline{2-5}'))
            table.add_row((MultiColumn(1,align='r|',data=''),MultiColumn(4,align='c|',data=NoEscape(r'\textit{\textbf{Perfil de suelo}}'))))
            table.append(NoEscape(r'\cline{2-5}'))  
            table.add_row((MultiColumn(1,align='r|',data=''),bold('S0'),bold('S1'),bold('S2'),bold('S3')))
            table.add_hline()
            for row in data:
                table.add_row([NoEscape(i) for i in row])
                table.add_hline()
        tab.append(NoEscape(r'\caption*{Fuente: E-030 (2018)}'))

    return obj


def sist_estructural(sist_x,sist_y,o_type=Subsubsection):       
    data = {'Acero':['Acero:',''],
            'Pórticos Especiales de Acero Resistentes a Momentos':['Porticos Especiales Resistentes a Momento (SMF)',8],
            'Pórticos Intermedios de Acero Resistentes a Momentos':['Porticos Intermedios Resistentes a Momento (IMF)',5],
            'Pórticos Ordinarios de Acero Resistentes a Momentos':['Porticos Ordinarios Resistentes a Momento (OMF)',4],
            'Pórticos Especiales de Acero Concénticamente Arriostrados':['Porticos Especiales Concentricamente Arrriostrados (SCBF)',7],
            'Pórticos Ordinarios de Acero Concénticamente Arriostrados':['Porticos Ordinarios Concentricamente Arrriostrados (OCBF)',4],
            'Pórticos Acero Excéntricamente Arriostrados':['Porticos Excentricamente Arriostrados (EBF)',8],
            'Concreto':['Concreto Armado:',''],
            'Pórticos de Concreto Armado':['Porticos',8],
            'Dual de Concreto Armado':['Dual',7],
            'De Muros Estructurales de Concreto Armado':['De muros estructurales',6],
            'Muros de Ductilidad Limita de Concreto Armado':['Muros de ductilidad limitada',4],
            'Albañilería Armada o Confinada':[r'\textbf{Albañilería Armada o Confinada}',3],
            'Madera':[r'\textbf{Madera}',7]}
    for sist in [sist_x,sist_y]:
        data[sist][0] = str(data[sist][0])+r'\cellcolor[rgb]{ .949,  .949,  .949} '
        data[sist][1] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+str(data[sist][1])+r'}}'+r'\cellcolor[rgb]{ .949,  .949,  .949} '
   

    obj = def_obj(o_type,'Sistema Estructural')
    obj.packages.append(Package('array'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('caption'))

    obj.append('Después de realizar el análisis sísmico se determino que los sistemas estructurales en X, Y son ')
    obj.append(NoEscape('{} y {} respectivamente'.format(sist_x,sist_y)))
    obj.append(NoEscape('%insertion'))
    
    with obj.create(Table(position='ht!')) as tab:
        tab.append(NoEscape(r'\caption{Coeficiente básico de reducción}'))
        with obj.create(Tabular(r'|>{\arraybackslash}m{10cm}| >{\centering\arraybackslash}m{4cm}|')) as table:
            table.add_hline()
            table.add_row((MultiColumn(2,align='|c|',data=bold('SISTEMAS ESTRUCTURALES')),))
            table.add_hline()
            table.add_row((bold('Sistema Estructural'),MultiColumn(1,align=NoEscape('m{4cm}|'),data=bold('Coeficiente Básico de Reducción Ro'))))
            table.add_hline()
            for row in data.values():
                if row[1]:
                    table.add_row([NoEscape(i) for i in row])
                    table.add_hline()
                else:
                    table.add_row((MultiColumn(2,align='|l|',data=bold(row[0])),))
                    table.add_hline()
        tab.append(NoEscape(r'\caption*{Fuente: E-030 (2018)}'))

    return obj
            
            

def factor_amplificacion(o_type=Subsubsection):
    obj = def_obj(o_type,'Factor de Amplificación sísmica')
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('amsmath'))
    obj.packages.append(Package('caption'))
    
    eq = r'''
    \begin{align*}
        &T< T_{P}         &   C&=2,5\cdot\left ( \frac{T_{P}}{T} \right )\\
        &T_{P}< T< T_{L}  &   C&=2,5\cdot\left ( \frac{T_{P}}{T} \right )\\
        &T> T_{L}         &   C&=2,5\cdot\left ( \frac{T_{P}\;T_{L}}{T^{2}} \right )
    \end{align*}'''
            
   
    obj.append(NoEscape('%insertion'))

    obj.append('Se determina según el artículo 14 de la E-030')
    obj.append(NoEscape(r'\setlength{\jot}{0.5cm}'))
    with obj.create(Figure(position='h!')):
        obj.append(NoEscape(r'\caption{Factor de amplificación}'))
        with obj.create(MiniPage(width=r'0.5\textwidth')):
            obj.append(NoEscape(eq))
        with obj.create(MiniPage(width=r'0.4\textwidth')):
            obj.append(NoEscape(r'\centering'))
            obj.append(NoEscape('\\includegraphics[width=6.5cm]{images/Amplificacion}'))
        obj.append(NoEscape(r'\caption*{Fuente: Muñoz (2020)}'))
    return obj


def factor_importancia(categoria,o_type=Subsubsection):
    obj = def_obj(o_type,'Factor de Importancia')
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('caption'))
    obj.packages.append(Package('xcolor'))
    obj.packages.append(Package('array'))
    obj.packages.append(Package('multirow'))
    obj.packages.append(Package('float'))
    obj.packages.append(Package('graphicx'))
    
    cat_ind = {'A1':0,'A2':1,'B':2,'C':3,'D':4}
    data = [['A Edificaciones Escenciales','A1: Establecimiento del sector salud (públicos y privados) del segundo y tercer nivel, según lo normado por el ministerio de salud.','Con aislamiento 1.0 y sin aislamiento 1.5.'],
            ['','A2: Edificaciones escenciales para el manejo de las emergencias, el funcionamiento del gobierno y en general aquellas que puedan servir de refugio después de un desastre.','1.50'],
            ['B Edificaciones Importantes ','Edificaciones donde se reúnen gran cantidad de personas tales como cines, teatros, estadios, coliseos, centros comerciales, terminales de buses de pasajeros, establecimientos penitenciarios, o que guardan patrimonios valiosos como museos y bibliotecas.',r'1.30'],
            ['C Edificaciones Comunes','Edificaciones comunes tales como: viviendas, oficinas, hoteles, restaurantes, depósitos e instalaciones industriales cuya falla no acarree peligros adicionales de incendios o fugas de contaminantes.',r'1.00'],
            ['D Edificaciones temporales','Construcciones provisionales para depósitos, casetas y otras similares.','A criterio del proyectista']]
    
    data[0][0] = r'\multirow{2}[4]{3cm}{'+data[0][0] + '}'
    data[cat_ind[categoria]][2] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{' + data[cat_ind[categoria]][2] + r'}}'
    if cat_ind[categoria] < 2:
        data[cat_ind[categoria]] = [data[cat_ind[categoria]][0]] + [i + r'\cellcolor[rgb]{1,  .949,  .8}' for i in data[cat_ind[categoria]][1:]]
    else:
        data[cat_ind[categoria]] = [i + r'\cellcolor[rgb]{ .949,  .949,  .949}' for i in data[cat_ind[categoria]]]
    data = [row[:2]+[r'\multicolumn{1}{>{\centering\arraybackslash}m{2.8cm}|}{'+row[2]+'}'] for row in data]
        
    obj.append(NoEscape('%insertion'))

    with obj.create(Table(position='H')):
        obj.append(NoEscape('\centering'))
        obj.append(NoEscape('\caption{Factor de Uso o Importancia}'))
        with obj.create(Tabular(NoEscape(r'|>{\arraybackslash}m{3cm}|m{8cm}|>{\arraybackslash}m{2.8cm}|'))) as table:
            table.add_hline()
            table.add_row((MultiColumn(3,align='|c|',data=bold('CATEGORIA DE LA EDIFICACION')),))
            table.add_hline()
            table.add_row((MultiColumn(1,align='|c|',data=bold('CATEGORIA')),MultiColumn(1,align='|c|',data=bold('DESCRIPCION')),MultiColumn(1,align='|c|',data=bold('FACTOR U'))))
            table.add_hline()
            table.add_row([NoEscape(i) for i in data[0]])
            table.append(NoEscape(r'\cline{2-3}'))
            for row in data[1:]:
                table.add_row([NoEscape(i) for i in row])
                table.add_hline()
        obj.append(NoEscape(r'\caption*{Fuente: E-030 (2018)}'))

    return obj

def tabla_resumen(Z,U,S,Tp,Tl,Rox,Roy,Ia,Ip,o_type=Subsubsection):
    obj = def_obj(o_type,'Tabla resumen de parámetros sísmicos')
    obj.packages.append(Package('float'))
    obj.packages.append(Package('array'))
    obj.append(NoEscape('%insertion'))
    Rx=Rox*Ia*Ip
    Ry=Roy*Ia*Ip
    ZUSg_Rx=Z*U*S*9.81/Rx
    ZUSg_Ry=Z*U*S*9.81/Ry
    with obj.create(Table(position='H')) as table:
        table.append(NoEscape('\centering'))
        table.add_caption('Resumen de parámetros sísmicos')
        table.append(NoEscape(r'\extrarowheight = -0.3ex'))
        table.append(NoEscape(r'\renewcommand{\arraystretch}{1.5}'))
        with table.create(Tabular(r'm{5cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|')) as tabular:
            tabular.add_hline(2,4)
            tabular.add_row('',MultiColumn(3,align='c|',data=bold("PARÁMETROS SÍSMICOS")))
            tabular.add_hline(2,4)
            tabular.add_row('','',NoEscape(r'\textit{\textbf{X}}'),NoEscape(r'\textit{\textbf{Y}}'))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Factor de Zona (Tabla N° 1)}'), NoEscape(r'\textbf{Z}'),MultiColumn(2,align='c|',data='{:.2f}'.format(Z))))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Factor de Uso (Tabla N° 5)}'), NoEscape(r'\textbf{U}'), MultiColumn(2,align='c|',data='{:.2f}'.format(U))))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Factor de Suelo (Tabla N° 3)}'), NoEscape(r'\textbf{S}'), MultiColumn(2,align='c|',data='{:.2f}'.format(S))))
            tabular.add_hline(2,4)
            tabular.add_row((MultiRow(2, data=NoEscape(r'\textit{Periodos(Tabla N° 4)}')), NoEscape(r'\textbf{T\raisebox{-0.5ex}{\scriptsize{P}}}'),MultiColumn(2,align='c|',data='{:.2f}'.format(Tp)) ))
            tabular.add_hline(2, 4)
            tabular.add_row(('', NoEscape(r'\textbf{T\raisebox{-0.5ex}{\scriptsize{L}}}'),MultiColumn(2,align='c|',data='{:.2f}'.format(Tl)) ))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Coef. Básico de Reducción (Tabla N°7)}'), NoEscape(r'\textbf{R\raisebox{-0.5ex}{\scriptsize{o}}}'),'{:.2f}'.format(Rox),'{:.2f}'.format(Roy)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Irregularidad en altura (Tabla N°8)}'), NoEscape(r'\textbf{I\raisebox{-0.5ex}{\scriptsize{a}}}'), '{:.2f}'.format(Ia),'{:.2f}'.format(Ia)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Irregularidad en planta (Tabla N°9)}'), NoEscape(r'\textbf{I\raisebox{-0.5ex}{\scriptsize{p}}}'), '{:.2f}'.format(Ip), '{:.2f}'.format(Ip)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Coef. de Reducción (Articulo 22)}'), NoEscape(r'\textbf{R}'), '{:.2f}'.format(Rx), '{:.2f}'.format(Ry)))
            tabular.add_hline(2,4)
            tabular.add_row(('', NoEscape(r'\textbf{ZUSg/R}'), '{:.2f}'.format(ZUSg_Rx), '{:.2f}'.format(ZUSg_Ry)))
            tabular.add_hline(2,4)
    return obj

def espectro_respuesta(T,Sax,Say,Tp,Tl,Rx,Ry,o_type=Subsubsection):
    y_max = max(max(Sax),max(Say))
    plt.clf()
    plt.ylim(0,y_max+0.02)
    plt.xlim(0,4)
    plt.plot(T,Sax,'r',label='X (R=%.2f)'%Rx)
    plt.plot(T,Say,'b',label='Y (R=%.2f)'%Ry)
    plt.axvline(x = Tl, color = 'g',linestyle='dotted')
    plt.text(Tp,y_max+0.005, 'Tp', fontsize=12, color='k')
    plt.text(Tl,y_max+0.005, 'Tl', fontsize=12, color='k')
    plt.axvline(x = Tp, color = 'g',linestyle='dotted')
    plt.xlabel('T (s)')
    plt.ylabel('Sa $(m/s^2)$')
    plt.grid(linestyle='dotted', linewidth=1)
    plt.legend()
    fig = plt.gcf()
    fig.set_frameon(False)
    plt.savefig("images/espectro_respuestas.pdf",dpi=300,pad_inches=0,bbox_inches='tight')

    obj = def_obj(o_type,NoEscape('Espectro de respuesta de aceleraciones'))
    obj.packages.append(Package('float'))

    obj.append(NoEscape('%insertion'))
    with obj.create(Figure(position='H')) as fig:
        fig.append(NoEscape('\\includegraphics[width=0.8\\textwidth]{images/espectro_respuestas}'))
        fig.add_caption('Espectro de aceleraciones')
    return obj

def peso_sismico(o_type=Subsubsection):
    obj = def_obj(o_type,NoEscape('Peso sísmico'))          
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('booktabs'))
    obj.packages.append(Package('array'))
        

    mbox = mybox3(r'Art. 26')
    mbox.append(NoEscape(r'\textit{El peso (P), se calcula adicionando a la carga permanente y total de la edificación un porcentaje de la carga viva o sobrecarga. En edificaciones de categoría C, se toma el 25\% de la carga viva.}'))
    obj.append(mbox)

    obj.append(NoEscape('%insertion'))

    return obj

def excentricidad_accidental(o_type=Subsubsection):
    obj = def_obj(o_type,NoEscape('Excentricidad accidental'))         
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('booktabs'))
    obj.packages.append(Package('array'))
        

    mbox = mybox3(r'Art. 28.5')
    mbox.append(NoEscape(r'\textit{La incertidumbre en la localización de los centros de masa en cada nivel, se considera mediante una excentricidad accidental perpendicular a la dirección del sismo igual a 0,05 veces la dimensión del edificio en la dirección perpendicular a la dirección de análisis. En cada caso se considera el signo más desfavorable.}'))
    obj.append(mbox)

    obj.append(NoEscape('%insertion'))

    fig = Figure(position='ht!')
    fig.append(NoEscape(r'\centering'))
    fig.append(NoEscape(r'\caption{Excentricidad de la masa en ETABS}'))
    fig.append(NoEscape(r'\includegraphics[scale=0.7]{images/excentricidad.PNG}'))
    fig.append(NoEscape(r'\label{masa}'))
    obj.append(fig)

    return obj
    

        
def ana_modal(table,o_type=Subsection):
    obj = def_obj(o_type,NoEscape('Análisis modal Art. 26.1 E-030'))
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('booktabs'))
    obj.packages.append(Package('array'))
    obj.packages.append(Package('float'))
        
    mbox = mybox3(r'Art. 26.1.1')
    mbox.append(NoEscape(r'\textit{Los modos de vibración pueden determinarse por un procedimiento de análisis que considere apropiadamente las características de rigidez y la distribución de las masas.}'))
    obj.append(mbox)
    mbox2 = mybox3(r'Art. 29.1.2')
    mbox2.append(NoEscape(r'\textit{En cada dirección se consideran aquellos modos de vibración cuya suma de masas efectivas sea por lo menos el 90\% de la masa total, pero se toma en cuenta por lo menos los tres primeros modos predominantes en la dirección de análisis.}'))
    obj.append(mbox2)
    
    obj.append(NoEscape('%insertion'))
    
    table = table.astype(float).style.hide(axis='index')
    table.format('{:.3f}')
    table.format('{:.0f}',subset= pd.IndexSlice[:,'Mode'])
    table = table.to_latex(hrules=True,column_format = 'c'*8,)
    
    with obj.create(Table(position='H')):
        obj.append(NoEscape(r'\extrarowheight = -0.3ex'))
        obj.append(NoEscape(r'\renewcommand{\arraystretch}{1.3}'))
        obj.append(NoEscape('\centering'))
        obj.append(NoEscape('\caption{Periodos y porcentajes de masa participativa}'))
        obj.append(NoEscape(table))

    return obj

def analisis_irregularidades(o_type=Subsection):
    obj = def_obj(o_type,NoEscape(r'Análisis de Irregularidades')) 
    obj.append(NoEscape('%insertion'))

    return obj

def irreg_rigidez(sis_x,sis_y,o_type=Subsubsection):
    obj = def_obj(o_type,NoEscape('Irregularidad de Rigidez-Piso Blando'))
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('booktabs'))
    
    def latex_table(table):
        table = table[['Story','OutputCase','VX','VY','lat_rig(k)','0.7_prev_k','0.8k_prom','is_reg']]
        table.columns = ['Story','OutputCase','VX','VY','Rigidez Lateral(k)',r'70\%k previo',r'80\%Prom(k)','is\_reg']
        for i in ['VX','VY','Rigidez Lateral(k)',r'70\%k previo',r'80\%Prom(k)']:
            table.loc[:,i] = table.loc[:,i].astype(float)
        table = table.style.hide(axis='index')
        table = table.format('{:.3f}',subset=pd.IndexSlice[:,['VX','VY','Rigidez Lateral(k)',r'70\%k previo',r'80\%Prom(k)']])
        table = table.to_latex(hrules=True, column_format = 'c'*8).replace('0.000','')
        return table
    
     
    mbox = mybox2('Tabla N°9 E-030')
    mbox.append(NoEscape('Existe irregularidad de rigidez cuando, en cualquiera de las direcciondes de análisis, en un entrepiso la rigidez lateral es menor que 70\% de la rigidez lateral del entrepiso inmediato superior, o es menor que 80\\% de la rigidez lateral promedio de los tres niveles superiores adyacentes. \n Las rigideces laterales pueden calcularse como la razón entre la fuerza cortante del entrepiso y el correspondiente desplazamiento relatibo en el centro de masas, ambos evaluados para la misma condición de carga '))
    obj.append(mbox)
    mbox2 = mybox2('Tabla N°9 E-030')
    mbox2.append(NoEscape('''
Existe irregularidad extrema de rigidez cuando, en cualquiera de las direcciones de análisis, en un entrepiso la rigidez lateral es menor que 60\\% de la rigidez lateral del entrepiso inmediato superior, o es menor que 70\\% de la rigidez lateral promedio de los tres niveles superiores adyacentes.
Las rigideces laterales pueden calcularse como la razon entre la fuerza cortante del entrepiso y el correspondiente desplazamiento relativo en el centro de masas, ambos evaluados para la misma condición de carga.'''))
    obj.append(mbox2)
    
    obj.append('Las rigideces laterales pueden calcularse como la razon entre la fuerza cortante del entrepiso y el correspondiente desplazamiento relativo en el centro de masas, ambos evaluados para la misma condición de carga. \n')
    obj.append(NoEscape('%insertion'))
    
    sis_x = latex_table(sis_x)
    sis_y = latex_table(sis_y)
    
    
    with obj.create(Table(position='h!')):
        obj.append(NoEscape('\centering'))
        obj.append(NoEscape('\caption{Irregularidad de rigidez}'))
        obj.append(NoEscape(sis_x))
        
    with obj.create(Table(position='h!')):
        obj.append(NoEscape('\centering'))
        obj.append(NoEscape('\caption{Irregularidad de rigidez}'))
        obj.append(NoEscape(sis_y))

    return obj
        

def irreg_masa(masa,o_type=Subsubsection):
    def latex_table(table):
        table.columns = ['Story','Masa','1.5 Masa','Tipo de Piso','is\_reg']
        table = table.replace('',0.0)
        for i in  ['Masa','1.5 Masa']:
            table.loc[:,i] = table.loc[:,i].astype(float)
        table = table.style.hide(axis='index')
        table = table.format('{:.3f}',subset=pd.IndexSlice[:,['Masa','1.5 Masa']])
        table = table.to_latex(hrules=True, column_format = 'c'*5).replace('0.000','')
        return table
    
    obj = def_obj(o_type,NoEscape('Irregularidad de Masa o Peso'))
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('booktabs'))
    obj.packages.append(Package('float'))
    
    mbox = mybox2('Tabla N°9 E-030')
    mbox.append(NoEscape('Se tiene irregularidad de masa (o peso) cuando el peso de un piso determinado según el artículo 26, es nayor que 1,5 veces el peso de un piso adyascente. Este criterio no se aplica en azoteas ni en sótanos'))
    obj.append(mbox)

    obj.append(NoEscape('%insertion'))
    
    with obj.create(Table(position='H')):
        obj.append(NoEscape('\centering'))
        obj.append(NoEscape('\caption{Irregularidad de Masa o Peso}'))
        obj.append(NoEscape(latex_table(masa)))
    
    return obj
    

def irreg_torsion(sis_x,sis_y,insert='',o_type=Subsubsection):
    def latex_table(table):
        table.columns = ['Story', 'OutputCase', 'Direction', 'Max Drift', 'Avg Drift', 'Ratio', 'Height', 'Drifts', '< Driftmax/2', 'Es Regular']
        table = table.style.hide(axis='index')
        # table = table.format('{:.3f}',subset=pd.IndexSlice[:,['Masa','1.5 Masa Piso Inferior','1.5 Masa Piso Superior']])
        table = table.to_latex(hrules=True, column_format = 'c'*10)
        return table
    
    obj = def_obj(o_type,NoEscape('Irregularidad Torsional'))
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('booktabs'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('float'))
    
    mbox = mybox2('Tabla N°9 E-030')
    mbox.append(NoEscape('Existe irregularidad torsional cuando, en cualquiera de las direcciones de análisis el desplazamiento relativo de entrepiso en un edificion ($\\Delta_{max}$) en esa dirección, calculado incluyendo excentricidad accidental, es mayor que 1,3 veces el desplazamineto relativo promedio de los extremos del mismo entrepiso para la condicion de carga ($\Delta_{prom}$). \n Este crriterio sólo se aplica en edificios con diafragmas rígidos y sólo si el máximo desplazamiento relativo de entrepiso es mayor que 50\\% del desplazamiento permisible indicado en la Tabla N° 11'))
    obj.append(mbox)
    mbox2 = mybox2('Tabla N°9 E-030')
    mbox2.append(NoEscape('Existe irregularidad torsional cuando, en cualquiera de las direcciones de análisis el desplazamiento relativo de entrepiso en un edificion ($\\Delta_{max}$) en esa dirección, calculado incluyendo excentricidad accidental, es mayor que 1,5 veces el desplazamineto relativo promedio de los extremos del mismo entrepiso para la condicion de carga ($\Delta_{prom}$). \n Este crriterio sólo se aplica en edificios con diafragmas rígidos y sólo si el máximo desplazamiento relativo de entrepiso es mayor que 50\\% del desplazamiento permisible indicado en la Tabla N° 11'))
    obj.append(mbox)

    obj.append(NoEscape('%insertion'))
    
    fig = Figure(position='H')
    fig.append(NoEscape(r'\centering'))
    fig.append(NoEscape(r'\caption{Irregularidad torsional}'))
    fig.append(NoEscape(r'\includegraphics[scale=0.7]{images/i_torsion.PNG}'))
    fig.append(NoEscape(r'\caption*{\small Fuente: Muñoz (2020)}'))
    obj.append(fig)
    
    table = Table(position='H')
    table.append(NoEscape('\centering'))
    table.append(NoEscape('\caption{Irregularidad Torsional}'))
    table.append(NoEscape('\\resizebox{\\textwidth}{!}{'))
    table.append(NoEscape(latex_table(sis_x)+'}'))
    obj.append(table)
    
    table2 = Table(position='ht!')
    table2.append(NoEscape('\centering'))
    table2.append(NoEscape('\caption{Irregularidad Torsional}'))
    table2.append(NoEscape('\\resizebox{\\textwidth}{!}{'))
    table2.append(NoEscape(latex_table(sis_y)+'}'))
    obj.append(table2)

    return obj
    

def irreg_discontinuidad_diaf(sec_change=None,openings=None,o_type=Subsubsection):
    '''
    recibe el objeto y produce un informe de discontinuidad de diafragma
    sintaxis de sec_change (diccionario):
        {aligerado: (longitud,espesor),
         macisa: (longitud,esperor)}
        tipo de seccion 1: [longitud,espesor]
    sintaxis de openings:
        aberturas : [(largo, ancho),]
        area_planta: area 
    '''
    
    obj = def_obj(o_type,NoEscape('Irregularidad por Discontinuidad del Diafragma'))
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('caption'))
    obj.packages.append(Package('array'))
    obj.packages.append(Package('float'))
    

    mbox = mybox2('Tabla N°9 E-030')
    mbox.append(NoEscape(r'\textit{La estructura se califica como irregular cuando los diafragmas tienen discontinuidades abruptas o variaciones importantes en rigidez, incluyendo aberturas mayores que 50\% del área bruta del diafragma.} \\ \textit{También  existe  irregularidad  cuando,  en  cualquiera de  los pisos y para cualquiera de las direcciones de análisis, se tiene alguna sección transversal del diafragma con un área neta resistente menor que 25\% del área de la sección transversal total de la misma dirección calculada con las dimensiones totales de la planta.}'))
    obj.append(mbox)

    obj.append(NoEscape('%insertion'))
    obj.append(NoEscape(r'\vspace{-10pt}'))
    fig = Figure(position='H')
    fig.append(NoEscape(r'\centering'))
    fig.append(NoEscape(r'\caption{Irregularidad por discontinuidad del diafragma}'))
    fig.append(NoEscape(r'\includegraphics[scale=0.7]{images/i_diafragma.PNG}'))
    fig.append(NoEscape(r'\caption*{\small Fuente: Muñoz (2020)}'))
    obj.append(fig)
    
    if sec_change:
        data = [['Longitud del aligerado (L1)',sec_change['aligerado'][0],'m'],
                ['Espesor del aligerado (e1)',sec_change['aligerado'][1],'m'],
                ['Area del aligerado A1=L1$\\cdot$ e1','area1','$m^2$'],
                ['Longitud de la losa macisa (L2)',sec_change['macisa'][0],'m'],
                ['Espesor de la losa macisa (e2)',sec_change['macisa'][1],'m'],
                ['Area de la losa macisa A1=L1$\\cdot$ e1','area2','$m^2$'],
                ['Ratio','ratio','\%'],
                ['Ratio límite','25.00','\%'],
                ['Verificación','','']]
        
        data[2][1] = '%.2f'%(float(sec_change['aligerado'][0])*float(sec_change['aligerado'][1]))
        data[5][1] = '%.2f'%(float(sec_change['macisa'][0])*float(sec_change['macisa'][1]))
        data[6][1] = '%.2f'%(float(data[5][1])/float(data[2][1])*100)
        data[8][1] = r'\textcolor[rgb]{ .267,  .447,  .769}{\textbf{Regular}}' if float(data[6][1]) > float(data[7][1]) else r'\textcolor[rgb]{ 1,  0,  0}{\textbf{Irregular}}'
        obj.append(NoEscape(r'\vspace{-30pt}'))
        table = Table(position='H')
        table.append(NoEscape(r'\centering'))
        table.append(NoEscape(r'\caption{Irregularidad por discontinuidad del diafragma (a)}'))
        tab = Tabular('llcr')
        tab.append(NoEscape(r'\cline{1-3}'))
        for row in data:
            tab.append(NoEscape(r'\multicolumn{2}{r}{%s} & %s & \multicolumn{1}{l}{%s} \\'%(row[0],row[1],row[2])))
        tab.append(NoEscape(r'\cline{1-3}'))
        table.append(tab)
        obj.append(table)

    if openings:
        data = [[r'\textbf{Abertura}', r'\textbf{Largo (m)}',r'\textbf{Ancho (m)}',r'\textbf{Área $m^2$}'],]
        
        for i,j in enumerate(openings['aberturas']):
            data.append([i+1,'%.2f'%(float(j[0])),'%.2f'%(float(j[1])),'%.2f'%(float(j[0])*float(j[1]))])
        
        a_total = sum(float(i[3]) for i in data[1:])
        a_planta = float(openings['area_planta'])
        ratio = float(a_total)/float(a_planta)*100
        verif = r'\textcolor[rgb]{ .267,  .447,  .769} {Regular}' if ratio < 50 else r'\textcolor[rgb]{ 1,  0,  0}{Irregular}'

        obj.append(NoEscape(r'\vspace{-15pt}'))
        table = Table(position='H')
        table.append(NoEscape(r'\centering'))
        table.append(NoEscape(r'\caption{Irregularidad por discontinuidad del diafragma (b)}'))
        tab = Tabular('cccc')
        tab.add_hline()
        for row in data:
            tab.add_row([NoEscape(cell) for cell in row])
            tab.add_hline()
        tab.add_row(('',MultiColumn(2,data='Área total de aberturas:',align='r'),NoEscape(r'%.2f $m^2$'%a_total)))
        tab.add_row(('',MultiColumn(2,data='Área total de la planta:',align='r'),NoEscape(r'%.2f $m^2$'%a_planta)))
        tab.add_row(('',MultiColumn(2,data='Ratio:',align='r'),NoEscape(r'{:.2f} \%'.format(ratio))))
        tab.add_row(('',MultiColumn(2,data='Ratio límite:',align='r'),NoEscape('50.00 \%')))
        tab.add_row(('',MultiColumn(2,data='Verificación:',align='r'),NoEscape(verif)))
        table.append(tab)
        obj.append(table)

    return obj

def irreg_esquinas_entrantes(datos_esquinas=None,o_type=Subsubsection):     
    '''
    recibe el objeto y produce un informe de esquinas entrantes
    sintaxis de datos_esquinas (diccionario):
        {descripción: Dimensión}
    '''
    obj = def_obj(o_type,NoEscape('Irregularidad por Esquinas entrantes'))
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('caption'))
    obj.packages.append(Package('array'))
    obj.packages.append(Package('float'))

    mbox = mybox2('Tabla N°9 E-030')
    mbox.append(NoEscape(r'\textit{La estructura se califica como irregular cuando tiene esquinas entrantes  cuyas  dimensiones  en  ambas  direcciones  son mayores que 20\% de la correspondiente dimensión total en planta}'))
    obj.append(mbox)
    
    obj.append(NoEscape('%insertion'))
    
    fig = Figure(position='H')
    fig.append(NoEscape(r'\centering'))
    fig.append(NoEscape(r'\caption{Irregularidad por esquinas entrantes}'))
    fig.append(NoEscape(r'\includegraphics[scale=0.5]{images/i_esquinas.PNG}'))
    fig.append(NoEscape(r'\caption*{\small Fuente: Muñoz (2020)}'))
    obj.append(fig)
    
    if datos_esquinas:
        data = [['Esquina entrante en X(a)',datos_esquinas['esq_X'],'m'],
                ['Esquina entrante en Y(b)',datos_esquinas['esq_Y'],'m'],
                ['Dimensión total en X(A)',datos_esquinas['dim_X'],'m'],
                ['Dimensión total en Y(B)',datos_esquinas['dim_Y'],'m'],
                ['a/A','a/A','\%'],
                ['b/B','b/B','\%'],
                ['Limite <','20.0','\%'],
                ['Verificación','','']]
        
        data[4][1] = '%.2f'%(float(datos_esquinas['esq_X'])/float(datos_esquinas['dim_X'])*100)
        data[5][1] = '%.2f'%(float(datos_esquinas['esq_Y'])/float(datos_esquinas['dim_Y'])*100)
        data[7][1] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{Irregular}}' if (float(data[4][1])>20 and float(data[5][1])>20  ) else r'\textcolor[rgb]{ .267,  .447,  .769}{\textbf{Regular}}'
        
        table = Table(position='H')
        table.append(NoEscape(r'\centering'))
        table.append(NoEscape(r'\caption{Irregularidad por esquinas entrantes}'))
        tab = Tabular('llcr')
        tab.append(NoEscape(r'\cline{1-3}'))
        for row in data:
            tab.append(NoEscape(r'\multicolumn{2}{l}{%s} & %s & \multicolumn{1}{l}{%s} \\'%(row[0],row[1],row[2])))
        tab.append(NoEscape(r'\cline{1-3}'))
        table.append(tab)
        obj.append(table)

    return obj

def analisis_dinamico(o_type=Subsection):
    obj = def_obj(o_type,'Análisis Dinámico Espectral Art. 29 E-030') 
    obj.append(r'El análisis dinámico modal espectral consiste calcular la respuesta para cada modo ingresando al espectro de pseudo-aceleraciones definido en \ref{ssubsec:Espectroderespuestadeaceleraciones}, para posteriormente combinar los resultados según los criterios que se menciona en la norma E-030:')
    obj.append(NoEscape('%insertion'))

    return obj

def criterios_combinacion(o_type=Subsubsection):
    obj = def_obj(o_type,'Criterios de combinación') 
    obj.packages.append(Package('tcolorbox'))
    obj.append(NoEscape('%insertion'))
    
    mbox = mybox3(r'Art. 29.3.1')
    mbox.append(NoEscape(r'\textit{Mediante los criterios de combinación que se indican, se puede obtener la respuesta máxima elástica esperada (r) tanto para las fuerzas internas en los elementos componentes de la estructura, como para los parámetros globales  del edificio como fuerza cortante en la base, cortantes de entrepiso, momentos  de volteo, desplazamientos totales y relativos de entrepiso.}'))
    obj.append(mbox)

    mbox = mybox3(r'Art. 29.3.2')
    mbox.append(NoEscape(r'\textit{La respuesta máxima elástica esperada (r) correspondiente al efecto conjunto  de  los  diferentes  modos  de  vibración  empleados  (ri)  puede determinarse usando la combinación cuadrática completa de los valores calculados para cada modo.}'))
    obj.append(mbox)
    
    with obj.create(Alignat(aligns=1,numbering=True,escape=False)) as eq:  #Insertar ecuación
        eq.append(r'r=\sqrt{\sum \sum r_{i}\,\rho _{i}\,r_{i}}')

    mbox = mybox3(r'Art. 29.3.3')
    mbox.append(NoEscape(r'\textit{Donde r representa las respuestas modales, desplazamientos o fuerzas, los coeficientes de correlación están dados por:}'))
    obj.append(mbox)

    with obj.create(Alignat(aligns=1,numbering=True,escape=False)) as eq:  
        eq.append(r'\rho_{ij}=\frac{8\beta ^{2}\left ( 1+\lambda  \right )\lambda ^{3/2}}{\left ( 1-\lambda ^{2} \right )+4\beta ^{2}\lambda \left ( 1+\lambda  \right )^{2}}\quad\quad  \lambda =\frac{\omega _{j}}{\omega _{i}}')

    flushleft = Environment() #Creación de entorno flushleft
    flushleft._latex_name = 'flushleft'
    flushleft.append(NoEscape(r'Donde:\\'))
    flushleft.append(NoEscape(r'$\beta$: fracción del amortiguamiento crítico, que se puede suponer constante para todos los modos igual a 0,05.\\'))
    flushleft.append(NoEscape(r'$\omega _{j}$,$\omega _{i}$: son las frecuencias angulares de los modos i, j\\'))
    obj.append(flushleft)

    return obj

def desplazamientos_laterales(heights,disp_x,disp_y,Rx,Ry,o_type=Subsection):
    max_disp_x = max(disp_x)
    max_disp_y = max(disp_y)
    plt.clf()
    plt.ylim(0,max(heights)*1.05)
    plt.xlim(0,float(max(max_disp_x,max_disp_y))+0.003)
    plt.plot(disp_x,heights,'r',label='X (R=%.2f)'%Rx)
    plt.plot(disp_y,heights,'b',label='Y (R=%.2f)'%Ry)
    plt.scatter(disp_x,heights,color='r',marker='x')
    plt.scatter(disp_y,heights,color='b',marker='x')
    plt.xlabel('Desplazamientos (m)')
    plt.ylabel('h (m)')
    plt.grid(linestyle='dotted', linewidth=1)
    plt.legend()
    fig = plt.gcf()
    fig.set_size_inches(8, 6)
    fig.set_frameon(False)
    plt.savefig("images/desplazamientos_laterales.pdf",dpi=300,pad_inches=0,bbox_inches='tight')

    obj = def_obj(o_type,'Determinación de desplazamientos laterales Art. 31 E-030')
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('float'))
    obj.append(NoEscape('%insertion'))
    
    mbox = mybox3(r'Art. 31.3.1')
    mbox.append(NoEscape(r'\textit{Para  estructuras  regulares, los  desplazamientos  laterales  se  calculan multiplicando por 0,75 R los resultados obtenidos del análisis lineal y elástico con las solicitaciones sísmicas reducidas. Para estructuras irregulares, los desplazamientos laterales se calculan multiplicando por 0,85 R los resultados obtenidos del análisis lineal elástico.}'))
    obj.append(mbox)

    with obj.create(Figure(position='H')) as fig:
        fig.append(NoEscape('\\includegraphics[width=0.8\\textwidth]{images/desplazamientos_laterales}'))
        fig.add_caption('Desplazamientos inelásticos')
    
    return obj

def verificacion_derivas(sist_x,sist_y,heights,drifts_x,drifts_y,max_drift,Rx,Ry,o_type=Subsection):
    max_drift_x = max(drifts_x)
    max_drift_y = max(drifts_y)
    plt.clf()
    plt.ylim(0,max(heights)*1.05)
    plt.xlim(0,max(max_drift_x,max_drift_y,max_drift)*1.02)
    plt.plot(drifts_x,heights,'r',label='X (R=%.2f)'%Rx)
    plt.plot(drifts_y,heights,'b',label='Y (R=%.2f)'%Ry)
    plt.scatter(drifts_x,heights,color='r',marker='x')
    plt.scatter(drifts_y,heights,color='b',marker='x')
    plt.axvline(x = max_drift, color = 'c',linestyle='dotted')
    plt.axvline(x = max_drift/2, color = 'g',linestyle='dotted')
    plt.text(max_drift-0.001,max(heights),round(max_drift,4), fontsize=10, color='k')
    plt.text(max_drift/2-0.001,max(heights),round(max_drift/2,4), fontsize=10, color='k')
    plt.xlabel('Derivas')
    plt.ylabel('h (m)')
    plt.grid(linestyle='dotted', linewidth=1)
    plt.legend(loc='lower right')
    fig = plt.gcf()
    fig.set_frameon(False)
    plt.savefig("images/derivas.pdf",dpi=300,pad_inches=0,bbox_inches='tight')
    plt.clf()

    obj=def_obj(o_type,'Verificación de derivas máximas Art. 32 E-030')
    obj.packages.append(Package('array'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('multirow'))
    obj.packages.append(Package('caption'))
    obj.append(NoEscape('%insertion'))

    sistemas = {'Pórticos de Concreto Armado':'Concreto Armado',
                'Dual de Concreto Armado':'Concreto Armado',
                'De Muros Estructurales de Concreto Armado':'Concreto Armado',
                'Pórticos Especiales de Acero Resistentes a Momentos':'Acero',
                'Pórticos Intermedios de Acero Resistentes a Momentos':'Acero',
                'Pórticos Ordinarios de Acero Resistentes a Momentos':'Acero',
                'Pórticos Especiales de Acero Concénticamente Arriostrados':'Acero',
                'Pórticos Ordinarios de Acero Concénticamente Arriostrados':'Acero',
                'Pórticos Acero Excéntricamente Arriostrados':'Acero',
                'Muros de Ductilidad Limita de Concreto Armado':'Edificios de concreto armado con muros de ductilidad limitada',
                'Albañilería Armada o Confinada':'Albañilería',
                'Madera':'Madera'}

    data = [['Concreto Armado',0.007],
                ['Acero',0.010],
                ['Albañilería',0.005],
                ['Madera',0.010],
                ['Edificios de concreto armado con muros de ductilidad limitada',0.005]]
    
    for i,j in enumerate(data):
        if j[0] in (sistemas[sist_x],sistemas[sist_y]):
            data[i][0] = data[i][0]+r'\cellcolor[rgb]{ .949,  .949,  .949} '
            data[i][1] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+str(data[i][1])+r'}}'+r'\cellcolor[rgb]{ .949,  .949,  .949}'
    
    table = Table(position='ht!')
    table.append(NoEscape(r'\centering'))
    table.append(NoEscape(r'\caption{Derivas máximas}'))
    tab = Tabular(NoEscape(r'>{\raggedright\arraybackslash}p{9.8cm} >{\raggedleft\arraybackslash}p{1cm}'))
    tab.append(NoEscape(r'\hline'))
    tab.append(NoEscape(r'\multicolumn{2}{c}{\multirow{2}[1]{*}{\textbf{LIMITES PARA LA DISTORSION DE ENTREPISO}}} \\'))
    tab.append(NoEscape(r'\multicolumn{2}{c}{} \\'))
    tab.append(NoEscape(r'\hline'))
    tab.append(NoEscape(r'\textbf{Material predominante:} & $\Delta_{i}/h_{ei}$ \\'))
    tab.append(NoEscape(r'\hline'))
    for row in data:
            tab.append(NoEscape(r'{%s} & %s \\'%(row[0],row[1])))
            tab.append(NoEscape(r'\hline'))
    table.append(tab)
    table.append(NoEscape(r'\caption*{Fuente: E-030 (2018)}'))
    obj.append(table)
    
    with obj.create(Figure(position='ht!')) as fig:
        fig.append(NoEscape('\\includegraphics[width=0.8\\textwidth]{images/derivas}'))
        fig.add_caption('Derivas máxima de entrepiso')
    
    return obj

def verificacion_sist_est(o_type=Subsection):
    obj=def_obj(o_type,'Verificación del sistema estructural')
    obj.packages.append(Package('caption')) 
    obj.append(r'Se verificará que efectivamente se tiene un sistema estructural de muros en la dirección X, en la dirección Y no se verificara dado que no existen muros estructurales. Como se muestra en la figura \ref{fig:sist_est_etabs} el valor de cortante que absorben los muros es de 64 ton, y la cortante total es aproximadamente 70 ton (ver figura \ref{fig:corte_basal}) por lo que el porcentaje que toman los muros es mayor al 90%.')
    obj.append(NoEscape('%insertion'))
    
    fig = Figure(position='ht!')
    fig.append(NoEscape(r'\centering'))
    fig.append(NoEscape(r'\caption{Sistema estructural}'))
    fig.append(NoEscape(r'\includegraphics[scale=0.7]{images/sist_estructural.PNG}'))
    fig.append(NoEscape(r'\caption*{\small Fuente: Muñoz (2020)}'))
    fig.append(NoEscape(r'\label{fig:sist_est}'))
    obj.append(fig)

    fig = Figure(position='ht!')
    fig.append(NoEscape(r'\centering'))
    fig.append(NoEscape(r'\caption{Verificación del sistema estructural en X}'))
    fig.append(NoEscape(r'\includegraphics[scale=0.7]{images/sist_estructural_etabs.PNG}'))
    fig.append(NoEscape(r'\caption*{\small Fuente: Muñoz (2020)}'))
    fig.append(NoEscape(r'\label{fig:sist_est_etabs}'))
    obj.append(fig)
    
    return obj

def analisis_estatico(o_type=Subsection):
    obj = def_obj(o_type,'Análisis estático o de fuerzas estáticas equivalentes Art. 28 E-030') 
    obj.append(NoEscape('%insertion'))

    return obj

def cortante_basal(Z,U,Tx,Ty,Cx,Cy,kx,ky,S,Rox,Roy,Ia,Ip,sis_estatico,o_type=Subsubsection):
    obj = def_obj(o_type,'Fuerza cortante en la base Art 28.2 E-030') 
    obj.append(NoEscape('%insertion'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('subfigure'))
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('float'))
    obj.packages.append(Package('booktabs'))
    
    mbox = mybox3(r'Art. 28.2.1')
    mbox.append(NoEscape(r'\textit{La fuerza cortante total en la base de la estructura, correspondiente a la dirección considerada, se determina por la siguiente expresión:}'))
    obj.append(mbox)
    
    with obj.create(Alignat(aligns=1,numbering=True,escape=False)) as eq:  #Insertar ecuación
        eq.append(r'V=\frac{Z\;\cdot U\cdot\;C\cdot\;S}{R}\;P\;\;\;\;\;\;\;\;\;\;\;\frac{C}{R}\geq 0,11')
    
    obj.append(NoEscape(r'Según el articulo 28.4.2 el periodo fundamental de vibración puede estimarse con la ecuación:'))

    with obj.create(Alignat(aligns=1,numbering=True,escape=False)) as eq:  #Insertar ecuación
        eq.append(r'T=2\pi\cdot \displaystyle\sqrt{\frac{\left (\displaystyle\sum_{i=1}^{n} P_{i}\cdot d_{i}^{2}\right )}{g\cdot\left (\displaystyle\sum_{i=1}^{n}f_{i}\cdot d_{i}  \right ) }}')
    
    flushleft = Environment() #Creación de entorno flushleft
    flushleft._latex_name = 'flushleft'
    flushleft.append(NoEscape(r'Donde:\\'))
    flushleft.append(NoEscape(r'$P_{i}$: es el peso sísmico en el nivel i.\\'))
    flushleft.append(NoEscape(r'$f_{i}$: es la fuerza lateral en el nivel i correspondiente a una distribución en altura semejante a la del primer modo en la dirección de análisis.\\'))
    flushleft.append(NoEscape(r'$d_{i}$: es el desplazamiento lateral del centro de masa del nivel  i en traslación pura (restringiendo los giros en planta) debido a las fuerzas $f_{i}$. Los desplazamientos se calculan suponiendo comportamiento lineal elástico de la estructura y, para el caso de estructuras de concreto armado y de albañilería, considerando las secciones sin fisurar.\\'))
    obj.append(flushleft)
    obj.append(NoEscape(r'Lo anterior equivale a calcular los modos de vibrar en el modelo matemático restringiendo el grado de libertad de rotación.Lo anterior equivale a calcular los modos de vibrar en el modelo matemático restringiendo el grado de libertad de rotación.'))
    
    fig = Figure(position='ht!')
    fig.append(NoEscape(r'\centering'))
    fig.append(NoEscape(r'\subfigure[X]{\includegraphics[height=70mm]{images/TX.PNG}}\hspace{1cm}'))
    fig.append(NoEscape(r'\subfigure[Y]{\includegraphics[height=70mm]{images/TY.PNG}}'))
    fig.append(NoEscape(r'\caption{Periodos fundamentales en traslación pura}'))
    fig.append(NoEscape(r'\label{fig:periodos_fund}'))
    obj.append(fig)
    Ps = sum(sis_estatico['Weight'])
    Rx=Rox*Ia*Ip
    Ry=Roy*Ia*Ip
    ZUSC_Rx=Z*U*S*Cx/Rx
    ZUSC_Ry=Z*U*S*Cy/Ry
    Vx=ZUSC_Rx*Ps
    Vy=ZUSC_Ry*Ps

    with obj.create(Table(position='H')) as table:
        table.append(NoEscape('\centering'))
        table.add_caption('Análisis sísmico estático')
        table.append(NoEscape(r'\extrarowheight = 0ex'))
        table.append(NoEscape(r'\renewcommand{\arraystretch}{1.2}'))
        with table.create(Tabular(r'>{\arraybackslash}m{7cm}|>{\centering\arraybackslash}m{2.5cm}|>{\centering\arraybackslash}m{2cm}|>{\centering\arraybackslash}m{2cm}|')) as tabular:
            tabular.add_hline(2,4)
            tabular.add_row('',MultiColumn(3,align='c|',data=bold("PARÁMETROS SÍSMICOS")))
            tabular.add_hline(2,4)
            tabular.add_row('','',NoEscape(r'\textit{\textbf{X}}'),NoEscape(r'\textit{\textbf{Y}}'))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Factor de Zona (Tabla N° 1)}'), NoEscape(r'\textbf{Z}'),MultiColumn(2,align='c|',data='{:.2f}'.format(Z))))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Factor de Uso (Tabla N° 5)}'), NoEscape(r'\textbf{U}'), MultiColumn(2,align='c|',data='{:.2f}'.format(U))))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Periodos en traslación pura obtenidos del ETABS (Art. 28.4.2)}'), NoEscape(r'\textbf{T}'),'{:.2f}'.format(Tx),'{:.2f}'.format(Ty)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Factor de Amplificación (Art. 14)}'), NoEscape(r'\textbf{C}'),'{:.2f}'.format(Cx),'{:.2f}'.format(Cy)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Factor de Suelo (Tabla N°3)}'), NoEscape(r'\textbf{S}'),MultiColumn(2,align='c|',data='{:.2f}'.format(S))))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Coef. Básico de Reducción (Tabla N°7)}'), NoEscape(r'\textbf{R\raisebox{-0.5ex}{\scriptsize{o}}}'),'{:.2f}'.format(Rox),'{:.2f}'.format(Roy)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Irregularidad en altura (Tabla N°8)}'), NoEscape(r'\textbf{I\raisebox{-0.5ex}{\scriptsize{a}}}'), '{:.2f}'.format(Ia),'{:.2f}'.format(Ia)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Irregularidad en planta (Tabla N°9)}'), NoEscape(r'\textbf{I\raisebox{-0.5ex}{\scriptsize{p}}}'), '{:.2f}'.format(Ip), '{:.2f}'.format(Ip)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Coef. de Reducción (Articulo 22)}'), NoEscape(r'\textbf{R}'), '{:.2f}'.format(Rx), '{:.2f}'.format(Ry)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Verificación (Articulo 28.2.2)}'), NoEscape(r'\textbf{C/R>0.11}'), '{:.2f}'.format(Cx/Rx), '{:.2f}'.format(Cy/Ry)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Peso sísmico (ETABS)}'), NoEscape(r'\textbf{Ps (Ton)}'), MultiColumn(2,align='c|',data='{:.2f}'.format(Ps))))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Coeficientes}'), NoEscape(r'\textbf{ZUCS/R}'), '{:.2f}'.format(ZUSC_Rx), '{:.2f}'.format(ZUSC_Ry)))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Cortante estática (Art.28.2)}'), NoEscape(r'\textbf{V (ton)}'), NoEscape(r'\cellcolor[rgb]{ 1,  .949,  .8}\textcolor[rgb]{ 1,  0,  0}{\textbf{'+'{:.2f}'.format(Vx)+'}}'), NoEscape(r'\cellcolor[rgb]{ 1,  .949,  .8}\textcolor[rgb]{ 1,  0,  0}{\textbf{'+'{:.2f}'.format(Vy)+'}}')))
            tabular.add_hline(2,4)
            tabular.add_row((NoEscape(r'\textit{Coeficiente k (Art.28.3.2)}'), NoEscape(r'\textbf{k}'), '{:.2f}'.format(kx), '{:.2f}'.format(ky)))
            tabular.add_hline(2,4)

    def latex_table(tab):
        table = tab.copy()
        table.columns = ['Piso','Peso','Altura',r'$H^{kx}$',r'$H^{ky}$','PxHx','PxHy','ax','ay','Vx','Vy']
        for i in  ['Peso','Altura',r'$H^{kx}$',r'$H^{ky}$','PxHx','PxHy','ax','ay','Vx','Vy']:
            table.loc[:,i] = table.loc[:,i].astype(float)
        table = table.style.hide(axis='index')
        table = table.format('{:.3f}',subset=pd.IndexSlice[:,['Peso','Altura',r'$H^{kx}$',r'$H^{ky}$','PxHx','PxHy','ax','ay','Vx','Vy']])
        table = table.to_latex(hrules=True, column_format = 'c'*11)
        return table


    with obj.create(Table(position='H')) as table:
        table.append(NoEscape('\centering'))
        table.add_caption('Análisis sísmico estático por pisos')
        table.append(NoEscape(latex_table(sis_estatico)))

    return obj

def fuerza_cortante_min(tabla_corte_min,o_type=Subsection):
    obj = def_obj(o_type,'Fuerza cortante mínima Art. 29.4 E-030')
    obj.packages.append(Package('tcolorbox'))
    obj.packages.append(Package('array'))
    obj.packages.append(Package('booktabs'))
    obj.append(NoEscape('%insertion'))
    
    mbox = mybox2(r'Art. 29.4.1')
    mbox.append(NoEscape(r'\textit{Para cada una de las direcciones consideradas en el análisis, la fuerza cortante en el primer entrepiso del edificio no puede ser menor que el 80\% del valor calculado según el artículo 25 para estructuras regulares, ni menor que el 90\% para estructuras irregulares.}'))
    obj.append(mbox)

    mbox = mybox2(r'Art. 29.4.2')
    mbox.append(NoEscape(r'\textit{Si fuera necesario incrementar el cortante para cumplir los mínimos señalados,  se escalan proporcionalmente todos los otros resultados obtenidos, excepto los  desplazamientos.}'))
    obj.append(mbox)

    def latex_table(table):
        table.columns = table.iloc[0]
        table=table[1:]
        for i in  ['X','Y']:
            table.loc[:,i] = table.loc[:,i].astype(float)
        table = table.style.hide(axis='index')
        table = table.format('{:.2f}',subset=pd.IndexSlice[:,['X','Y']])
        table = table.to_latex(hrules=True, column_format = 'c'*3).replace('%','\%')
        return table
    obj.append(NoEscape('%insertion'))
    
    with obj.create(Table(position='h!')) as table:
        table.append(NoEscape('\centering'))
        table.append(NoEscape('\caption{Escalamiento de la cortante dinámica}'))
        table.append(NoEscape(latex_table(tabla_corte_min)))

    return obj

def separacion_edificios(datos_sep,o_type=Subsection):
    obj = def_obj(o_type,'Separación entre edificios Art. 33 E-030')
    obj.packages.append(Package('subfigure')) 
    obj.packages.append(Package('tcolorbox')) 
    obj.packages.append(Package('float')) 
    obj.packages.append(Package('array')) 
    obj.append(NoEscape('%insertion'))

    mbox = mybox2(r'Art. 33.1')
    mbox.append(NoEscape(r'\textit{Toda estructura está separada de las estructuras vecinas, desde el nivel del terreno natural, una distancia mínima s para evitar el contacto durante un movimiento sísmico.}'))
    obj.append(mbox)

    mbox = mybox2(r'Art. 33.2')
    mbox.append(NoEscape(r'\textit{Esta distancia no es menor que los 2/3 de la suma de los desplazamientos máximos de los edificios adyacentes ni menor que:}'))
    obj.append(mbox)
    
    with obj.create(Alignat(aligns=1,numbering=True,escape=False)) as eq:  #Insertar ecuación
        eq.append(r's=0.006\;h\geq0.03\;m')
    
    obj.append(NoEscape(r'Donde h es la altura medida desde el nivel del terreno natural hasta el nivel considerado para evaluar s'))

    mbox = mybox2(r'Art. 33.3')
    mbox.append(NoEscape(r'\textit{El edificio se retira de los límites de propiedad adyacentes a otros lotes edificables,  o  con  edificaciones,  distancias  no  menores  que  2/3  del desplazamiento máximo calculado según el artículo 28 ni menores que s/2 si la edificación existente cuenta con una junta sísmica reglamentaria.}'))
    obj.append(mbox)

    fig = Figure(position='ht!')
    fig.append(NoEscape(r'\centering'))
    fig.append(NoEscape(r'\caption{Separación entre edificios}'))
    fig.append(NoEscape(r'\includegraphics[scale=0.5]{images/sep_edificios.PNG}'))
    fig.append(NoEscape(r'\label{fig:sep_edificios}'))
    obj.append(fig)

    if datos_sep:
        data = [['Altura del edificio','h',datos_sep['altura_edificio'],'cm'],
                ['Separación mínima entre edificios','s=0.006h',datos_sep['altura_edificio']*0.006,'>3cm'],
                ['Separación mínima del limite de propiedad','s/2',datos_sep['altura_edificio']*0.006/2,'cm'],
                ['Desplazamiento máximo en X',r'$\Delta_x$',datos_sep['despl_max_X'],'cm'],
                ['Desplazamiento máximo en Y',r'$\Delta_y$',datos_sep['despl_max_Y'],'cm'],
                ['Separación del limite de propiedad X',r'2/3$\Delta_{x}$',datos_sep['despl_max_X']*2/3,'cm'],
                ['Separación del limite de propiedad Y',r'2/3$\Delta_{y}$',datos_sep['despl_max_Y']*2/3,'cm']]
        
        data[1][2] ='%.2f'%(datos_sep['altura_edificio']*0.006)
        data[2][2] ='%.2f'%(datos_sep['altura_edificio']*0.006/2)
        data[3][2] ='%.2f'%(datos_sep['despl_max_X'])
        data[4][2] ='%.2f'%(datos_sep['despl_max_Y'])
        data[5][2]='%.2f'%(datos_sep['despl_max_X']*2/3)
        data[6][2]='%.2f'%(datos_sep['despl_max_Y']*2/3)

        table = Table(position='H')
        table.append(NoEscape(r'\centering'))
        table.append(NoEscape(r'\caption{Cálculo de la junta sísmica}'))
        table.append(NoEscape(r'\extrarowheight = -0.3ex'))
        table.append(NoEscape(r'\renewcommand{\arraystretch}{1.5}'))
        tab = Tabular('l|c|c|l')
        tab.append(NoEscape(r'\cline{2-3}'))
        for row in data:
            tab.append(NoEscape(r'\textit{%s} & \textbf{%s} & {%s} & {%s} \\'%(row[0],row[1],row[2],row[3])))
            tab.append(NoEscape(r'\cline{2-3}'))
        table.append(tab)
        table.append(NoEscape(r'\label{tab:junta_sis}'))
        obj.append(table)

    separacion=max(datos_sep['altura_edificio']*0.006/2,3/2,datos_sep['despl_max_X']*2/3,datos_sep['despl_max_Y']*2/3)
    separacion=ceil(separacion / 0.5) * 0.5  #Redondea a múltiplo de 0.5cm mayor que el número inicial

    obj.append(NoEscape(r'Según lo calculado en la tabla \ref{tab:junta_sis} '))
    obj.append(NoEscape(r' el edificio tendrá que ser separado del limite de propiedad {:.2f} cm como mínimo en ambas direcciones, en el caso que no exista junta reglamentaria el edificio actual se separa del edificio existente el valor de s/2 que le corresponde, más el valor s/2 de la estructura vecina.'.format(separacion)))         
    
    return obj

#Generación del documento
    
if __name__ == '__main__':
    from analisis_sismico_etabs import sismo, sist_x, sist_y

    seism_x = sismo.loads.seism_loads['Sismo_DinX'] + ' Max'
    seism_y = sismo.loads.seism_loads['Sismo_DinY'] + ' Max'
    zona = sismo.data.zona
    suelo = sismo.data.suelo
    categoria = sismo.data.categoria
    Z,U,S,Tp,Tl = sismo.data.Z,sismo.data.U,sismo.data.S,sismo.data.Tp,sismo.data.Tl
    Rox,Roy,Ia,Ip = sismo.data.Rox,sismo.data.Roy,sismo.data.Ia,sismo.data.Ip
    Tx,Ty,Cx,Cy = sismo.data.Tx,sismo.data.Ty,sismo.data.Cx,sismo.data.Cy
    kx,ky = sismo.data.kx,sismo.data.ky

    p_blando_x = sismo.tables.piso_blando_table.query('OutputCase == @seism_x')
    p_blando_y = sismo.tables.piso_blando_table.query('OutputCase == @seism_y')
    torsion_x = sismo.tables.torsion_table.query('OutputCase == @seism_x')
    torsion_y = sismo.tables.torsion_table.query('OutputCase == @seism_y')

    #Espectro de Respuestas
    T = sismo.T
    Sax = sismo.Sax
    Say = sismo.Say
    Rx = sismo.data.Rx
    Ry = sismo.data.Ry

    #Desplazamientos
    disp_x = sismo.disp_x
    disp_y = sismo.disp_y
    heights = sismo.heights

    #Derivas
    drifts_x = sismo.drifts_x
    drifts_y = sismo.drifts_y
    max_drift =sismo.data.max_drift_x
    heights_drifts = sismo.heights_drifts

    #datos discontinuidad de diafragma
    sec_change = {'aligerado':[7.51,0.05],
                'macisa':[2.25,0.20]}
    openings = {'aberturas':[(4.02,2.3),(1.1,2.3),(1.2,19)],
                'area_planta' : 120.41}
    
    #datos de esquinas entrantes
    datos_esquinas={'esq_X':4.95,
                'esq_Y':2.30,
                'dim_X':7.51,
                'dim_Y':15.28}
    
    #Cargas sismicas
    sis_estatico = sismo.tables.static_seism

    # Datos separacion
    datos_sep={'altura_edificio':max(heights)*100,
               'despl_max_X':max(disp_x)*100,
               'despl_max_Y':max(disp_y)*100}

    geometry_options = { "left": "2.5cm", "top": "1.5cm" }
    doc = Document(geometry_options=geometry_options)
    doc.packages.append(Package('xcolor', options=['dvipsnames']))
    doc.packages.append(Package('graphicx'))
    doc.preamble.append(NoEscape(r'\graphicspath{ {%s/} }'%os.getcwd().replace('\\','/')))
    
    sec = Section('Análisis Sísmico')
    
    p_sitio = parametros_sitio()
    f_zona = factor_zona(zona)
    f_suelo = factor_suelo(zona, suelo)
    p_suelo = periodos_suelo(suelo)   
    s_est = sist_estructural(sist_x,sist_y)
    f_amp = factor_amplificacion()
    f_imp = factor_importancia(categoria)
    t_resumen = tabla_resumen(Z,U,S,Tp,Tl,Rox,Roy,Ia,Ip)
    e_resp = espectro_respuesta(T,Sax,Say,Tp,Tl,Rx,Ry)
    p_sis = peso_sismico()
    e_accidental = excentricidad_accidental()
    a_modal = ana_modal(sismo.tables.modal)
    a_irreg = analisis_irregularidades()          
    i_rig = irreg_rigidez(p_blando_x,p_blando_y)
    i_masa = irreg_masa(sismo.tables.rev_masa_table)        
    i_torsion = irreg_torsion(torsion_x,torsion_y)
    i_discontinuidad = irreg_discontinuidad_diaf(sec_change=sec_change, openings=openings)
    i_esquinas = irreg_esquinas_entrantes(datos_esquinas)
    analisis_din = analisis_dinamico()
    criterios_comb= criterios_combinacion()
    desplaz_lat= desplazamientos_laterales(heights,disp_x,disp_y,Rx,Ry)
    verif_derivas= verificacion_derivas(sist_x,sist_y,heights_drifts,drifts_x,drifts_y,max_drift,Rx,Ry)
    verif_sist_est = verificacion_sist_est()
    analisis_est = analisis_estatico()
    corte_basal= cortante_basal(Z,U,Tx,Ty,Cx,Cy,kx,ky,S,Rox,Roy,Ia,Ip,sis_estatico)
    corte_basal_min = fuerza_cortante_min(sismo.tables.shear_table)
    sep_edificios= separacion_edificios(datos_sep)
    
    obj_list = [p_sitio,f_zona,f_suelo,p_suelo,s_est,f_amp,f_imp,t_resumen,
            e_resp,p_sis,e_accidental,a_modal,
            a_irreg,i_rig,i_masa,i_torsion,i_discontinuidad,i_esquinas,
            analisis_din,criterios_comb,
            desplaz_lat,verif_derivas,verif_sist_est,
            analisis_est,corte_basal,corte_basal_min,sep_edificios]

    for i in obj_list:
        sec.append(i)

    doc.append(sec)
    print("\n")
    print("Iniciando la generación del documento en formato .pdf y .tex...")
    doc.generate_pdf('out/Memoria Sismo2')
    doc.generate_tex('out/Memoria Sismo2')
    print("El documento ha sido generado con éxito")
    