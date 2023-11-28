from datetime import datetime as dt




class Queue_Object:
    # Queue object for session arbitrade

    def __init__(self, signal: int, symbol: str, trade_datetime: dt):
        self.signal = signal 
        self.symbol = symbol 
        self.trade_datetime = trade_datetime
        
    def print_info(self):
        print('Symbol: ', self.symbol)
        print('Signal: ', self.signal)
        print('Trade Datetime: ', self.trade_datetime)





class Queue_Handler:
    """
    Class for handling the trade queue. Holds all remaining trades, next batch, and executed trades. 

    Parameters
    ----------
    trade_queue: list
        Remaining trades to execute

    trades_executed: list
        Executed trades by this instance

    next_batch: list
        List of trades to simultaneously execute at the next time interval.


    Methods
    -------
    process_remaining_signals
        Takes a dataframe slice that contains trades to be executed

    signals_in_queue
        Returns remaining number of trades in the trade queue

    add_to_queue
        Takes a queue object to append to the trade queue

    next_trade_in_queue
        Returns datetime of the next trade in queue
    
    update_queue
        Updates queue in case a trade is missed or not executed

    pop_trade
        Pops trade from queue

    next_signals
        Creates a list of the next batch of trades to be executed 

    remove_from_queue
        Removes specific trade from queue and appends to executed trades
        
    """
    def __init__(self):
        self.trade_queue = [] # REMAINING SIGNALS
        self.trades_executed = [] # LIST OF POPPED TRADES
        self.next_batch = [] # NEXT BATCH OF TRADES
    

    def process_remaining_signals(self, remaining_signals:list):
        """
        Takes a dataframe slice that contains trades to be executed in the form of a vector. 

        Transforms the received list, into a queue, of QueueObject

        Parameters
        ----------
        remaining_signals: list
            List of trades to be executed

        Returns
        -------
        trade queue size: int
            Returns the number of trades in the queue
        """
        for r in remaining_signals:
            signal, symbol, trade_datetime = [r[i] for i in range(len(r))]
            trade_object = Queue_Object(signal = signal, symbol = symbol, trade_datetime = trade_datetime)
            self.add_to_queue(trade_object)

        return len(self.trade_queue)

    def signals_in_queue(self):
        """
        trade queue size: int  
            Returns the number of trades in the queue
        """
        return len(self.trade_queue)

    def add_to_queue(self, queue_object: Queue_Object):
        """
        Takes a queue object to append to the trade queue list 

        Parameters
        ----------
        queue_object: Queue_Object
            adds a trade object to the trade queue
        """
        self.trade_queue.append(queue_object)

    def next_trade_in_queue(self):
        """
        Returns the datetime of the next trade in queue. 

        Returns
        -------
        trade queue datetime: datetime
            Datetime of next trade in the queue
        """
        return self.trade_queue[0].trade_datetime

    def update_queue(self, last_server_time):
        """
        Updates queue in case a trade is missed / not executed. 

        Parameters
        ----------
        last_server_time: datetime
            Receives last server time and checks the queue if the first trade in the queue is missed. 
            
            If the trade is missed, the queue is updated.
        """
        for t in self.trade_queue:
            if t.trade_datetime > last_server_time:
                break
            self.trade_queue.remove(t)

    def pop_trade(self):
        """
        Pops trade from trade queue

        Returns
        -------
        popped: QueueObject
            Trade removed from queue
        """
        popped = self.trade_queue.pop(0)
        self.trades_executed.append(popped)
        return popped
    
    def next_signals(self):
        """
        Creates a list of the next batch of trades to be executed. 

        Used for executing multiple trades in 1 time interval. 

        Returns
        -------
        next_batch: list
            List of the next batch of trades to execute

        size: int
            Number of trades to execute
        """
        self.next_batch.clear()
        next_trade_time = self.trade_queue[0].trade_datetime
        
        for t in self.trade_queue:
            # time consuming since it iterates through all signals
            if t.trade_datetime != next_trade_time:
                continue
            self.next_batch.append(t)
        #[n.print_info() for n in self.next_batch]
        return self.next_batch, len(self.next_batch)
    
    def remove_from_queue(self, trade_object):
        """
        Removes specific trade object from queue, and appends to executed trades list.

        Parameters
        ----------
        trade_object: QueueObject
            Trade to remove from queue
        """
        self.trade_queue.remove(trade_object)
        self.trades_executed.append(trade_object)

