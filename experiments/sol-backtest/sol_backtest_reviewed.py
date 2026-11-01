import argparse, urllib.request, urllib.parse, time, math, json, csv
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_CSV_PATH = BASE_DIR / 'data' / 'raw' / 'SOL-USDT_okx_1D_raw.csv'
SUMMARY_JSON_PATH = BASE_DIR / 'artifacts' / 'sol_backtest_summary.json'

INST='SOL-USDT'; BAR='1Dutc'
REQ_START_MS=int(datetime(2021,1,1,tzinfo=timezone.utc).timestamp()*1000)
REQ_END_MS=int(datetime(2026,9,27,23,59,59,tzinfo=timezone.utc).timestamp()*1000)
FETCH_START_MS=int(datetime(2020,6,15,tzinfo=timezone.utc).timestamp()*1000)
OOS_START_MS=int(datetime(2025,1,1,tzinfo=timezone.utc).timestamp()*1000)
FEE=0.001; SLIP=0.0005; COST=FEE+SLIP; INITIAL=1.0

def iso(ms): return datetime.fromtimestamp(ms/1000, tz=timezone.utc).isoformat()
def days_between(ms1, ms2): return (ms2-ms1)/1000/86400

def load_rows_from_cached_csv(csv_path: Path = RAW_CSV_PATH):
    rows = []
    with csv_path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = datetime.fromisoformat(row['timestamp_utc'])
            ts = int(dt.timestamp() * 1000)
            if FETCH_START_MS <= ts <= REQ_END_MS:
                rows.append({
                    'ts': ts,
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume']),
                })
    return sorted(rows, key=lambda x: x['ts'])

def fetch_rows_from_okx():
    base_url='https://www.okx.com/api/v5/market/history-candles'
    all_rows=[]; after=None
    for _ in range(300):
        params={'instId':INST,'bar':BAR,'limit':'100'}
        if after: params['after']=after
        url=base_url+'?'+urllib.parse.urlencode(params)
        req_obj=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 VibeTrading research bot'})
        with urllib.request.urlopen(req_obj, timeout=20) as resp:
            js=json.loads(resp.read().decode('utf-8'))
        if js.get('code')!='0': raise RuntimeError(js)
        data=js.get('data', [])
        if not data: break
        all_rows.extend(data)
        oldest=min(int(x[0]) for x in data)
        if oldest < FETCH_START_MS: break
        after=str(oldest)
        time.sleep(0.03)

    by_ts={}
    for r in all_rows:
        ts=int(r[0])
        if FETCH_START_MS <= ts <= REQ_END_MS and r[8] == '1':
            by_ts[ts]={'ts':ts,'open':float(r[1]),'high':float(r[2]),'low':float(r[3]),'close':float(r[4]),'volume':float(r[5]),'raw':r}
    rows=[by_ts[k] for k in sorted(by_ts)]
    RAW_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RAW_CSV_PATH.open('w', encoding='utf-8', newline='') as f:
        w=csv.writer(f); w.writerow(['timestamp_utc','open','high','low','close','volume'])
        for r in rows: w.writerow([iso(r['ts']),r['open'],r['high'],r['low'],r['close'],r['volume']])
    return rows

# EMA causal on closes (current bar close only known at end of that bar); signal at bar i executes at open i+1.
def add_emas(rows):
    alpha50=2/(50+1); alpha200=2/(200+1)
    ema50=None; ema200=None
    closes=[]
    for i,r in enumerate(rows):
        c=r['close']; closes.append(c)
        if i==49: ema50=sum(closes[-50:])/50
        elif i>49: ema50=alpha50*c+(1-alpha50)*ema50
        if i==199: ema200=sum(closes[-200:])/200
        elif i>199: ema200=alpha200*c+(1-alpha200)*ema200
        r['ema50']=ema50; r['ema200']=ema200
        r['raw_signal']=1 if (ema50 is not None and ema200 is not None and ema50>ema200) else 0

def maxdd(eqs):
    peak=-1e99; m=0.0
    for e in eqs:
        if e>peak: peak=e
        dd=e/peak-1 if peak>0 else 0
        if dd<m: m=dd
    return m

def sharpe(rets):
    if len(rets)<2: return float('nan')
    mean=sum(rets)/len(rets)
    var=sum((x-mean)**2 for x in rets)/(len(rets)-1)
    sd=math.sqrt(var)
    return mean/sd*math.sqrt(365) if sd else float('nan')

def cagr(eqs, tss):
    if len(eqs)<2 or eqs[0]<=0: return float('nan')
    d=days_between(tss[0], tss[-1])
    return (eqs[-1]/eqs[0])**(365/d)-1 if d>0 else float('nan')

def summarize(bt):
    eqs=bt['equity']; tss=bt['timestamps']
    eqs_for_dd=[INITIAL]+eqs
    rets=[eqs[0]/INITIAL-1]+[eqs[i]/eqs[i-1]-1 for i in range(1,len(eqs))]
    elapsed_days=days_between(tss[0], tss[-1])+1
    cagr_initial=(eqs[-1]/INITIAL)**(365/elapsed_days)-1 if elapsed_days>0 else float('nan')
    return {'total_return':eqs[-1]/INITIAL-1,'cagr':cagr_initial,'max_drawdown':maxdd(eqs_for_dd),'sharpe':sharpe(rets),'trade_count':bt['trades'],'start_equity_date':iso(tss[0]),'end_equity_date':iso(tss[-1]),'start_equity':INITIAL,'first_close_marked_equity':eqs[0],'end_equity':eqs[-1]}

def backtest_bh(test_rows):
    entry=test_rows[0]['open']*((1+SLIP)*(1+FEE)); qty=INITIAL/entry
    eqs=[qty*r['close']*((1-SLIP)*(1-FEE)) for r in test_rows]
    tss=[r['ts'] for r in test_rows]
    return {'equity':eqs,'timestamps':tss,'trades':1}

def backtest_ema(all_rows, start_ms, end_ms):
    cash=INITIAL; qty=0.0; pos=0; trades=0; log=[]; eqs=[]; tss=[]
    for i,r in enumerate(all_rows):
        ts=r['ts']
        if i>0 and start_ms <= ts <= end_ms:
            target=all_rows[i-1]['raw_signal']
            px=r['open']
            if target != pos:
                if target==1:
                    qty=cash/(px*((1+SLIP)*(1+FEE))); cash=0.0; trades+=1
                    log.append({'timestamp_utc':iso(ts),'action':'buy','price':px,'signal_bar':iso(all_rows[i-1]['ts'])})
                else:
                    cash=qty*px*((1-SLIP)*(1-FEE)); qty=0.0; trades+=1
                    log.append({'timestamp_utc':iso(ts),'action':'sell','price':px,'signal_bar':iso(all_rows[i-1]['ts'])})
                pos=target
        if start_ms <= ts <= end_ms:
            val=cash + (qty*r['close']*((1-SLIP)*(1-FEE)) if pos==1 else 0.0)
            eqs.append(val); tss.append(ts)
    return {'equity':eqs,'timestamps':tss,'trades':trades,'trade_log':log}

def run_sol_evaluation(offline: bool = True):
    rows = load_rows_from_cached_csv() if (offline and RAW_CSV_PATH.exists()) else fetch_rows_from_okx()
    add_emas(rows)
    req=[r for r in rows if REQ_START_MS <= r['ts'] <= REQ_END_MS]
    oos=[r for r in rows if OOS_START_MS <= r['ts'] <= REQ_END_MS]
    results={}
    for name,bt in [('buy_hold',backtest_bh(req)),('ema50_ema200',backtest_ema(rows,REQ_START_MS,REQ_END_MS)),('buy_hold_oos',backtest_bh(oos)),('ema50_ema200_oos',backtest_ema(rows,OOS_START_MS,REQ_END_MS))]:
        results[name]=summarize(bt)
        if 'trade_log' in bt: results[name]['trade_log']=bt['trade_log']
    coverage={'source':'OKX public REST /api/v5/market/history-candles','instrument':INST,'bar':BAR,'raw_rows':len(rows),'raw_start_utc':iso(rows[0]['ts']),'raw_end_utc':iso(rows[-1]['ts']),'requested_rows':len(req),'requested_start_utc':iso(req[0]['ts']),'requested_end_utc':iso(req[-1]['ts']),'warmup_rows_before_2021':len([r for r in rows if r['ts']<REQ_START_MS]),'oos_rows':len(oos),'oos_start_utc':iso(oos[0]['ts']),'oos_end_utc':iso(oos[-1]['ts']),'fee_each_side':FEE,'slippage_each_side':SLIP,'leverage':1,'funding_rate':0,'execution':'signals from completed close bars; target executed at next daily open; equity marked at close net of exit cost if long'}
    SUMMARY_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {'coverage':coverage,'results':results}
    with SUMMARY_JSON_PATH.open('w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
    return payload

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--live-fetch', action='store_true', help='Re-fetch candles from OKX instead of using cached raw CSV')
    args = parser.parse_args()
    out = run_sol_evaluation(offline=not args.live_fetch)
    print(json.dumps(out, indent=2))
