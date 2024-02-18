import streamlit as st
import pandas as pd
from sqlalchemy import create_engine 

from scripts.formato_direccion import formato_direccion
from scripts.getuso_destino import getuso_destino
from scripts.groupcatastro import groupcatastro

@st.cache_data
def getcatastropolygon(polygon=None,precuso=[],areamin=0,areamax=0):
    
    user        = st.secrets["user_bigdata"]
    password    = st.secrets["password_bigdata"]
    host        = st.secrets["host_bigdata_lectura"]
    schema      = st.secrets["schema_bigdata"]
    engine      = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')

    datalotes    = pd.DataFrame()
    datacatastro = pd.DataFrame()
 
    if isinstance(polygon, str):
        datapoints = pd.read_sql_query(f"SELECT lotcodigo FROM  {schema}.data_bogota_lotes_point WHERE ST_CONTAINS(ST_GEOMFROMTEXT('{polygon}'), POINT(longitud, latitud))" , engine)
        if not datapoints.empty:
            query      = "','".join(datapoints['lotcodigo'].unique())
            query      = f" lotcodigo IN ('{query}')"        
            datalotes = pd.read_sql_query(f"SELECT lotcodigo as barmanpre, ST_AsText(geometry) as wkt FROM  bigdata.data_bogota_lotes WHERE {query}" , engine)
        
            # Remover vias
            query               = "','".join(datapoints['lotcodigo'].unique())
            query               = f" barmanpre IN ('{query}')"          
            datacatastro_novias = pd.read_sql_query(f"SELECT  barmanpre  FROM  bigdata.data_bogota_catastro WHERE precdestin IN ('65','66') AND {query}" , engine)
            idd          = datalotes['barmanpre'].isin(datacatastro_novias['barmanpre'])
            if sum(idd)>0:
                datalotes = datalotes[~idd]

    if not datalotes.empty:
        query = ""
        
        # Filtro por barmanpre
        barmanprelist = "','".join(datalotes['barmanpre'].unique())
        query        += f" barmanpre IN ('{barmanprelist}')" 
        
        # Filtro por area
        if areamin>0:
            query += f" AND preaconst>={areamin}"
        if areamax>0:
            query += f" AND preaconst<={areamax}"
             
        # Filtro por uso del suelo
        if precuso!=[] and precuso!='':
            if isinstance(precuso, str):
                query += f" AND precuso = '{precuso}'"
            elif isinstance(precuso, list):
                precusolist  = "','".join(precuso)
                query += f" AND precuso IN ('{precusolist}')"
                
        datacatastro = pd.read_sql_query(f"SELECT id,precbarrio,prenbarrio,prechip,predirecc,preaterre,preaconst,precdestin,precuso,preuvivien,preusoph,prevetustz,barmanpre,latitud,longitud,coddir,piso,estrato  FROM  bigdata.data_bogota_catastro WHERE {query} AND (precdestin<>'65')" , engine)
    
    if datalotes.empty and datacatastro.empty and (polygon is None or polygon == ''):
        # Filtro por area
        query = ""
        if areamin>0:
            query += f" AND preaconst>={areamin}"
        if areamax>0:
            query += f" AND preaconst<={areamax}"
             
        # Filtro por uso del suelo
        if precuso!=[] and precuso!='':
            if isinstance(precuso, str):
                query += f" AND precuso = '{precuso}'"
            elif isinstance(precuso, list):
                precusolist  = "','".join(precuso)
                query += f" AND precuso IN ('{precusolist}')"

        query = query.strip().strip('AND')
        if query!="":
            datacatastro = pd.read_sql_query(f"SELECT id,precbarrio,prenbarrio,prechip,predirecc,preaterre,preaconst,precdestin,precuso,preuvivien,preusoph,prevetustz,barmanpre,latitud,longitud,coddir,piso,estrato  FROM  bigdata.data_bogota_catastro WHERE {query} AND (precdestin<>'65') LIMIT 1000" , engine)

        if not datacatastro.empty:
            lotlist   = "','".join(datacatastro['barmanpre'].unique())
            query     = f" lotcodigo IN ('{lotlist}')"        
            datalotes = pd.read_sql_query(f"SELECT lotcodigo as barmanpre, ST_AsText(geometry) as wkt FROM  bigdata.data_bogota_lotes WHERE {query}" , engine)
    engine.dispose()
    
    if not datacatastro.empty:
        dataprecuso,dataprecdestin = getuso_destino()
        dataprecuso.rename(columns={'codigo':'precuso','tipo':'usosuelo','descripcion':'desc_usosuelo'},inplace=True)
        dataprecdestin.rename(columns={'codigo':'precdestin','tipo':'actividad','descripcion':'desc_actividad'},inplace=True)
        datacatastro = datacatastro.merge(dataprecuso,on='precuso',how='left',validate='m:1')
        datacatastro = datacatastro.merge(dataprecdestin,on='precdestin',how='left',validate='m:1')
        datacatastro['formato_direccion'] = datacatastro['predirecc'].apply(lambda x: formato_direccion(x))
        for i in ['preaconst','preaterre']:
            idd = datacatastro[i].isnull()
            if sum(idd)>0:
                datacatastro.loc[idd,i] = 0
        datalotes = datalotes[datalotes['barmanpre'].isin(datacatastro['barmanpre'])]
    
    if not datalotes.empty  and not datacatastro.empty:
        datagrupada = groupcatastro(datacatastro)
        datagrupada['merge'] = 1
        datalotes  = datalotes.merge(datagrupada,on='barmanpre',how='left',validate='m:1')
        datalotes  = datalotes[datalotes['merge']==1]
        datalotes.drop(columns=['merge'],inplace=True)

    return datacatastro,datalotes
