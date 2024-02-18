import streamlit as st
import numpy as np
import pandas as pd
import streamlit.components.v1 as components
from bs4 import BeautifulSoup

def display_snr_proceso(dataprocesos=pd.DataFrame(),titulo='',downloadname = "Descargar información",showstats=False,download=True):
    if not dataprocesos.empty:
        dataexport = dataprocesos.copy()
        
        html_stats = ""
        if showstats:
            html_stats         = ""
            formato_variables = {'Transacciones':len(dataprocesos),'Valor promedio por mt2':f"${dataprocesos['valortransaccionmt2'].median():,.0f}"}
            for key,value in formato_variables.items():
                html_stats += f"""
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
            if html_stats:
                html_stats = f"""
                <div class="container-fluid py-1" style="margin-top: 0px;margin-bottom: 50px;">
                  <div class="row">
                    {html_stats}
                  </div>
                </div>      
                """

        for i in ['predirecc','codigo','nombre','tarifa','cuantia','fecha_documento_publico','tipo_documento_publico','numero_documento_publico','entidad','link']:
            if i not in dataprocesos:
                dataprocesos[i] = ''
        for i in ['cuantia']:
            if i not in dataprocesos:
                dataprocesos[i] = 0
                
        dataprocesos.replace({None: '', np.nan: ''}, inplace=True)
        html_tabla = ""
        for _,i in dataprocesos.iterrows():
            html_tabla += f""" 
            <tr>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                <h6 class="mb-0 text-sm">{i['predirecc']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['codigo']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['nombre']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['tarifa']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">${i['cuantia']:,.0f}</h6>
              </td>         
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['fecha_documento_publico']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['preaconst']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['tipo_documento_publico']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['numero_documento_publico']}</h6>
              </td>          
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                 <a href="{i['link']}" target="_blank">
                 <img src="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/publicimg/pdf.png" alt="link" width="20" height="20">
                 </a>                    
              </td>
            """
        tabla_vigencia = f"""
        <div class="impuesto-table">
            <table class="table align-items-center mb-0">
              <thead>
                <tr style="margin-bottom: 0px;">
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Dirección</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Código</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Nombre</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Tarifa</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Cuantía</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Fecha</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Área construida</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Tipo documento</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Número de documento</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Link</th>
                  </tr>
              </thead>
              <tbody>
              {html_tabla}
              </tbody>
            </table>
        </div>
        """
        style = """
        <style>
            .tabla_principal {
              max-width: 100%; 
              max-height: 100%; 
            }              
            .impuesto-table {
              overflow-x: auto;
              overflow-y: auto; 
              max-width: 100%; 
              max-height: 400px; 
            }
            .chart-container {
              display: flex;
              justify-content: center;
              align-items: center;
              height: 100%;
              width: 100%; 
              margin-top:100px;
            }
            body {
                font-family: Arial, sans-serif;
            }
            
            canvas {
                max-width: 100%;
                max-height: 100%;
                max-height: 300px;
            }
        </style>
        """
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
          <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet">
          <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet">
          <link id="pagestyle" href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" rel="stylesheet">
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          {style}
        </head>
        <body>
          <div class="container-fluid py-4" style="margin-bottom: 0px;margin-top: -20px;">
            <div class="row">
              <div class="col-xl-12 col-sm-6 mb-xl-0 mb-2">
                <div class="card h-100">
                  <div class="card-body p-3">  
                    <div class="container-fluid py-4">
                      <div class="row" style="margin-bottom: 0px;margin-top: -40px;">
                        <div class="card-body p-3">
                          <div class="row">
                            <div class="numbers">
                              <h3 class="font-weight-bolder mb-0" style="text-align: center; font-size: 1.5rem; padding-bottom: 8px;">{titulo}</h3>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    {html_stats}
                    <div class="container-fluid py-4">
                      <div class="row" style="margin-bottom: -50px;margin-top: -50px;">
                        {tabla_vigencia}
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
        
        if download:
            variables = ['predirecc', 'codigo', 'nombre', 'tarifa', 'cuantia','preaconst', 'fecha_documento_publico', 'tipo_documento_publico', 'numero_documento_publico', 'entidad', 'link', 'preaconst', 'preaterre', 'valortransaccionmt2']
            variables = [x for x in variables if x in dataexport]
            if variables:
                dataexport = dataexport[variables]
                dataexport.rename(columns={'predirecc': 'Direccion', 'codigo': 'Codigo', 'nombre': 'Nombre', 'tarifa': 'Tarifa', 'cuantia': 'Cuantia','preaconst':'Area construida', 'fecha_documento_publico': 'Fecha del documento', 'tipo_documento_publico': 'Tipo de documento', 'numero_documento_publico': 'Numero de documento publico', 'entidad': 'Notaria', 'link': 'Link', 'preaconst': 'Area construida', 'preaterre': 'Area de terreno', 'valortransaccionmt2': 'Cuantia por mt2'},inplace=True)
            col1, col2 = st.columns([3,1])
            with col2:
                csv = convert_df(dataexport)     
                st.download_button(
                   downloadname,
                   csv,
                   "data_info_transacciones.csv",
                   "text/csv"
                )

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')
