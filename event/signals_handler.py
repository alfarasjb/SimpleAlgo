import signals
import gui
import event

class Signals_Handler:
    """
    Trigger point from root.py

    ...
    Methods
    -------
    update_signals() - updates signals and patterns
    create_signals_tab() - draws UI 
    """

    def __init__(self):

        self.symbols_list = ['EURUSD','AUDUSD','GBPUSD','USDCHF','USDCAD','USDJPY'] # Uniform symbols order
        self.fcast = signals.Forecast(symbols = self.symbols_list)
        self.generic = signals.Signals(symbols = self.symbols_list)
        self.signals_objects = [] # contains weekly and daily signals
        self.signals_elements = []
        self.signals_tab = None

        self.patterns = []
        self.signals_objects = []
        self.signals = []
       
    def update_signals(self):

        self.patterns.clear()
        self.signals.clear()
        self.signals_objects.clear()

        if event.mt5_py.is_connected():
            self.fcast.update() # updates weekly forecast
            self.patterns = self.generic.get_data() # returns list of pattern objects 
        

        ## FETCH CSV
        if len(self.signals) == 0:
            self.signals = self.fcast.read_data() # returns list of signals objects
        
        [self.patterns.append(None) for _ in self.signals if len(self.patterns) != len(self.signals)]

        for s, p in zip(self.signals, self.patterns):
            sig_row_obj = Signals_Row_Object(
                symbol = s.symbol,
                date = s.date,
                signal = s.signal,
                pattern = p.pattern if p is not None else None,
                bias = p.bias if p is not None else None,
                open = p.open if p is not None else None,
                last_updated = p.last_updated if p is not None else None
            )
            
            self.signals_objects.append(sig_row_obj)
        
    def create_signals_tab(self, master):

        if len(self.signals_elements) != 0 and self.signals_tab is not None:
            # delete all elements
            self.signals_tab.delete_all_rows()
        self.signals_tab = gui.Signals_Tab(master, self.signals_objects)
        self.signals_tab.build_signals_row()
        self.signals_elements = self.signals_tab._signals_elements


    def get_symbol_data(self, sym):
        # use this for gu fill finder
        for o in self.signals_objects:
            if o.symbol != sym:
                continue 
            return o 


class Signals_Row_Object:


    def __init__(self, symbol = None, date = None, signal = None, 
    pattern = None, bias = None, open = None, last_updated = None):
        
        self.symbol = symbol
        self.date = date
        self.signal = signal 
        self.pattern = pattern 
        self.bias = bias 
        self.open = open 
        self.last_updated = last_updated