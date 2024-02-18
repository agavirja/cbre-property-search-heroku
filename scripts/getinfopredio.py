import streamlit as st
import pandas as pd
from sqlalchemy import create_engine 

from scripts.coddir import coddir
from scripts.getdatasnr import getdatasnr
from scripts.formato_direccion import formato_direccion
from scripts.getdatavigencia import getdatavigencia
from scripts.getuso_destino import getuso_destino

from scripts.getinfopredialpolygon import getinfopredialpolygon

def splitdate(x,pos):
    try: return int(x.split('-')[pos].strip())
    except: return None
    
@st.cache_data
def getinfopredio(inputvar):
    
    user      = st.secrets["user_bigdata"]
    password  = st.secrets["password_bigdata"]
    host      = st.secrets["host_bigdata_lectura"]
    schema    = st.secrets["schema_bigdata"]
    engine    = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')

    datalotes,datacatastro,datavigencia,datasnrprocesos,datasnrtable = [pd.DataFrame()]*5
    
    if 'matricula' in inputvar and inputvar['matricula']!='' and inputvar['matricula'] is not None and not any([x for x in ['*','delete'] if x in inputvar['matricula'].lower()]):  
        datapaso = pd.DataFrame()
        query    = ''
        if isinstance(inputvar['chip'], str):
            query = f" numeroMatriculaInmobiliaria ='{inputvar['matricula']}'"
        elif isinstance(inputvar['chip'], list):
            query = "','".join(inputvar['matricula'])
            query = f" numeroMatriculaInmobiliaria IN ('{query}')"
        if query!='':
            datapaso = pd.read_sql_query(f"SELECT numeroChip as chip FROM  {schema}.data_bogota_catastro_predio WHERE {query}" , engine)
        
        if not datapaso.empty:
            query    = "','".join(datapaso['chip'].unique())
            query    = f" prechip IN ('{query}')"      
            datapaso = pd.read_sql_query(f"SELECT barmanpre FROM {schema}.data_bogota_catastro WHERE {query}" , engine)
            if not datapaso.empty:
                inputvar['barmanpre'] = list(datapaso['barmanpre'].unique())
                
    if 'chip' in inputvar and inputvar['chip']!='' and inputvar['chip'] is not None and not any([x for x in ['*','delete'] if x in inputvar['chip'].lower()]):  
        query = ''
        if isinstance(inputvar['chip'], str):
            query = f" prechip = '{inputvar['chip']}'"
        elif isinstance(inputvar['chip'], list):
            query = "','".join(inputvar['chip'])
            query = f" prechip IN ('{query}')"
        if query!='':
            datapaso = pd.read_sql_query(f"SELECT barmanpre FROM {schema}.data_bogota_catastro WHERE {query}" , engine)
            if not datapaso.empty:
                inputvar['barmanpre'] = list(datapaso['barmanpre'].unique())

    if 'direccion' in inputvar and inputvar['direccion']!='' and inputvar['direccion'] is not None and not any([x for x in ['*','delete'] if x in inputvar['direccion'].lower()]): 
        datapaso = pd.read_sql_query(f"SELECT barmanpre FROM  {schema}.data_bogota_catastro WHERE coddir ='{coddir(inputvar['direccion'])}'" , engine)
        if not datapaso.empty:
            inputvar['barmanpre'] = list(datapaso['barmanpre'].unique())

    if 'barmanpre' in inputvar and inputvar['barmanpre'] is not None and inputvar['barmanpre']!='':
        if isinstance(inputvar['barmanpre'], list):
            inputvar['barmanpre'] = inputvar['barmanpre'][0]
        datalotes,datacatastro,datavigencia,datasnrprocesos,datasnrtable = getinfopredialpolygon(inputvar)
    
    return datalotes,datacatastro,datavigencia,datasnrprocesos,datasnrtable
