import etabs_utils as etb
import pandas as pd
import comtypes.client


SapModel, EtabsObject = etb.connect_to_etabs()


etb.set_concrete(SapModel,fc=210)
etb.set_rebar(SapModel)

etb.set_beam_sections(SapModel, b=30, h=45)

etb.set_column_sections(SapModel,b=30,h=50)

etb.set_shell_sections(SapModel,20)

points = {
    'X':[0,0,1,1],
    'Y':[0,1,1,0],
    'Z':[0,0,0,0]}
etb.draw_shell(SapModel,points,20)

etb.set_wall_sections(SapModel,e=20)

etb.set_wall_sections(SapModel,e=25)

s_data = etb.get_story_data(SapModel)
s_data.Height = s_data.Height.astype('float64')
s_data.dtypes
s_data = s_data.sort_values(by=['Story'])
s_data['t_height'] = s_data['Height'].cumsum()
s_data.index = s_data.Story


pi=[800,800]
pf=[800,1600]
stories = ['Story1','Story3']
etb.draw_wall(SapModel,pi,pf,20,stories)

SapModel.AreaObj.GetAllAreas()