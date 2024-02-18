import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

def display_precuso(data=pd.DataFrame(),titulo=''):
    if not data.empty:
        if 'porcentaje' in data:
            data = data.sort_values(by='porcentaje',ascending=False)

        html_tabla = ""
        for _,i in data.iterrows():
            porcentaje = "{:.1%}".format(i['porcentaje']) if 'porcentaje' in i and isinstance(i['porcentaje'], float) else ''
            html_tabla += f""" 
            <tr>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;margin-top: 0px;margin-bottom: -20px;">
                <h6 class="mb-0 text-sm">{i['usosuelo']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['predios_precuso']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['preaconst_precuso']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['preaterre_precuso']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{porcentaje}</h6>
              </td>      
            """
        tabla_vigencia = f"""
        <div class="impuesto-table">
            <table class="table align-items-center mb-0">
              <thead>
                <tr style="margin-bottom: 0px;">
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Uso del suelo</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Predios por uso del suelo</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Área construida total</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Área de terreno total</th>
                  <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Porcentaje</th>
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
