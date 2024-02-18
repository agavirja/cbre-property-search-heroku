import streamlit as st
import pandas as pd
from sqlalchemy import create_engine 

@st.cache_data
def getmanzanaslote(barmanpre):
    user        = st.secrets["user_bigdata"]
    password    = st.secrets["password_bigdata"]
    host        = st.secrets["host_bigdata_lectura"]
    schema      = st.secrets["schema_bigdata"]
    engine      = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')
    data        = pd.read_sql_query(f"SELECT * FROM  {schema}.data_groupbarmanpre WHERE barmanpre LIKE '{barmanpre[0:9]}%'" , engine)
    datalote    = pd.read_sql_query(f"SELECT lotcodigo as barmanpre, ST_AsText(geometry) as wkt FROM  {schema}.data_bogota_lotes WHERE lotcodigo LIKE '{barmanpre[0:9]}%'" , engine)
    if not data.empty:
        query = "','".join(data['barmanpre'])
        query = f" barmanpre IN ('{query}')"
        datacatastro = pd.read_sql_query(f"SELECT barmanpre  FROM  {schema}.data_bogota_catastro WHERE {query} AND (precdestin<>'65') AND (precdestin<>'66') " , engine)
        if not datacatastro.empty:
            data     = data[data['barmanpre'].isin(datacatastro['barmanpre'])]
            datalote = datalote[datalote['barmanpre'].isin(datacatastro['barmanpre'])]
    engine.dispose()
    
    
    return data,datalote
