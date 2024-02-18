import streamlit as st
import pandas as pd
from sqlalchemy import create_engine 
from datetime import datetime

from scripts.groupcatastro import groupcatastro
from scripts.merge_usosuelo_actividad import merge_usosuelo_actividad

@st.cache_data
def getInfoCatastralByPolygon(polygon=None,barmanpre=None,precuso=[],areamin=0,areamax=0,antiguedadmin=0,antiguedadmax=0):
    
    user      = st.secrets["user_bigdata"]
    password  = st.secrets["password_bigdata"]
    host      = st.secrets["host_bigdata_lectura"]
    schema    = st.secrets["schema_bigdata"]
    engine    = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')

    datalotes   = pd.DataFrame()
    datachip    = pd.DataFrame()
    dataprecuso = pd.DataFrame()
    
    #-------------------------------------------------------------------------#
    # Cuando hay poligono
    #-------------------------------------------------------------------------#
    if isinstance(polygon, str):
        # Filtro por uso del suelo
        query = ""
        if precuso!=[] and precuso!='':
            if isinstance(precuso, str):
                query += f" AND precuso = '{precuso}'"
            elif isinstance(precuso, list):
                precusolist  = "','".join(precuso)
                query += f" AND precuso IN ('{precusolist}')"
        
        if query!="":
            query = query.strip().strip('AND')+' AND '
        dataprecuso = pd.read_sql_query(f"SELECT barmanpre,precuso,predios_precuso,preaconst_precuso,preaterre_precuso FROM  {schema}.bogota_catastro_compacta_precuso WHERE {query} (ST_CONTAINS(ST_GEOMFROMTEXT('{polygon}'), geometry) OR ST_Intersects(geometry,ST_GEOMFROMTEXT('{polygon}')) OR ST_Touches(geometry,ST_GEOMFROMTEXT('{polygon}'))) " , engine)
       
    #-------------------------------------------------------------------------#
    # Cuando NO hay poligono y hay barmanopre [estudio de un solo inmueble]
    #-------------------------------------------------------------------------#
    elif not isinstance(polygon, str) and barmanpre is not None:
        query = ""
        if isinstance(barmanpre, str):
            query += f" barmanpre = '{barmanpre}'"
        elif isinstance(barmanpre, list):
            lista  = "','".join(barmanpre)
            query += f" barmanpre IN ('{lista}')"
        if query!="":
            dataprecuso = pd.read_sql_query(f"SELECT barmanpre,precuso,predios_precuso,preaconst_precuso,preaterre_precuso FROM  {schema}.bogota_catastro_compacta_precuso WHERE {query}" , engine)
       
    #-------------------------------------------------------------------------#
    # Nivel Bogota
    #-------------------------------------------------------------------------#
    if polygon is None and barmanpre is None:
        query = ""
        if areamin>0:
            query += f" AND preaconst>={areamin}"
        if areamax>0:
            query += f" AND preaconst<={areamax}"
            
        # Filtro por antiguedad
        if antiguedadmin>0:
            antmin = datetime.now().year-antiguedadmin
            query += f" AND prevetustz<={antmin}"
        if antiguedadmax>0:
            antmax = datetime.now().year-antiguedadmax
            query += f" AND prevetustz>={areamax}"

        # Filtro por pre uso            
        if precuso!=[] and precuso!='':
            if isinstance(precuso, str):
                query += f" AND precuso = '{precuso}'"
            elif isinstance(precuso, list):
                precusolist  = "','".join(precuso)
                query += f" AND precuso IN ('{precusolist}')"
                
        databarmanpre = pd.DataFrame()
        if query!="":
            query         = query.strip().strip('AND')+' AND '
            databarmanpre = pd.read_sql_query(f"SELECT distinct( barmanpre) as barmanpre FROM  bigdata.data_bogota_catastro WHERE {query} ( precdestin<>'65' OR precdestin<>'66') LIMIT 1000" , engine)
            
        if not databarmanpre.empty:
            query = "','".join(databarmanpre[databarmanpre['barmanpre'].notnull()]['barmanpre'].unique())
            query = f"barmanpre IN ('{query}')"
            dataprecuso = pd.read_sql_query(f"SELECT barmanpre,precuso,predios_precuso,preaconst_precuso,preaterre_precuso FROM  {schema}.bogota_catastro_compacta_precuso WHERE {query}" , engine)
       

    if not dataprecuso.empty:
        dataprecuso = merge_usosuelo_actividad(dataprecuso)
        dataprecuso = dataprecuso.groupby('barmanpre').apply(lambda x: x.to_dict(orient='records')).reset_index()
        dataprecuso.columns = ['barmanpre','infoByprecuso']
    
        query = "','".join(dataprecuso['barmanpre'].unique())
        query = f" barmanpre IN ('{query}')" 
        
        #datalotes = pd.read_sql_query(f"SELECT barmanpre,precbarrio,prenbarrio,formato_direccion,coddir,preaconst,preaterre,prevetustzmin,prevetustzmax,estrato,predios,connpisos,connsotano,contsemis,conelevaci,ST_AsText(geometry) as wkt FROM  bigdata.bogota_catastro_compacta WHERE {query} " , engine)
        datalotes = pd.read_sql_query(f"SELECT barmanpre,precbarrio,prenbarrio,formato_direccion,coddir,preaconst,preaterre,prevetustzmin,prevetustzmax,estrato,predios,connpisos,connsotano,contsemis,conelevaci FROM  bigdata.bogota_catastro_compacta WHERE {query} " , engine)
        datalotes = datalotes.merge(dataprecuso,on='barmanpre',how='left',validate='m:1')

    if not datalotes.empty:
        # Merge polygon
        query        = "','".join(datalotes['barmanpre'].unique())
        query        = f" lotcodigo IN ('{query}')" 
        datageometry = pd.read_sql_query(f"SELECT lotcodigo as barmanpre, ST_AsText(geometry) as wkt FROM  bigdata.data_bogota_lotes WHERE {query}" , engine)
        datageometry = datageometry.drop_duplicates(subset='barmanpre',keep='first')
        datalotes    = datalotes.merge(datageometry,on='barmanpre',how='left',validate='m:1')

    if not datalotes.empty:
        # Filtro por area construida
        query = "','".join(datalotes['barmanpre'].unique())
        query = f" barmanpre IN ('{query}')" 
        if areamin>0:
            query += f" AND preaconst>={areamin}"
        if areamax>0:
            query += f" AND preaconst<={areamax}"

        # Filtro por antiguedad
        if antiguedadmin>0:
            antmin = datetime.now().year-antiguedadmin
            query += f" AND prevetustz<={antmin}"
        if antiguedadmax>0:
            antmax = datetime.now().year-antiguedadmax
            query += f" AND prevetustz>={antmax}"
            
        datafilter = pd.read_sql_query(f"SELECT  distinct(barmanpre)  FROM  bigdata.data_bogota_catastro WHERE {query} AND ( precdestin<>'65' OR precdestin<>'66') " , engine)
        idd        = datalotes['barmanpre'].isin(datafilter['barmanpre'])
        if sum(idd)>0:
            datalotes = datalotes[idd]
            
        # Chips
        if precuso!=[] and precuso!='':
            if isinstance(precuso, str):
                query += f" AND precuso = '{precuso}'"
            elif isinstance(precuso, list):
                precusolist  = "','".join(precuso)
                query += f" AND precuso IN ('{precusolist}')"
        datachip = pd.read_sql_query(f"SELECT distinct(prechip), barmanpre,preaconst,preaterre,predirecc,precuso,precdestin FROM  bigdata.data_bogota_catastro WHERE {query} AND ( precdestin<>'65' OR precdestin<>'66')" , engine)
    engine.dispose()
    return datalotes,datachip
