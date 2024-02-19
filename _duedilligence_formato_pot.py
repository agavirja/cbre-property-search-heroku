import streamlit as st
import pandas as pd
import shapely.wkt as wkt
import plotly.express as px
import streamlit.components.v1 as components
import webbrowser
from bs4 import BeautifulSoup
from sqlalchemy import create_engine 

from modulos.map_streetview import map_streetview
from modulos.display_pot import display_pot

from scripts.point2POT import point2POT
from scripts.getmanzanaslote import getmanzanaslote

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
        datamanzana,datamanzanalotes = getmanzanaslote(barmanpre)
        
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
        map_streetview(polygon)
        
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
        
    result = point2POT(latitud,longitud)

    #st.write('Poner informacion de la manzana, cuantos predios, cuantos lotes, tamano, etc')
    
    #-------------------------------------------------------------------------#
    # Display POT
    display_pot(result,datamanzanalotes,datamanzana,latitud,longitud)
    
    
    col1,col2 = st.columns(2)
    with col1:
        if st.button('Análisis del edificio'):
            webbrowser.open_new_tab(f"http://urbextestapp.streamlit.app/Due_dilligence_digital?code={barmanpre}&variable=barmanpre")
    with col2:
        if st.button('Tendencia de mercado en la zona'):
            webbrowser.open_new_tab(f"http://urbextestapp.streamlit.app/Due_dilligence_digital?code={barmanpre}&variable=barmanpre&tipo=radio")
    components.html(
        """
    <script>
    const elements = window.parent.document.querySelectorAll('.stButton button')
    elements[0].style.backgroundColor = '#68c8ed';
    elements[0].style.fontWeight = 'bold';
    elements[0].style.color = 'white';
    elements[0].style.width = '100%';
    
    elements[1].style.backgroundColor = '#68c8ed';
    elements[1].style.fontWeight = 'bold';
    elements[1].style.color = 'white';
    elements[1].style.width = '100%';
    
    elements[2].style.backgroundColor = '#68c8ed';
    elements[2].style.fontWeight = 'bold';
    elements[2].style.color = 'white';
    elements[2].style.width = '100%';
    </script>
    """
    )
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
