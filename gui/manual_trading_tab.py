import customtkinter as ctk
import templates
import event

class Manual_Trading:
    def __init__(self, master):
        self.master = master
        self._pending_order_params = []
        self.build_manual_trading()

    def build_manual_trading(self):
        symbols_list = ['Symbols']
        option_menu_var = ctk.StringVar(value = 'Symbols')
        po_params = ['Price', 'Stop Loss', 'Take Profit', 'Volume']

        self.symbol_frame = ctk.CTkFrame(self.master)

        self.symbol_label = ctk.CTkLabel(self.symbol_frame, text = 'Symbol')
        self.symbols_dropdown = ctk.CTkOptionMenu(self.symbol_frame,
                    values = symbols_list, variable = option_menu_var)
        self.po_frame = ctk.CTkFrame(self.symbol_frame)
        self.po_header = ctk.CTkLabel(self.po_frame, text = 'PENDING ORDER')

        self.symbol_frame.pack(fill = 'x')
        self.symbol_frame.grid_columnconfigure((0, 1), weight = 1)
        self.symbol_frame.grid_rowconfigure((0, 1), weight = 1)
        self.symbol_label.grid(row = 0, column = 0, padx = 20, pady = (20, 10))
        self.symbols_dropdown.grid(row = 0, column = 1, padx = 20, pady = 20)
        self.po_frame.grid(row = 1, column = 0, padx = 10, pady = 10)
        self.po_frame.grid_rowconfigure(4, weight = 1)
        self.po_header.grid(row = 0, column = 0, columnspan = 2, padx = 20, pady = 10)

        # PRICE FIELDS

        for i, param in enumerate(po_params):
            self.po_label = ctk.CTkLabel(self.po_frame, text = param)
            self.po_field = ctk.CTkEntry(self.po_frame)

            self.po_label.grid(row = i + 1, column = 0, padx = 20, pady = 10)
            self.po_field.grid(row = i + 1, column = 1, padx = 20, pady = 10)

            self._pending_order_params.append((self.po_field))
        
        self.blim_button = ctk.CTkButton(self.po_frame, text ='Buy Limit', 
            command = lambda order_type = 'Buy Limit': self.send_pending_order(order_type))
        self.slim_button = ctk.CTkButton(self.po_frame, text = 'Sell Limit', 
            command = lambda order_type = 'Sell Limit' : self.send_pending_order(order_type))
        self.manual_trading_frame = ctk.CTkFrame(self.symbol_frame)
        self.manual_header = ctk.CTkLabel(self.manual_trading_frame, text = 'MARKET ORDER')

        self.blim_button.grid(row = 5, column = 1, padx = 20, pady = 10)
        self.slim_button.grid(row = 5, column = 0, padx = 20, pady = 10)		
        self.manual_trading_frame.grid(row = 1, column = 1, padx = 10, pady = 10)
        self.manual_trading_frame.grid_rowconfigure(4, weight = 1)
        self.manual_header.grid(row = 0, column = 0, columnspan = 2, padx = 20, pady = 10)

    # Buy Limit Sell Limit
    def send_pending_order(self, order_type: str):
        # Processing order form

        # Creates a list containing trade info to send to trade handler
        order_params = ['Manual', self.symbols_dropdown.get(), order_type, 'Pending', 'Pending']
        
        for order in self._pending_order_params:
            price = float(order.get()) if order.get() != '' else 0
            order_params.append(price)
        order_params.append(0.01)

        # Process order send
        pending_order = templates.Trade_Package(order_params) # repackaging
        print(order_params)

        '''
        Trade handler class, explore possibility of creating class instance 
        on init instead of internally.
        '''
        trade_handler = event.trade_handler

        # Sends packaged order parameters to MT5 event handler
        trade_handler.send_order(pending_order) 
                
    def update_symbols_dropdown(self, symbols):
        # FIX UPDATING 
        self.symbols_dropdown.configure(values = symbols)