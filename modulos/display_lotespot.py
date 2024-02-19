import streamlit as st
import pandas as pd
import shapely.wkt as wkt
import folium
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from bs4 import BeautifulSoup

from modulos.stylefunctions import style_function,style_referencia,style_lote_transacciones,style_lote

def display_lotespot(datalotes,polygon=None,latitud=None,longitud=None,barmanpreref=None,showheader=True):
    
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

    if not datalotes.empty:
        #---------------------------------------------------------------------#
        # Mapa de transacciones en el radio
        m = folium.Map(location=[latitud, longitud], zoom_start=16,tiles="cartodbpositron")

        if polygon:
            try: folium.GeoJson(polygon, style_function=style_function).add_to(m)
            except:
                try: folium.GeoJson(wkt.loads(polygon) , style_function=style_function).add_to(m)
                except: pass
                    
        for _,items in datalotes.iterrows():
            poly      = items['wkt']
            polyshape = wkt.loads(poly)
            try:    codigos = items['combinacion']
            except: codigos = '|'
            try:    combinacion = f"<b> Número de combinación de lotes:</b> {items['num_lotes_comb']}<br>"
            except: combinacion = "<b> Número de combinación de lotes:</b> Sin información <br>"            
            popup_content =  f'''
            <!DOCTYPE html>
            <html>
                <body>
                    <div id="popupContent" style="cursor:pointer; display: flex; flex-direction: column; flex: 1;width:220px;">
                        <a href="http://localhost:8501/Busqueda_lotes_poligono?code={codigos}" target="_blank" style="color: black;">
                            {combinacion}
                        </a>
                    </div>
                </body>
            </html>
            '''
            folium.GeoJson(polyshape, style_function=style_lote).add_child(folium.Popup(popup_content)).add_to(m)

        st_map = st_folium(m,width=1600,height=600)