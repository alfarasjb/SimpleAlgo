import pandas as pd 
import numpy as np 
from dependencies import Dependencies
from parse import Parse
from ma_query import MA_Query
import yfinance as yf
import datetime as dt
import os


directory = 'C:/Users/JB/AppData/Roaming/MetaQuotes/Terminal/Common/Files/Forecasts'
Symbols = ['EURUSD','AUDUSD','GBPUSD','USDCHF','USDCAD','USDJPY']
yf_syms = ['EURUSD=X','AUDUSD=X','GBPUSD=X', 'CHF=X','CAD=X','JPY=X']
TF = 'W'


def get_data(raw, yf_sym, path, local):
    raw.index = pd.to_datetime(raw.index)
    last_date = raw.index[-1]
    last_date

    start_date = last_date + pd.Timedelta(days = 1)
    yf_start_date = start_date + pd.Timedelta(weeks = 1) - pd.Timedelta(days = 1)
    yf_start_date

    print(f'Fetching latest data for {yf_sym} from Yahoo Finance...')
    yf_df = yf.download(yf_sym, start = yf_start_date, interval = '1wk')
    yf_df = yf_df.loc[:, ['Open','High', 'Low','Close']]
    yf_df = round(yf_df, 5)
    construct_df(raw, yf_df,path, local)

def construct_df(raw, yf_df, path, local):
    raw.index = pd.to_datetime(raw.index)
    yfdf_list = yf_df.index.astype('str').tolist()
    raw_index_list = raw.index.astype('str').tolist()
    datelist = [date in raw_index_list for date in yfdf_list]
    False in datelist 
    raw = pd.concat([raw, yf_df], axis = 0) if False in datelist else raw
    print('Building...')
    write_to_csv(raw, path, local)
    
def write_to_csv(raw, path, local):
    query = MA_Query(path)
    parsed_df = query.get_parsed_df(raw, 10)
    parsed_df.set_index('Date', inplace = True)
    parsed_df.index = pd.to_datetime(parsed_df.index)
    parsed_df = parsed_df.loc[:, ['Open','High', 'Low','Close', 'Forecast']]
    #vals = [parsed_df.index, parsed_df['Forecast']]
    #data.append(vals)
    parsed_df.to_csv(local)
    print(f'{local} has been updated.')

def run():
    for idx, Symbol in enumerate(Symbols):
        dep = Dependencies()
        git = dep.currencies(Symbol, TF)
        local = f'{directory}/{Symbol}_{TF}.csv'
        exists = os.path.exists(local)
        yf_sym = yf_syms[idx]

        df = pd.read_csv(local) if exists else pd.read_csv(git)

        parsed = df if exists else Parse(git).df_raw
        if 'Date' in df.columns:
            df.set_index('Date', inplace = True)
        raw = parsed
        raw.index = pd.to_datetime(raw.index)
        raw.dropna(inplace = True)
        today = dt.date.today()
        recorded = raw.index[-1].date()
        diff = today - recorded
        if diff >= pd.Timedelta(days = 7):
            path = local if exists else git
            # NEW WEEK, EXECUTE ALL, FETCH DATA
            get_data(raw, yf_sym, path, local)
            print (f'Updating {Symbol}_{TF}.csv')
        else:
            print(f'{Symbol}_{TF}.csv is up to date')

run()
'''
try: 
    while True:
        if __name__ == "__main__":
            run()
        
            next = input("---")
            print('\n\n')
except KeyboardInterrupt:
    pass

'''