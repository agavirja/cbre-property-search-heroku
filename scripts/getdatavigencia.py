import streamlit as st
import pandas as pd
import json
from sqlalchemy import create_engine 

def getparam(x,tipo,pos):
    try: return json.loads(x)[pos][tipo]
    except: return None
    
@st.cache_data
def getdatavigencia(chip):
    user     = st.secrets["user_bigdata"]
    password = st.secrets["password_bigdata"]
    host     = st.secrets["host_bigdata_lectura"]
    schema   = st.secrets["schema_bigdata"]
    datavigencia = pd.DataFrame()
    
    if isinstance(chip, list):
        query = "','".join(chip)
        query = f" chip IN ('{query}')"
    elif isinstance(chip, str):
        query =  f" chip='{chip}'"
    
    if query:
        engine        = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')
        datavigencia  = pd.read_sql_query(f"SELECT chip,vigencia,nroIdentificacion,valorAutoavaluo,valorImpuesto,indPago,idSoporteTributario  FROM  {schema}.data_bogota_catastro_vigencia WHERE {query}" , engine)
        datashd2024   = pd.read_sql_query(f"SELECT chip,year as vigencia,identificacion as nroIdentificacion,avaluo_catastral as valorAutoavaluo,impuesto_ajustado as valorImpuesto,copropiedad  FROM  {schema}.data_bogota_shd_2024 WHERE {query}" , engine)
        if not datashd2024.empty:
            datashd2024  = datashd2024.drop_duplicates()
            datavigencia = pd.concat([datashd2024,datavigencia])
        if not datavigencia.empty:
            query   = "','".join(datavigencia[datavigencia['nroIdentificacion'].notnull()]['nroIdentificacion'].astype(str).unique())
            query   = f" nroIdentificacion IN ('{query}')"
            datapropietarios = pd.read_sql_query(f"SELECT nroIdentificacion,tipoPropietario,tipoDocumento,primerNombre,segundoNombre,primerApellido,segundoApellido,email,telefonos FROM  {schema}.data_bogota_catastro_propietario WHERE {query}" , engine)
            if not datapropietarios.empty:
                for i in [1,2,3,4,5]:
                    datapropietarios[f'telefono{i}'] = datapropietarios['telefonos'].apply(lambda x: getparam(x,'numero',i-1))
                for i in [1,2,3]:
                    datapropietarios[f'email{i}'] = datapropietarios['email'].apply(lambda x: getparam(x,'direccion',i-1))
                datapropietarios.drop(columns=['telefonos','email'],inplace=True)
                datapropietarios = datapropietarios.drop_duplicates(subset='nroIdentificacion',keep='first')
            datavigencia = datavigencia.merge(datapropietarios,on='nroIdentificacion',how='left',validate='m:1')
        engine.dispose()
    return datavigencia
