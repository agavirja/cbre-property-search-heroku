import streamlit as st
import pandas as pd
import geopandas as gpd
import shapely.wkt as wkt
from sqlalchemy import create_engine 

from scripts.formato_direccion import formato_direccion
from scripts.getuso_destino import getuso_destino

@st.cache_data
def getconsolidacionlotes(polygon=None,areamin=0,areamax=0,predios=0,maxpiso=100,pot=None):
    
    user        = st.secrets["user_bigdata"]
    password    = st.secrets["password_bigdata"]
    host        = st.secrets["host_bigdata_lectura"]
    schema      = st.secrets["schema_bigdata"]
    engine      = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')
    
    datapredios       = pd.DataFrame()
    datalotescatastro = pd.DataFrame()
    
    if isinstance(polygon, str):
        datalotes = pd.read_sql_query(f"SELECT idcode,ST_AsText(geometry) as wkt FROM  {schema}.combinacion_lotes_1000_datapoint WHERE ST_CONTAINS(ST_GEOMFROMTEXT('{polygon}'), geometry)" , engine)
        if not datalotes.empty:
            query       = "','".join(datalotes['idcode'].unique())
            query       = f" idcode IN ('{query}')"   
            if areamin>0:
                query += f' AND areaterreno>={areamin}'
            if areamax>0:
                query += f' AND areaterreno<={areamax}'
            if predios>0:
                query += f' AND predios<={predios}'
            datapredios = pd.read_sql_query(f"SELECT idcode,barmanpre,areaterreno,predios,delgeometry as geometry FROM  bigdata.combinacion_lotes_1000 WHERE {query}" , engine)
            datapredios['geometry'] = gpd.GeoSeries.from_wkt(datapredios['geometry'])
            datapredios             = gpd.GeoDataFrame(datapredios, geometry='geometry')

            # Altura max de la construccion existente en el lote         
            datafilter = pd.read_sql_query(f"SELECT barmanpre as barmanpre_merge,connpisos FROM  bigdata.bogota_catastro_compacta WHERE connpisos<={maxpiso} AND ST_CONTAINS(ST_GEOMFROMTEXT('{polygon}'), geometry)" , engine)
            datafilter = datafilter.drop_duplicates(subset='barmanpre_merge',keep='first')
            datafilter['isin'] = 1
            
            datapredios['barmanpre_merge'] = datapredios['barmanpre'].str.split('-')
            datapredios = pd.merge(datapredios.explode('barmanpre_merge'), datafilter, how='inner', on='barmanpre_merge')
            datapredios = datapredios[datapredios['isin']==1]
            datapredios = datapredios.drop_duplicates(subset='idcode',keep='first')
            datapredios.drop(columns=['isin'],inplace=True)
        
            """
            # Altura max de la construccion existente en el lote  
            datafilter = pd.read_sql_query(f"SELECT barmanpre as barmanpre_merge,connpisos,ST_AsText(geometry) as wkt FROM  bigdata.bogota_catastro_compacta WHERE connpisos<={maxpiso} AND ST_CONTAINS(ST_GEOMFROMTEXT('{polygon}'), geometry)" , engine)
            datafilter = datafilter.drop_duplicates(subset='barmanpre_merge',keep='first')

            datafilter['geometry'] = gpd.GeoSeries.from_wkt(datafilter['wkt'])
            datafilter = gpd.GeoDataFrame(datafilter, geometry='geometry')
            datafilter['isin'] = 1
            
            datapredios = gpd.sjoin(datapredios, datafilter, how="left", op="intersects")
            datapredios = datapredios[datapredios['isin']==1]
            datapredios = datapredios.drop_duplicates(subset='idcode',keep='first')
            variables   = [x for x in ['isin','index_left','index_right'] if x in datapredios]
            datapredios.drop(columns=variables,inplace=True)
            """
            
            #-----------------------------------------------------------------#
            # P.O.T
            #-----------------------------------------------------------------#
            datapredios = mergePOT(datapredios,polygon,pot,engine)
            
            # Data lotes de catastro
            lista = []
            for i in datapredios['barmanpre'].unique():
                listapaso = list(set([x.strip() for x in i.split('-')]))
                lista    += listapaso
                lista     = list(set(lista))
            if lista!=[]:
                query = "','".join(lista)
                query = f" lotcodigo IN ('{query}')"   
                datalotescatastro = pd.read_sql_query(f"SELECT lotcodigo as barmanpre, ST_AsText(geometry) as wkt FROM  bigdata.data_bogota_lotes WHERE {query}" , engine)
                datapredios,datalotescatastro = num_combinaciones_lote(datapredios,datalotescatastro)
    else:
        query = ''
        if areamin>0:
            query += f' AND areaterreno>={areamin}'
        if areamax>0:
            query += f' AND areaterreno<={areamax}'
        if predios>0:
            query += f' AND predios<={predios}'

        query = query.strip().strip('AND').strip()
        datapredios = pd.read_sql_query(f"SELECT idcode,barmanpre,areaterreno,predios,delgeometry as geometry  FROM  bigdata.combinacion_lotes_1000 WHERE {query}" , engine)      
            
    engine.dispose()
    return datapredios,datalotescatastro

@st.cache_data
def getlotebycod(codigos):
    
    user        = st.secrets["user_bigdata"]
    password    = st.secrets["password_bigdata"]
    host        = st.secrets["host_bigdata_lectura"]
    schema      = st.secrets["schema_bigdata"]
    engine      = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')

    datapredios   = pd.DataFrame()
    datacompacta  = pd.DataFrame()
    datausosuelo  = pd.DataFrame()
    dataactividad = pd.DataFrame()
    
    if isinstance(codigos, str):
        query       = "','".join(codigos.split('|'))
        query       = f" idcode IN ('{query}')"   
        datapredios = pd.read_sql_query(f"SELECT idcode,barmanpre,areaterreno,predios,delgeometry as geometry FROM  bigdata.combinacion_lotes_1000 WHERE {query}" , engine)

        if not datapredios.empty:
            lista = []
            for i in datapredios['barmanpre'].unique():
                listapaso = list(set([x.strip() for x in i.split('-')]))
                lista    += listapaso
                lista     = list(set(lista))
            if lista!=[]:
                query         = "','".join(lista)
                query         = f" barmanpre IN ('{query}')"                       
                datacompacta  = pd.read_sql_query(f"SELECT * FROM  bigdata.bogota_catastro_compacta WHERE {query}" , engine)
                datausosuelo  = pd.read_sql_query(f"SELECT * FROM  bigdata.bogota_catastro_compacta_precuso WHERE {query}" , engine)
                dataactividad = pd.read_sql_query(f"SELECT * FROM  bigdata.bogota_catastro_compacta_precdestin WHERE {query}" , engine)
    
                dataprecuso,dataprecdestin = getuso_destino()
                dataprecuso.rename(columns={'codigo':'precuso','tipo':'usosuelo','descripcion':'desc_usosuelo'},inplace=True)
                dataprecdestin.rename(columns={'codigo':'precdestin','tipo':'actividad','descripcion':'desc_actividad'},inplace=True)
                if not datausosuelo.empty:
                    datausosuelo  = datausosuelo.merge(dataprecuso,on='precuso',how='left',validate='m:1')
                if not dataactividad.empty:
                    dataactividad = dataactividad.merge(dataprecdestin,on='precdestin',how='left',validate='m:1')
    engine.dispose()
    return datapredios,datacompacta,datausosuelo,dataactividad

#-----------------------------------------------------------------------------#
# P.O.T
#-----------------------------------------------------------------------------#
def mergePOT(datapredios,polygon,pot,engine):
    if pot is not None and pot!=[]:
        for items in pot:
            #-------------------------------------------------------------#
            # Tratamiento urbanistico
            if 'tipo' in items and 'tratamientourbanistico' in items['tipo']:
                consulta = ''
                if 'alturaminpot' in items and items['alturaminpot']>0:
                    consulta += f" AND (alturamax_num>={items['alturaminpot']} OR alturamax_num IS NULL)"
                if 'tratamiento' in items and items['tratamiento']!=[]:
                    query    = "','".join(items['tratamiento'])
                    consulta += f" AND nombretra IN ('{query}')"
                
                if consulta!='':
                    consulta        = consulta.strip().strip('AND')+' AND '
                    datatratamiento = pd.read_sql_query(f"SELECT ST_AsText(geometry) AS wkt FROM  pot.bogota_tratamientourbanistico WHERE {consulta} (ST_CONTAINS(ST_GEOMFROMTEXT('{polygon}'), geometry) OR ST_Intersects(geometry,ST_GEOMFROMTEXT('{polygon}')) OR ST_Touches(geometry,ST_GEOMFROMTEXT('{polygon}')))" , engine)
                    datatratamiento['geometry'] = gpd.GeoSeries.from_wkt(datatratamiento['wkt'])
                    datatratamiento = gpd.GeoDataFrame(datatratamiento, geometry='geometry')
                    datatratamiento['isin'] = 1
                    
                    datapredios = gpd.sjoin(datapredios, datatratamiento, how="left", op="intersects")
                    datapredios = datapredios[datapredios['isin']==1]
                    datapredios = datapredios.drop_duplicates(subset='idcode',keep='first')
                    variables   = [x for x in ['isin','index_left','index_right'] if x in datapredios]
                    datapredios.drop(columns=variables,inplace=True)
                
            #-------------------------------------------------------------#
            # Area de actividad
            if 'tipo' in items and 'areaactividad' in items['tipo']:
                consulta = ''
                if 'nombreare' in items and items['nombreare']!=[]:
                    query    = "','".join(items['nombreare'])
                    consulta += f"nombreare IN ('{query}')"
                if consulta!='':
                    consulta      = consulta.strip().strip('AND')+' AND '
                    dataactividad = pd.read_sql_query(f"SELECT ST_AsText(geometry) AS wkt FROM  pot.bogota_areaactividad WHERE {consulta} (ST_CONTAINS(ST_GEOMFROMTEXT('{polygon}'), geometry) OR ST_Intersects(geometry,ST_GEOMFROMTEXT('{polygon}')) OR ST_Touches(geometry,ST_GEOMFROMTEXT('{polygon}')))" , engine)
                    dataactividad['geometry'] = gpd.GeoSeries.from_wkt(dataactividad['wkt'])
                    dataactividad = gpd.GeoDataFrame(dataactividad, geometry='geometry')
                    dataactividad['isin'] = 1
                    
                    datapredios = gpd.sjoin(datapredios, dataactividad, how="left", op="intersects")
                    datapredios = datapredios[datapredios['isin']==1]
                    datapredios = datapredios.drop_duplicates(subset='idcode',keep='first')
                    variables   = [x for x in ['isin','index_left','index_right'] if x in datapredios]
                    datapredios.drop(columns=variables,inplace=True)
            
            #-------------------------------------------------------------#
            # Actuacion Estrategica
            if 'tipo' in items and 'actuacionestrategica' in items['tipo']:
                if 'isin' in items and any([w for w in ['si','no'] if w in items['isin'].lower()]):
                    datactuacionestrategica = pd.read_sql_query(f"SELECT ST_AsText(geometry) AS wkt FROM  pot.bogota_actuacionestrategica WHERE (ST_CONTAINS(ST_GEOMFROMTEXT('{polygon}'), geometry) OR ST_Intersects(geometry,ST_GEOMFROMTEXT('{polygon}')) OR ST_Touches(geometry,ST_GEOMFROMTEXT('{polygon}')))" , engine)
                    datactuacionestrategica['geometry'] = gpd.GeoSeries.from_wkt(datactuacionestrategica['wkt'])
                    datactuacionestrategica = gpd.GeoDataFrame(datactuacionestrategica, geometry='geometry')
                    datactuacionestrategica['isin'] = 1
                    datapredios = gpd.sjoin(datapredios, datactuacionestrategica, how="left", op="intersects")
                    
                    if 'si' in items['isin'].lower():
                        datapredios = datapredios[datapredios['isin']==1]
                    elif 'no' in items['isin'].lower():
                        datapredios = datapredios[datapredios['isin'].isnull()]
                    datapredios = datapredios.drop_duplicates(subset='idcode',keep='first')
                    variables   = [x for x in ['isin','index_left','index_right'] if x in datapredios]
                    datapredios.drop(columns=variables,inplace=True)
            
    return datapredios

def num_combinaciones_lote(datapredios,datalotescatastro):
    if not datapredios.empty and not datalotescatastro.empty:
        datalotescatastro.index = range(len(datalotescatastro))
        datalotescatastro['num_lotes_comb'] = None
        datalotescatastro['combinacion']    = None
        for i in range(len(datalotescatastro)):
            barmanpre = datalotescatastro['barmanpre'].iloc[i]
            idd       = datapredios['barmanpre'].str.contains(barmanpre)
            if sum(idd)>0:
                datalotescatastro.loc[i,'num_lotes_comb'] = sum(idd)
                datalotescatastro.loc[i,'combinacion'] = '|'.join(datapredios[idd]['idcode'].unique())
        
        idd = datalotescatastro['num_lotes_comb'].isnull()
        datalotescatastro = datalotescatastro[~idd]
    return datapredios,datalotescatastro
