from .base import Base
from threading import Thread
from datetime import datetime as dt, timezone as tz, timedelta 
import pause

import templates 

class Equities_Stat_Arb(Base):
    

    def __init__(self, symbol: str, timeframe: str, enabled: bool = False):
        super().__init__('Equities_Stat_Arb', timeframe, symbol, enabled)
    
    def loop(self):
        
        while self.enabled:
            self.log('RUNNING LOOP')

            next_interval, ts, server = self.get_next_interval()
            pause.until(ts)

            if self.exit_event.is_set():
                break 

    def start_strat(self):
        self.start_thread(self.loop)