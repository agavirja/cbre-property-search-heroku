import streamlit as st
import pandas as pd
import shapely.wkt as wkt
import folium
from folium.features import CustomIcon
from streamlit_folium import st_folium

from modulos.stylefunctions import style_function,style_referencia,style_lote_transacciones,style_lote

def display_owner_map(data,latitud,longitud):
    
    if not data.empty:
        #---------------------------------------------------------------------#
        # Mapa de transacciones en el radio
        m = folium.Map(location=[latitud, longitud], zoom_start=12,tiles="cartodbpositron")

        for _,items in data.iterrows():
            poly      = items['wkt']
            polyshape = wkt.loads(poly)
    
            try:    titular = f"<b> Empresa:</b> {items['titular']}<br>"
            except: titular = "<b> Empresa:</b> Sin información <br>" 
            try:    direccion = f"<b> Dirección:</b> {items['predirecc']}<br>"
            except: direccion = "<b> Dirección:</b> Sin información <br>" 
            try:    barrio = f"<b> Barrio:</b> {items['prenbarrio']}<br>"
            except: barrio = "<b> Barrio:</b> Sin información <br>" 
            try:    fecha = f"<b> Fecha del documento:</b> {items['fecha_documento_publico']}<br>"
            except: fecha = "<b> Fecha del documento:</b> Sin información <br>" 
           
            popup_content =  f'''
            <!DOCTYPE html>
            <html>
                <body>
                    <div id="popupContent" style="cursor:pointer; display: flex; flex-direction: column; flex: 1;width:200px;">
                        <a href="http://urbextestapp.streamlit.app/Due_dilligence_digital?code={items['barmanpre']}&variable=barmanpre" target="_blank" style="color: black;">
                            {titular}
                            {direccion}
                            {barrio}
                            {fecha}
                        </a>
                    </div>
                </body>
            </html>
            '''
            folium.GeoJson(polyshape, style_function=style_referencia).add_child(folium.Popup(popup_content)).add_to(m)
            folium.Marker(location=[items["latitud"], items["longitud"]]).add_to(m)
        st_map = st_folium(m,width=1600,height=600)
