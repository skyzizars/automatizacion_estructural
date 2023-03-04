import sys
import os
sys.path.append(os.getcwd())


import latex_utils as ltx
from pylatex import Document, Section, Subsection,Subsubsection, Tabular, NoEscape, MiniPage, Center, MultiColumn, Table, Figure, Tabularx
from pylatex.utils import NoEscape, bold
from pylatex.package import Package
from pylatex.base_classes import Environment
from ordered_set import OrderedSet
import pandas as pd
import warnings
warnings.simplefilter('ignore', category=Warning)

def factor_zona(obj,zona,insert='',o_type=Subsubsection):
    obj.packages.append(Package('array'))
    obj.packages.append(Package('colortbl'))
    obj.packages.append(Package('graphicx'))
    obj.packages.append(Package('caption'))
    
    
    df = [['4','0.45'],['3','0.35'],['2','0.25'],['1','0.10']]
    df[4-zona][1] = r'\textcolor[rgb]{ 1,  0,  0}{\textbf{'+df[4-zona][1]+r'}}'
    df[4-zona] = [i+r'\cellcolor[rgb]{ .949,  .949,  .949} ' for i in df[4-zona]]
        
    with obj.create(o_type('Factor de Zona')):
        obj.append(insert)
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
                    obj.append(NoEscape('\\includegraphics[width=4cm]{mapa_zona}'))
            tab.append(NoEscape(r'\caption*{Fuente: E-030 (2018)}'))



if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.getcwd()+'\\..')
    
    zona = 2
    suelo = 'S1'
    categoria = 'A2'
    
    #Generación del documento
    geometry_options = { "left": "2.5cm", "top": "1.5cm" }
    doc = Document(geometry_options=geometry_options)
    doc.packages.append(Package('xcolor', options=['dvipsnames']))
    
    
    s1 = Section('Análisis Sísmico')

    coments_zona1 = 'La ubicación de este proyecto es en la ciudad de Cusco, en el distrito de Cusco. Siguiendo los parámetros de la norma de diseño sismorresistente E.030 de octubre de 2018, la estructura se encuentra en la Zona '+str(zona)

    factor_zona(s1, zona, insert=coments_zona1, o_type=Subsection)
    coments_zona2=NoEscape(r'Este factor se interpreta como la aceleración máxima horizontal en el suelo rígido con una probabilidad de 10 \% de ser excedida en 50 años')
    s1.append(coments_zona2)
    
    
    doc.append(s1)

    doc.generate_pdf('prueba_memoria')
    doc.generate_tex('prueba_memoria')