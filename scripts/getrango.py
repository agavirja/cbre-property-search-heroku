import pandas as pd
import numpy as np
from datetime import datetime

def getrango(df,variable):
    addlabel   = ''
    if  any([x for x in ['preaconst','preaterre','areaconstruida'] if x in variable]):
        addlabel = ' mt2'
    elif 'avaluocatastral' in variable:
        addlabel = 'millones'
        df[variable] = df[variable]/1000000
    elif 'avaluoxmt2' in variable:
        addlabel = 'millones'
        df[variable] = df[variable]/1000000
    elif 'cuantia' in variable:
        addlabel = 'millones'
        df[variable] = df[variable]/1000000
    if 'prevetustz' in variable:
        df['antiguedad'] = datetime.now().year-df['prevetustz']
        variable = 'antiguedad'
        
    idd = np.isinf(df[variable]) | np.isneginf(df[variable]) | (df[variable].isnull())
    df  = df[~idd]

    if not df.empty:
        df = df.sort_values(by=variable,ascending=True)
        try:
            df          = df.sort_values(by=variable,ascending=True)
            total_rows  = len(df)
            df.index    = range(len(df))
            percentages = [0.25, 0.35, 0.20, 0.12, 0.08]
            limits = [0] + [int(p * total_rows) for p in percentages[:-1]]
            limits = list(np.cumsum(limits))+[total_rows]
            labels = []
            for i in range(len(limits) - 1):
                start_val = int(df.loc[limits[i], variable])
                end_val = int(df.loc[limits[i + 1] - 1, variable])
                if any([x for x in ['avaluocatastral','avaluoxmt2','cuantia'] if x in variable]):
                    start_val = f'${start_val:,.0f}'
                    end_val   = f'${end_val:,.0f}'
                labels.append(f"{start_val}-{end_val} {addlabel}")
            df['rango']     = pd.cut(df.index,bins=limits,labels=labels,include_lowest=True)
            df['categoria'] = pd.cut(df.index,bins=limits,labels=[1,2,3,4,5],include_lowest=True)
        except:
            try:
                Q1              = df[variable].quantile(0.025)
                Q3              = df[variable].quantile(0.975)
                IQR             = Q3 - Q1
                limite_inferior = Q1 - 1.5 * IQR
                limite_superior = Q3 + 1.5 * IQR
                
                num_values  = 5
                idd         = (df[variable] >= limite_inferior) & (df[variable] <= limite_superior)
                dfnew       = df[idd]
                hist, bins  = np.histogram(dfnew[variable], bins=num_values)
                bins[0]     = 0
                bins[-1]    = np.inf
                cuantiles, bins = pd.cut(df[variable],bins, labels=False, retbins=True)
                
                if 'avaluocatastral' in variable:
                    addlabel = 'mm'
                    labels = [f'Menor a ${int(round(bins[1], 0)/1000000)} {addlabel}' if i == 0 else f'${int(round(bins[i], 0)/1000000)} a ${int(round(bins[i+1], 0)/1000000)} {addlabel}' for i in range(num_values - 1)]
                    labels.append(f'Mayor a ${int(round(bins[-2], 0)/1000000)} {addlabel}')
                elif 'avaluoxmt2' in variable:
                    addlabel = 'mm'
                    labels = [f'Menor a ${round(bins[1]/1000000, 1)} {addlabel}' if i == 0 else f'${round(bins[i]/1000000, 1)} a ${round(bins[i+1]/1000000, 1)} {addlabel}' for i in range(num_values - 1)]
                    labels.append(f'Mayor a ${round(bins[-2]/1000000, 1)} {addlabel}')
                elif 'cuantia' in variable:
                    addlabel = 'mm'
                    labels = [f'Menor a ${int(round(bins[1], 0)/1000000)} {addlabel}' if i == 0 else f'${int(round(bins[i], 0)/1000000)} a ${int(round(bins[i+1], 0)/1000000)} {addlabel}' for i in range(num_values - 1)]
                    labels.append(f'Mayor a ${int(round(bins[-2], 0)/1000000)} {addlabel}')
                else:
                    labels = [f'Menor a {int(round(bins[1], 0))} {addlabel}' if i == 0 else f'{int(round(bins[i], 0))} a {int(round(bins[i+1], 0))} {addlabel}' for i in range(num_values - 1)]
                    labels.append(f'Mayor a {int(round(bins[-2], 0))} {addlabel}')
                df['rango'] = pd.cut(df[variable],bins, labels=labels)
                df['categoria'] = pd.cut(df[variable],bins, labels=[1,2,3,4,5])
            except: 
                df['rango'] = df[variable].copy()
                df['categoria'] = 1
    else:
        df = pd.DataFrame()
    return df
