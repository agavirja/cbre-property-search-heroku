import streamlit as st
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup


from scripts.censodane import censodane

def display_dane(polygon):
    datacensodane = censodane(str(polygon))
    if not datacensodane.empty:
        html = """
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
                      <h3 class="font-weight-bolder mb-0" style="text-align: center;font-size: 1.5rem;">Analisis Demográfico</h3>
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
        
        col1, col2 = st.columns(2)
        with col1: 
            variables = [x for x in ['Total personas','Total viviendas','Hogares','Hombres','Mujeres'] if x in datacensodane]
            df = datacensodane[variables].copy()
            df = df.T.reset_index()
            df.columns = ['name','value']
            df.index = range(len(df))
            fig      = px.bar(df, x="name", y="value", text="value", title="Viviendas")
            fig.update_traces(texttemplate='%{y:,.0f}', textposition='outside', marker_color='#0095ff')
            fig.update_layout(title_x=0.2,height=400, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True,sharing="streamlit", theme="streamlit")
    
        with col2: 
            variables = [x for x in ['0 a 9 años', '10 a 19 años', '20 a 29 años', '30 a 39 años', '40 a 49 años', '50 a 59 años', '60 a 69 años', '70 a 79 años', '80 años o más'] if x in datacensodane]
            df = datacensodane[variables].copy()
            df = df.T.reset_index()
            df.columns = ['name','value']
            df.index = range(len(df))
            fig      = px.bar(df, x="name", y="value", text="value", title="Edades")
            fig.update_traces(texttemplate='%{y:,.0f}', textposition='outside', marker_color='#0095ff')
            fig.update_layout(title_x=0.2,height=400, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True,sharing="streamlit", theme="streamlit")
