from pylatex import Document, Section, Subsection,Subsubsection, Tabular, NoEscape, MiniPage, Center, MultiColumn, Table, Figure, Tabularx
from pylatex.utils import NoEscape, bold
from pylatex.package import Package
from pylatex.base_classes import Environment
#from ordered_set import OrderedSet
import pandas as pd
import warnings
warnings.simplefilter('ignore', category=Warning)

s1=Section('Sección 1')
s1.packages.append(Package('array'))
s1.append('Línea 1')
#print(s1.dumps())
with s1.create(Subsection('Subsección 1')) as ss1:
    s1.append('dadadasf')

ss1=Subsection('Subsección 1')
ss1.apppend('dadadss')
s1.append(ss1)

Doc=Document()
Doc.append('Título')
Doc.append(s1)
print(Doc.dumps())
