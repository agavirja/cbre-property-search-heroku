import streamlit as st
from bs4 import BeautifulSoup

def display_datamarket(datamarket,tiponegocio):

    if 'venta' in tiponegocio.lower():
        vardep = 'valorventa'
    elif 'arriendo' in tiponegocio.lower():
        vardep = 'valorarriendo'
    if not datamarket.empty:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet" />
          <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet" />
          <link id="pagestyle" href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" rel="stylesheet" />
        </head>
        <body>
        <div class="container-fluid py-1" style="margin-top: 0px;margin-bottom: 20px;">
          <div class="row">
            <div class="col-xl-12 col-sm-6 mb-xl-0 mb-2">
              <div class="card">
                <div class="card-body p-3">
                  <div class="row">
                    <div class="numbers">
                      <h3 class="font-weight-bolder mb-0" style="text-align: center;font-size: 1.5rem;">Oferta en {tiponegocio.lower()}</h3>
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
        
        dfmap           = datamarket.iloc[0:10,:].copy()
        market_imagenes = ''
        for i, inmueble in dfmap.iterrows():
            if isinstance(inmueble['imagen_principal'], str) and len(inmueble['imagen_principal'])>20: imagen_principal =  inmueble['imagen_principal']
            else: imagen_principal = "https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png"
            url_export   = f"http://urbextestapp.streamlit.app/Ficha_del_inmueble?code={inmueble['code']}&tiponegocio={tiponegocio.lower()}&tipoinmueble={inmueble['tipoinmueble'].lower()}" 
            if isinstance(inmueble['direccion'], str): direccion = inmueble['direccion'][0:35]
            else: direccion = '&nbsp'
                
            market_imagenes += f'''    
              <div class="propiedad">
                <a href="{url_export}" target="_blank">
                <div class="imagen">
                  <img src="{imagen_principal}">
                </div>
                </a>
                <div class="caracteristicas">
                  <h3>${inmueble[vardep]:,.0f} | <strong>{inmueble["areaconstruida"]}</strong> mt<sup>2</sup></h3>
                  <p>Dirección: {direccion}</p>
                </div>
              </div>
              ''' 

        if market_imagenes!="":  
            style = """
                <style>
                  .contenedor-propiedades {
                    overflow-x: scroll;
                    white-space: nowrap;
                    margin-bottom: 40px;
                    margin-top: 30px;
                  }
                  .propiedad {
                    display: inline-block;
                    vertical-align: top;
                    margin-right: 20px;
                    text-align: center;
                    width: 300px;
                  }
                  .imagen {
                    height: 200px;
                    margin-bottom: 10px;
                    overflow: hidden;
                  }
                  .imagen img {
                    display: block;
                    height: 100%;
                    width: 100%;
                    object-fit: cover;
                  }
                  .caracteristicas {
                    background-color: #f2f2f2;
                    padding: 4px;
                    text-align: left;
                  }
                  .caracteristicas h3 {
                    font-size: 18px;
                    margin-top: 0;
                  }
    
                </style>
            """
        
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet">
              <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet">
              <link id="pagestyle" href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" rel="stylesheet">
              {style}
            </head>
            <body>
              <div class="container-fluid py-4" style="margin-top: -50px;margin-bottom: 20px;">
                <div class="row">
                  <div class="col-xl-12 col-sm-6 mb-xl-0 mb-2">
                    <div class="card">
                      <div class="card-body p-3">            
                        <div class="container-fluid py-2">
                          <div class="row">
                            <div class="contenedor-propiedades">
                                {market_imagenes}
                            </div>                      
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
