import texto as txt
from pylatex import Document, Section, Subsection
from pylatex import Package
from pylatex.utils import NoEscape

doc = Document()
doc.packages.append(Package('amssymb'))


mem_datos = txt.replace_variables(txt.datos, txt.variables)




with doc.create(Section("Análisis de la Viga")):
    with doc.create(Subsection('Datos')):
        doc.append(NoEscape(mem_datos))
        
    with doc.create(Subsection("Diseño por flexión")):
        pass
        
doc.generate_pdf('./archivos/Texto')
