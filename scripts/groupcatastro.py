import streamlit as st
import pandas as pd

@st.cache_data
def groupcatastro(df):
    w     = {'formato_direccion':'first','barmanpre':'count','prenbarrio':'first','prevetustz':['min','max'],'estrato':'median','preaconst':'sum','preaterre':'sum','usosuelo': lambda x: list(x.unique()),'actividad':lambda x: list(x.unique())}
    lista = ['barmanpre','direccion','predios','barrio','antiguedad_min','antiguedad_max','estrato','areaconstruida','areaterreno','usosuelo','actividad']
    for i in ['avaluocatastral','avaluoxmt2','predialxmt2']:
        if i in df:
            w.update({i:'median'})
            lista.append(i)
            
    df = df.groupby(['barmanpre']).agg(w).reset_index()
    df.columns = lista
    return df
