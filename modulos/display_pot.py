import streamlit as st
import numpy as np
import pandas as pd
import streamlit.components.v1 as components
import folium
import shapely.wkt as wkt
import plotly.express as px
from streamlit_folium import st_folium
from bs4 import BeautifulSoup

from modulos.stylefunctions import style_function,style_referencia,style_lote_transacciones,style_lote
from modulos.display_listjson import display_listjson


def display_pot(datajson,datalotes,datamanzana,latitud,longitud):

    if datajson!={} or datajson!=[]:
        diccionario = getdiccionario()
        delfromkey  = ['id','responsabl','shapeleng','shapearea','responsabl','fechacapt','fechaacto','escalacap']
        
        html_build = ""
        for key,value in datajson.items():
            item = f"{key}"
            if key in diccionario:
                item = diccionario[key]
            html_paso = f"""
            <div class="box">
                <div class="title">{item}</div>
            """
            for keys,values in value[0].items():
                if keys not in delfromkey:
                    item = f"{keys}"
                    if keys in diccionario:
                        item = diccionario[keys]
                    html_paso += f"""
                    <div class="property" style="text-align: left;"><span>{item}:</span> <span>{values}</span></div>
                    """
            html_build += f"""
            {html_paso}
            </div>
            """
        
        style = """
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
    
            .container {
                display: flex;
                flex-wrap: wrap;
            }
    
            .box {
                border: 1px solid #ddd;
                padding: 10px;
                margin: 10px;
                width: 100%;
            }
    
            .title {
                font-weight: bold;
                font-size: 1.2em;
                margin-bottom: 10px;
            }
    
            .property {
                display: flex;
                justify-content: space-between;
            }
        </style>
        """
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {style}
        </head>
        <body>
            <div class="container">
                {html_build}
            </div>
        </body>
        </html>
        
        """
        
        texto = BeautifulSoup(html, 'html.parser')
        st.markdown(texto, unsafe_allow_html=True)
        
    
    datapaso = pd.DataFrame()
    if not datalotes.empty and not datamanzana.empty:
        datapaso         =  datamanzana.groupby('barmanpre').agg({'areaconstruida_total':'first','areaterreno_total':'first','predios_total':'first','propietarios':'first','formato_direccion':'first'}).reset_index()
        datapaso.columns = ['barmanpre','areaconstruida','areaterreno','predios','propietarios','direccion']
        datalotes        = datalotes.merge(datapaso,on='barmanpre',how='left',validate='m:1')
        
        datapaso['idmerge'] = 1
        datapaso         = datapaso.groupby('idmerge').agg({'areaconstruida':'sum','areaterreno':'sum','predios':'sum','propietarios':'sum'}).reset_index()
        datapaso.columns = ['idmerge','areaconstruida','areaterreno','predios','propietarios']
        datapaso.drop(columns=['idmerge'],inplace=True)
        datapaso['total_lotes'] = len(datalotes)
        
    if not datalotes.empty:
        
        #---------------------------------------------------------------------#
        # Mapa de transacciones en el radio
        m = folium.Map(location=[latitud, longitud], zoom_start=17,tiles="cartodbpositron")

        for _,items in datalotes.iterrows():
            poly      = items['wkt']
            polyshape = wkt.loads(poly)
            
            try:    direccion = f"<b> Dirección:</b> {items['direccion']}<br>"
            except: direccion = "<b> Área construida:</b> Sin información <br>"
            try:    areaterreno = f"<b> Área de terreno:</b> {round(items['areaterreno'],2)}<br>"
            except: areaterreno = "<b> Área de terreno:</b> Sin información <br>"
            try:    areaconstruida = f"<b> Área construida:</b> {round(items['areaconstruida'],2)}<br>"
            except: areaconstruida = "<b> Área construida:</b> Sin información <br>"
            try:    predios = f"<b> Predios:</b> {int(items['predios'])}<br>"
            except: predios = "<b> Predios:</b> Sin información <br>"
            try:    propietarios = f"<b> Propietarios:</b> {int(items['propietarios'])}<br>"
            except: propietarios = "<b> Propietarios:</b> Sin información <br>"
            
            popup_content =  f'''
            <!DOCTYPE html>
            <html>
                <body>
                    <div id="popupContent" style="cursor:pointer; display: flex; flex-direction: column; flex: 1;width:200px;">
                        <a href="https://cbre-property-981cc52a6655.herokuapp.com/Due_dilligence_digital?code={items['barmanpre']}&variable=barmanpre" target="_blank" style="color: black;">
                            {direccion}
                            {areaterreno}
                            {areaconstruida}
                            {predios}
                            {propietarios}
                        </a>
                    </div>
                </body>
            </html>
            '''
            
            folium.GeoJson(polyshape, style_function=style_lote).add_child(folium.Popup(popup_content)).add_to(m)
        st_map = st_folium(m,width=1600,height=400)
        
        
    if not datapaso.empty:

        variables = [
            {'name':'Número de lotes','variable':'total_lotes'},
            {'name':'Número de predios','variable':'predios'},
            {'name':'Número de propietarios','variable':'propietarios'},
            {'name':'Área de terreno','variable':'areaterreno'},
            {'name':'Área construida','variable':'areaconstruida'},
            ]
         
        resumen = []
        for i in variables:
            if i['variable'] in datapaso:
                if any([x for x in ['areaterreno','areaconstruida'] if i['variable'] in x]):
                    i.update({'value':round(datapaso[i['variable']].iloc[0],2)})
                elif any([x for x in ['total_lotes','predios','propietarios'] if i['variable'] in x]):
                    i.update({'value':int(datapaso[i['variable']].iloc[0])})
                resumen.append(i)
        display_listjson(resumen,3)
        
        
    if not datamanzana.empty:
        df = datamanzana.groupby('usosuelo').agg({'predios':'sum','areaconstruida':'sum','areaterreno':'sum'}).reset_index()
        df.columns = ['usosuelo','predios','areaconstruida','areaterreno']


        # Tipologia de predios en la manzana
        df         = df.sort_values(by='predios',ascending=False)
        df.index   = range(len(df))
        fig        = px.bar(df, x="usosuelo", y="predios", text="predios", title="Tipología de predios")
        fig.update_traces(texttemplate='%{y:.0f}', textposition='outside', marker_color='#0095ff')
        fig.update_layout(title_x=0.5,height=400, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True,sharing="streamlit", theme="streamlit")
  
        # Por area de areaterreno de los predios en la manzana
        df         = df.sort_values(by='areaterreno',ascending=False)
        df.index   = range(len(df))
        fig        = px.bar(df, x="usosuelo", y="areaterreno", text="areaterreno", title="Área de terreno de los predios")
        fig.update_traces(texttemplate='%{y:.0f}', textposition='outside', marker_color='#0095ff')
        fig.update_layout(title_x=0.5,height=400, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True,sharing="streamlit", theme="streamlit")

        # Por area de predios en la manzana
        df         = df.sort_values(by='areaconstruida',ascending=False)
        df.index   = range(len(df))
        fig        = px.bar(df, x="usosuelo", y="areaconstruida", text="areaconstruida", title="Área construida de los predios")
        fig.update_traces(texttemplate='%{y:.0f}', textposition='outside', marker_color='#0095ff')
        fig.update_layout(title_x=0.5,height=400, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True,sharing="streamlit", theme="streamlit")
   
        
@st.cache_data
def getdiccionario():
    diccionario = {'bogota_areaactividad':'Área de actividad', 
     'bogota_perimetrourbano':'Perimetro Urbano',
     'bogota_tratamientourbanistico':'Tratamiento Urbanistico',
     'bogota_unidadplaneamientolocal':'Unidad Planeamiento Local',
     'bogota_actuacionestrategica': 'Actuación Estrategica',
      'bogota_amenazaindesbordamiento': 'Amenaza de desbordamiento',
      'bogota_amenazainrompimientojarillo': 'Amenaza rompimiento',
      'bogota_amenazammrural': 'Amenaza mural',
      'bogota_cluster': 'Cluster',
      'bogota_espaciopublicocentropoblado': 'Espacio público centro poblado',
      'bogota_nodoequipamientourbano': 'Nodo equipamiento urbano',
      'bogota_nodotranspote': 'Nodo de transporte',
      'bogota_planparcial': 'Plan parcial',
      'bogota_priorizacionestudiosmm': 'Priorización Estidio',
      'bogota_sectorconsolidado': 'Secotr Consolidado',
      'bogota_sectorincompatibleusoresid': 'Secotr incompatible uso residencial',
      'bogota_sectorinteresurbanistico': 'Sector interés urbanistico',
      'bogota_sectorusoresidencial': 'Sector uso residencial',
      'bogota_sisdistareasprote': 'sisdistareasprote',
      'bogota_suelopriorizado': 'Suelo priorizado',
      'bogota_sueloreserva': 'Suelo reserva',
      'bogota_unidadplaneamientorural': 'Unidad planeamiento rural',
      'bogota_zonaindustrial': 'Zona industrial',
      
      'codigoid':'Código',
      'codigoare':'Código área de actividad',
      'nombreare':'Nombre área de actividad',
      'actoadmin':'Acto administrativo',
      'numeroact':'Número de acto adminsitrativo',
      'normativa':'Normativa',
      'observacio':'Observación',
      'codigotra':'Código tratamiento urbano',
      'nombretra':'Nombre tratamiento urbano',
      'tipologia':'Tipología',
      'alturamax':'Altura máxima',
      'nombre':'Nombre',
      'vocacion':'Vocación',
      'areaha':'Área Ha',
      'sector':'Sector',
     }
    
    return diccionario
