
import customtkinter as ctk
from itertools import product

class Signals_Tab:
    """Buils Signals Tab on main UI

    ...

    Methods
    -------
    build_signals_row() - builds a signal row for individual symbols
    refresh() - recalculates signals
    empty() - returns if list is empty
    """
    def __init__(self, master, data = None):
        self.master = master # tabview name 
        self.data = data # returned data from fcast

        self._signals_elements = []
        self._patterns_elements = []

        self.signals_frame = ctk.CTkFrame(master)
        self.signals_frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

        # header 
        self.header_frame = ctk.CTkFrame(self.signals_frame)
        self.symbol_header = ctk.CTkLabel(self.header_frame, text = 'Symbol')
        self.date_header = ctk.CTkLabel(self.header_frame, text = 'Date')
        self.signal_header = ctk.CTkLabel(self.header_frame, text = 'Weekly')
        self.pattern_header = ctk.CTkLabel(self.header_frame, text = 'Pattern')
        self.bias_header = ctk.CTkLabel(self.header_frame, text = 'Bias')
        self.open_header = ctk.CTkLabel(self.header_frame, text = 'Open')
        self.last_updated_header = ctk.CTkLabel(self.header_frame, text = 'Last Updated')

        self.header_frame.place(relx = 0.02, rely = 0.02, relwidth = 0.96, relheight = 0.08)
        self.symbol_header.place(x = 30, rely = 0.05)
        self.date_header.place(x = 115, rely = 0.05)
        self.signal_header.place(x = 200, rely = 0.05)
        self.pattern_header.place(x = 285, rely = 0.05)
        self.bias_header.place(x = 370, rely = 0.05)
        self.open_header.place(x = 435, rely = 0.05)
        self.last_updated_header.place(x = 530, rely = 0.05)

        self.content_frame = ctk.CTkFrame(self.signals_frame)
        self.content_frame.place(relx = 0.02, rely = 0.15, relwidth = 0.96, relheight = 0.8)

        #self.build_signals_row()
        #self.build_patterns_row()

    def build_signals_row(self):
        """Builds a signal row for individual symbols
        """
        master = self.content_frame 
        for i, d in enumerate(self.data):
            y = (i * 30) + 10
            self.symbol_row = ctk.CTkLabel(master, text = d.symbol)
            self.date_row = ctk.CTkLabel(master, text = d.date)
            self.signal_row = ctk.CTkLabel(master, text = d.signal)
            self.pattern_row = ctk.CTkLabel(master, text = d.pattern)
            self.bias_row = ctk.CTkLabel(master, text = d.bias)
            self.open_row = ctk.CTkLabel(master, text = d.open)
            self.last_updated_row = ctk.CTkLabel(master, text = d.last_updated)


            self.symbol_row.place(x = 30, y = y)
            self.date_row.place(x = 100, y = y)
            self.signal_row.place(x = 200, y = y)
            self.pattern_row.place(x = 285, y = y)
            self.bias_row.place(x = 370, y = y)
            self.open_row.place(x = 430, y = y)
            self.last_updated_row.place(x = 520, y = y)
            

            self._signals_elements.append([self.symbol_row, self.date_row, self.signal_row, 
                self.pattern_row, self.bias_row, self.open_row, self.last_updated_row])
    
    def empty(self):
        """Checks if list is empty

        Returns
        -------
        bool - True if list is not empty
        """
        return len(self._signals_elements) == 0
    

    def delete_all_rows(self):
        for e in self._signals_elements:
            for i in e:
                i.destroy()