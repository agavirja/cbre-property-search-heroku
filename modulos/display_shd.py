import streamlit as st
import numpy as np
import streamlit.components.v1 as components
import hashlib
from bs4 import BeautifulSoup


def display_shd(datavigencia,titulo=''):
    if not datavigencia.empty:
        
        #---------------------------------------------------------------------#
        # url predial [posterior a 2024] [digital ocean]
        datavigencia['urlpredial'] = datavigencia['idSoporteTributario'].apply(lambda x: f"https://oficinavirtual.shd.gov.co/barcode/certificacion?idSoporte={x}")
        idd = datavigencia['vigencia']>=2024
        if sum(idd)>0:
            datavigencia.loc[idd,'urlpredial'] = datavigencia.loc[idd].apply(lambda x: geturl(x['chip'],x['vigencia']),axis=1)
        #---------------------------------------------------------------------#

        dataexport = datavigencia.copy()
        for i in ['vigencia', 'indPago', 'tipoPropietario', 'tipoDocumento', 'nroIdentificacion', 'copropiedad', 'primerNombre', 'segundoNombre', 'primerApellido', 'segundoApellido', 'telefono1', 'telefono2', 'telefono3', 'email1', 'email2']:
            if i not in datavigencia:
                datavigencia[i] = ''
        for i in ['valorAutoavaluo', 'valorImpuesto']:
            if i not in datavigencia:
                datavigencia[i] = 0
        for i in ['telefono1', 'telefono2', 'telefono3']:
            if i in datavigencia:
                datavigencia[i] = datavigencia[i].apply(lambda x:phoneformat(x) )
            
        datavigencia.replace({None: '', np.nan: ''}, inplace=True)
        html_tabla = ""
        for _,i in datavigencia.iterrows():
            html_tabla += f""" 
            <tr>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['vigencia']}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">${i['valorAutoavaluo']:,.0f}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">${i['valorImpuesto']:,.0f}</h6>
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['indPago']}</h6>
              </td>         
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                 <a href="{i['urlpredial']}" target="_blank">
                 <img src="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/publicimg/pdf.png" alt="link" width="20" height="20">
                 </a>                    
              </td>
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['tipoPropietario']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['tipoDocumento']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['nroIdentificacion']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['copropiedad']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['primerNombre']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['segundoNombre']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['primerApellido']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['segundoApellido']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['telefono1']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['telefono2']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['telefono3']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['email1']}</h6>
              </td>  
              <td class="align-middle text-center text-sm" style="border: none;padding: 8px;">
                <h6 class="mb-0 text-sm">{i['email2']}</h6>
              </td>  
            """
        tabla_vigencia = f"""
        <div class="impuesto-table">
            <table class="table align-items-center mb-0" style="background-color: #ffffff;" >
                <thead>
                    <tr style="margin-bottom: 0px;background-color: #ffffff;">
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Vigencia</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Avaluo</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Predial</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Indicador</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Link</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Tipo propietario</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Tipo documento</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Identificacion</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Copropiedad</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Primer nombre</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Segundo nombre</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Primer apellido</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Segundo apellido</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Telefono 1</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Telefono 2</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Telefono 3</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Email 1</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Email 2</th>
                      <th class="align-middle text-center" style="border-top:none; border-left:none;border-right:none;border-bottom: 1px solid #ccc;">Email 3</th>
                    </tr>
                </thead>
                <tbody>
                    {html_tabla}
                </tbody>
                </div>
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
                scroll-behavior: smooth;
                scroll-margin-top: 0px;
            }
        
            .chart-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
                width: 100%;
                margin-top: 100px;
            }
        
            body {
                font-family: Arial, sans-serif;
            }
        
            .table th, .table td {
                padding: 12px;
                text-align: center;
                min-width: 100px;
            }
        
            .table th {
                background-color: #ffffff;
                position: sticky;
                top: 0; 
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
                      <div class="row" style="margin-bottom: 0px;margin-top: -20px;">
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
                      <div class="row" style="margin-bottom: -30px;margin-top: -50px;">
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

        variables = ['chip', 'vigencia', 'nroIdentificacion', 'valorAutoavaluo', 'valorImpuesto', 'copropiedad', 'indPago', 'tipoPropietario', 'tipoDocumento', 'primerNombre', 'segundoNombre', 'primerApellido', 'segundoApellido', 'telefono1', 'telefono2', 'telefono3', 'telefono4', 'telefono5', 'email1', 'email2', 'email3']
        variables = [x for x in variables if x in dataexport]
        if variables:
            dataexport = dataexport[variables]
            dataexport.rename(columns={"chip":"Chip","vigencia":"Vigencia","nroIdentificacion":"Identificacion","valorAutoavaluo":"Avaluo catastral","valorImpuesto":"Predial","copropiedad":"Porcentaje copropiedad","indPago":"Indicador de pago","tipoPropietario":"Tipo propietario","tipoDocumento":"Tipo documento","primerNombre":"Primer nombre","segundoNombre":"Segundo nombre","primerApellido":"Primer apellido","segundoApellido":"Segundo apellido","telefono1":"Telefono 1","telefono2":"Telefono 2","telefono3":"Telefono 3","telefono4":"Telefono 4","telefono5":"Telefono 5","email1":"Email 1","email2":"Email 2","email3":"Email 3"},inplace=True)
            col1, col2 = st.columns([3,1])
            with col2:
                csv = convert_df(dataexport)     
                st.download_button(
                   "Descargar información",
                   csv,
                   "data_info_prediales.csv",
                   "text/csv"
                )
                
                #components.html(
                #    """
                #<script>
                #const elements = window.parent.document.querySelectorAll('.stDownloadButton button')
                #elements[0].style.width = '100%';
                #elements[0].style.fontWeight = 'bold';
                #elements[0].style.backgroundColor = '#17e88f';
                #</script>
                #"""
                #)
    
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def phoneformat(x):
    try:    return str(int(x))
    except: return x

def generar_codigo(x):
    hash_sha256 = hashlib.sha256(x.encode()).hexdigest()
    codigo      = hash_sha256[:12]
    return codigo

def geturl(chip,year):
    filename = generar_codigo(f'{year}{chip}{year}')
    return f'https://prediales.nyc3.digitaloceanspaces.com/{filename.upper()}.pdf'