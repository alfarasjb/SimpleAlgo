'''
TODOS/NOTES

- calculate MA/pivot internally 


INDICATORS: 
- ma
- pivot


METHODS:
request data ->  
get signal -> returns long or short or neutral for the week 

MISC:
also show last signal date
store to sql or csv? 
'''

from event.mt5 import MT5_Py
import numpy as np
import pandas as pd
from datetime import datetime as dt
from signals.utilities.ma_query import MA_Query
import logging 

_log = logging.getLogger(__name__)

class Forecast:
    
    def __init__(self):
        self.mt5_py = MT5_Py()
        
        self._samples = 10
        self._signals = []

        self._symbols = ['EURUSD','AUDUSD','GBPUSD','USDCHF','USDCAD','USDJPY']

    def update(self):
        _log.info('Updating Signals')
        for sym in self._symbols:
            local = f'signals/forecasts/{sym}_W.csv'
            df = pd.read_csv(local) 

            if 'Date' in df.columns:
                df.set_index('Date', inplace = True)

            df.index = pd.to_datetime(df.index)
            df.dropna(inplace = True)
            today = dt.today().date()
            recorded = df.index[-1].date()
            diff = today - recorded 
            if diff >= pd.Timedelta(days = 7):
                self.get_data(df, local, sym)


    def get_data(self, df: pd.DataFrame, path:str, symbol:str):
        last_date = df.index[-1]
        start_date = (last_date + pd.Timedelta(days = 1)).to_pydatetime()

        fetch_start_date = start_date + pd.Timedelta(weeks = 1) - pd.Timedelta(days = 1)

        if self.mt5_py.check_connection_status() == 'Not Connected':
            self.mt5_py.launch_mt5()
        data = self.mt5_py.request_price_data(timeframe = 'w1', symbol = symbol,
                    request_type = 'rates', start_date = start_date, end_date = dt.today())

        columns = ['Date', 'Open', 'High', 'Low', 'Close']
        rx_df = pd.DataFrame(data = data, columns = columns)
        rx_df.set_index('Date', inplace = True)
        raw = pd.concat([df, rx_df], axis = 0)
        query = MA_Query()
        parsed_df = query.get_parsed_df(raw, 10)
        parsed_df.set_index('Date', inplace = True)
        parsed_df.index = pd.to_datetime(parsed_df.index)
        parsed_df = parsed_df.loc[:, ['Open','High','Low','Close','Forecast']]
        
        parsed_df.to_csv(path)
        _log.info(f'{path} has been updated.')
    
    def read_data(self):
        fcast = {
            1 : 'Long',
            0 : 'Neutral',
            -1 : 'Short'
        }
        for sym in self._symbols:
            df = pd.read_csv(f'signals/forecasts/{sym}_W.csv')
            last_signal = df.iloc[-1]
            sig = Signal(sym,last_signal.Date, fcast[last_signal.Forecast])

            self._signals.append(sig)
        return self._signals
        

class Signal:
    def __init__(self, symbol:str, date: dt, signal:str):
        self.symbol = symbol 
        self.date = date 
        self.signal = signal 

        #print('SYMBOL: ', self.symbol, ' DATE: ',self.date, ' SIGNAL: ', self.signal)

