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
    def __init__(self):
        self.trade_queue = [] # REMAINING SIGNALS
        self.trades_executed = [] # LIST OF POPPED TRADES
        self.next_batch = [] # NEXT BATCH OF TRADES
    
    def process_remaining_signals(self, remaining_signals):
        for r in remaining_signals:
            signal, symbol, trade_datetime = [r[i] for i in range(len(r))]
            trade_object = Queue_Object(signal = signal, symbol = symbol, trade_datetime = trade_datetime)
            self.add_to_queue(trade_object)

        return len(self.trade_queue)

    def signals_in_queue(self):
        return len(self.trade_queue)

    def add_to_queue(self, queue_object: Queue_Object):
        self.trade_queue.append(queue_object)

    def next_trade_in_queue(self):
        return self.trade_queue[0].trade_datetime

    
    def pop_trade(self):
        popped = self.trade_queue.pop(0)
        self.trades_executed.append(popped)
        return popped
    
    def next_signals(self):
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
        self.trade_queue.remove(trade_object)
        self.trades_executed.append(trade_object)

