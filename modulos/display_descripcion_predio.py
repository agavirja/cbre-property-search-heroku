import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from bs4 import BeautifulSoup

def display_descripcion_predio(dataparticular_catastro=pd.DataFrame(),datageneral_catastro=pd.DataFrame()):
    html_paso = ""
    if not dataparticular_catastro.empty:
        variable1 = [{'variable': 'Barrio:', 'value': 'prenbarrio'}, {'variable': 'Dirección:', 'value': 'formato_direccion'}, {'variable': 'Predio', 'value': 'predirecc'}, {'variable': 'Chip:', 'value': 'prechip'}, {'variable': 'Matrícula:', 'value': 'matricula'}, {'variable': 'Cédula catastral:', 'value': 'precedcata'}, {'variable': 'Actividad:', 'value': 'actividad'},{'variable': 'Uso del suelo', 'value': 'usosuelo'},{'variable': 'PH:', 'value': 'preusoph'}]
        variable2 = [{'variable': 'Antiguedad:', 'value': 'prevetustz'}, {'variable': 'Área construida del predio:', 'value': 'preaconst'}, {'variable': 'Área terreno del predio:', 'value': 'preaterre'}, {'variable': 'Estrato:', 'value': 'estrato'}, {'variable': '# de predios mismo uso:', 'value': 'predios_uso'},{'variable': '# de predios total:', 'value': 'prediostotal'}, {'variable': 'Área construida mismo uso del suelo:', 'value': 'areaconstruida_uso'}, {'variable': 'Área construida total:', 'value': 'areaconstruidatotal'}, {'variable': 'Área de terreno total:', 'value': 'areaterrenototal'}]
        html_paso = ""
        K         = max(len(variable1),len(variable2))
        for i in range(K):
            try:
                key,value = variable1[i]['variable'],variable1[i]['value']
                valor = dataparticular_catastro[value].iloc[0] if value in dataparticular_catastro and dataparticular_catastro[value].iloc[0] is not None else 'Sin Información'
                if any([value in x for x in ['areaconstruida','areaterreno','preaconst','preaterre','areaconstruida_uso','areaterreno_uso','areaconstruidatotal','areaterrenototal']]):
                    try: valor = round(valor,2)
                    except: pass
                if any([value in x for x in ['estrato','predios','prevetustz','antiguedad_min','antiguedad_max','predios_uso','prediostotal','antiguedad_min_uso','antiguedad_max_uso','antiguedad_mintotal','antiguedad_maxtotal']]):
                    try: valor = int(valor)
                    except: pass
                html_paso1 = f"""
                  <td  style="border: none;margin-bottom: -30px;margin-top: -60px;">
                    <h6 class="mb-0 text-sm">{key}</h6>
                  </td>
                  <td  style="border: none;margin-bottom: -30px;margin-top: -60px;">
                    <h6 class="mb-0 text-sm">{valor}</h6>
                  </td>
                """
            except: 
                html_paso1 = """
                  <td  style="border: none;margin-bottom: -30px;margin-top: -60px;">
                    <h6 class="mb-0 text-sm"></h6>
                  </td>
                  <td  style="border: none;margin-bottom: -30px;margin-top: -60px;">
                    <h6 class="mb-0 text-sm"></h6>
                  </td>
                """            
            try:
                key,value = variable2[i]['variable'],variable2[i]['value']
                valor = dataparticular_catastro[value].iloc[0] if value in dataparticular_catastro and dataparticular_catastro[value].iloc[0] is not None else 'Sin Información'
                if any([value in x for x in ['areaconstruida','areaterreno','preaconst','preaterre','areaconstruida_uso','areaterreno_uso','areaconstruidatotal','areaterrenototal']]):
                    try: valor = round(valor,2)
                    except: pass
                if any([value in x for x in ['estrato','predios','prevetustz','antiguedad_min','antiguedad_max','predios_uso','prediostotal','antiguedad_min_uso','antiguedad_max_uso','antiguedad_mintotal','antiguedad_maxtotal']]):
                    try: valor = int(valor)
                    except: pass
                html_paso2 = f"""
                  <td style="border: none;">
                    <h6 class="mb-0 text-sm">{key}</h6>
                  </td>
                  <td class="align-middle text-center text-sm" style="border: none;">
                    <h6 class="mb-0 text-sm">{valor}</h6>
                  </td>
                """
            except: 
                html_paso2 = """
                  <td style="border: none;">
                    <h6 class="mb-0 text-sm"></h6>
                  </td>
                  <td class="align-middle text-center text-sm" style="border: none;">
                    <h6 class="mb-0 text-sm"></h6>
                  </td>
                """
            html_paso += f""" 
            <tr>
              {html_paso1}
              {html_paso2}
            </tr>
            """
    elif not datageneral_catastro.empty:
        variable1 = [{'variable': 'Barrio:', 'value': 'prenbarrio'}, {'variable': 'Dirección:', 'value': 'formato_direccion'},{'variable': 'Antiguedad min:', 'value': 'antiguedad_mintotal'},{'variable': 'Antiguedad max:', 'value': 'antiguedad_maxtotal'}]
        variable2 = [{'variable': 'Estrato:', 'value': 'estrato'},{'variable': '# de predios:', 'value': 'prediostotal'}, {'variable': 'Área construida total:', 'value': 'areaconstruidatotal'}, {'variable': 'Área de terreno total:', 'value': 'areaterrenototal'}]
        html_paso = ""
        K         = max(len(variable1),len(variable2))
        for i in range(K):
            try:
                key,value = variable1[i]['variable'],variable1[i]['value']
                valor = datageneral_catastro[value].iloc[0] if value in datageneral_catastro and datageneral_catastro[value].iloc[0] is not None else 'Sin Información'
                if any([value in x for x in ['areaconstruida','areaterreno','preaconst','preaterre','areaconstruida_uso','areaterreno_uso','areaconstruidatotal','areaterrenototal']  ]):
                    try: valor = round(valor,2)
                    except: pass
                if any([value in x for x in ['estrato','predios','prevetustz','antiguedad_min','antiguedad_max','predios_uso','prediostotal','antiguedad_min_uso','antiguedad_max_uso','antiguedad_mintotal','antiguedad_maxtotal']]):
                    try: valor = int(valor)
                    except: pass
                html_paso1 = f"""
                  <td  style="border: none;margin-bottom: -30px;margin-top: -60px;">
                    <h6 class="mb-0 text-sm">{key}</h6>
                  </td>
                  <td  style="border: none;margin-bottom: -30px;margin-top: -60px;">
                    <h6 class="mb-0 text-sm">{valor}</h6>
                  </td>
                """
            except: 
                html_paso1 = """
                  <td  style="border: none;margin-bottom: -30px;margin-top: -60px;">
                    <h6 class="mb-0 text-sm"></h6>
                  </td>
                  <td  style="border: none;margin-bottom: -30px;margin-top: -60px;">
                    <h6 class="mb-0 text-sm"></h6>
                  </td>
                """            
            try:
                key,value = variable2[i]['variable'],variable2[i]['value']
                valor = datageneral_catastro[value].iloc[0] if value in datageneral_catastro and datageneral_catastro[value].iloc[0] is not None else 'Sin Información'
                if any([value in x for x in ['areaconstruida','areaterreno','preaconst','preaterre','areaconstruida_uso','areaterreno_uso','areaconstruidatotal','areaterrenototal']  ]):
                    try: valor = round(valor,2)
                    except: pass
                if any([value in x for x in ['estrato','predios','prevetustz','antiguedad_min','antiguedad_max','predios_uso','prediostotal','antiguedad_min_uso','antiguedad_max_uso','antiguedad_mintotal','antiguedad_maxtotal']]):
                    try: valor = int(valor)
                    except: pass
                html_paso2 = f"""
                  <td style="border: none;">
                    <h6 class="mb-0 text-sm">{key}</h6>
                  </td>
                  <td class="align-middle text-center text-sm" style="border: none;">
                    <h6 class="mb-0 text-sm">{valor}</h6>
                  </td>
                """
            except: 
                html_paso2 = """
                  <td style="border: none;">
                    <h6 class="mb-0 text-sm"></h6>
                  </td>
                  <td class="align-middle text-center text-sm" style="border: none;">
                    <h6 class="mb-0 text-sm"></h6>
                  </td>
                """
            html_paso += f""" 
            <tr>
              {html_paso1}
              {html_paso2}
            </tr>
            """
            
    if html_paso:
        tabla = f"""
        <div class="css-table">
            <table class="table align-items-center mb-0">
              <tbody>
              {html_paso}
              </tbody>
            </table>
        </div>
        """
        style = """
        <style>          
            .css-table {
                overflow-x: auto;
                overflow-y: auto;
                width: 100%;
                height: 100%;
            }
            .css-table table {
                border-collapse: collapse;
                border-spacing: 0;
                width: 100%;
                border-top: none;
            }
            .css-table td {
                border-bottom: 1px solid #dee2e6;
                text-align: left;
            }
            .css-table h6 {
                margin: 0; 
                line-height: 1; 
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
          <div class="container-fluid py-4" style="margin-bottom: 0px;margin-top: -50px;">
            <div class="row">
              <div class="col-xl-12 mb-xl-0 mb-2">
                <div class="card h-100">
                  <div class="card-body p-3">     
                    <div class="container-fluid py-4">
                      <div class="row" style="margin-bottom: 0px;margin-top: -20px;">
                        <div class="card-body p-3">
                          <div class="row">
                            <div class="numbers">
                              <h3 class="font-weight-bolder mb-0" style="text-align: center; font-size: 1.5rem; padding-bottom: 8px;">Información del predio</h3>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>                       
                    <div class="container-fluid py-4">
                      <div class="row" style="margin-bottom: -30px;margin-top: -50px;">
                        {tabla}
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
