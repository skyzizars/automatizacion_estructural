from turtle import position
from pylatex import Document, Section, Subsection, Figure, Tabular, MultiColumn, SubFigure
from pylatex.utils import NoEscape

doc = Document()


txt_zonificación = r'''
La ubicación de este proyecto es en la ciudad de Cusco, en el distrito de Cusco. Siguiendo los
parámetros de la norma de diseño sismorresistente E.030 de octubre de 2018, la estructura se
encuentra en la Zona 2. Por lo tanto el factor de zona tendrá el valor de: 0.25
'''
tabla_zona = [('ZONA','Z'),(4,0.45),(3,0.35),(2,0.25),(1,'0.10')]

with doc.create(Section('Análisis Sísmico')):
    with doc.create(Subsection('Parámetros de Sitio')):
        doc.append(NoEscape(txt_zonificación))
        with doc.create(Figure(position='t')) as fig:
            with doc.create(SubFigure(position='h!')) as left_fig:
                left_fig.add_image('zonificacion.jpg',width='5cm')

            with doc.create(SubFigure(position='b')) as right_fig:
                with doc.create(Tabular('cc')) as table:
                    table.add_row((MultiColumn(2,data='Factor de Zona'),))
                    for row in tabla_zona:
                        table.add_row(row)


doc.generate_pdf('Reporte Sísmico',clean_tex=True)