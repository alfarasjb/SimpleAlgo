import signals
import gui

class Signals_Handler:
    """
    Trigger point from root.py
    """

    def __init__(self):
        self.symbols_list = ['EURUSD','AUDUSD','GBPUSD','USDCHF','USDCAD','USDJPY'] # Uniform symbols order
        self.fcast = signals.Forecast(symbols = self.symbols_list)
        self.generic = signals.Signals(symbols = self.symbols_list)
        self.signals_objects = [] # contains weekly and daily signals

    """
    fetch from ma query
    fetch from generic
    ui triggers go here
    """
    print('Created instance of signals handler')

    def get_patterns(self):
        # check if mt5 is connected
        # run this once mt5 is connected
        # returns patterns
        pass 

    def get_weekly(self):
        # run on startup
        data = self.fcast.read_data()
        # receives a list of signals objects
        # create signals row object from here
        for d in data:
            sig = Signals_Row_Object()
        return data

    def update_weekly(self):
        # call this on launch mt5
        self.fcast.update()

    def create_signals_tab(self, master):
        self.signals_tab = gui.Signals_Tab()

class Signals_Row_Object:
    # Pass this object to signals tab
    def __init__(self):
        self.symbol = None
        self.date = None 
        self.signal = None
        self.pattern = None 
        self.bias = None 
        self.open = None 
        self.last_updated = None