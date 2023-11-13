import customtkinter as ctk


class Strats_Tab:
    """Builds Strategies Tab on main UI

    ...

    Methods
    -------
    build_ui() - builds main UI elements
    build_active_strats() - creates a list of active, usable strategies
    switch_strat() - enable/disable strategy thread
    add_strat() - adds strategy from directory to active strategies pool
    build_strat_row() - ui method for building a strat row
    remove_strat() - removes strategy from active pool
    """


    def __init__(self, master, init_strat):
        self.master = master
        self.init_strat = init_strat

        
        self.strat_names = self.init_strat.filenames
        self.strat_objects = self.init_strat.class_object

        self._active_strats_switch = []
        self.build_ui()
        self.build_active_strats()

    def build_ui(self):
        """Builds main UI elements
        """
        
        strat_names = list(self.strat_objects.keys())
        timeframes = ['m1','m5','m15','m30']
        strat_menu_var = ctk.StringVar(value = 'Strategies')
        tf_menu_var = ctk.StringVar(value = 'Timeframe')
        symbols_menu_var = ctk.StringVar(value = 'Symbols')

        self.strat_hdr_frame = ctk.CTkFrame(self.master)
        self.strat_hdr_frame.grid(row = 0, column = 0, padx = 20, pady = 10)

        master = self.strat_hdr_frame
        self.strats_dropdown = ctk.CTkOptionMenu(master,
            values = strat_names, variable = strat_menu_var)
        self.tf_dropdown = ctk.CTkOptionMenu(master,
            values = timeframes, variable = tf_menu_var, width = 120)
        self.target_symbol = ctk.CTkEntry(master, placeholder_text = 'Symbol', width = 100)
        self.volume_entry = ctk.CTkEntry(master, placeholder_text = 'Volume', width = 80)
        self.add_button = ctk.CTkButton(master, text = 'Confirm',
            command = self.add_strat, width = 70)

        
        self.strats_dropdown.grid(row = 0, column = 0, padx = 20, pady = 10)
        self.tf_dropdown.grid(row = 0, column = 1, padx = (0, 10), pady = 10)
        self.target_symbol.grid(row = 0, column = 2)
        self.volume_entry.grid(row = 0, column = 3, padx = 10)
        self.add_button.grid(row = 0, column = 4, padx = 10, pady = 10)

    def build_active_strats(self):
        """Creates a list of active, usable strategies
        """
        pady = (5, 0)
        labels = ['Strategy', 'Symbol', 'Timeframe', 'Volume', 'Toggle', '']

        self.scroll_frame = ctk.CTkScrollableFrame(self.master, width = 650, fg_color = 'transparent')
        self.scroll_frame.grid(row = 1, column = 0, columnspan = 3, padx = 10)
        self.scroll_frame.grid_columnconfigure(4, weight = 1)

        for j, label in enumerate(labels):
            self.header_label = ctk.CTkLabel(self.scroll_frame, text = label)
            self.header_label.grid(row = 0, column = j, padx = 30, pady = pady)


        ## BUILD HEADER
        for i, st in enumerate(self.init_strat._strategies_in_table):
            self.build_strat_row(st[0].name, st[0].timeframe, st[0].symbol, i)


    def switch_strat(self, index):
        """Enables/Disables strategy thread
        """
        strategy = self.init_strat._strategies_in_table[index]
        switch = self._active_strats_switch[index]
        self.init_strat.running_strategy(index, switch.get())
        self.init_strat._strategies_in_table[index][1] = switch.get()

    def add_strat(self):
        """Adds strategy in directory to active strategies trading pool
        """


        key = self.strats_dropdown.get() # name of the strategy
        obj = self.strat_objects[key] if key in list(self.strat_objects.keys()) else None

        try:
            if obj != None:
                strats_in_table = len(self.init_strat._strategies_in_table)
                timeframe = self.tf_dropdown.get()
                symbol = self.target_symbol.get()
                volume = float(self.volume_entry.get())

                self.init_strat.add_strat_to_table(obj, timeframe, symbol, volume, key)
                self.build_strat_row(key, timeframe, symbol, volume, strats_in_table)
            else:
                print(key)
        except: 
            print('except')
            return None
    def build_strat_row(self, strat_name, timeframe, symbol, volume, i):
        """UI Method for building a strat row
        """
        state = self.init_strat._strategies_in_table[i][1]
        pady = (5, 0)
        padx = (20, 0)
        self.st_label = ctk.CTkLabel(self.scroll_frame, text = strat_name)
        self.st_symbol = ctk.CTkLabel(self.scroll_frame, text = symbol)
        self.st_tf = ctk.CTkLabel(self.scroll_frame, text = timeframe)
        self.st_vol = ctk.CTkLabel(self.scroll_frame, text = volume)
        self.st_switch = ctk.CTkSwitch(self.scroll_frame, text = '',
            command = lambda index = i : self.switch_strat(index))
        self.st_cancel_button = ctk.CTkButton(self.scroll_frame, text = 'X',
            command = lambda index = i : self.remove_strat(index), width = 20, height = 20)

        self.st_label.grid(row = i + 1, column = 0, padx = padx, pady = pady)
        self.st_symbol.grid(row = i + 1, column = 1, padx = padx, pady = pady)
        self.st_tf.grid(row = i + 1, column = 2, padx = padx, pady = pady)
        self.st_vol.grid(row = i + 1, column = 3, padx = padx, pady = pady)
        self.st_switch.grid(row = i + 1, column = 4, padx = (40, 5), pady = pady)
        self.st_cancel_button.grid(row = i + 1, column = 5, padx = 0, pady = pady)


        if state == 1:
            self.st_switch.select()
        elif state == 0:
            self.st_switch.deselect()

        self._active_strats_switch.append(self.st_switch)

    def remove_strat(self, i):
        """Removes strategy from active pool
        """
        strat_to_remove = self.init_strat._strategies_in_table[i]
        switch_to_remove = self._active_strats_switch[i]

        if strat_to_remove[1] == 1:
            self.init_strat.running_strategy(i, 0)
        self.init_strat.remove_strat_from_table(strat_to_remove)
        self._active_strats_switch.remove(switch_to_remove)
        self.build_active_strats()