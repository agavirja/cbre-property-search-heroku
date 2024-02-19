import streamlit as st
import pandas as pd
import numpy as np
import shapely.wkt as wkt
import plotly.express as px
import folium
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from bs4 import BeautifulSoup

from scripts.getinfopredialpolygon import getinfopredialpolygon
from scripts.getdatamarketcoddir import getdatamarketcoddir
from scripts.getrango import getrango
from scripts.inmuebleANDusosuelo import usosuelo2inmueble,inmueble2usosuelo

from modulos.display_snr_proceso import display_snr_proceso
from modulos.display_transacciones_polygon import display_transacciones_polygon
from modulos.display_dane import display_dane
from modulos.display_listjson import display_listjson

def main(inputvar):
    
    formato = {
               'reporte_busquedapredio':False,
               'inputvar_busquedapredio':{}
               }
    
    for key,value in formato.items():
        if key not in st.session_state: 
            st.session_state[key] = value
            
    col1,col2,col3 = st.columns(3)
    with col3:
        if st.button('Nueva busqueda'):
            st.session_state.reporte_busquedapredio = False
            st.session_state.inputvar_busquedapredio = {}
                
    if 'tipoinmueble' in inputvar:
        inputvar['precuso'] = inmueble2usosuelo(inputvar['tipoinmueble'])
    
    datalotes,datacatastro,datavigencia,datasnrprocesos,datasnrtable = getinfopredialpolygon(inputvar)

    #st.dataframe(datalotes)
    #st.dataframe(datacatastro)
    #st.dataframe(datavigencia)
    #st.dataframe(datasnrprocesos)
    #st.dataframe(datasnrtable)

    latitud  = 4.610270
    longitud = -74.079573
    polygon  = inputvar['polygon'] if 'polygon' in inputvar and isinstance(inputvar['polygon'], str) else None
    
    if polygon is not None:
        try:
            polygonl = wkt.loads(polygon)
            latitud  = polygonl.centroid.y
            longitud = polygonl.centroid.x
        except: pass
    
    dataprocesos_filter = pd.DataFrame()
    if not datasnrtable.empty and not datacatastro.empty:
        idd = datasnrtable['prechip'].isin(datacatastro['prechip'])
        if sum(idd)>0:
            idd = datasnrprocesos['docid'].isin(datasnrtable[idd]['docid'])
            if sum(idd)>0:
                dataprocesos_filter = datasnrprocesos[idd]
                idd                 = dataprocesos_filter['codigo'].isin(['125','126','168','169','0125','0126','0168','0169'])
                dataprocesos_filter = dataprocesos_filter[idd]

    # Header
    resumen = []
    if not datacatastro.empty:
            resumen += [
                {'name':'Número de predios','value':len(datacatastro)},
                {'name':'&nbsp;','value':'&nbsp;'},
                        ]
    if not dataprocesos_filter.empty:
        datapaso = dataprocesos_filter[dataprocesos_filter['valortransaccionmt2']>0]
        if not datapaso.empty:
            resumen += [
                {'name':'Número de transacciones','value':len(datapaso)},
                {'name':'Valor promedio transacciones','value':f"${datapaso['valortransaccionmt2'].median():,.0f}"},
                        ]
    if not datavigencia.empty and not datacatastro.empty:
        df = dataavaluostat(datavigencia,datacatastro)
        if not df.empty:
            resumen += [
                {'name':'Avalúo catastral por mt2','value':f"${df['avaluocatastralmt2'].median():,.0f}" },
                {'name':'Predial por mt2','value':f"${df['predialmt2'].median():,.0f}" },
                        ]

    display_listjson(resumen,2)
    #-------------------------------------------------------------------------#
    # Display Mapa poligonos
    display_transacciones_polygon(dataprocesos_filter,datalotes,polygon=polygon,latitud=latitud,longitud=longitud,showheader=False)

    #---------------------------------------------------------------------#
    # Analisis de las transacciones
    if not dataprocesos_filter.empty:
        col1, col2 = st.columns(2)
        with col1:
            df = dataprocesos_filter[dataprocesos_filter['preaconst'].notnull()]
            df = getrango(df,'preaconst')
            df['conteo'] = 1
            df = df.groupby(['rango','categoria'])['conteo'].count().reset_index()
            df.columns   = ['rango','categoria','conteo']
            df           = df[df['conteo']>0]
            df           = df.sort_values(by='categoria',ascending=True)
            df.index     = range(len(df))
            fig          = px.bar(df, x="rango", y="conteo", text="conteo", title="Áreas de los predios de transacciones")
            fig.update_traces(texttemplate='%{y:.0f}', textposition='outside', marker_color='#0095ff')
            fig.update_layout(title_x=0.2,height=400, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True,sharing="streamlit", theme="streamlit")
            
        with col2:
            df = dataprocesos_filter[dataprocesos_filter['preaconst'].notnull()]
            df = df[(df['cuantia']>0) & (df['preaconst']>0)]
            df['cuantia'] = df['cuantia']/df['preaconst']
            df            = getrango(df,'preaconst')
            df['conteo']  = 1
            df = df.groupby(['rango','categoria'])['cuantia'].median().reset_index()
            df.columns   = ['rango','categoria','cuantia']
            df           = df[df['cuantia']>0]
            df           = df.sort_values(by='categoria',ascending=True)
            df.index     = range(len(df))
            fig          = px.bar(df, x="rango", y="cuantia", text="cuantia", title="Cuantía por área de los predios")
            fig.update_traces(texttemplate='$%{y:,.0f}', textposition='outside', marker_color='#0095ff')
            fig.update_layout(title_x=0.2,height=400, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True,sharing="streamlit", theme="streamlit")
            
        with col1:
            df = dataprocesos_filter.groupby('year')['cuantia'].count().reset_index()
            if not df.empty:
                df.columns  = ['year','conteo']
                df['year']   = pd.to_numeric(df['year'],errors='coerce')
                df           = df[(df['conteo']>0) & (df['year']>0)]
                df           = df.sort_values(by='year',ascending=True)
                df.index     = range(len(df))
                df['year']   = df['year'].astype(int).astype(str)
                fig          = px.bar(df, x="year", y="conteo", text="conteo", title="Transacciones por año")
                fig.update_traces(texttemplate='%{y:,.0f}', textposition='outside', marker_color='#0095ff')
                fig.update_layout(title_x=0.2,height=400, xaxis_title=None, yaxis_title=None)
                st.plotly_chart(fig, use_container_width=True,sharing="streamlit", theme="streamlit")
            
        with col2:
            df = dataprocesos_filter[dataprocesos_filter['cuantia'].notnull()]
            df = getrango(df,'cuantia')
            df['conteo'] = 1
            df = df.groupby(['rango','categoria'])['conteo'].count().reset_index()
            df.columns   = ['rango','categoria','conteo']
            df           = df[df['conteo']>0]
            df           = df.sort_values(by='categoria',ascending=True)
            df.index     = range(len(df))
            try: df['rango'] = df['rango'].apply(lambda x: f"${x:,.0f} MM")
            except: pass
            fig          = px.bar(df, x="rango", y="conteo", text="conteo", title="Transacciones por cuantía")
            fig.update_traces(texttemplate='%{y:.0f}', textposition='outside', marker_color='#0095ff')
            fig.update_layout(title_x=0.2,height=400, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True,sharing="streamlit", theme="streamlit")


    #-------------------------------------------------------------------------#
    # Display Transacciones
    if not dataprocesos_filter.empty:
        display_snr_proceso(dataprocesos_filter,titulo='Transacciones',downloadname='Descargar  información',showstats=False)

    #-------------------------------------------------------------------------#
    # Analisis demografico
    if 'polygon' in inputvar and isinstance(inputvar['polygon'], str):
        display_dane(inputvar['polygon'])
    
@st.cache_data
def dataavaluostat(datavigencia,datacatastro):
    dfgroup         = datavigencia.groupby(['chip'])['vigencia'].max().reset_index()
    dfgroup.columns = ['chip','vigencia']
    dfgroup['ind']  = 1
    datavigencia  = datavigencia.merge(dfgroup,on=['chip','vigencia'],how='left',validate='m:1')
    datavigencia  = datavigencia[datavigencia['ind']==1]
    datavigencia  = datavigencia[['chip','valorAutoavaluo','valorImpuesto']]
    datavigencia  = datavigencia.drop_duplicates(subset='chip')
    datavigencia.columns = ['prechip','avaluocatastral','predial']
    
    datamerge    = datacatastro.drop_duplicates(subset='prechip',keep='first')
    datavigencia = datavigencia.merge(datamerge[['prechip','preaconst']],on='prechip',how='left',validate='m:1')
    datavigencia['avaluocatastralmt2'] = datavigencia['avaluocatastral']/datavigencia['preaconst']
    datavigencia['predialmt2']         = datavigencia['predial']/datavigencia['preaconst']
    return datavigencia
    
    
