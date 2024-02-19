import streamlit as st
import pandas as pd
import numpy as np
import shapely.wkt as wkt
import plotly.express as px
import streamlit.components.v1 as components
import webbrowser
from bs4 import BeautifulSoup

from scripts.getinfopredio import getinfopredio
from scripts.getlatlng import getlatlng
from scripts.getdatamarket import getdatamarketbycoddir
from scripts.inmuebleANDusosuelo import usosuelo2inmueble
from scripts.coddir import coddir 

from modulos.map_streetview import map_streetview
from modulos.display_descripcion_predio import display_descripcion_predio
from modulos.display_shd import display_shd
from modulos.display_snr_proceso import display_snr_proceso
from modulos.display_datamarket import display_datamarket

def main(inputvar):
         
    with st.spinner('Buscando información'):
        chip,datacatastro,databarmapre,datalote,datavigencia,datasnrprocesos,datasnrtable = getinfopredio(inputvar)

    if datacatastro.empty and databarmapre.empty:
        desc_predio = ""
        if 'chip' in inputvar and inputvar['chip']:
            desc_predio = f" para el chip {inputvar['chip']}"
        elif 'direccion' in inputvar and inputvar['direccion']: 
            desc_predio = f" para la dirección {inputvar['direccion']}"
        elif 'matricula' in inputvar and inputvar['matricula']:  
            desc_predio = f" para la matrícula {inputvar['matricula']}"
        elif 'nombrepropiedad' in inputvar and inputvar['nombrepropiedad']:  
            desc_predio = f" para el nombre de la propiedad {inputvar['nombrepropiedad']}"
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
            <div class="col-xl-12 col-sm-6 mb-xl-0 mb-2">
              <div class="card">
                <div class="card-body p-3">
                  <div class="row">
                    <div class="numbers">
                      <h3 class="font-weight-bolder mb-0" style="text-align: center;font-size: 1.5rem;">No se encontró información del predio {desc_predio}</h3>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        </body>
        </html>        
        """
        texto = BeautifulSoup(html, 'html.parser')
        st.markdown(texto, unsafe_allow_html=True)
        
    latitud, longitud, direccion = None, None, None
    if not datacatastro.empty:
        if 'latitud' in datacatastro and datacatastro['latitud'].iloc[0]: latitud = datacatastro['latitud'].iloc[0]
        if 'longitud' in datacatastro and datacatastro['longitud'].iloc[0]: longitud = datacatastro['longitud'].iloc[0]
        if 'formato_direccion' in datacatastro and datacatastro['formato_direccion'].iloc[0]: direccion = datacatastro['formato_direccion'].iloc[0]
    if not direccion and 'direccion' in inputvar and inputvar['direccion']:
        direccion = inputvar['direccion']
        
    if not latitud and not longitud: 
        ciudad    = 'bogota'
        direccion = f"{direccion},{ciudad},colombia"
        latitud,longitud = getlatlng(direccion)
        
    #-------------------------------------------------------------------------#
    # Mapa y streetview
    #-------------------------------------------------------------------------#
    polygon = None
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
        
    if latitud and longitud and not polygon:
        map_streetview(polygon=None,latitud=latitud,longitud=longitud)
    
    #-------------------------------------------------------------------------#
    # Data del predio
    datapredio    = pd.DataFrame()
    datashdpredio = pd.DataFrame()
    datasnrpredio = pd.DataFrame()
    if chip:
        datapredio    = datacatastro[datacatastro['prechip']==chip]
        datashdpredio = datavigencia[datavigencia['chip']==chip]
        if 'prechip' in datasnrtable:
            idd = datasnrtable['prechip']==chip
            if sum(idd)>0:
                idd           = datasnrprocesos['docid'].isin(datasnrtable[idd]['docid'])
                datasnrpredio = datasnrprocesos[idd]
            
    #-------------------------------------------------------------------------#
    # Descripcion del predio
    #-------------------------------------------------------------------------#
    display_descripcion_predio(datapredio,datacatastro)

    #-------------------------------------------------------------------------#
    # Descripcion SHD del predio
    #-------------------------------------------------------------------------#
    display_shd(datashdpredio,titulo='Histórico catastral del predio')

    #-------------------------------------------------------------------------#
    # Descripcion SNR del predio
    #-------------------------------------------------------------------------#
    display_snr_proceso(datasnrpredio,titulo='Transacciones del predio')
    
    #-------------------------------------------------------------------------#
    # Data oferta
    #-------------------------------------------------------------------------#
    datamarketventa    = pd.DataFrame()
    datamarketarriendo = pd.DataFrame()
    tipoinmueble       = None
    fcoddir            = (datapredio['coddir'].iloc[0] if not datapredio.empty and 'coddir' in datapredio
                           else datacatastro['coddir'].iloc[0] if not datacatastro.empty and 'coddir' in datacatastro
                           else coddir(direccion) if direccion is not None and direccion != '' else None)
    
    if not datacatastro.empty:
        usosuelo     = list(datacatastro['precuso'].unique())
        tipoinmueble = usosuelo2inmueble(usosuelo)
        tipoinmueble = [x for x in tipoinmueble if any([w for w in ['bodega', 'edificio', 'apartamento', 'consultorio', 'oficina', 'local', 'lote', 'casa', 'hotel'] if x.lower() in w])]
        
    if fcoddir is not None and tipoinmueble!=[]:
        for i in tipoinmueble:
            datapaso = getdatamarketbycoddir(coddir=fcoddir, tipoinmueble=i, tiponegocio='Venta')
            datamarketventa = pd.concat([datamarketventa,datapaso])
        for i in tipoinmueble:
            datapaso = getdatamarketbycoddir(coddir=fcoddir, tipoinmueble=i, tiponegocio='Arriendo')
            datamarketarriendo = pd.concat([datamarketarriendo,datapaso])
            
    if not datamarketventa.empty:
        display_datamarket(datamarketventa,tiponegocio='venta')
        
    if not datamarketarriendo.empty:
        display_datamarket(datamarketarriendo,tiponegocio='arriendo')
         

    
    #st.write('Data de oferta [venta-arriendo]')
    #st.write('Resumen de cuentas: valor mt2 oferta, transacciones edificio, avaluo, predial, etc')
    #st.write('Si es apartamento, oficina, local, etc, poner propiedades nuevas de GI')

    #-------------------------------------------------------------------------#
    # Botones para redireccionar
    style = """
    <style>
    .custom-button {
        display: inline-block;
        padding: 10px 20px;
        background-color: #68c8ed;
        color: #ffffff; 
        font-weight: bold;
        text-decoration: none;
        border-radius: 20px;
        width: 100%;
        border: none;
        cursor: pointer;
        text-align: center;
        letter-spacing: 1px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .custom-button:visited {
        color: #ffffff;
    }
    </style>
    """
    
    col1,col2 = st.columns(2)
    barmanpre = None
    if not datapredio.empty:
        barmanpre = datapredio['barmanpre'].iloc[0]
        with col1:
            nombre = 'Análisis del edificio'
            html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">{style}</head><body><a href="http://urbextestapp.streamlit.app/Due_dilligence_digital?code={barmanpre}&variable=barmanpre" class="custom-button">{nombre}</a></body></html>"""
            html = BeautifulSoup(html, 'html.parser')
            st.markdown(html, unsafe_allow_html=True)
        with col2:
            nombre = 'Tendencia de mercado en la zona'
            html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">{style}</head><body><a href="http://urbextestapp.streamlit.app/Due_dilligence_digital?code={barmanpre}&variable=barmanpre&tipo=radio" class="custom-button">{nombre}</a></body></html>"""
            html = BeautifulSoup(html, 'html.parser')
            st.markdown(html, unsafe_allow_html=True)
    with col1:
        nombre = 'Análisis del P.O.T'
        html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">{style}</head><body><a href="http://urbextestapp.streamlit.app/Due_dilligence_digital?code={barmanpre}&variable=barmanpre&tipo=pot" class="custom-button">{nombre}</a></body></html>"""
        html = BeautifulSoup(html, 'html.parser')
        st.markdown(html, unsafe_allow_html=True)

    #with col2:
    #    if st.button('Valorización y precio de referencia del predio'):
    #        webbrowser.open_new_tab('www.google.com')

    
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
    
    elements[3].style.backgroundColor = '#68c8ed';
    elements[3].style.fontWeight = 'bold';
    elements[3].style.color = 'white';
    elements[3].style.width = '100%';
    
    elements[4].style.backgroundColor = '#68c8ed';
    elements[4].style.fontWeight = 'bold';
    elements[4].style.color = 'white';
    elements[4].style.width = '100%';
    </script>
    """
    )
