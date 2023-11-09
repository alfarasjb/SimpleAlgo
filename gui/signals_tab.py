
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
    def __init__(self, master, data):
        self.master = master # tabview name 
        self.data = data # returned data from fcast

        self._signals_elements = []

        self.signals_frame = ctk.CTkFrame(master)
        self.signals_frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

        # header 
        self.header_frame = ctk.CTkFrame(self.signals_frame)
        self.symbol_header = ctk.CTkLabel(self.header_frame, text = 'Symbol')
        self.date_header = ctk.CTkLabel(self.header_frame, text = 'Date')
        self.signal_header = ctk.CTkLabel(self.header_frame, text = 'Signal')
        self.refresh_button_header = ctk.CTkButton(self.header_frame, text = 'Refresh', command = self.refresh)
        
        self.header_frame.place(relx = 0.02, rely = 0.02, relwidth = 0.96, relheight = 0.08)
        self.symbol_header.place(x = 30, rely = 0.05)
        self.date_header.place(x = 190, rely = 0.05)
        self.signal_header.place(x = 330, rely = 0.05)
        self.refresh_button_header.place(x = 480, rely = 0.05)

        self.content_frame = ctk.CTkFrame(self.signals_frame)
        self.content_frame.place(relx = 0.02, rely = 0.15, relwidth = 0.96, relheight = 0.8)

        self.build_signals_row()

    def build_signals_row(self):
        """Builds a signal row for individual symbols
        """
        master = self.content_frame 
        for i, d in enumerate(self.data):
            y = (i * 30) + 10
            self.symbol_row = ctk.CTkLabel(master, text = d.symbol)
            self.date_row = ctk.CTkLabel(master, text = d.date)
            self.signal_row = ctk.CTkLabel(master, text = d.signal)
            
            self.symbol_row.place(x = 30, y = y)
            self.date_row.place(x = 180, y = y)
            self.signal_row.place(x = 330, y = y)

            self._signals_elements.append([self.symbol_row, self.date_row, self.signal_row])
    
    def refresh(self):
        """Recalculates signals
        """
        raise NotImplementedError


    def empty(self):
        """Checks if list is empty

        Returns
        -------
        bool - True if list is not empty
        """
        return len(self._signals_elements) == 0