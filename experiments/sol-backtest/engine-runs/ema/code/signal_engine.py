import pandas as pd
class SignalEngine:
    def generate(self, data_map):
        result={}
        for code, df in data_map.items():
            close=df['close']
            fast=close.ewm(span=50,adjust=False,min_periods=50).mean()
            slow=close.ewm(span=200,adjust=False,min_periods=200).mean()
            result[code]=((fast>slow)&slow.notna()).astype(float)
        return result
