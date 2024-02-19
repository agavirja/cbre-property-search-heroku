import streamlit as st
import pandas as pd
from sqlalchemy import create_engine 

from scripts.coddir import coddir
from scripts.getdatasnr import getdatasnr
from scripts.formato_direccion import formato_direccion
from scripts.getdatavigencia import getdatavigencia
from scripts.getuso_destino import getuso_destino

def splitdate(x,pos):
    try: return int(x.split('-')[pos].strip())
    except: return None
    
@st.cache_data
def getinfopredio(inputvar):
    
    user        = st.secrets["user_bigdata"]
    password    = st.secrets["password_bigdata"]
    host        = st.secrets["host_bigdata_lectura"]
    schema      = st.secrets["schema_bigdata"]
    engine      = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')

    datacatastro    = pd.DataFrame()
    databarmapre    = pd.DataFrame()
    datalote        = pd.DataFrame()
    datavigencia    = pd.DataFrame()
    datasnrprocesos = pd.DataFrame()
    datasnrtable    = pd.DataFrame()
    
    #----------------#
    # Data catastral #
    if 'matricula' in inputvar and inputvar['matricula']!='' and inputvar['matricula'] is not None and not any([x for x in ['*','delete'] if x in inputvar['matricula'].lower()]):  
        datapaso = pd.read_sql_query(f"SELECT numeroChip as chip FROM  {schema}.data_bogota_catastro_predio WHERE numeroMatriculaInmobiliaria ='{inputvar['matricula']}'" , engine)
        if not datapaso.empty:
            inputvar['chip'] = datapaso['chip'].to_list()
                        
    if 'direccion' in inputvar and inputvar['direccion']!='' and inputvar['direccion'] is not None and not any([x for x in ['*','delete'] if x in inputvar['direccion'].lower()]): 
        datapaso = pd.read_sql_query(f"SELECT prechip as chip FROM  {schema}.data_bogota_catastro WHERE coddir ='{coddir(inputvar['direccion'])}'" , engine)
        if not datapaso.empty:
            inputvar['chip'] = datapaso['chip'].to_list()
            
    if 'barmanpre' in inputvar and inputvar['barmanpre']!='' and inputvar['barmanpre'] is not None and not any([x for x in ['*','delete'] if x in inputvar['barmanpre'].lower()]): 
        datapaso = pd.read_sql_query(f"SELECT prechip as chip FROM  {schema}.data_bogota_catastro WHERE barmanpre ='{inputvar['barmanpre']}'" , engine)
        if not datapaso.empty:
            inputvar['chip'] = datapaso['chip'].to_list()

    if 'chip' in inputvar and isinstance(inputvar['chip'], list) and len(inputvar['chip'])==1:
        inputvar['chip'] = inputvar['chip'][0]
   
    if 'chip' in inputvar and inputvar['chip']!='' and inputvar['chip'] is not None:
        query = ''
        if isinstance(inputvar['chip'], str):
            query = f" prechip = '{inputvar['chip']}'"

        elif isinstance(inputvar['chip'], list):
            if len(inputvar['chip'])==1:
                query = f" prechip = '{inputvar['chip'][0]}'"
            else:
                query = "','".join(inputvar['chip'])
                query = f" prechip IN ('{query}')"

        if query!='':
            datapaso = pd.read_sql_query(f"SELECT barmanpre  FROM  {schema}.data_bogota_catastro WHERE {query} AND (precdestin<>'65')" , engine)
            if not datapaso.empty:
                query = "','".join(datapaso['barmanpre'].unique())
                query = f" barmanpre IN ('{query}')"
                datacatastro = pd.read_sql_query(f"SELECT precbarrio,prenbarrio,prechip,precedcata,predirecc,preaterre,preaconst,precdestin,precuso,preuvivien,preusoph,prevetustz,barmanpre,latitud,longitud,coddir,piso,estrato  FROM  {schema}.data_bogota_catastro WHERE {query} AND (precdestin<>'65')" , engine)
            
        if not datacatastro.empty:
            query = "','".join(datacatastro['prechip'].unique())
            query = f" numeroChip IN ('{query}')"       
            datapaso     = pd.read_sql_query(f"SELECT numeroChip as prechip, numeroMatriculaInmobiliaria as matricula FROM  {schema}.data_bogota_catastro_predio WHERE {query}" , engine)
            if not datapaso.empty:
                datamerge    = datapaso.drop_duplicates(subset='prechip',keep='first')
                datacatastro = datacatastro.merge(datamerge,on='prechip',how='left',validate='m:1')
            else: datacatastro['matricula'] = ''

            # Data lote
            query    = "','".join(datacatastro['barmanpre'].unique())
            query    = f" lotcodigo IN ('{query}')"
            datalote = pd.read_sql_query(f"SELECT lotcodigo as barmanpre, ST_AsText(geometry) as wkt FROM  {schema}.data_bogota_lotes WHERE {query}" , engine)
            
            # uso suelo y actividad del predio
            dataprecuso,dataprecdestin = getuso_destino()
            dataprecuso.rename(columns={'codigo':'precuso','tipo':'usosuelo','descripcion':'desc_usosuelo'},inplace=True)
            dataprecdestin.rename(columns={'codigo':'precdestin','tipo':'actividad','descripcion':'desc_actividad'},inplace=True)
            datacatastro = datacatastro.merge(dataprecuso,on='precuso',how='left',validate='m:1')
            datacatastro = datacatastro.merge(dataprecdestin,on='precdestin',how='left',validate='m:1')
            datacatastro['formato_direccion'] = datacatastro['predirecc'].apply(lambda x: formato_direccion(x))
 
            # Data agregada por barmanpre
            query = "','".join(datacatastro['barmanpre'].unique())
            query = f" barmanpre IN ('{query}')"       
            databarmapre = pd.read_sql_query(f"SELECT barmanpre, precuso, predios as predios_uso, areaconstruida as areaconstruida_uso,areaterreno as areaterreno_uso, predios_total as prediostotal, areaconstruida_total as areaconstruidatotal, areaterreno_total as areaterrenototal, propietarios, total_avaluo, total_predial, avaluomt2 FROM  {schema}.data_groupbarmanpre WHERE {query}" , engine)
            if not databarmapre.empty:
                datacatastro = datacatastro.merge(databarmapre,on=['barmanpre','precuso'])

    engine.dispose()
    
    #----------#
    # Data SHD #
    if not datacatastro.empty:
        datavigencia = getdatavigencia(list(datacatastro['prechip'].unique()))

    #----------#
    # Data SNR #
    if not datacatastro.empty:
        chip = list(datacatastro['prechip'].unique())
        datasnrprocesos,datasnrtable = getdatasnr(chip,tipovariable='chip')
        
    if not datasnrprocesos.empty and not datasnrtable.empty:
        datamerge    = datacatastro.drop_duplicates(subset='prechip',keep='first')
        datasnrtable = datasnrtable.merge(datamerge[['prechip','preaconst','preaterre','predirecc']],on='prechip',how='left',validate='m:1')
        if 'preaconst' in datasnrtable:
            datamerge         = datasnrtable.groupby('docid').agg({'preaconst':max,'preaterre':max,'predirecc':'first'}).reset_index()
            datamerge.columns = ['docid','preaconst','preaterre','predirecc']
            datasnrprocesos   = datasnrprocesos.merge(datamerge,on='docid',how='left',validate='m:1')
            datasnrprocesos['valortransaccionmt2'] = None
            idd = (datasnrprocesos['preaconst']>0) & (datasnrprocesos['codigo'].isin(['125','126','168','169','0125','0126','0168','0169']))
            if sum(idd)>0:
                datasnrprocesos.loc[idd,'valortransaccionmt2'] = datasnrprocesos.loc[idd,'cuantia']/datasnrprocesos.loc[idd,'preaconst']
            idd = (~idd) & (datasnrprocesos['preaterre']>0) & (datasnrprocesos['codigo'].isin(['125','126','168','169','0125','0126','0168','0169']))
            if sum(idd)>0:
                datasnrprocesos.loc[~idd,'valortransaccionmt2'] = datasnrprocesos.loc[~idd,'cuantia']/datasnrprocesos.loc[~idd,'preaterre']
                
    if not datasnrprocesos.empty and 'fecha_documento_publico' in datasnrprocesos:
        datasnrprocesos['year']  = datasnrprocesos['fecha_documento_publico'].apply(lambda x: splitdate(x,0) )
        datasnrprocesos['month'] = datasnrprocesos['fecha_documento_publico'].apply(lambda x: splitdate(x,1) )

    #-----------------#
    # Chip del predio #
    chip = None
    if isinstance(inputvar['chip'], str):
        chip = inputvar['chip']
    elif isinstance(inputvar['chip'], list) and len(inputvar['chip'])==1:
        chip = inputvar['chip'][0]
    
    return chip,datacatastro,databarmapre,datalote,datavigencia,datasnrprocesos,datasnrtable
