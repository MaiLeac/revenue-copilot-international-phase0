import pandas as pd
class SignalEngine:
    def generate(self,data_map):
        return {code:pd.Series(1.0,index=df.index) for code,df in data_map.items()}
