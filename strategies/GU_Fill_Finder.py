from .base import Base
from threading import Thread
from datetime import datetime as dt, timezone as tz, timedelta 
import pytz
import pause 
import templates
import MetaTrader5 as mt5


class GU_Fill_Finder(Base):


    def __init__(self, symbol:str, timeframe: str, enabled: bool = False, volume: float = 0.01):
        super().__init__('GU_Fill_Finder', timeframe, symbol, enabled)
        self.volume = volume
        self.set_magic()
        self.orders = []
        

    def set_magic(self):
        """
        Sets Magic Number

        Returns
        -------
        magic: int
            Magic Number
        
        """
        if self.magic != 0:
            return self.magic 
        
        self.magic = self.trade_handler.register_magic(self.name)
        return self.magic



    def loop(self):
        """
        Main Algo Loop
        """
        
        while self.enabled:

            self.log('RUNNING LOOP')
            next_interval, ts, server = self.get_next_interval()
            pause.until(ts)

            
            # end thread if disabled
            if self.exit_event.is_set():
                break 

            # not entry window
            # continue
            if not self.entry_window_open():
                self.log('ENTRY WINDOW CLOSED')
                continue

            # order already exists
            # break
            if self.order_exists() and len(self.orders) != 0:
                self.log('ORDER ALREADY EXISTS')
                break

            # fetch data, process
            # if not fill
            # break 
            is_fill, bias = self.pattern()
            if not is_fill: 
                self.log('INVALID PATTERN')
                break 

            # fill direction follows weekly: open < ma, short, vice versa
            # break
            print('VALID PATTERN | BIAS: ', bias)
            # get h1 data 
            price = self.get_price(bias)
            self.process(bias, price)


    def start_strat(self):
        """
        Starts algo thread
        """
        self.start_thread(self.loop)


    def process(self, bias, limit_price):
        """
        Main algo logic and decision-making

        Parameters
        ----------
        bias: str
            Long or Short: decides order type

        limit_price: float
            Buy Limit / Sell Limit price
        """
        
        # Declaration
        comment = f'{self.name}_{self.timeframe}'
        order_type = 'Buy Limit' if bias == 'Long' else 'Sell Limit'

        self.log(bias.upper())
        order_package = templates.Trade_Package(
            src = self.name,
            symbol = self.symbol,
            price = limit_price,
            sl = 0,
            tp = 0,
            comment = comment,
            order_type = order_type,
            volume = self.volume,
            magic = int(self.set_magic()),
            deal = 'Pending'
        )
        self.trade_handler.send_order(order_package)
        self.orders.append(order_package)
    

    def entry_window_open(self):
        """
        Checks if entry window is open.
        Entry Window: 16:00 - 18:00 Server Time
        
        Returns
        -------
        bool
            True - Entry Window is open
            False - Entry Window is closed
        """
        data = self.request_data(tf = 'h4', request_type = 'pos', start_index = 0, num_bars = 1)
        hr = data[0][0].hour
        minute = data[0][0].minute

        ### SESSION (Server Time) ###
        start = 16
        end = 18
        
        if (hr < start) or (hr > end):
            return False 
        return True
    

    def order_exists(self):
        """
        Checks if order exists by iterating through all open positions and orders, 
        and verifying by magic number.

        Returns
        -------
        bool
            True - Orders exists
            False - No orders executed
        """

        orders_list = mt5.orders_get()
        positions_list = mt5.positions_get()
    
        for order in orders_list:
            if order.magic == self.magic:
                return True
        for position in positions_list:
            if position.magic == self.magic:
                return True 
        
        return False
        

    def get_price(self, bias):
        """
        Main logic for deciding on entry price. 
        Compares High vs Open for Shorts, and Low vs Open for Longs

        Returns
        -------
        rounded: float
            Price rounded to nearest 5 pips
        """

        today = dt.today()
        timezone = pytz.timezone('Etc/UTC')

        # h4 last open
        h4_data = self.request_data(tf = 'h4', request_type = 'pos', start_index = 1, num_bars = 1)
        h4_o = h4_data[0][1]

        start_hour = 15
        end_hour = 16

        start_datetime = dt(today.year, today.month, today.day, start_hour, 0, 0, tzinfo = timezone)
        end_datetime = dt(today.year, today.month, today.day, end_hour, 0, 0, tzinfo = timezone)
        
        # ny hl
        data = self.request_data(tf = 'h1', request_type = 'rates', start_date = start_datetime, end_date = start_datetime)
        # time, o, h, l, c 
        price = data[0][2] if bias == 'Short' else data[0][3]
        references = [price, h4_o]

        reference_price = min(references) if bias == 'Long' else max(references)
        
        # parsing price to nearest 5 pips
        rounded = round(reference_price, 4)
        factor = 10000
        if bias == 'Long' and (rounded > reference_price):
            rounded -= (5 * factor)
        
        elif bias == 'Short' and (reference_price > rounded):
            rounded += (5 * factor)
        
        print('Rounded Price: ', rounded)
        return rounded


    def pattern(self):
        """
        Logic for parsing pattern. Algo only chooses Fills

        Returns
        -------
        bool
            True - Valid Fill

        bias
            Long - last h4 is bullish
            Short - last h4 is bearish
        """
        data = self.request_data(tf = 'h4',
                        request_type = 'pos', start_index = 1, num_bars = 4)
        directions = []
        for ohlc in data:
            o, h, l, c = [ohlc[i] for i in range(1, 5)]
            direction = 1 if c > o else 0 
            directions.append(direction)

        d_0, d_4, d_8, d_12 = [directions[i] for i in range(4)]
        h_0, h_4, h_8, h_12 = [data[i][2] for i in range(4)]
        l_0, l_4, l_8, l_12 = [data[i][3] for i in range(4)]
        o_0, o_4, o_8, o_12 = [data[i][1] for i in range(4)]
        c_0, c_4, c_8, c_12 = [data[i][4] for i in range(4)]
        t_0, t_4, t_8, t_12 = [data[i][0] for i in range(4)]

        bias = 'Long' if d_12 == 1 else 'Short'

        if ((d_8 == 1 and d_12 == 0 and l_12 > o_0)) or \
            ((d_8 == 0 and d_12 == 1 and h_12 < o_0)):
            
            return True, bias
        
        return False, bias