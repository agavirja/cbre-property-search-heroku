import streamlit as st
import pandas as pd
import json
import re
import unidecode
from sqlalchemy import create_engine 

@st.cache_data
def getdatabarmanpre(inputvar):
    
    user     = st.secrets["user_bigdata"]
    password = st.secrets["password_bigdata"]
    host     = st.secrets["host_bigdata_lectura"]
    schema   = st.secrets["schema_bigdata"]
    engine   = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')
    
    tipoinmueble   = inputvar['tipoinmueble']
    areamin        = inputvar['areamin']
    areamax        = inputvar['areamax']
    maxpropietario = inputvar['maxpropietario']
    maxpredios     = inputvar['maxpredios']
    maxavaluo      = inputvar['maxavaluo']
    polygon        = inputvar['polygon']

    query    = ''
    if areamin>0:
        query += f' AND areaconstruida_total>={areamin}'
    if areamax>0:
        query += f' AND areaconstruida_total<={areamax}'
    if maxpropietario>0:
        query += f' AND propietarios<={maxpropietario}'
    if maxpredios>0:
        query += f' AND predios<={maxpredios}'
    if maxavaluo>0:
        query += f' AND total_avaluo<={maxavaluo}'
    if not 'todo' in tipoinmueble.lower():
        query += f' AND tipoinmueble="{tipoinmueble}"'
    if isinstance(polygon, str):
        query += f' AND ST_CONTAINS(ST_GEOMFROMTEXT("{polygon}"), POINT(longitud, latitud))'
        
    query     = query.strip().strip('AND')
    data      = pd.read_sql_query(f"SELECT * FROM  bigdata.data_groupbarmanpre WHERE {query}" , engine)
    datalotes = pd.DataFrame()
    if not data.empty:
        #query = "','".join(data['barmanpre'].unique())
        #query = f" barmanpre IN ('{query}')"
        #data = pd.read_sql_query(f"SELECT * FROM  bigdata.data_groupbarmanpre WHERE {query}" , engine)
        lotlist   = "','".join(data['barmanpre'].unique())
        query     = f" lotcodigo IN ('{lotlist}')"        
        datalotes = pd.read_sql_query(f"SELECT lotcodigo as barmanpre, ST_AsText(geometry) as wkt FROM  bigdata.data_bogota_lotes WHERE {query}" , engine)
        datamerge = data.drop_duplicates(subset='barmanpre',keep='first')
        datalotes = datalotes.merge(datamerge,on='barmanpre',how='left',validate='m:1')
    
    return data,datalotes
