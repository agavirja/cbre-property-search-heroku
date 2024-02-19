import streamlit as st
import pandas as pd
import shapely.wkt as wkt
import folium
from folium.features import CustomIcon
from streamlit_folium import st_folium

from modulos.stylefunctions import style_function,style_referencia,style_lote_transacciones,style_lote

def display_reconversion_map(data,latitud,longitud):
    
    if not data.empty:
        #---------------------------------------------------------------------#
        # Mapa de transacciones en el radio
        m = folium.Map(location=[latitud, longitud], zoom_start=12,tiles="cartodbpositron")

        for _,items in data.iterrows():
            poly      = items['wkt']
            polyshape = wkt.loads(poly)

            try:    direccion = f"<b> Dirección:</b> {items['formato_direccion']}<br>"
            except: direccion = "<b> Dirección:</b> Sin información <br>"     
            try:    areaconstruida = f"<b> Área construida:</b> {items['areaconstruida_total']}<br>"
            except: areaconstruida = "<b> Área construida:</b> Sin información <br>" 
            try:    areaterrno = f"<b> Área terreno:</b> {items['areaterreno_total']:.1f}<br>"
            except: areaterrno = "<b> Área terreno:</b> Sin información <br>" 
            try:    propietarios = f"<b> Propietarios:</b> {items['propietarios']}<br>"
            except: propietarios = "<b> Propietarios:</b> Sin información <br>" 
            try:    predios = f"<b> Total de predios:</b> {items['predios_total']}<br>"
            except: predios = "<b> Total de predios:</b> Sin información <br>"                       
            try:    avaluo = f"<b> Total avalúo:</b> ${items['total_avaluo']:,.0f}<br>"
            except: avaluo = "<b> Total avalúo:</b> Sin información <br>" 
            try:    usosuelo = f"<b> Uso del suelo:</b> {items['usosuelo']}<br>"
            except: usosuelo = "<b> Uso del suelo:</b> Sin información <br>" 
            try:    avaluomt2 = f"<b> Uso del suelo:</b> ${items['avaluomt2']:,.0f}<br>"
            except: avaluomt2 = "<b> Uso del suelo:</b> Sin información <br>" 
            try:    
                if items['valortransaccionesmt2'] is not None: 
                    transaccionesmt2 = f"<b> Transacciones por mt2:</b> ${items['valortransaccionesmt2']:,.0f}<br>"
                else:   transaccionesmt2 = "<b> Transacciones por mt2:</b> Sin información <br>"     
            except: transaccionesmt2 = "<b> Transacciones por mt2:</b> Sin información <br>"                 
            
            popup_content =  f'''
            <!DOCTYPE html>
            <html>
                <body>
                    <div id="popupContent" style="cursor:pointer; display: flex; flex-direction: column; flex: 1;width:200px;">
                        <a href="https://cbre-property-981cc52a6655.herokuapp.com/Due_dilligence_digital?code={items['barmanpre']}&variable=barmanpre" target="_blank" style="color: black;">
                            {direccion}    
                            {areaconstruida}
                            {areaterrno}
                            {propietarios}
                            {predios}
                            {avaluo}
                            {usosuelo}
                            {avaluomt2}
                            {transaccionesmt2}
                        </a>
                    </div>
                </body>
            </html>
            '''
            folium.GeoJson(polyshape, style_function=style_referencia).add_child(folium.Popup(popup_content)).add_to(m)
            folium.Marker(location=[items["latitud"], items["longitud"]]).add_to(m)
        st_map = st_folium(m,width=1600,height=600)
