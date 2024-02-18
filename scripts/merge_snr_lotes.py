import pandas as pd

def merge_snr_lotes(datasnrprocesos,datacatastro,datalotes):

    datacompraventa = pd.DataFrame()

    if not datasnrprocesos.empty and not datacatastro.empty:
        if 'predirecc' in datasnrprocesos and all([x for x in ['predirecc','barmanpre'] if x in datacatastro]):
            datacompraventa = datasnrprocesos[datasnrprocesos['codigo'].isin(['125','126','168','169','0125','0126','0168','0169'])]
            datamerge       = datacatastro[['predirecc','barmanpre']].drop_duplicates(subset='predirecc',keep='first')
            datacompraventa = datacompraventa.merge(datamerge,on='predirecc',how='left',validate='m:1')
            datacompraventa = datacompraventa.groupby(['barmanpre']).agg({'cuantia':['count','sum'],'valortransaccionmt2':'median'}).reset_index()
            datacompraventa.columns = ['barmanpre','transacciones','valortransacciones','valortransaccionesmt2']
        
    if not datalotes.empty and not datacompraventa.empty:
        datalotes = datalotes.merge(datacompraventa,on='barmanpre',how='left',validate='m:1')

    return datalotes
