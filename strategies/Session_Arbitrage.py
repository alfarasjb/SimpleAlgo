from .base import Base
from threading import Thread
from datetime import datetime as dt, timezone as tz, timedelta 
import pytz
import pause
import templates
import MetaTrader5 as mt5
import os
import pandas as pd
from .session_arb_ref import Queue_Handler

'''
OBJECTIVES:
1. read all csvs in directory, to combine into 1 dataframe, as the master list


DRAFT 
'''

class Session_Arbitrage(Base):

    def __init__(self, symbol: str, timeframe: str, enabled: bool = False, volume: float = 0.01):
        super().__init__('Session_Arbitrage', timeframe, symbol, enabled)
        self.volume = volume
        #self.set_magic()
        self.orders = []

        self.magic = 253253 # PERMANENTLY RESERVED MAGIC NUMBER

        self.symbols_in_pool = []
        #self.symbols = ['AUDUSD','EURUSD','GBPUSD','USDJPY','USDCHF','USDCAD']
        self.symbols = ['GBPUSD','AUDUSD']
        self.comment = f'S_Arb_m5'

        self.trade_queue = []

        
        self.trade_handler.register_magic(self.name, self.magic)
        self.queue_handler = Queue_Handler() # instance of queue handler
        self.combined_dfs = None
        self.scan()

    def scan(self):
        directory = 'strategies/session_arb_ref/pickle'
        export = 'strategies/session_arb_ref/db'
        dir_files = []
        pickle_df = pd.DataFrame()
        dfs = []
        [dir_files.append(d) for d in os.listdir(directory) if d.endswith('.pkl') and 'signal' not in d]
        for d in dir_files:
            s = d.split('_') # s[0] is symbol name
            if not s[1].startswith(self.timeframe):
                continue
            data = pd.read_pickle(f'{directory}/{d}')
            dfs.append(data)
        
        self.log('Files in directory')
        #self.log(dir_files)
        print(dir_files)
        self.combined_dfs = pd.concat(dfs).sort_values(by = 'time', ascending = True).reset_index(drop = True)
        self.combined_dfs['datetime'] = pd.to_datetime(self.combined_dfs['hour'].astype('str').str.zfill(2) + ':' + self.combined_dfs['min'].astype('str').str.zfill(2))
        
        pickle_file_name = f'signal_{self.timeframe}.pkl'

        signal_files = []
        [signal_files.append(s) for s in os.listdir(export) if s.endswith('pkl') and s.split('_')[1].startswith(self.timeframe)]

        print(signal_files)
        if len(signal_files) == 1:
            main_pickle_file = signal_files[0]
            pickle_df = pd.read_pickle(f'{export}/{main_pickle_file}')
        
        merged = pd.concat([pickle_df, self.combined_dfs]).drop_duplicates().sort_values(by = 'time', ascending = True).reset_index(drop = True)

        print('MERGED')
        print(merged)

        merged.to_pickle(f'{export}/{pickle_file_name}')
        self.signals_main = merged.copy()
        
#        self.combined_dfs.to_pickle(f'{export}/signal_{self.timeframe}.pkl', index = False)
        
    

    def set_magic(self):
        if self.magic != 0:
            return self.magic 
        
        self.magic = self.trade_handler.register_magic(self.name)
        return self.magic 
    
    def parse_data(self, kind = 'loop'):
        # knid is loop or init

        # server time 
        last_server_time = self.get_last_server_timestamp()

        if kind == 'loop':
            self.log('RUNNING LOOP')

        elif kind == 'init':
            self.log('INITIALIZING LOOP')

            # remaining signals in dataframe
            remaining_signals = self.signals_main.loc[self.signals_main['datetime'] > last_server_time][['signal','symbol','datetime']].values.tolist()

            # creates list of queue object from df
            added_to_queue = self.queue_handler.process_remaining_signals(remaining_signals)
            queue_append_message = f'{added_to_queue} Trades Added to Queue'
            self.log(queue_append_message) 

        # next trade in queue (datetime)
        next_trade_interval = self.queue_handler.next_trade_in_queue() # used to get the next date
        trade_interval_message = f'Next Trade in Queue: {next_trade_interval}'
        self.log(trade_interval_message)

        # next batch of trades as queue object, and number of trades in next batch
        next_batch, trades_in_batch = self.queue_handler.next_signals()
        batch_message = f'{trades_in_batch} Trades in Next Batch'
        self.log(batch_message)

        signals_in_queue = self.queue_handler.signals_in_queue()
        queue_message = f'{signals_in_queue} Trades Remaining in Queue'
        self.log(queue_message)

        next_interval, ts, server_time = self.get_next_interval()

        for b in next_batch: 
            message = f'NEXT BATCH | Symbol: {b.symbol}, Signal: {b.signal}, Trade Datetime: {b.trade_datetime}'
            self.log(message)

        return next_trade_interval, next_batch, ts

    def loop(self):
        '''
        On init, get next trade time, get next batch, get number of trades in next batch
        
        '''
        #print(next_sig)
        #server_message = f'NEXT SERVER TIME: {server_time}'
        #trade_message = f'NEXT TRADE TIME: {next_trade}'

        next_trade_interval, next_batch, ts = self.parse_data('init')

        while self.enabled: 
            if not self.mt5.is_connected():
                self.log('CONNECTION ERROR. NOT CONNECTED TO MT5')

            pause.until(ts)
            ## CHECK IF THREAD IS STILL ACTIVE
            if self.exit_event.is_set():
                break
            
            close_all_thread = Thread(target = self.close_all_orders)
            close_all_thread.start()

            
            try:
                last_server_time = self.get_last_server_timestamp()
                message = f'LAST SERVER TIME {last_server_time}'
                self.log(message)
                trade_dt_message = f'TRADE DATETIME {next_trade_interval}'
                self.log(trade_dt_message)

                if (last_server_time == next_trade_interval):
                #if (last_server_time == next_trade):
                #if (last_server_time.hour == next_trade_hour) and (last_server_time.minute == next_trade_min):
                    # execute trade
                    #signals_to_process = len(next_sig)
                    print('MATCH')
                    for s in next_batch:
                        print(s.symbol)
                        # s is a queue object
                        t = Thread(target = self.process, args = [s])
                        #t = Thread(target = self.process, args = [next_sig.iloc[s]])
                        #t = Thread(target = self.process, args = [])
                        t.start()
                        print('PROCESSING')
                        s.print_info()

                    
            except ConnectionError:
                self.log('CONNECTION ERROR. NOT CONNECTED TO MT5')
            
            # next trade interval: used as reference for trade execution
            # next batch trades to execute in next cycle
            next_trade_interval, next_batch, ts = self.parse_data('loop')

            if last_server_time > next_trade_interval:
                    self.log('Updating Queue')
                    self.queue_handler.update_queue(last_server_time)

    

    def close_all_orders(self):
        self.log('Close All By Magic')
        close_thread = Thread(target = self.trade_handler.close_all_by_magic, args = [self.magic])
        close_thread.start()

    def start_strat(self):
        self.start_thread(self.loop)

    def process(self, trade_object):
        # split the received dataframe into individual threads
        signal = trade_object.signal
        symbol = trade_object.symbol
        #signal = df_row['signal']
        #symbol = df_row['symbol']
        comment = f'S_Arb_m5'

        order_type = 'Market Buy' if signal == 1 else 'Market Sell'
        message = f'{symbol} | {order_type}'
        self.log(message)

        
        order_package = templates.Trade_Package(
            src = self.name,
            symbol = symbol,
            price = 0,
            sl = 0, 
            tp = 0,
            comment = comment,
            order_type = order_type,
            volume = self.volume,
            magic = self.magic,
            deal = 'Market')

       
        self.trade_handler.send_order(order_package)
        self.orders.append(order_package)
        self.symbols_in_pool.append(symbol)

        self.queue_handler.remove_from_queue(trade_object)
