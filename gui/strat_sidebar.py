import customtkinter as ctk
import logging


_log = logging.getLogger(__name__)
class Strat_Sidebar:
    """Builds Strategy sidebar

    Shows available strategies in strategies directory (set in config)

    ...

    Methods
    -------
    build_sidebar() - Builds sidebar UI
    algo_trading_button_color() - sets button color
    toggle_algo_trading() - Toggles algo trading
    """
    

    def __init__(self, master, strat_names, algo_trading_enabled: bool = False):
        self._strats = strat_names
        self.master = master
        self._algo_trading_enabled = algo_trading_enabled
    
        self.build_sidebar()

    def build_sidebar(self):
        """Builds sidebar UI
        """
        algo_button_status, algo_button_clr = self.algo_trading_button_color()
        
        header = ctk.CTkLabel(self.master, text = 'STRATEGIES', font = ctk.CTkFont(size = 14, weight = 'bold'))
        self.algo_trading_button = ctk.CTkButton(self.master, text = algo_button_status, 
                fg_color = algo_button_clr, hover_color = algo_button_clr, command = self.toggle_algo_trading)
        
        header.grid(row = 0, column = 0, columnspan = 2, padx = 30, pady = (20, 10))
        self.algo_trading_button.grid(row = 1, column = 0, columnspan = 2, padx = 30, pady = (10, 20))

        # build strategies list 
        for i, strat in enumerate(self._strats):
            strat_name = ctk.CTkLabel(self.master, text = strat.replace('.py',''))
            strat_name.grid(row = i + 2, column = 0, padx = 10, pady = (0, 10))

    @staticmethod
    def algo_trading_button_color(enabled: bool = False):
        """Toggles algo trading button color

        Parameters
        ----------
        enabled: bool
            Bool if algo trading is enabled/disabled
        
        Returns
        -------
        ret_str: str
            Text to display on algo trading button
        color: str
            Algo trading button color 
        """
        status = 'Enabled' if enabled else 'Disabled'
        color = 'green' if enabled else 'grey'
        ret_str = f'Algo Trading {status}'
        return ret_str, color
    

    def toggle_algo_trading(self):
        """Toggles algo trading
        """
        self._algo_trading_enabled = not self._algo_trading_enabled
        algo_status, algo_clr = self.algo_trading_button_color(self._algo_trading_enabled)
        self.algo_trading_button.configure(text = algo_status, fg_color = algo_clr, hover_color = algo_clr)
        
        enabled = 'Enabled' if self._algo_trading_enabled else 'Disabled'
        _log.info('ROOT: Algo Trading %s', enabled)
        # TODO: TOGGLE MT5 ALGO TRADING