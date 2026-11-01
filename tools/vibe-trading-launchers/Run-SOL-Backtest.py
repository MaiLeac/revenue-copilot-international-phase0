import json
from datetime import date, datetime, timedelta
from pathlib import Path
from src.tools.backtest_tool import run_backtest

end_date=(date.today()-timedelta(days=1)).isoformat()
root=Path.home()/'.vibe-trading'/'runs'/('verified_sol_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
signal='''import pandas as pd
class SignalEngine:
    def generate(self, data_map):
        result={}
        for code, df in data_map.items():
            close=df['close']
            fast=close.ewm(span=50,adjust=False,min_periods=50).mean()
            slow=close.ewm(span=200,adjust=False,min_periods=200).mean()
            result[code]=((fast>slow)&slow.notna()).astype(float)
        return result
'''
bh='''import pandas as pd
class SignalEngine:
    def generate(self,data_map):
        return {code:pd.Series(1.0,index=df.index) for code,df in data_map.items()}
'''
for name,code,start in [('ema',signal,'2021-01-01'),('buy_hold',bh,'2021-01-01'),('ema_oos',signal,'2025-01-01'),('buy_hold_oos',bh,'2025-01-01')]:
    path=root/name
    (path/'code').mkdir(parents=True,exist_ok=True)
    cfg=dict(source='okx',codes=['SOL-USDT'],start_date='2020-06-15',end_date=end_date,evaluation_start_date=start,interval='1D',initial_cash=10000,commission=0.001,taker_rate=0.001,maker_rate=0.001,slippage=0.0005,leverage=1,funding_rate=0,engine='daily',position_adjustment='hold',optimizer=None,extra_fields=None)
    (path/'config.json').write_text(json.dumps(cfg,indent=2),encoding='utf-8')
    (path/'code'/'signal_engine.py').write_text(code,encoding='utf-8')
    result=json.loads(run_backtest(str(path)))
    (path/'engine_result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(name,json.dumps(result),flush=True)
    if result['status']!='ok': raise SystemExit(1)
