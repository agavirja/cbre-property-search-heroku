import streamlit as st
import pandas as pd
import json
import re
import unidecode
from sqlalchemy import create_engine 

@st.cache_data
def getdatasnr(inputs,tipovariable=''):
    
    user     = st.secrets["user_bigdata"]
    password = st.secrets["password_bigdata"]
    host     = st.secrets["host_bigdata_lectura"]
    schema   = st.secrets["schema_bigdata"]
    engine   = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')
    query    = None
    
    datamatricula = pd.DataFrame()
    datasnr       = pd.DataFrame()
    datatable     = pd.DataFrame()
    dataprocesos  = pd.DataFrame()
    
    if 'chip' in tipovariable.lower():
        if isinstance(inputs, list):
            query = "','".join(inputs)
            query = f" numeroChip IN ('{query}')"
        elif isinstance(inputs, str):
            query =  f" numeroChip='{inputs}'"
        
        if query:
            datamatricula = pd.read_sql_query(f"SELECT numeroChip as prechip,numeroMatriculaInmobiliaria as matricula FROM  bigdata.data_bogota_catastro_predio WHERE {query}" , engine)
            datamatricula = datamatricula.drop_duplicates()
        
        if not datamatricula.empty:
            query     = "','".join(datamatricula['matricula'].astype(str).unique())
            query     = f" value IN ('{query}')"
            datasnr   = pd.read_sql_query(f"SELECT docid,value as matricula FROM  bigdata.snr_data_matricula WHERE {query}" , engine)
        
    elif 'matricula' in tipovariable.lower():
        if isinstance(inputs, list):
            query = "','".join(inputs)
            query = f" value IN ('{query}')"
        elif isinstance(inputs, str):
            query =  f" value='{inputs}'"
            
        if query:
            datasnr = pd.read_sql_query(f"SELECT docid,value as matricula FROM  bigdata.snr_data_matricula WHERE {query}" , engine)

    if not datasnr.empty:
        query     = "','".join(datasnr['docid'].astype(str).unique())
        query     = f" docid IN ('{query}') AND oficina LIKE '%bogota%' AND entidad LIKE '%bogota%'"
        datatable = pd.read_sql_query(f"SELECT docid, fecha_documento_publico,tipo_documento_publico, numero_documento_publico,datos_solicitante,documento_json,entidad FROM  bigdata.snr_data_completa WHERE {query}" , engine)
        datatable = add2tablaSNR(datatable)
        variables = [x for x in ['docid', 'fecha_documento_publico', 'tipo_documento_publico', 'numero_documento_publico','entidad'] if x in datatable]
        datatable = datatable[variables]
        datamerge = datasnr[datasnr['docid'].isin(datatable['docid'])]
        datatable = datamerge.merge(datatable,on='docid',how='left',validate='m:1')
    
    if not datatable.empty:
        query        = "','".join(datatable['docid'].astype(str).unique())
        query        = f" docid IN ('{query}')"
        dataprocesos = pd.read_sql_query(f"SELECT docid,codigo,nombre,tarifa,cuantia FROM  bigdata.snr_tabla_procesos WHERE {query}" , engine)
        dataprocesos = dataprocesos.drop_duplicates()
        if not datamatricula.empty:
            datamerge    = datamatricula.drop_duplicates(subset='matricula',keep='first')
            datatable    = datatable.merge(datamerge,on='matricula',how='left',validate='m:1')
        
    if not dataprocesos.empty:
        datamerge    = datatable.sort_values(by=['docid','fecha_documento_publico'],ascending=False).drop_duplicates(subset=['docid'],keep='first')
        dataprocesos = dataprocesos.merge(datamerge[['docid','fecha_documento_publico','tipo_documento_publico','numero_documento_publico','entidad']],on='docid',how='left',validate='m:1')
        dataprocesos['link'] = dataprocesos['docid'].apply(lambda x: f'https://radicacion.supernotariado.gov.co/app/static/ServletFilesViewer?docId={x}')
        dataprocesos['fecha_documento_publico'] = dataprocesos['fecha_documento_publico'].dt.strftime('%Y-%m-%d')
        dataprocesos = dataprocesos.sort_values(by='fecha_documento_publico',ascending=False)
    engine.dispose()
    
    # datatable:    Todas las matriculas asociadas a un mismo docid
    # dataprocesos: Todas los procesos asociados a un docid
    return dataprocesos,datatable

def add2tablaSNR(datatable):
    datatable = datatable.drop_duplicates()
    datatable['fecha_documento_publico'] = pd.to_datetime(datatable['fecha_documento_publico'],errors='coerce')
    idd       = datatable['fecha_documento_publico'].isnull()
    
    # Los que tienen fecha nula
    if sum(idd)>0:
        datatable['merge']   = range(len(datatable))
        datapaso                 = datatable[idd]
        datapaso['fechanotnull'] = datapaso['documento_json'].apply(lambda x: getEXACTfecha(x))
        formato_fecha = '%d-%m-%Y'
        datapaso['fechanotnull'] = pd.to_datetime(datapaso['fechanotnull'],format=formato_fecha,errors='coerce')
        datatable  = datatable.merge(datapaso[['merge','fechanotnull']],how='left',validate='m:1')
        idd = (datatable['fecha_documento_publico'].isnull()) & (datatable['fechanotnull'].notnull())
        if sum(idd)>0:
            datatable.loc[idd,'fecha_documento_publico'] = datatable.loc[idd,'fechanotnull']
        datatable.drop(columns=['fechanotnull','merge'],inplace=True)
    return datatable

def getEXACTfecha(x):
    result = None
    try:
        x = json.loads(x)
        continuar = 0
        for i in ['fecha','fecha:','fecha expedicion','fecha expedicion:','fecha recaudo','fecha recaudo:']:
            for j in x:
                if i==re.sub('\s+',' ',unidecode(j['value'].lower())):
                    posicion = x.index(j)
                    result   = x[posicion+1]['value']
                    continuar = 1
                    break
            if continuar==1:
                break
    except: result = None
    if result is None:
        result = getINfecha(x)
    return result
    
def getINfecha(x):
    result = None
    try:
        x = json.loads(x)
        continuar = 0
        for i in ['fecha','fecha:','fecha expedicion','fecha expedicion:','fecha recaudo','fecha recaudo:']:
            for j in x:
                if i in re.sub('\s+',' ',unidecode(j['value'].lower())):
                    posicion = x.index(j)
                    result   = x[posicion+1]['value']
                    continuar = 1
                    break
            if continuar==1:
                break
    except: result = None
    return result
