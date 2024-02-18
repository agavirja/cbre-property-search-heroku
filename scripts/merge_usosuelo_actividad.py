import streamlit as st
from scripts.getuso_destino import getuso_destino
from scripts.formato_direccion import formato_direccion

@st.cache_data
def merge_usosuelo_actividad(data):
    dataprecuso,dataprecdestin = getuso_destino()
    dataprecuso.rename(columns={'codigo':'precuso','tipo':'usosuelo','descripcion':'desc_usosuelo'},inplace=True)
    dataprecdestin.rename(columns={'codigo':'precdestin','tipo':'actividad','descripcion':'desc_actividad'},inplace=True)
    if 'precuso' in data:
        data = data.merge(dataprecuso,on='precuso',how='left',validate='m:1')
    if 'precdestin' in data:
        data = data.merge(dataprecdestin,on='precdestin',how='left',validate='m:1')
    if 'predirecc' in data: 
        data['formato_direccion'] = data['predirecc'].apply(lambda x: formato_direccion(x))
    return data
