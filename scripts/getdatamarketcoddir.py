import streamlit as st
import pandas as pd
from sqlalchemy import create_engine 

@st.cache_data
def getdatamarketcoddir(inputvar):
    
    tipoinmueble = inputvar['tipoinmueble']
    if 'areaconstruida' in inputvar:
        areaconstruida = inputvar['areaconstruida']
    
    polygon  = inputvar['polygon']
    consulta = f' WHERE ST_CONTAINS(ST_GEOMFROMTEXT("{polygon}"),geometry)'
        
    user     = st.secrets["user_bigdata"]
    password = st.secrets["password_bigdata"]
    host     = st.secrets["host_bigdata_lectura"]
    schema   = 'market'
    
    dataventa    = pd.DataFrame()
    dataarriendo = pd.DataFrame()
    
    for ti in tipoinmueble:
        tabla     = f'data_ofertas_venta_{ti.lower()}_bogota'
        engine    = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')
        dataventapaso = pd.read_sql_query(f"""
        SELECT id,direccion, imagen_principal,fecha_inicial, areaconstruida, valorventa, valorarriendo, habitaciones, banos, garajes, estrato, antiguedad, latitud, longitud, valormt2
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY direccion, areaconstruida, habitaciones, banos, garajes, valorventa
                       ORDER BY id) AS row_num
            FROM market.{tabla}
            {consulta}
        ) AS filtered_market
        WHERE filtered_market.row_num = 1
        LIMIT 200;
        """, engine)
        if not dataventapaso.empty:
            dataventa = pd.concat([dataventa,dataventapaso])
            
        tabla        = f'data_ofertas_arriendo_{ti.lower()}_bogota'
        dataarriendopaso = pd.read_sql_query(f"""
        SELECT  id,direccion, imagen_principal, fecha_inicial, areaconstruida, valorventa, valorarriendo, habitaciones, banos, garajes, estrato, antiguedad, latitud, longitud, valormt2
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY direccion, areaconstruida, habitaciones, banos, garajes, valorarriendo
                       ORDER BY id) AS row_num
            FROM market.{tabla}
            {consulta}
        ) AS filtered_market
        WHERE filtered_market.row_num = 1
        LIMIT 200;
        """, engine)
        if not dataarriendopaso.empty:
            dataarriendo = pd.concat([dataarriendo,dataarriendopaso])
    return dataventa,dataarriendo   
