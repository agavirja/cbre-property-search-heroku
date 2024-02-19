import streamlit as st
import numpy as np
import pandas as pd
import streamlit.components.v1 as components
from bs4 import BeautifulSoup


def display_predios_lote(datacatastro=pd.DataFrame(),titulo=''):
    
    if not datacatastro.empty:
        
        dataexport   = datacatastro.copy()
        datacatastro = datacatastro.sort_values(by=['preaconst','predirecc'],ascending=[False,True])
        datacatastro.replace({None: '', np.nan: ''}, inplace=True)
        
        html_tabla = ""
        for _,i in datacatastro.iterrows():
            
            valorAutoavaluo = ""
            if 'valorAutoavaluo' in i:
                try:    value = f"${i['valorAutoavaluo']:,.0f}"
                except: value = ""
                valorAutoavaluo = f"""
                  <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                    <h6 class="mb-0 text-sm">{value}</h6>
                  </td>
                """
            valorImpuesto = ""
            if 'valorImpuesto' in i:
                try:    value = f"${i['valorImpuesto']:,.0f}"
                except: value = ""
                valorImpuesto = f"""
                  <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                    <h6 class="mb-0 text-sm">{value}</h6>
                  </td>
                """             
                
            html_tabla += f""" 
            <tr>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                 <a href="http://urbextestapp.streamlit.app/Due_dilligence_digital?code={i['prechip']}&variable=chip" target="_blank">
                 <img src="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/publicimg/pdf.png" alt="link" width="20" height="20">
                 </a>                    
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                <h6 class="mb-0 text-sm">{i['predirecc']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                <h6 class="mb-0 text-sm">{i['prechip']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                <h6 class="mb-0 text-sm">{i['preaconst']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                <h6 class="mb-0 text-sm">{i['preaterre']}</h6>
              </td>
              {valorAutoavaluo}
              {valorImpuesto}
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                <h6 class="mb-0 text-sm">{i['usosuelo']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                <h6 class="mb-0 text-sm">{i['actividad']}</h6>
              </td>         
            """
            
        valorAutoavaluo = ""
        if 'valorAutoavaluo' in datacatastro:
            valorAutoavaluo = """<th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Avalúo catastral</th>"""

        valorImpuesto = ""
        if 'valorImpuesto' in datacatastro:
            valorImpuesto = """<th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Predial</th>"""
            
        tabla_vigencia = f"""
        <div class="impuesto-table">
            <table class="table align-items-center mb-0">
              <thead>
                <tr style="margin-bottom: 0px;">
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Link al predio</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Dirección</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Chip</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Área construida</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Área terreno</th>
                  {valorAutoavaluo}
                  {valorImpuesto}
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Uso del suelo</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Actividad</th>
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
        
        variables = ['prenbarrio', 'predirecc', 'prechip', 'preaterre', 'preaconst', 'preuvivien', 'preusoph', 'prevetustz', 'estrato', 'usosuelo', 'actividad', 'prediostotal','valorAutoavaluo','valorImpuesto']
        variables = [x for x in variables if x in dataexport]
        if variables:
            dataexport = dataexport[variables]
            dataexport.rename(columns={'prenbarrio': 'Barrio', 'prechip': 'Chip', 'predirecc': 'Direccion', 'preaterre': 'Area de terreno', 'preaconst': 'Area construida', 'preuvivien': 'Uso de vivienda', 'preusoph': 'PH', 'prevetustz': 'Antiguedad', 'estrato': 'Estrato', 'usosuelo': 'Uso del suelo', 'actividad': 'Actividad', 'prediostotal': 'Predios','valorAutoavaluo':'Avaluo Catastral','valorImpuesto':'Predial'},inplace=True)
        col1, col2 = st.columns([3,1])

        with col2:
            csv = convert_df(dataexport)     
            st.download_button(
               "Descargar información",
               csv,
               "data_info_predios.csv",
               "text/csv"
            )

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')
