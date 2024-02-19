import streamlit as st
import pandas as pd
import shapely.wkt as wkt
import folium
from folium.features import CustomIcon
from streamlit_folium import st_folium

from modulos.stylefunctions import style_function,style_referencia,style_lote_transacciones,style_lote

def display_brand_map(data,latitud,longitud):
    
    if not data.empty:
        #---------------------------------------------------------------------#
        # Mapa de transacciones en el radio
        m = folium.Map(location=[latitud, longitud], zoom_start=12,tiles="cartodbpositron")

        for _,items in data.iterrows():
            poly      = items['wkt']
            polyshape = wkt.loads(poly)
    
            try:    empresa = f"<b> Empresa:</b> {items['empresa']}<br>"
            except: empresa = "<b> Empresa:</b> Sin información <br>" 
            try:    direccion = f"<b> Dirección:</b> {items['direccion']}<br>"
            except: direccion = "<b> Dirección:</b> Sin información <br>" 
            try:    nombre = f"<b> Nombre:</b> {items['nombre']}<br>"
            except: nombre = "<b> Nombre:</b> Sin información <br>" 
            try:    barrio = f"<b> Barrio:</b> {items['prenbarrio']}<br>"
            except: barrio = "<b> Barrio:</b> Sin información <br>"      
            popup_content =  f'''
            <!DOCTYPE html>
            <html>
                <body>
                    <div id="popupContent" style="cursor:pointer; display: flex; flex-direction: column; flex: 1;width:200px;">
                        <a href="https://cbre-property-981cc52a6655.herokuapp.com/Due_dilligence_digital?code={items['lotcodigo']}&variable=barmanpre" target="_blank" style="color: black;">
                            {empresa}
                            {direccion}
                            {nombre}
                            {barrio}
                        </a>
                    </div>
                </body>
            </html>
            '''
            
            folium.GeoJson(polyshape, style_function=style_referencia).add_child(folium.Popup(popup_content)).add_to(m)
            icon = folium.features.CustomIcon(
                icon_image = items["marker"],
                icon_size  = (15, 15),
            )
            folium.Marker(location=[items["latitud"], items["longitud"]], icon=icon).add_to(m)
        st_map = st_folium(m,width=1600,height=600)
