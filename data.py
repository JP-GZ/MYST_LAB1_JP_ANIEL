

import pandas as pd
import re
from datetime import datetime
import os
from os import path
import yfinance as yf
import numpy as np
import warnings
warnings.filterwarnings("ignore")
abspath = path.abspath('files')

# Variables a consultar
direccion = abspath
data_files = {}
fechas = []
fecha_formato = []
tickers = []
inv_i = 1000000
comission = 0.00125


for i in os.listdir(abspath):
    fechas.append(re.search(r'\d+',i).group(0))
    fechas.sort(key=lambda date:datetime.strptime(date,'%Y%m%d'))
fecha_formato = [(pd.to_datetime(fechas[j]).date()).strftime('%Y-%m-%d') for j in range(len(fechas))]


for i in fechas:
        data = pd.read_csv(direccion + '/NAFTRAC_' + i + '.csv', skiprows=2)
        data = data.dropna(how='any')
        data = data.astype({'Precio': str})
        data['Precio'] = [i.replace(',', '') for i in data['Precio']]
        data['Ticker'] = [i.replace('*', '') for i in data['Ticker']]
        data['Ticker'] = data['Ticker'].str.replace('GFREGIOO', 'RA', regex=True)
        data['Ticker'] = data['Ticker'].str.replace('MEXCHEM', 'ORBIA', regex=True)
        data['Ticker'] = data['Ticker'].str.replace('LIVEPOLC.1', 'LIVEPOLC-1', regex=True)

        data.drop(data.index[data['Ticker'] == 'KOFL'], inplace=True)
        data.drop(data.index[data['Ticker'] == 'LASITE'], inplace=True)
        data.drop(data.index[data['Ticker'] == 'BSMXB'], inplace=True)
        data.drop(data.index[data['Ticker'] == 'NMKA'], inplace=True)
        data.drop(data.index[data['Ticker'] == 'KOFUBL'], inplace=True)
        data.drop(data.index[data['Ticker'] == 'MXN'], inplace=True)
        data.drop(data.index[data['Ticker'] == 'USD'], inplace=True)
        data.drop(data.index[data['Ticker'] == 'SITES1A-1'], inplace=True)
        data.drop(data.index[data['Ticker'] == 'SITESA-1'], inplace=True)
        data.drop(data.index[data['Ticker'] == 'SITESB.1'], inplace=True)
        data.drop(data.index[data['Ticker'] == 'LASITEB.1'], inplace=True)

        data = data.astype({'Precio': float})
        data['Ticker'] = data['Ticker'].astype(str) + '.MX'

        data['Peso (%)'] = data['Peso (%)'] / 100
        data_files[i] = data


tickers = [list(data_files[i]['Ticker']) for i in fechas]
tickers = [item for sublist in tickers for item in sublist]
tickers= list(set(tickers))


fecha_incial = fecha_formato[0]
yahoo_data = yf.download(tickers, start= fecha_incial, group_by="close", interval='1d')
data_close = yahoo_data.loc[ : , ([0],['Close'])]

for tick in tickers:
        closes=yahoo_data.loc[ : , (tick , ['Close'])]
        closes= closes.droplevel(1, axis=1)
        data_close= pd.concat([data_close,closes], axis=1, join="inner")


data_close.reset_index(inplace=True)
precios_cierre = data_close[data_close['Date'].isin(fecha_formato)]
precios_cierre.set_index('Date', inplace=True)
precios_cierre = precios_cierre.drop('RA.MX',axis=1)
precios_cierre = precios_cierre.drop('VOLARA.MX',axis=1)

Port_pasivo= data_files[fechas[0]]
Port_pasivo= Port_pasivo [['Ticker', 'Peso (%)']]
Port_pasivo = Port_pasivo [~Port_pasivo ['Ticker'].isin(['KOFL','BSMXB','NMKA.MX','KOFUBL.MX','MXN','USD' ])]
Port_pasivo.reset_index(inplace=True, drop=True)

prices_p= pd.DataFrame(precios_cierre.T[fechas[0]])
prices_p.reset_index(inplace=True)
prices_p= prices_p.rename(columns = { prices_p.columns[0]: 'Ticker', prices_p.columns[1]: 'Precios'}, inplace = False)

Port_pasivo = pd.merge(Port_pasivo, prices_p,on=['Ticker'])
Port_pasivo = Port_pasivo.sort_values('Ticker')

Port_pasivo['Titulos'] = np.floor((inv_i * Port_pasivo['Peso (%)']) / (Port_pasivo['Precios'] + (Port_pasivo['Precios'] * comission)))
Port_pasivo['Titulos Totales']=Port_pasivo['Titulos'].cumsum()
Port_pasivo['Capital'] = np.round(Port_pasivo['Titulos'] * (Port_pasivo['Precios'] + (Port_pasivo['Precios'] * comission)), 2)
Port_pasivo['Comisiones'] = np.round(Port_pasivo['Precios'] * comission * Port_pasivo['Titulos'], 2)
Port_pasivo['Comisiones Acomuladas']=Port_pasivo['Comisiones'].cumsum()

Port_pasivo=Port_pasivo.reset_index(drop=True)