import streamlit as st
import pandas as pd
import numpy as np
import shapely.wkt as wkt
import plotly.express as px
import folium
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from bs4 import BeautifulSoup

from scripts.getdatamarket import getdatamarket

from modulos.stylefunctions import style_function

def main(inputvar):
    
    formato = {
               'reporte_mls':False,
               'inputvar_mls':{}
               }
    
    for key,value in formato.items():
        if key not in st.session_state: 
            st.session_state[key] = value
            
    col1,col2,col3 = st.columns(3)
    with col3:
        if st.button('Nueva busqueda'):
            st.session_state.reporte_mls = False
            st.session_state.inputvar_mls = {}
            st.rerun()

    polygon         = inputvar['polygon'] if 'polygon' in inputvar else None
    tipoinmueble    = inputvar['tipoinmueble'] if 'tipoinmueble' in inputvar else None
    tiponegocio     = inputvar['tiponegocio'] if 'tiponegocio' in inputvar else None
    areamin         = inputvar['areamin'] if 'areamin' in inputvar else 0
    areamax         = inputvar['areamax'] if 'areamax' in inputvar else 0
    valormin        = inputvar['valormin'] if 'valormin' in inputvar else 0
    valormax        = inputvar['valormax'] if 'valormax' in inputvar else 0
    habitacionesmin = inputvar['habitacionesmin'] if 'habitacionesmin' in inputvar else 0
    habitacionesmax = inputvar['habitacionesmax'] if 'habitacionesmax' in inputvar else 0
    banosmin        = inputvar['banosmin'] if 'banosmin' in inputvar else 0
    banosmax        = inputvar['banosmax'] if 'banosmax' in inputvar else 0
    garajesmin      = inputvar['garajesmin'] if 'garajesmin' in inputvar else 0
    garajesmax      = inputvar['garajesmax'] if 'garajesmax' in inputvar else 0
    
    with st.spinner('Buscando información'):
        datamarket = getdatamarket(polygon=polygon, tipoinmueble=tipoinmueble, tiponegocio=tiponegocio, areamin=areamin, areamax=areamax, valormin=valormin, valormax=valormax, habitacionesmin=habitacionesmin, habitacionesmax=habitacionesmax, banosmin=banosmin, banosmax=banosmax, garajesmin=garajesmin, garajesmax=garajesmax)


        
    #-------------------------------------------------------------------------#
    # Ordenar
    col1,col2 = st.columns(2)
    
    with col1:
        seleccion = st.selectbox('Ordenar por:', options=['Más reciente','Menos reciente','Mayor valor','Menor valor','Mayor área','Menor área'])
        
    if 'venta' in tiponegocio.lower():
        valor = 'valorventa'
    elif 'arriendo' in tiponegocio.lower():
        valor = 'valorarriendo'
                
    if 'Más reciente' in seleccion:
        datamarket = datamarket.sort_values(by='fecha_inicial',ascending=False)
    if 'Menos reciente' in seleccion:
        datamarket = datamarket.sort_values(by='fecha_inicial',ascending=True)
    if 'Mayor valor' in seleccion:
        datamarket = datamarket.sort_values(by=valor,ascending=False)
    if 'Menor valor' in seleccion:
        datamarket = datamarket.sort_values(by=valor,ascending=True)
    if 'Mayor área' in seleccion:
        datamarket = datamarket.sort_values(by='areaconstruida',ascending=False)
    if 'Menor área' in seleccion:
        datamarket = datamarket.sort_values(by='areaconstruida',ascending=True)        
    
    datashow = pd.DataFrame()
    if not datamarket.empty:
        datamarket.index = range(len(datamarket))
        datashow = datamarket[0:200]
    #-------------------------------------------------------------------------#
    # Mapa principal
    m = folium.Map(location=[st.session_state.latitud, st.session_state.longitud], zoom_start=st.session_state.zoom_start,tiles="cartodbpositron")
    if st.session_state.geojson_data is not None:
        folium.GeoJson(st.session_state.geojson_data, style_function=style_function).add_to(m)
    
    
    if not datashow.empty:
        img_style = '''
                <style>               
                    .property-image{
                      flex: 1;
                    }
                    img{
                        width:200px;
                        height:120px;
                        object-fit: cover;
                        margin-bottom: 2px; 
                    }
                </style>
                '''
        for i, items in datashow.iterrows():
            if isinstance(items['imagen_principal'], str) and len(items['imagen_principal'])>20: imagen_principal =  items['imagen_principal']
            else: imagen_principal = "https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png"

            if 'venta' in tiponegocio.lower():
                valor = items['valorventa'] 
            elif 'arriendo' in tiponegocio.lower():
                valor = items['valorarriendo']
                
            direccion = "<b> Dirección:</b> Sin información <br>" 
            try:    
                if items['direccion'] is not None:
                    direccion = f"<b> Dirección:</b> {items['direccion']}<br>"
            except: pass
            try:    caracteristicas = f"<b> Área construida:</b> {items['areaconstruida']}<br>"
            except: caracteristicas = "<b> Área construida:</b> Sin información <br>" 
            try:    barrio = f"<b> Barrio:</b> {items['scanombre']}<br>"
            except: barrio = "<b> Barrio:</b> Sin información <br>" 
            try:    precio = f"<b> Precio:</b> ${valor:,.0f}<br>"
            except: precio = "<b> Precio:</b> Sin información <br>" 
            try:    valormt2 = f"<b> Valor por m<sup>2</sup>:</b> ${items['valormt2']:,.0f}<br>"
            except: valormt2 = "<b> Valor por m<sup>2</sup>:</b> Sin información <br>" 
            if all([x for x in ['habitaciones','banos','garajes'] if x in items]):
                try:    caracteristicas = f"{items['areaconstruida']} m<sup>2</sup> | {items['habitaciones']} H | {items['banos']} B | {items['garajes']} G <br>"
                except: caracteristicas = "<b> Caracteristicas:</b> Sin información <br>" 
             
            popup_content = f'''
            <!DOCTYPE html>
            <html>
              <head>
                {img_style}
              </head>
              <body>
                <div id="popupContent" style="cursor:pointer; display: flex; flex-direction: column; flex: 1;width:200px;">
                    <a href="https://cbre-property-981cc52a6655.herokuapp.com/Ficha_del_inmueble?code={items['code']}&tiponegocio={items['tiponegocio'].lower()}&tipoinmueble={items['tipoinmueble'].lower()}" target="_blank" style="color: black;">
                        <div class="property-image">
                          <img src="{imagen_principal}"  alt="property image" onerror="this.src='https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png';">
                        </div>
                        {precio}
                        {valormt2}
                        {caracteristicas}
                        {direccion}
                        {barrio}
                    </a>
                </div>
              </body>
            </html>
            '''
            folium.Marker(location=[items["latitud"], items["longitud"]], popup=popup_content).add_to(m)
    st_map = st_folium(m,width=1600,height=600)
    
    #-------------------------------------------------------------------------#
    # Lista de inmuebles
    if not datashow.empty:
        css_format = """
            <style>
              .property-image {
                width: 100%;
            	   height: 250px;
            	   overflow: hidden; 
                margin-bottom: 10px;
              }
              .price-info {
                font-family: 'Roboto', sans-serif;
                font-size: 20px;
                margin-bottom: 2px;
                text-align: center;
              }
              .caracteristicas-info {
                font-family: 'Roboto', sans-serif;
                font-size: 12px;
                margin-bottom: 2px;
                text-align: center;
              }
              img{
                max-width: 100%;
                width: 100%;
                height:100%;
                object-fit: cover;
                margin-bottom: 10px; 
              }
            </style>
        """
        
        imagenes = ''
        for i, items in datashow.iterrows():
            if isinstance(items['imagen_principal'], str) and len(items['imagen_principal'])>20: imagen_principal =  items['imagen_principal']
            else: imagen_principal = "https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png"
    
            if 'venta' in tiponegocio.lower():
                valor = items['valorventa'] 
            elif 'arriendo' in tiponegocio.lower():
                valor = items['valorarriendo']
                
            direccion = "<b> Dirección:</b> Sin información <br>" 
            try:    
                if items['direccion'] is not None:
                    direccion = f"<b> Dirección:</b> {items['direccion']}<br>"
            except: pass
            try:    caracteristicas = f"<b> Área construida:</b> {items['areaconstruida']}<br>"
            except: caracteristicas = "<b> Área construida:</b> Sin información <br>" 
            try:    barrio = f"<b> Barrio:</b> {items['scanombre']}<br>"
            except: barrio = "<b> Barrio:</b> Sin información <br>" 
            try:    precio = f"<b> Precio:</b> ${valor:,.0f}<br>"
            except: precio = "<b> Precio:</b> Sin información <br>" 
            try:    valormt2 = f"<b> Valor por m<sup>2</sup>:</b> ${items['valormt2']:,.0f}<br>"
            except: valormt2 = "<b> Valor por m<sup>2</sup>:</b> Sin información <br>" 
            if all([x for x in ['habitaciones','banos','garajes'] if x in items]):
                try:    caracteristicas = f"{items['areaconstruida']} m<sup>2</sup> | {items['habitaciones']} H | {items['banos']} B | {items['garajes']} G <br>"
                except: caracteristicas = "<b> Caracteristicas:</b> Sin información <br>" 
                 
            imagenes += f'''
            <div class="col-xl-3 col-sm-6 mb-xl-2 mb-2">
              <div class="card h-100">
                <div class="card-body p-3">
                <a href="https://cbre-property-981cc52a6655.herokuapp.com/Ficha_del_inmueble?code={items['code']}&tiponegocio={items['tiponegocio'].lower()}&tipoinmueble={items['tipoinmueble'].lower()}" target="_blank" style="color: black;">
                    <div class="property-image">
                      <img src="{imagen_principal}"  alt="property image" onerror="this.src='https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png';">
                    </div>
                    {precio}
                    {valormt2}
                    {caracteristicas}
                    {direccion}
                    {barrio}
                </a>
                </div>
              </div>
            </div>            
            '''
        if imagenes!='':
            texto = f"""
                <!DOCTYPE html>
                <html>
                  <head>
                  <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet"/>
                  <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet"/>
                  <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" id="pagestyle" rel="stylesheet"/>
                  {css_format}
                  </head>
                  <body>
                  <div class="container-fluid py-4">
                    <div class="row">
                    {imagenes}
                    </div>
                  </div>
                  </body>
                </html>
                """
            texto = BeautifulSoup(texto, 'html.parser')
            st.markdown(texto, unsafe_allow_html=True)
    
