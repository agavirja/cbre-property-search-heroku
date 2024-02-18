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
            if 'actividad' in items and items['actividad'] is not None:
                if isinstance(items['actividad'], list):
                    pop_actividad = "<b>Actividad del predio:</b><br>"
                    for j in items['actividad']:
                        pop_actividad += f"""
                        &bull; {j}<br>
                        """
                        
            if 'usosuelo' in items and items['usosuelo'] is not None:
                if isinstance(items['usosuelo'], list):
                    pop_usosuelo = "<b>Uso del suelo:</b><br>"
                    for j in items['usosuelo']:
                        pop_usosuelo += f"""
                        &bull; {j}<br>
                        """          

            antiguedad            = f"<b> Antiguedad:</b> {items['antiguedad_min']}<br>" if 'antiguedad_min' in items and (isinstance(items['antiguedad_min'], float) or isinstance(items['antiguedad_min'], int)) else ''
            estrato               = f"<b> Estrato:</b> {int(items['estrato'])}<br>" if 'estrato' in items and (isinstance(items['estrato'], float) or isinstance(items['estrato'], int)) else ''
            numero_predios        = f"<b> Número de predios:</b> {int(items['predios'])}<br>" if 'predios' in items and (isinstance(items['predios'], float) or isinstance(items['predios'], int)) else ''
            transacciones         = f"<b> Transacciones:</b> {int(items['transacciones'])}<br>" if 'transacciones' in items and (isinstance(items['transacciones'], float) or isinstance(items['transacciones'], int)) else ''
            valormt2transacciones = f"<b> Valor mt2 transacciones:</b> ${items['valortransaccionesmt2']:,.0f}<br>" if 'valortransaccionesmt2' in items and (isinstance(items['valortransaccionesmt2'], float) or isinstance(items['valortransaccionesmt2'], int)) else ''
            areaconstruida        = f"<b> Área total construida:</b> {round(items['areaconstruida'],2)}<br>" if 'areaconstruida' in items and (isinstance(items['areaconstruida'], float) or isinstance(items['areaconstruida'], int))  else ''
            areaterreno           = f"<b> Área total terreno:</b> {round(items['areaterreno'],2)}<br>" if 'areaterreno' in items and (isinstance(items['areaterreno'], float) or isinstance(items['areaterreno'], int))else ''
            direccion             = f"<b> Direccion:</b> {items['direccion']}<br>" if 'direccion' in items else ''
            barrio                = f"<b> Barrio:</b> {items['barrio']}<br>" if 'barrio' in items else ''
                        
            direccion_formato = f"<b> Direccion:</b> {items['formato_direccion']}<br>" if 'formato_direccion' in items and direccion=='' else ''
            preaconst         = f"<b> Área total construida:</b> {round(items['preaconst'],2)}<br>" if 'preaconst' in items and (isinstance(items['preaconst'], float) or isinstance(items['preaconst'], int)) and areaconstruida=='' else ''
            preaterre         = f"<b> Área total terreno:</b> {round(items['preaterre'],2)}<br>" if 'preaterre' in items and (isinstance(items['preaterre'], float) or isinstance(items['preaterre'], int)) and areaterreno=='' else ''
            prevetustez       = f"<b> Antiguedad:</b> {int(items['prevetustzmin'])}<br>" if 'prevetustzmin' in items and (isinstance(items['prevetustzmin'], float) or isinstance(items['prevetustzmin'], int)) and antiguedad=='' else ''
            connpisos         = f"<b> Pisos construidos:</b> {int(items['connpisos'])}<br>" if 'connpisos' in items and (isinstance(items['connpisos'], float) or isinstance(items['connpisos'], int)) else ''
            prenbarrio        = f"<b> Barrio:</b> {items['prenbarrio']}<br>" if 'prenbarrio' in items and barrio=='' else ''
            
            infoprecuso = ""
            if 'infoByprecuso' in items: 
                for witer in items['infoByprecuso']:
                    infoprecuso += f"""
                    <b><br>
                    <b> Uso del suelo:</b> {witer['usosuelo']}<br>
                    <b> Predios:</b> {witer['predios_precuso']}<br>                    
                    """
                    try:
                        infoprecuso += f"""
                        <b> % del Área:</b>{witer['preaconst_precuso']/items['preaconst']:,.2%}<br>
                        """
                    except: pass

            popup_content =  f'''
            <!DOCTYPE html>
            <html>
                <body>
                    <div id="popupContent" style="cursor:pointer; display: flex; flex-direction: column; flex: 1;width:200px;">
                        <a href="https://cbre-property-981cc52a6655.herokuapp.com/Due_dilligence_digital?code={items['barmanpre']}&variable=barmanpre" target="_blank" style="color: black;">
                            {direccion}
                            {direccion_formato}
                            {areaconstruida}
                            {preaconst}
                            {areaterreno}
                            {preaterre}
                            {numero_predios}
                            {transacciones}
                            {valormt2transacciones}
                            {connpisos}
                            {pop_actividad}
                            {pop_usosuelo}
                            {barrio}
                            {prenbarrio}
                            {estrato}
                            {antiguedad}
                            {prevetustez}
                            {infoprecuso}
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
