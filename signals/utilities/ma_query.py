import pandas as pd
import numpy as np 
import pandas_ta as ta

class MA_Query():
    
    def __init__(self, path='', maType = 'sma', useMA = True, usePivot = True, useDelta = True, useOpen = True):
        self = self
        self.path = path
        self.lastElement = pd.DataFrame()
        self.maType = maType
        self.useMA = useMA
        self.usePivot = usePivot
        self.useDelta = useDelta
        self.useOpen = useOpen
        
     
        self.df_parsed = pd.DataFrame()
        self.acc_df = pd.DataFrame() # Acc table relative to different MA Periods
        self.df_signals = pd.DataFrame()

        #Attrib
        self.best_acc = 0;
        self.best_prd = 0;
    
    def get_parsed_df(self, df, period):
        self.df = df
        self.period = period
        df_parsed = df.loc[:, ["Open","High","Low","Close"]]
        ma_string = f"MA Length - {period}"
        open = df_parsed['Open']
        close = df_parsed['Close']
        high = df_parsed["High"]
        low = df_parsed["Low"]
        
        pivot = (high + low + close) / 3
       
        # SETTING PRICE REFERENCES (WK Pivot, Candle Direction, Moving Average)
        
        '''   
        ## TEST CASE: USING FORECAST AS ACTUAL [1]

        
        '''
        # INDICATORS #
        if self.maType == 'sma':
            df_parsed['Close_SMA'] = ta.sma(close, length = period)
        elif self.maType == 'ema':
            df_parsed['Close_SMA'] = ta.ema(close, length = period)
        df_parsed['Close_EMA'] = ta.ema(close, length = period)
        df_parsed['Close_Pivot'] = pivot
        
        close_sma = df_parsed['Close_SMA']
        close_ema = df_parsed['Close_EMA']
        close_pivot = df_parsed['Close_Pivot']
        
        df_parsed['Ref_SMA'] = close_sma.shift(periods = 1) # sma[0] on mql4
        df_parsed['Ref_EMA'] = close_ema.shift(periods = 1)
        df_parsed['Ref_Pivot'] = close_pivot.shift(periods = 1) #use hlc[1]
        
        ref_sma = df_parsed['Ref_SMA']
        ref_ema = df_parsed['Ref_EMA']
        ref_pivot = df_parsed['Ref_Pivot']
        
        df_parsed['Prev_SMA'] = close_sma.shift(periods = 2) # sma[1]
        df_parsed['Prev_EMA'] = close_ema.shift(periods = 2)
        df_parsed['Prev_Pivot'] = close_pivot.shift(periods = 2) #use hlc[2]
        prev_sma = df_parsed['Prev_SMA']
        prev_ema = df_parsed['Prev_EMA']
        prev_pivot = df_parsed['Prev_Pivot']
        
        df_parsed['Prev_Close'] = close.shift(periods = 1)
        df_parsed['Prev_Open'] = open.shift(periods = 1)     
        prev_close = df_parsed['Prev_Close']
        prev_open = df_parsed['Prev_Open']
        
        ## DIRECTIONS ## 
        # CONDITION 1 #
        df_parsed['Candle_Dir'] = np.where(close > open, 1, -1)
        candle_dir = df_parsed['Candle_Dir']
        
        # CONDITION 2 # 
        df_parsed['SMA_Dir'] = np.where(prev_close > prev_sma, 1, -1)
        #df_parsed['SMA_Dir'] = np.where(prev_close > ref_sma, 1, -1)
        sma_dir = df_parsed['SMA_Dir']
        
        # CONDITION 3 #
        df_parsed['SMA_Open_Dir'] = np.where(open > ref_sma, 1, -1)
        sma_open_dir = df_parsed['SMA_Dir']
        
        # CONDITION 4 # 
        df_parsed['Piv_Dir'] = np.where(open > ref_pivot, 1, -1)
        piv_dir = df_parsed['Piv_Dir']
        
        # CONDITION 5 # 
        df_parsed['SMA_Delta'] = np.where(ref_sma > prev_sma, 1, -1)
        sma_delta_dir = df_parsed['SMA_Delta']
        
        
        df_parsed['Forecast'] = np.where(
            (candle_dir == sma_dir) & 
            (candle_dir == piv_dir) &  
            (candle_dir == sma_delta_dir) &  
            (candle_dir == sma_open_dir), 
            candle_dir, 0)
        
        df_parsed['Actual'] = candle_dir
        
        
        #shift back for accuracy calulation
        df_parsed['Actual'] = df_parsed['Actual'].shift(periods = -1)
        
        actual = df_parsed["Actual"]
        forecast = df_parsed["Forecast"]
        
        df_parsed['Signal'] = df_parsed['Forecast']
        signal = df_parsed['Signal']
    
        
        ## Determines if forecast was successful
        df_parsed["Match"] = np.where(actual == signal, actual * signal, 0)
    
        df_parsed['Actual'].fillna(0.0, inplace = True)
        df_parsed.dropna(inplace = True)
        
        self.df_signals = df_parsed.loc[:, ['Close', 'Signal']]
        df_parsed.reset_index(inplace = True, drop = False)
        
        df_parsed.index.rename(ma_string, inplace = True)
        

        self.df_parsed = df_parsed
        return self.df_parsed
    
    def get_filtered_ls(self, parsed):
        self.parsed = parsed
        main = self.parsed.copy()
        
        main = main.loc[main["Signal"] != 0]
        #filter entries only with valid forecast (+1 / -1)
        match_count = len(main[main['Match'] == 1]) # successful forecast
        fail_count = len(main[main['Match'] == 0]) # failed forecast
        
        total = match_count + fail_count
        accuracy = (match_count / total) * 100
        self.accuracy = accuracy
          
        return match_count, fail_count, total, accuracy
    
        
    def get_accuracy_df(self, df, periodStart, periodEnd):
        self.periodStart = periodStart
        self.periodEnd = periodEnd
        self.df = df
        columns = ["Period", "Accuracy"]
        acc_df = pd.DataFrame(columns = columns)

        for p in range(self.periodStart, self.periodEnd):
            parsed = self.get_parsed_df(df, p)
            match, fail, total, acc = self.get_filtered_ls(parsed)
            
            row = [p, acc]
            acc_df.loc[len(acc_df)] = row
            
        maxVal = acc_df['Accuracy'].max()
        minVal = acc_df["Accuracy"].min()
        self.acc_df = acc_df
        return self.acc_df
    
    def get_limits_df(self, df, periodStart, periodEnd):
        self.periodStart = periodStart
        self.periodEnd = periodEnd
        self.df = df
        
        acc_data = self.get_accuracy_df(self.df, self.periodStart, self.periodEnd)
        acc = acc_data["Accuracy"]
        
        maxVal = acc.max()
        minVal = acc.min()
                
        min_df = acc_data.loc[acc == minVal]
        max_df = acc_data.loc[acc == maxVal]

        self.best_acc = maxVal
        self.best_prd = acc_data.loc[acc_data.Accuracy == maxVal].iloc[0].Period
        return max_df, min_df, self.best_prd, self.best_acc