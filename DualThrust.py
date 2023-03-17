from functools import reduce
from pandas import DataFrame
from freqtrade.strategy import IStrategy

import talib.abstract

from freqtrade.strategy.interface import IStrategy

import datetime

import pandas as pd

class DualThrustStrategy(IStrategy):
    INTERFACE_VERSION: int = 3
    # ROI table:
    minimal_roi = {"0": 0.15, "30": 0.1, "60": 0.05}
    # minimal_roi = {"0": 1}

    # Stoploss:
    stoploss = -0.265

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.05
    trailing_stop_positive_offset = 0.1
    trailing_only_offset_is_reached = False

    timeframe = "5m"

    can_short = True

    K1 = 0.4
    K2 = 0.6

    BuyLine =0
    SellLine=0



    start_time=0
    end_time=0




    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:


        print('--------populate_indicators-----')

 #       pd.set_option('display.max_columns',None)
  #      pd.set_option('display.max_rows', None)

        self.end_time = dataframe.iloc[-1]['date']

        selfs.start_time = self.end_time + datetime.timedelta(days=-1)
        self.start_time = self.start_time.strftime("%Y%m%d")
        self.end_time = self.end_time.strftime("%Y%m%d")

        df2 = dataframe[(dataframe['date'] >= self.start_time) & (dataframe['date'] < self.end_time)]

        DayHigh = df2.max()['high']
        DayLow = df2.min()['low']
        DayCloseH=df2.max()['close']
        DayCloseL=df2.max()['close']

        Range=max(DayHigh-DayCloseL,DayCloseH-DayLow)

        self.BuyLine = dataframe.iloc[-1]['open'] + self.K1*Range
        self.SellLine = dataframe.iloc[-1]['open'] - self.K2*Range

        dataframe['ma']= talib.MA(dataframe['close'], timeperiod=20)

        # Calculate OBV
  #      dataframe['obv'] = ta.OBV(dataframe['close'], dataframe['volume'])

        # Add your trend following indicators here
  #      dataframe['trend'] = dataframe['close'].ewm(span=20, adjust=False).mean()
  #      print(dataframe)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        print('--------populate_entry_trend-----')

        # Add your trend following buy signals here
        dataframe.loc[
             ((dataframe['high'] > self.BuyLine) &
             (dataframe['high'].shift(1) < self.BuyLine)&
             (dataframe['ma'] > self.BuyLine)),
             'enter_long'] = 1

        # Add your trend following sell signals here
        dataframe.loc[
             ((dataframe['low'] < self.SellLine) &
             (dataframe['low'].shift(1) > self.SellLine)&
              (dataframe['ma'] < self.SellLine)),
             'enter_short'] = 1
 #           print(dataframe)
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        print('--------populate_exit_trend-----')
        # Add your trend following exit signals for long positions here
        dataframe.loc[
            ((dataframe['low'] < self.SellLine) &
             (dataframe['low'].shift(1) > self.SellLine) |
             (min(dataframe[-11:-1]['low']) < self.SellLine)),
            'exit_long'] = 1

        # Add your trend following exit signals for short positions here
        dataframe.loc[
            ((dataframe['high'] > self.BuyLine) &
             (dataframe['high'].shift(1) < self.BuyLine) |
             (max(dataframe[-11:-1]['high'])> self.BuyLine),
             'exit_short'] = 1
 #       print(dataframe)
        return dataframe

