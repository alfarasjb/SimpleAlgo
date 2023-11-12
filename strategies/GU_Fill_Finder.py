from .base import Base
from threading import Thread
from datetime import datetime as dt, timezone as tz, timedelta 
import pause 

import templates

class GU_Fill_Finder(Base):

    def __init__(self, symbol:str, timeframe: str, enabled: bool = False, volume: float = 0.01):
        super().__init__('GU_Fill_Finder', timeframe, symbol, enabled)
        self.volume = volume

    def loop(self):
        """Main Algo Loop
        
        """
        
        while self.enabled:
            self.log('RUNNING LOOP')
            break

    def start_strat(self):
        """Starts algo thread
        """
        self.start_thread(self.loop)

    def process(self, rcv_data):
        """Main algo logic and decision-making

        Parameters
        ----------
        rcv_data: vector
            data to process and trade reference
        """
        raise NotImplementedError