import streamlit as st
import pandas as pd
import shapely.wkt as wkt
import folium
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from bs4 import BeautifulSoup

from modulos.stylefunctions import style_function,style_referencia,style_lote_transacciones,style_lote

def display_transacciones_polygon(dataprocesos=pd.DataFrame(),datalotespolygon=pd.DataFrame(),polygon=None,latitud=None,longitud=None,barmanpreref=None,showheader=True):
    
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

    if not dataprocesos.empty:
        if showheader:
            html_paso         = ""
            formato_variables = {'Transacciones':len(dataprocesos),'Valor promedio por mt2':f"${dataprocesos['valortransaccionmt2'].median():,.0f}"}
            for key,value in formato_variables.items():
                html_paso += f"""
                <div class="col-xl-6 col-sm-4 mb-xl-2 mb-4">
                  <div class="card">
                    <div class="card-body p-3">
                      <div class="row">
                        <div class="numbers">
                          <h3 class="font-weight-bolder mb-0" style="text-align: center;font-size: 1.5rem;">{value}</h3>
                          <p class="mb-0" style="font-weight: 300;font-size: 1rem;text-align: center;">{key}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                """
            if html_paso:
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                  <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet" />
                  <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet" />
                  <link id="pagestyle" href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" rel="stylesheet" />
                </head>
                <body>
                <div class="container-fluid py-1" style="margin-top: 0px;margin-bottom: 50px;">
                  <div class="row">
                    {html_paso}
                  </div>
                </div> 
                </body>
                </html>
                """
                texto = BeautifulSoup(html, 'html.parser')
                st.markdown(texto, unsafe_allow_html=True)
                
    if not datalotespolygon.empty:
        #---------------------------------------------------------------------#
        # Mapa de transacciones en el radio
        m = folium.Map(location=[latitud, longitud], zoom_start=16,tiles="cartodbpositron")

        if polygon:
            try: folium.GeoJson(polygon, style_function=style_function).add_to(m)
            except:
                try: folium.GeoJson(wkt.loads(polygon) , style_function=style_function).add_to(m)
                except: pass
                    
        if 'transacciones' not in datalotespolygon: datalotespolygon['transacciones'] = 0
        else: 
            datalotespolygon['transacciones'] = pd.to_numeric(datalotespolygon['transacciones'],errors='coerce')
            idd = datalotespolygon['transacciones'].isnull()
            if sum(idd)>0:
                datalotespolygon.loc[idd,'transacciones'] = 0
        
        for _,items in datalotespolygon.iterrows():
            poly      = items['wkt']
            polyshape = wkt.loads(poly)
            
            pop_actividad = ""
            pop_usosuelo  = "" 
            if items['actividad'] is not None:
                if isinstance(items['actividad'], list):
                    pop_actividad = "<b>Actividad del predio:</b><br>"
                    for j in items['actividad']:
                        pop_actividad += f"""
                        &bull; {j}<br>
                        """
                        
            if items['usosuelo'] is not None:
                if isinstance(items['usosuelo'], list):
                    pop_usosuelo = "<b>Uso del suelo:</b><br>"
                    for j in items['usosuelo']:
                        pop_usosuelo += f"""
                        &bull; {j}<br>
                        """          
            try:
                if items['antiguedad_min']<items['antiguedad_max']:
                    antiguedad = f"<b> Antiguedad:</b> {items['antiguedad_min']}-{items['antiguedad_max']}<br>"
                else:
                    antiguedad = f"<b> Antiguedad:</b> {int(items['antiguedad_min'])}<br>"
            except: antiguedad = "<b> Antiguedad:</b> Sin información <br>"
            try:    estrato = f"<b> Estrato:</b> {int(items['estrato'])}<br>"
            except: estrato = "<b> Estrato:</b> Sin información <br>"
            try:    numero_predios = f"<b> Número de predios:</b> {int(items['predios'])}<br>"
            except: numero_predios = "<b> Número de predios:</b> Sin información <br>"
            try:    transacciones =  f"<b> Transacciones:</b> {int(items['transacciones'])}<br>"
            except: transacciones = "<b> Transacciones:</b> Sin información <br>"
            try:    valormt2transacciones = f"<b> Valor mt2 transacciones:</b> ${items['valortransaccionesmt2']:,.0f}<br>"
            except: valormt2transacciones = "<b> Valor mt2Transacciones:</b> Sin información <br>"
            try:    areaconstruida = f"<b> Área total construida:</b> {round(items['areaconstruida'],2)}<br>"
            except: areaconstruida = "<b> Área total construida:</b> Sin información <br>"
            try:    areaterreno = f"<b> Área total terreno:</b> {round(items['areaterreno'],2)}<br>"
            except: areaterreno = "<b> Área total terreno:</b> Sin información <br>"            
            popup_content =  f'''
            <!DOCTYPE html>
            <html>
                <body>
                    <div id="popupContent" style="cursor:pointer; display: flex; flex-direction: column; flex: 1;width:200px;">
                        <a href="https://cbre-property-981cc52a6655.herokuapp.com/Due_dilligence_digital?code={items['barmanpre']}&variable=barmanpre" target="_blank" style="color: black;">
                            <b> Direccion:</b> {items['direccion']}<br>
                            {areaconstruida}
                            {areaterreno}
                            {numero_predios}
                            {transacciones}
                            {valormt2transacciones}
                            {pop_actividad}
                            {pop_usosuelo}
                            <b> Barrio:</b> {items['barrio']}<br>
                            {estrato}
                            {antiguedad}
                        </a>
                    </div>
                </body>
            </html>
            '''
            
            if barmanpreref is not None and barmanpreref in items['barmanpre']:
                folium.GeoJson(polyshape, style_function=style_referencia).add_child(folium.Popup(popup_content)).add_to(m)
            elif items['transacciones'] > 0:
                folium.GeoJson(polyshape, style_function=style_lote_transacciones).add_child(folium.Popup(popup_content)).add_to(m)
            else:
                folium.GeoJson(polyshape, style_function=style_lote).add_child(folium.Popup(popup_content)).add_to(m)

        st_map = st_folium(m,width=1600,height=600)

        referencia = """<div class="rectangle reference-lot">Lote de referencia</div>"""
        if barmanpreref is None:
            referencia = ""
        
        contransacciones = """<div class="rectangle lots-with-transactions">Lotes con transacciones</div>"""
        if datalotespolygon['transacciones'].sum()==0:
            contransacciones = ""
            
        style = """
        <style>
          body {
            margin: 0;
            padding: 0;
          }
        
          .container {
            width: 100%;
            display: flex;
            justify-content: left;
            margin-bottom: 0px;
            margin-left: -50px;
            margin-top: -40px;
          }
          
          .rectangle {
            width: 180px;
            height: 30px;
            margin-right: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 10px; 
            font-weight: bold;
            font-family: 'arial';
            color: rgba(255, 255, 255, 1);
          }
        
          .reference-lot {
            background-color: rgba(178, 2, 86, 0.7);
          }
        
          .lots-with-transactions {
            background-color: rgba(51, 16, 93, 0.7);
          }
        
          .lots-without-transactions {
            background-color: rgba(0, 63, 45, 0.7);
          }
        </style>
        """
        labels = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mapa de Lotes</title>
        {style}
        </head>
        <body>
        <div class="container" style="margin-left: -20px;">
          {referencia}
          {contransacciones}
          <div class="rectangle lots-without-transactions">Lotes sin transacciones</div>
        </div>
        </body>
        </html>
        """
        texto = BeautifulSoup(labels, 'html.parser')
        st.markdown(texto, unsafe_allow_html=True)
