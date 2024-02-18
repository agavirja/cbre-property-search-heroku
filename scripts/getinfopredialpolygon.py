import streamlit as st
import pandas as pd
from sqlalchemy import create_engine 

from scripts.coddir import coddir
from scripts.getdatasnr import getdatasnr
from scripts.formato_direccion import formato_direccion
from scripts.getdatavigencia import getdatavigencia
from scripts.getuso_destino import getuso_destino
from scripts.getcatastropolygon import getcatastropolygon
from scripts.groupcatastro import groupcatastro
from scripts.merge_snr_lotes import merge_snr_lotes
from scripts.getlatlng import getlatlng
from scripts.inmuebleANDusosuelo import usosuelo2inmueble,inmueble2usosuelo
from scripts.getInfoCatastralByPolygon import getInfoCatastralByPolygon


def splitdate(x,pos):
    try: return int(x.split('-')[pos].strip())
    except: return None
    
@st.cache_data
def getinfopredialpolygon(inputvar):

  
    polygon       = inputvar['polygon'] if 'polygon' in inputvar and isinstance(inputvar['polygon'], str) else None 
    barmanpre     = inputvar['barmanpre'] if 'barmanpre' in inputvar else None
    precuso       = inputvar['precuso'] if 'precuso' in inputvar else []
    areamin       = inputvar['areamin'] if 'areamin' in inputvar and inputvar['areamin']>0 else 0
    areamax       = inputvar['areamax'] if 'areamax' in inputvar and inputvar['areamax']>0 else 0
    antiguedadmin = inputvar['antiguedadmin'] if 'antiguedadmin' in inputvar and inputvar['antiguedadmin']>0 else 0
    antiguedadmax = inputvar['antiguedadmax'] if 'antiguedadmax' in inputvar and inputvar['antiguedadmax']>0 else 0

    # Para ampliar la muestra, seleccionar todos los precuso acordes al tipo del inmueble: Por ejemplo, si es comercio NPH me compara solo con NPH, pero podemos traer todo lo que es comercio
    if precuso!=[]:
        typeinm = usosuelo2inmueble(precuso)
        precuso = inmueble2usosuelo(typeinm)
    
    datalotes       = pd.DataFrame()
    datachip        = pd.DataFrame()
    datavigencia    = pd.DataFrame()
    datasnrprocesos = pd.DataFrame()
    datasnrtable    = pd.DataFrame()
    
    datalotes,datachip = getInfoCatastralByPolygon(polygon=polygon,barmanpre=barmanpre,precuso=precuso,areamin=areamin,areamax=areamax,antiguedadmin=antiguedadmin,antiguedadmax=antiguedadmax)

    # funcion anterior: buscaba todos los predios en catastro, ahora busca solo los lotes compactos, es mas eficitente
    #datacatastro,datalotes = getcatastropolygon(polygon=polygon,precuso=precuso,areamin=areamin,areamax=areamax)
    
    #-----------------#
    # Informacion SHD #
    if not datachip.empty:
        chip = list(datachip['prechip'].unique())
        datavigencia = getdatavigencia(chip)

    #-----------------#
    # Informacion SNR #
    if not datachip.empty:
        chip = list(datachip['prechip'].unique())
        datasnrprocesos,datasnrtable = getdatasnr(chip,tipovariable='chip')
            
    if not datachip.empty and not datasnrtable.empty:
        datamerge    = datachip[['prechip','preaconst','preaterre','predirecc']]
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
    datalotes = merge_snr_lotes(datasnrprocesos,datachip,datalotes)
        
    return datalotes,datachip,datavigencia,datasnrprocesos,datasnrtable
