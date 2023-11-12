from .db_handler import DB_Handler
from .mt5 import MT5_Py
from .trade_handler import Trade_Handler
from .signals_handler import Signals_Handler


mt5_py = MT5_Py()
db = DB_Handler()
trade_handler = Trade_Handler()