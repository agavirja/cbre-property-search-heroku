import streamlit as st
import pandas as pd
import numpy as np
import shapely.wkt as wkt
import plotly.express as px
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
from sqlalchemy import create_engine 


from shapely.geometry import Point, Polygon
from geopy.distance import geodesic

from scripts.circle_polygon import circle_polygon
from scripts.getinfopredialpolygon import getinfopredialpolygon

from modulos.map_streetview import map_streetview
from modulos.display_transacciones_polygon import display_transacciones_polygon
from modulos.display_snr_proceso import display_snr_proceso


def main(inputvar):

    formato = {
               'reporte_duedilligence':False,
               'inputvar_duedilligence':{},
               'page_number':1,
               }
    for key,value in formato.items():
        if key not in st.session_state: 
            st.session_state[key] = value
            
    with st.spinner('Buscando información'):
        barmanpre     = inputvar['barmanpre']
        data,datalote = getinfolote(barmanpre)

    #-------------------------------------------------------------------------#
    # Mapa y streetview
    #-------------------------------------------------------------------------#
    polygon  = None
    latitud,longitud  = None, None
    if not data.empty and 'latitud' in data and 'longitud' in data:
        latitud  = data['latitud'].iloc[0]
        longitud = data['longitud'].iloc[0]

    if not datalote.empty:
        polygon = wkt.loads(datalote['wkt'].iloc[0]) 
        #map_streetview(polygon)
        
    if not latitud and not longitud and polygon:
        try:
            polygonl = wkt.loads(polygon) 
            latitud  = polygonl.centroid.y
            longitud = polygonl.centroid.x
        except: 
            try:
                latitud  = polygon.centroid.y
                longitud = polygon.centroid.x
            except: pass
        
    #if latitud and longitud and not polygon:
    #    map_streetview(polygon=None,latitud=latitud,longitud=longitud)
    
    maxmeters  = 500
    col1, col2 = st.columns(2)
    with col1:
        metros = st.slider('Metros a la redonda', min_value=0, max_value=maxmeters, value=200,step=100)

    inputvar = {
        'polygon':str(circle_polygon(maxmeters,latitud,longitud)),
        'areamin':0,
        'areamax':0,
        'precuso':data['precuso'].to_list(),
        'metros':maxmeters
        }
    
    #-------------------------------------------------------------------------#
    # Trasnacciones en metros a la redonda
    #-------------------------------------------------------------------------#
    datalotes,datacatastro,datavigencia,datasnrprocesos,datasnrtable = getdatabymeters(inputvar,latitud,longitud,metros)
    display_transacciones_polygon(datasnrprocesos,datalotes,polygon=str(circle_polygon(metros,latitud,longitud)),latitud=latitud,longitud=longitud,barmanpreref=barmanpre)

    #-------------------------------------------------------------------------#
    # Descripcion SNR del predio
    #-------------------------------------------------------------------------#
    if not datasnrprocesos.empty:
        
        col1, col2 = st.columns(2)
        with col1:
            filtro = st.selectbox('Filtrar transacciones por:', options=['Más reciente','Menos reciente','Mayor cuantía','Menor cuantía','Mayor área','Menor área'])
            if 'Más reciente' in filtro:
                datasnrprocesos = datasnrprocesos.sort_values(by='fecha_documento_publico',ascending=False)
            if 'Menos reciente' in filtro:
                datasnrprocesos = datasnrprocesos.sort_values(by='fecha_documento_publico',ascending=True)
            if 'Mayor cuantía' in filtro:
                datasnrprocesos = datasnrprocesos.sort_values(by='cuantia',ascending=False)
            if 'Menos cuantía' in filtro:
                datasnrprocesos = datasnrprocesos.sort_values(by='cuantia',ascending=True)   
            if 'Mayor área' in filtro:
                datasnrprocesos = datasnrprocesos.sort_values(by='preaconst',ascending=False)
            if 'Menos área' in filtro:
                datasnrprocesos = datasnrprocesos.sort_values(by='preaconst',ascending=True)   

        with col2:
            variables = ['predirecc', 'codigo', 'nombre', 'tarifa', 'cuantia','preaconst', 'fecha_documento_publico', 'tipo_documento_publico', 'numero_documento_publico', 'entidad', 'link', 'preaconst', 'preaterre', 'valortransaccionmt2']
            variables = [x for x in variables if x in datasnrprocesos]
            if variables:
                dataexport = datasnrprocesos[variables]
                dataexport.rename(columns={'predirecc': 'Direccion', 'codigo': 'Codigo', 'nombre': 'Nombre', 'tarifa': 'Tarifa', 'cuantia': 'Cuantia','preaconst':'Area construida', 'fecha_documento_publico': 'Fecha del documento', 'tipo_documento_publico': 'Tipo de documento', 'numero_documento_publico': 'Numero de documento publico', 'entidad': 'Notaria', 'link': 'Link', 'preaconst': 'Area construida', 'preaterre': 'Area de terreno', 'valortransaccionmt2': 'Cuantia por mt2'},inplace=True)
                
            st.write('')
            st.write('')
            csv = convert_df(dataexport)     
            st.download_button(
               'Descargar información transacciones',
               csv,
               "data_info_transacciones.csv",
               "text/csv"
            )

        display_snr_proceso(datasnrprocesos.iloc[0:50,:],titulo=f'Transacciones en un radio de {metros} metros',download=False)


    #st.write('Mostrar contra que se esta comparando en el poligono: mismo usosuelo')
    #st.write('Mostrar estadisticas de catastro: tipologia de los inmuebles')
    #st.write('Mostrar grafias de las estadisticas de transacciones, por ano, por mt2 de los apartamentos, etc')
    #st.write('Mostrar modulo GI nuevos - Si es apto,oficina, etc')


@st.cache_data
def getinfolote(barmanpre):
    user        = st.secrets["user_bigdata"]
    password    = st.secrets["password_bigdata"]
    host        = st.secrets["host_bigdata_lectura"]
    schema      = st.secrets["schema_bigdata"]
    engine      = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')
    data        = pd.read_sql_query(f"SELECT distinct(precuso) as precuso, latitud, longitud FROM  {schema}.data_bogota_catastro WHERE barmanpre ='{barmanpre}'" , engine)
    datalote    = pd.read_sql_query(f"SELECT lotcodigo as barmanpre, ST_AsText(geometry) as wkt FROM  {schema}.data_bogota_lotes WHERE lotcodigo ='{barmanpre}'" , engine)
    engine.dispose()
    return data,datalote
    
@st.cache_data
def getdistance(inputvar,latitud,longitud):
    datalotes,datacatastro,datavigencia,datasnrprocesos,datasnrtable = getinfopredialpolygon(inputvar)
    if not datalotes.empty:
        datalotes['distancia'] = datalotes['wkt'].apply(lambda x: calcular_distancia_punto_poligono(x,latitud,longitud))
    return datalotes,datacatastro,datavigencia,datasnrprocesos,datasnrtable 

@st.cache_data
def getdatabymeters(inputvar,latitud,longitud,metros):
    datalotes,datacatastro,datavigencia,datasnrprocesos,datasnrtable = getdistance(inputvar,latitud,longitud)
    if not datalotes.empty:
        datalotes = datalotes[datalotes['distancia']<=(metros/1000)]
        if not datacatastro.empty:
            datacatastro = datacatastro[datacatastro['barmanpre'].isin(datalotes['barmanpre'])]
            if not datavigencia.empty:
                datavigencia = datavigencia[datavigencia['chip'].isin(datacatastro['prechip'])]
            if not datasnrtable.empty:
                datasnrtable = datasnrtable[datasnrtable['prechip'].isin(datacatastro['prechip'])]
                if not datasnrprocesos.empty:
                    datasnrprocesos = datasnrprocesos[datasnrprocesos['docid'].isin(datasnrtable['docid'])]
                    datasnrprocesos = datasnrprocesos[datasnrprocesos['codigo'].isin(['125','126','168','169','0125','0126','0168','0169'])]
    
    if not datasnrprocesos.empty:
        datasnrprocesos = datasnrprocesos.sort_values(by='fecha_documento_publico',ascending=False)
    return datalotes,datacatastro,datavigencia,datasnrprocesos,datasnrtable

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def calcular_distancia_punto_poligono(row,latitud,longitud):
    polygon       = wkt.loads(row)
    punto_ejemplo = Point(longitud, latitud)
    distancia_km  = geodesic((punto_ejemplo.y, punto_ejemplo.x), (polygon.centroid.y, polygon.centroid.x)).kilometers
    return distancia_km
