import streamlit as st
import pandas as pd
from sqlalchemy import create_engine 

from scripts.coddir import coddir
from scripts.getdatasnr import getdatasnr
from scripts.formato_direccion import formato_direccion
from scripts.circle_polygon import circle_polygon
from scripts.getdatavigencia import getdatavigencia
from scripts.getuso_destino import getuso_destino
from scripts.getcatastropolygon import getcatastropolygon
from scripts.groupcatastro import groupcatastro
from scripts.merge_snr_lotes import merge_snr_lotes
from scripts.getlatlng import getlatlng

def splitdate(x,pos):
    try: return int(x.split('-')[pos].strip())
    except: return None
    
@st.cache_data
def getinfopredial(inputvar):
    user        = st.secrets["user_bigdata"]
    password    = st.secrets["password_bigdata"]
    host        = st.secrets["host_bigdata_lectura"]
    schema      = st.secrets["schema_bigdata"]
    
    dataparticular_catastro = pd.DataFrame()
    datageneral_catastro    = pd.DataFrame()
    datalote_particular     = pd.DataFrame()
    datavigencia_general    = pd.DataFrame()
    datalotespolygon        = pd.DataFrame()
    datacatastropolygon     = pd.DataFrame()
    datavigencia_particular = pd.DataFrame()
    datasnrprocesos         = pd.DataFrame()
    datasnrtable            = pd.DataFrame()
    usosuelo                = []
    polygonfilter           = None
    latitud                 = None
    longitud                = None
    
    if 'metros' not in inputvar: inputvar['metros'] = 500
        
    engine  = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')
    
    #----------------#
    # Data catastral #
    if 'matricula' in inputvar and inputvar['matricula'] and not any([x for x in ['*','delete'] if x in inputvar['matricula'].lower()]):  
        datapaso = pd.read_sql_query(f"SELECT chip FROM  {schema}.data_bogota_catastro_predio WHERE numeroMatriculaInmobiliaria ='{inputvar['matricula']}'" , engine)
        if not datapaso.empty:
            inputvar['chip'] = datapaso['chip'].to_list()
                        
    if 'direccion' in inputvar and inputvar['direccion'] and not any([x for x in ['*','delete'] if x in inputvar['direccion'].lower()]): 
        datapaso = pd.read_sql_query(f"SELECT prechip as chip FROM  {schema}.data_bogota_catastro WHERE coddir ='{coddir(inputvar['direccion'])}'" , engine)
        if not datapaso.empty:
            inputvar['chip'] = datapaso['chip'].to_list()
        else:
            ciudad    = 'bogota'
            direccion = f"{inputvar['direccion']},{ciudad},colombia"
            latitud,longitud = getlatlng(direccion)
            metros = 500
            if 'metros' in inputvar:
                metros = inputvar['metros']
            if latitud and longitud:
                polygonfilter = circle_polygon(metros,latitud,longitud)

    if 'barmanpre' in inputvar and inputvar['barmanpre'] and not any([x for x in ['*','delete'] if x in inputvar['barmanpre'].lower()]): 
        datapaso = pd.read_sql_query(f"SELECT prechip as chip FROM  {schema}.data_bogota_catastro WHERE barmanpre ='{inputvar['barmanpre']}'" , engine)
        if not datapaso.empty:
            inputvar['chip'] = datapaso['chip'].to_list()

    if 'chip' in inputvar and isinstance(inputvar['chip'], list) and len(inputvar['chip'])==1:
        inputvar['chip'] = inputvar['chip'][0]
   
    if 'chip' in inputvar and inputvar['chip']:
        if isinstance(inputvar['chip'], str):
            query = f" prechip = '{inputvar['chip']}'"
            dataparticular_catastro = pd.read_sql_query(f"SELECT precbarrio,prenbarrio,prechip,precedcata,predirecc,preaterre,preaconst,precdestin,precuso,preuvivien,preusoph,prevetustz,barmanpre,latitud,longitud,coddir,piso,estrato  FROM  {schema}.data_bogota_catastro WHERE {query} AND (precdestin<>'65')" , engine)
            if not dataparticular_catastro.empty:
                query    = f" numeroChip = '{inputvar['chip']}'"
                datapaso = pd.read_sql_query(f"SELECT numeroChip as prechip, numeroMatriculaInmobiliaria as matricula FROM  {schema}.data_bogota_catastro_predio WHERE {query}" , engine)
                if not datapaso.empty:
                    dataparticular_catastro = dataparticular_catastro.merge(datapaso,on='prechip',how='left',validate='m:1')
                query = "','".join(dataparticular_catastro['barmanpre'].astype(str).unique())
                query = f" barmanpre IN ('{query}')"
                datageneral_catastro = pd.read_sql_query(f"SELECT precbarrio,prenbarrio,prechip,predirecc,preaterre,preaconst,precdestin,precuso,preuvivien,preusoph,prevetustz,barmanpre,latitud,longitud,coddir,piso,estrato  FROM  {schema}.data_bogota_catastro WHERE {query} AND (precdestin<>'65')" , engine)

        elif isinstance(inputvar['chip'], list):
            if len(inputvar['chip'])==1:
                query = f" prechip = '{inputvar['chip'][0]}'"
                dataparticular_catastro = pd.read_sql_query(f"SELECT precbarrio,prenbarrio,prechip,precedcata,predirecc,preaterre,preaconst,precdestin,precuso,preuvivien,preusoph,prevetustz,barmanpre,latitud,longitud,coddir,piso,estrato  FROM  {schema}.data_bogota_catastro WHERE {query} AND (precdestin<>'65')" , engine)
                if not dataparticular_catastro.empty:
                    query = f" numeroChip = '{inputvar['chip']}'"
                    datapaso = pd.read_sql_query(f"SELECT numeroChip as prechip, numeroMatriculaInmobiliaria as matricula FROM  {schema}.data_bogota_catastro_predio WHERE {query}" , engine)
                    if not datapaso.empty:
                        dataparticular_catastro = dataparticular_catastro.merge(datapaso,on='prechip',how='left',validate='m:1')
                    query = "','".join(dataparticular_catastro['barmanpre'].astype(str).unique())
                    query = f" barmanpre IN ('{query}')"
                    datageneral_catastro = pd.read_sql_query(f"SELECT precbarrio,prenbarrio,prechip,predirecc,preaterre,preaconst,precdestin,precuso,preuvivien,preusoph,prevetustz,barmanpre,latitud,longitud,coddir,piso,estrato  FROM  {schema}.data_bogota_catastro WHERE {query} AND (precdestin<>'65')" , engine)            
            else:
                query = "','".join(inputvar['chip'])
                query = f" prechip IN ('{query}')"
                datageneral_catastro = pd.read_sql_query(f"SELECT precbarrio,prenbarrio,prechip,predirecc,preaterre,preaconst,precdestin,precuso,preuvivien,preusoph,prevetustz,barmanpre,latitud,longitud,coddir,piso,estrato  FROM  {schema}.data_bogota_catastro WHERE {query} AND (precdestin<>'65')" , engine)

    if datageneral_catastro.empty and 'barmanpre' in inputvar and inputvar['barmanpre']:
        query = f" barmanpre = '{inputvar['barmanpre']}'"
        dataparticular_catastro = pd.read_sql_query(f"SELECT precbarrio,prenbarrio,prechip,precedcata,predirecc,preaterre,preaconst,precdestin,precuso,preuvivien,preusoph,prevetustz,barmanpre,latitud,longitud,coddir,piso,estrato  FROM  {schema}.data_bogota_catastro WHERE {query} AND (precdestin<>'65')" , engine)

    if not dataparticular_catastro.empty or not datageneral_catastro.empty: 
        #-----------#
        # Data lote #
        if not datageneral_catastro.empty:
            query    = "','".join(datageneral_catastro['barmanpre'].unique())
            query    = f" lotcodigo IN ('{query}')"
            datalote_particular = pd.read_sql_query(f"SELECT lotcodigo as barmanpre, ST_AsText(geometry) as wkt FROM  {schema}.data_bogota_lotes WHERE {query}" , engine)
    
        #----------------#
        # Poligono radio #
        latitud, longitud = None,None
        if not dataparticular_catastro.empty:
            if 'preusoph' in dataparticular_catastro: dataparticular_catastro['preusoph'] = dataparticular_catastro['preusoph'].replace(['S','N'],['Si','No'])
            latitud  = dataparticular_catastro['latitud'].iloc[0]
            longitud = dataparticular_catastro['longitud'].iloc[0]
            
        elif not datageneral_catastro.empty:
            latitud  = datageneral_catastro['latitud'].iloc[0]
            longitud = datageneral_catastro['longitud'].iloc[0]
                                                             
        if latitud is not None and longitud is not None:
            polygonfilter = circle_polygon(inputvar['metros'],latitud,longitud)
            latitud       = latitud
            longitud      = longitud
            
        #---------------#
        # Uso del suelo #
        dataprecuso,dataprecdestin = getuso_destino()
        dataprecuso.rename(columns={'codigo':'precuso','tipo':'usosuelo','descripcion':'desc_usosuelo'},inplace=True)
        dataprecdestin.rename(columns={'codigo':'precdestin','tipo':'actividad','descripcion':'desc_actividad'},inplace=True)
        
        if not datageneral_catastro.empty:
            usosuelo             = list(datageneral_catastro[datageneral_catastro['precuso'].notnull()]['precuso'].unique())
            datageneral_catastro = datageneral_catastro.merge(dataprecuso,on='precuso',how='left',validate='m:1')
            datageneral_catastro = datageneral_catastro.merge(dataprecdestin,on='precdestin',how='left',validate='m:1')
            datageneral_catastro['formato_direccion'] = datageneral_catastro['predirecc'].apply(lambda x: formato_direccion(x))
            for i in ['preaconst','preaterre']:
                idd = datageneral_catastro[i].isnull()
                if sum(idd)>0:
                    datageneral_catastro.loc[idd,i] = 0
                    
        if not dataparticular_catastro.empty:
            usosuelo                = list(dataparticular_catastro[dataparticular_catastro['precuso'].notnull()]['precuso'].unique())
            dataparticular_catastro = dataparticular_catastro.merge(dataprecuso,on='precuso',how='left',validate='m:1')
            dataparticular_catastro = dataparticular_catastro.merge(dataprecdestin,on='precdestin',how='left',validate='m:1')
            dataparticular_catastro['formato_direccion'] = dataparticular_catastro['predirecc'].apply(lambda x: formato_direccion(x))
            for i in ['preaconst','preaterre']:
                idd = dataparticular_catastro[i].isnull()
                if sum(idd)>0:
                    dataparticular_catastro.loc[idd,i] = 0
        engine.dispose()
        
        #---------------------#
        # Informacion general #
        if polygonfilter:
            datacatastropolygon,datalotespolygon = getcatastropolygon(polygon=str(polygonfilter),precuso=usosuelo)

        datagrupada = pd.DataFrame()
        if not datageneral_catastro.empty:
            datagrupada = groupcatastro(datageneral_catastro)
            
        if not datalotespolygon.empty and not dataparticular_catastro.empty:
            datamerge = datalotespolygon[datalotespolygon['barmanpre'].isin(dataparticular_catastro['barmanpre'])]
            if not datalotespolygon.empty:
                datamerge = datalotespolygon.drop_duplicates(subset='barmanpre',keep='first')
                dataparticular_catastro = dataparticular_catastro.merge(datamerge[['barmanpre','predios','areaconstruida','areaterreno','antiguedad_min','antiguedad_max']],on='barmanpre',how='left',validate='m:1')
                dataparticular_catastro.rename(columns={'predios':'predios_uso','areaconstruida':'areaconstruida_uso','areaterreno':'areaterreno_uso','antiguedad_min':'antiguedad_min_uso','antiguedad_max':'antiguedad_max_uso'},inplace=True)
            
            if not datagrupada.empty:
                datamerge = datagrupada.drop_duplicates(subset='barmanpre',keep='first')
                dataparticular_catastro = dataparticular_catastro.merge(datamerge[['barmanpre','predios','areaconstruida','areaterreno','antiguedad_min','antiguedad_max']],on='barmanpre',how='left',validate='m:1')
                dataparticular_catastro.rename(columns={'predios':'prediostotal','areaconstruida':'areaconstruidatotal','areaterreno':'areaterrenototal','antiguedad_min':'antiguedad_mintotal','antiguedad_max':'antiguedad_maxtotal'},inplace=True)
                
        if not datalotespolygon.empty and not datageneral_catastro.empty:
            datamerge = datalotespolygon[datalotespolygon['barmanpre'].isin(datageneral_catastro['barmanpre'])]
            if not datalotespolygon.empty:
                datamerge = datalotespolygon.drop_duplicates(subset='barmanpre',keep='first')
                datageneral_catastro = datageneral_catastro.merge(datamerge[['barmanpre','predios','areaconstruida','areaterreno','antiguedad_min','antiguedad_max']],on='barmanpre',how='left',validate='m:1')
                datageneral_catastro.rename(columns={'predios':'predios_uso','areaconstruida':'areaconstruida_uso','areaterreno':'areaterreno_uso','antiguedad_min':'antiguedad_min_uso','antiguedad_max':'antiguedad_max_uso'},inplace=True)

            if not datagrupada.empty:
                datamerge = datagrupada.drop_duplicates(subset='barmanpre',keep='first')
                datageneral_catastro = datageneral_catastro.merge(datamerge[['barmanpre','predios','areaconstruida','areaterreno','antiguedad_min','antiguedad_max']],on='barmanpre',how='left',validate='m:1')
                datageneral_catastro.rename(columns={'predios':'prediostotal','areaconstruida':'areaconstruidatotal','areaterreno':'areaterrenototal','antiguedad_min':'antiguedad_mintotal','antiguedad_max':'antiguedad_maxtotal'},inplace=True)

        #-----------------#
        # Informacion SHD #
        if not dataparticular_catastro.empty:
            datavigencia_particular = getdatavigencia(dataparticular_catastro['prechip'].iloc[0])

        if not dataparticular_catastro.empty:
            datavigencia_general = getdatavigencia(dataparticular_catastro['prechip'].iloc[0])

        #-----------------#
        # Informacion SNR #
        if not datacatastropolygon.empty:
            chip = list(datacatastropolygon['prechip'].unique())
            datasnrprocesos,datasnrtable = getdatasnr(chip,tipovariable='chip')
            
        if not datacatastropolygon.empty and not datasnrtable.empty:
            datamerge    = datacatastropolygon[['prechip','preaconst','preaterre','predirecc']]
            datamerge    = datamerge.drop_duplicates(subset='prechip',keep='first')
            datasnrtable = datasnrtable.merge(datamerge,on='prechip',how='left',validate='m:1')
        
        if not datasnrprocesos.empty and not datasnrtable.empty:
            if 'preaconst' in datasnrtable:
                datamerge         = datasnrtable.groupby('docid').agg({'preaconst':max,'preaterre':max,'predirecc':'first'}).reset_index()
                datamerge.columns = ['docid','preaconst','preaterre','predirecc']
                datasnrprocesos   = datasnrprocesos.merge(datamerge,on='docid',how='left',validate='m:1')
                datasnrprocesos['valortransaccionmt2'] = None
                idd = datasnrprocesos['preaconst']>0
                if sum(idd)>0:
                    datasnrprocesos.loc[idd,'valortransaccionmt2'] = datasnrprocesos.loc[idd,'cuantia']/datasnrprocesos.loc[idd,'preaconst']
                if sum(~idd)>0:
                    datasnrprocesos.loc[~idd,'valortransaccionmt2'] = datasnrprocesos.loc[~idd,'cuantia']/datasnrprocesos.loc[~idd,'preaterre']
        if not datasnrprocesos.empty and 'fecha_documento_publico' in datasnrprocesos:
            datasnrprocesos['year']  = datasnrprocesos['fecha_documento_publico'].apply(lambda x: splitdate(x,0) )
            datasnrprocesos['month'] = datasnrprocesos['fecha_documento_publico'].apply(lambda x: splitdate(x,1) )

        #--------------------------------------------------------------------------------#
        # Merge lotes con transacciones [snr], cuantia y valor por mt2 de cada barmanpre #
        datalotespolygon = merge_snr_lotes(datasnrprocesos,datacatastropolygon,datalotespolygon)
        
    return dataparticular_catastro,datageneral_catastro,datalote_particular,datalotespolygon,datacatastropolygon,datavigencia_particular,datavigencia_general,datasnrprocesos,datasnrtable,polygonfilter,latitud,longitud,usosuelo
