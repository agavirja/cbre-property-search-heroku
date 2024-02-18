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
from scripts.merge_usosuelo_actividad import merge_usosuelo_actividad

from modulos.map_streetview import map_streetview
from modulos.display_descripcion_predio import display_descripcion_predio
from modulos.display_shd import display_shd
from modulos.display_snr_proceso import display_snr_proceso
from modulos.display_predios_lote import display_predios_lote
from modulos.display_datamarket import display_datamarket
from modulos.display_precuso import display_precuso

def main(inputvar):

    with st.spinner('Buscando información'):
        datalotes,datacatastro,datavigencia,datasnrprocesos,datasnrtable = getinfopredio(inputvar)
        datacatastro = merge_usosuelo_actividad(datacatastro)

    if datalotes.empty:
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
        
        
    latitud   = datalotes['latitud'].iloc[0] if 'latitud' in datalotes and isinstance(datalotes['latitud'].iloc[0], float) else None
    longitud  = datalotes['longitud'].iloc[0] if 'longitud' in datalotes and isinstance(datalotes['longitud'].iloc[0], float) else None
    direccion = datalotes['formato_direccion'].iloc[0] if 'formato_direccion' in datalotes and isinstance(datalotes['formato_direccion'].iloc[0], str) else None
    if not direccion and 'direccion' in inputvar and inputvar['direccion']:
        direccion = inputvar['direccion']
      
    polygon = None
    if not datalotes.empty and 'wkt' in datalotes:
        polygon = wkt.loads(datalotes['wkt'].iloc[0]) 
        map_streetview(polygon)
        
    if latitud is None and longitud is None and polygon:
        try:
            polygonl = wkt.loads(polygon) 
            latitud  = polygonl.centroid.y
            longitud = polygonl.centroid.x
        except: 
            try:
                latitud  = polygon.centroid.y
                longitud = polygon.centroid.x
            except: pass
        
    if not latitud and not longitud: 
        ciudad           = 'bogota'
        latitud,longitud = getlatlng(f"{direccion},{ciudad},colombia")
        
    #-------------------------------------------------------------------------#
    # Mapa y streetview
    #-------------------------------------------------------------------------#
    if latitud and longitud and not polygon:
        map_streetview(polygon=None,latitud=latitud,longitud=longitud)
    

    #-------------------------------------------------------------------------#
    # Descripcion del predio
    #-------------------------------------------------------------------------#
    display_descripcion_predio(datageneral_catastro=datalotes)
    
    if not datalotes.empty and 'infoByprecuso' in datalotes:
        datapaso  = pd.DataFrame(datalotes['infoByprecuso'].iloc[0])
        datamerge = datalotes[['barmanpre','preaconst']]
        datamerge = datamerge.drop_duplicates(subset='barmanpre',keep='first')
        datapaso  = datapaso.merge(datamerge,on='barmanpre',how='left',validate='m:1')
        datapaso['porcentaje'] = datapaso['preaconst_precuso']/datapaso['preaconst']
        if len(datapaso)>1:
            display_precuso(data=datapaso,titulo='Tipos de inmuebles')

    #-------------------------------------------------------------------------#
    # Descripcion SNR del predio
    #-------------------------------------------------------------------------#
    display_snr_proceso(datasnrprocesos,titulo='Transacciones del edificio')

    #---------------------------------------------------------------------#
    # Descripcion predios en el edificio
    #-------------------------------------------------------------------------#
    datacatastro = addinfocatastro(datacatastro,datavigencia)
    display_predios_lote(datacatastro,titulo='Descripción de predios')
    
    #---------------------------------------------------------------------#   
    # Descargar informacion propietarios
    datapropietarios = mergepropietarios(datacatastro,datavigencia)

    col1,col2  = st.columns([1,3])
    if not datapropietarios.empty:
        dataexport = pd.DataFrame()
        variables  = ['predirecc','prechip', 'vigencia', 'valorAutoavaluo', 'valorImpuesto', 'copropiedad', 'tipoDocumento', 'nroIdentificacion', 'primerNombre', 'segundoNombre', 'primerApellido', 'segundoApellido', 'telefono1', 'telefono2', 'telefono3', 'telefono4', 'telefono5', 'email1', 'email2', 'email3']
        variables  = [x for x in variables if x in datapropietarios]
        if variables!=[]:
            dataexport = datapropietarios[variables]
            dataexport = dataexport.sort_values(by='vigencia',ascending=False)
            dataexport.rename(columns={'predirecc': 'Direccion', 'prechip': 'Chip', 'vigencia': 'Ano', 'valorAutoavaluo': 'Avaluo Catastral', 'valorImpuesto': 'Predial', 'copropiedad': '% propiedad', 'tipoDocumento': 'Tipo de documento', 'nroIdentificacion': 'Numero documento', 'primerNombre': 'Primer nombre', 'segundoNombre': 'Segundo nombre', 'primerApellido': 'Primer apellido', 'segundoApellido': 'Segundo apellido', 'telefono1': 'Telefono 1', 'telefono2': 'Telefono 2', 'telefono3': 'Telefono 3', 'telefono4': 'Telefono 4', 'telefono5': 'Telefono 5', 'email1': 'Email 1', 'email2': 'Email 2', 'email3': 'Email 3'},inplace=True)

        if not dataexport.empty:
            with col1:
                csv = convert_df(dataexport)     
                st.download_button(
                   "Descargar información propietarios",
                   csv,
                   "data_info_propietarios.csv",
                   "text/csv"
                )

    #-------------------------------------------------------------------------#
    # Data oferta
    #-------------------------------------------------------------------------#
    datamarketventa    = pd.DataFrame()
    datamarketarriendo = pd.DataFrame()
    tipoinmueble       = None
    fcoddir            = (datalotes['coddir'].iloc[0] if not datalotes.empty and 'coddir' in datalotes
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
    #st.write('Mostrar grafias de las tipologias de predios')
    
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
    if not datalotes.empty:
        barmanpre = datalotes['barmanpre'].iloc[0]
        with col1:
            nombre = 'Tendencia de mercado en la zona'
            html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">{style}</head><body><a href="https://cbre-property-981cc52a6655.herokuapp.com/Due_dilligence_digital?code={barmanpre}&variable=barmanpre&tipo=radio" class="custom-button">{nombre}</a></body></html>"""
            html = BeautifulSoup(html, 'html.parser')
            st.markdown(html, unsafe_allow_html=True)
        with col2:
            nombre = 'Análisis del P.O.T'
            html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">{style}</head><body><a href="https://cbre-property-981cc52a6655.herokuapp.com/Due_dilligence_digital?code={barmanpre}&variable=barmanpre&tipo=pot" class="custom-button">{nombre}</a></body></html>"""
            html = BeautifulSoup(html, 'html.parser')
            st.markdown(html, unsafe_allow_html=True)

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
def addinfocatastro(datacatastro,datavigencia):
    datamerge = pd.DataFrame()
    if not datavigencia.empty:
        datamerge = datavigencia.sort_values(by=['chip','vigencia'],ascending=False)
        datamerge = datamerge.drop_duplicates(subset='chip',keep='first')
        datamerge.rename(columns={'chip':'prechip'},inplace=True)
    if not datamerge.empty and not datacatastro.empty:
        datacatastro = datacatastro.merge(datamerge[['prechip','valorAutoavaluo','valorImpuesto']],on='prechip',how='left',validate='m:1')
    return datacatastro

@st.cache_data
def mergepropietarios(datacatastro,datavigencia):
    datapropietarios = pd.DataFrame()
    if not datavigencia.empty:
        datapropietarios = datavigencia[datavigencia['nroIdentificacion'].notnull()]
    if not datapropietarios.empty:
        datapropietarios = datapropietarios.sort_values(by=['chip','vigencia'],ascending=False)
        df               = datapropietarios.groupby('chip')['vigencia'].max().reset_index()
        df.columns       = ['chip','vigencia']
        df['indmerge']   = 1
        datapropietarios = datapropietarios.merge(df,on=['chip','vigencia'],how='left',validate='m:1')
        datapropietarios = datapropietarios[datapropietarios['indmerge']==1]
        datapropietarios.rename(columns={'chip':'prechip'},inplace=True)
        datapropietarios.drop(columns=['indmerge'],inplace=True)
        
    if not datapropietarios.empty and not datacatastro.empty:
        datamerge        = datacatastro.drop_duplicates(subset='prechip',keep='first')
        datapropietarios = datapropietarios.merge(datamerge[['prechip','predirecc','preaconst']],on='prechip',how='left',validate='m:1')
    return datapropietarios

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')