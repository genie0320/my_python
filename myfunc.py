import os
import time
import requests
import json

import pickle
import pyupbit
import pandas as pd

import myIndex as myIndex

# ----------- 이하 지표관련 함수들 ------------------
def get_coin_data(coin:str, interval:str = 'minute15'):
    '''
    # 읽어온 데이터를 pandas df로 준비함.
    - 'date'를 index로 설정.
    '''

    ohlcv = pyupbit.get_ohlcv(coin, interval)

    df = pd.DataFrame(ohlcv)

    if not df.index.name:
        df.index.name = 'date'
    else:
        pass
    
    old_cols = list(df.columns)
    df.columns = [x.lower() for x in old_cols]
    # df.rename(columns = {"old_1": "new_1", "old_2": "new_2"}, inplace=True) 

    return df

def get_ma(df, period01=5, period02=20, column='close'):
    '''
    # 지정칼럼에 대한 장단기 SMA를 value로 계산하여 assign 한다.
    - 단기선이 장기선을 크로스하면 sell/buy 발생.
    - period01 : 단기선 계산 기간
    - period02 : 장기선 계산 기간
    '''
    _df = df[column].astype(float)
    ma_short = myIndex.SMA(_df, period01)
    ma_long = myIndex.SMA(_df, period02)

    # dataframe에 컬럼 추가
    df = df.assign(ma_short=ma_short, ma_long=ma_long)
    # df.rename(columns={'ma_short': f'ma({period01})', 
    #                    'ma_long': f'ma({period02})'}, inplace=True)

    return df

def get_rsi(df, rsi_period, rsi_signal_period):
    '''
    - RSI함수에서 df를 받아와서 concat 하는 함수
    '''
    _df = df['close'].astype(float)

    rsi = myIndex.RSI(_df, rsi_period, rsi_signal_period)
    df_rsi = pd.concat([df, rsi], axis=1)

    return df_rsi

def get_macd(df, fastperiod=12, slowperiod=26, signalperiod=9, column = 'close'):
    '''
    # MACD 3종세트를 value로 계산하여 assign 한다.
    '''
    _price = df[column].astype(float)
    macd = myIndex.EMA(_price, fastperiod) - myIndex.EMA(_price, slowperiod)
    macd_signal = myIndex.EMA(macd, signalperiod)
    macd_osc = macd - macd_signal

    df = df.assign(macd=macd, macd_signal=macd_signal, macd_osc=macd_osc )

    return df

# ----------- 이하 코인관련 함수들 ------------------
def get_ex_vols(period:str):
    '''
    # 거래량 상위종목 산출.
    원화거래 가능한 코인과 그 거래볼륨을 산출.
    
    :period = 'day', 'minute60'
    '''
    tickers = pyupbit.get_tickers('KRW')
    ex_vols = dict()
    coin_data = pd.DataFrame()
    # tickers = ['KRW-ETH','KRW-SSX']
    print(f'거래가능한 코인의 수 : ', len(tickers))
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    for ticker in tickers:
        try:
            df = pyupbit.get_ohlcv(ticker,interval=period) # 거래량기준으로 거래량*종가

            ex_vol = (df['close'][-1] * df['volume'][-1]) \
                + (df['close'][-2] * df['volume'][-2]) \
                + (df['close'][-3] * df['volume'][-3]) \
                + (df['close'][-4] * df['volume'][-4]) \
                + (df['close'][-5] * df['volume'][-5]) \
                + (df['close'][-6] * df['volume'][-6]) \
            
            ex_vols[ticker] = ex_vol

            # 읽어온 코인데이터를 히스토리삼아 저장
            try:
                file_path = f'data/{ticker}_data.pickle'
                
                if os.path.exists(file_path):
                    _df = pd.read_pickle(file_path)
                    df = pd.concat([_df, df], axis=0)
                    df = df.drop_duplicates()
                    df.to_pickle(file_path)
                else:
                    df.to_pickle(f'data/{ticker}_data.pickle')
                    
            except Exception as e:
                print('Exception : ', e)

            print(f'{now}{ticker} 데이터 저장이 완료되었습니다.')
            time.sleep(0.002)

        except Exception as e:
            print('Exception :', e)

    sorted_coin = (sorted(ex_vols.items(), key=lambda x: x[1], reverse=True)) # sorted를 하는 순간 dict > (Tuple들의) list가 된다.

    with open("sorted_coin.json", "w") as file:
    # Dump the Python data into the file as a JSON string
        json.dump(sorted_coin, file)    
        print('구매대상 코인 선별이 완료되었습니다.')

def get_top_coins(n:int) -> list:
    '''
    # 거래량이 가장 큰 코인을 n개 가져온다.
    
    :n : 가져올 코인의 수
    '''
    try:
        # Read JSON data from a file
        with open("sorted_coin.json", "r") as file:
            sorted_coin = json.loads(file.read())

        top_coin = sorted_coin[0:n]

        # return list(dict(top_coin).keys())
        return list(dict(top_coin).keys())
    except Exception as e:
        print('Exception : ', 'Read sorted coin data', e)

def CheckCoin(coins):
    '''
    업비트의 위험/주의 코인경보를 대상코인에서 제외한다.
    
    :return list[coin_caution, safe_coin]
    '''
    coin_caution = []

    url = "https://api.upbit.com/v1/market/all?isDetails=true"
    headers = {"accept": "application/json"}
    res = requests.get(url, headers=headers)
    all_coin = res.json()
    
    for coin in all_coin:
        if coin['market'].startswith('KRW') and coin['market_event']['warning'] == True:
            coin_caution.append(coin['market'])

    safe_coin = []
    
    for coin in coins:
        if coin not in coin_caution:
            safe_coin.append(coin)
        else:
            print(f'다음 코인은 구매대상에서 제외합니다. : {coin}')
    return [coin_caution, safe_coin]

def get_safe_coin() -> list:

    top_coin = get_top_coins(20)
    safe_coin = CheckCoin(top_coin)[1]

    return safe_coin

def get_all_df(coin:str) -> str:

    # Criteria
    criteria_interval = 'minute15'

    # MA
    ma_short_period = 5
    ma_long_period  = 20

    # RSI
    rsi_period = 30
    rsi_signal_period = 9

    # MACD parameters
    macd_fast_period = 12
    macd_slow_period  = 26
    macd_signal_period = 9

    _coin_df = get_coin_data(coin, criteria_interval)
    _coin_df_ma = get_ma(_coin_df, ma_short_period, ma_long_period)
    _coin_df_macd = get_macd(_coin_df_ma, macd_fast_period, macd_slow_period, macd_signal_period)
    _coin_df_rsi = get_rsi(_coin_df_macd, rsi_period, rsi_signal_period)

    return _coin_df_rsi.tail()

# ----------- 이하 매매타이밍관련 함수들 ------------------
def get_buy_signal(ohlcv_ma_rsi):
    '''
    5평선이 20평선보다 위에 있고, 
    이전 5평선보다 이번 5평선이 클 때 (가격상승중일때) TRUE 반환.
    '''
    signal = False
    
    _current = ohlcv_ma_rsi.iloc[-1]
    _prev = ohlcv_ma_rsi.iloc[-2]

    if _current['ma(5)'] - _current['ma(20)'] > 0:
        if _current['ma(5)'] >= _prev['ma(5)']:
            signal = True

    return signal


def get_last_order(coin):
    result = []
    file_path = "ex_rerult.json"

    with open(file_path) as f:
        js = json.loads(f.read()) ## json 라이브러리 이용

    for data in js:
        if data['coin'] == coin:
            result.append(data)

    # return df.filter(items = [coin], axis=0)
    return result





# ----------- 이하 테스트가 필요한 함수들 ------------------
def get_stochastic(df, n=14, m=5, t=5):
    '''
    일자(n,m,t)에 따른 Stochastic(KDJ)의 값을 구하기 위해 함수형태로 만듬
    '''
    # 입력받은 값이 dataframe이라는 것을 정의해줌
    df = pd.DataFrame(df)

    # n일중 최고가
    ndays_high = df.High.rolling(window=n, min_periods=1).max()
    
    # n일중 최저가
    ndays_low = df.Low.rolling(window=n, min_periods=1).min()

    # Fast%K 계산
    fast_k = ((df.Close - ndays_low) / (ndays_high - ndays_low)) * 100

    # Fast%D (=Slow%K) 계산
    slow_k = fast_k.ewm(span=m).mean()

    # Slow%D 계산
    slow_d = slow_k.ewm(span=t).mean()

    # dataframe에 컬럼 추가
    df = df.assign(fast_k=fast_k, fast_d=slow_k, slow_k=slow_k, slow_d=slow_d)

    return df

def TSI(df, s1=25, s2=13, s3=7):
    '''
    # 실제 강도 지수 (s1: 첫번째 스무딩 윈도우, s2: 두번째 스무딩 윈도우, s3: TSI를 스무딩)

    :사용방법 :
    - import numpy as np
    ohlcv_w_TSI = TSI(ohlcv_w_RSI, 25, 13, 10)
    ohlcv_w_TSI = TSI(ohlcv_w_TSI, 40, 20, 10)
    ohlcv_w_TSI.tail()
    '''
    # 입력받은 값이 dataframe이라는 것을 정의해줌
    df = pd.DataFrame(df)

    # Price Change (PC)
    PC = df.close.diff()

    # PC Smoothing (지수 이동 평균)
    PCS = EMA(PC, s1)
    
    # PC Double Smoothing
    PCDS = EMA(PCS, s2)

    # Absolute of PC
    APC = PC.abs()

    # APC Smoothing
    APCS = EMA(APC, s1)

    # APC Double Smoothing
    APCDS = EMA(APCS, s2)

    # True Strength Index (TSI)
    TSI = 100 * (PCDS / APCDS)
    TSI_signal = EMA(TSI, s3)  

    # Equilibrium Line (Zero Line)
    ZL = np.zeros([TSI.shape[0],1])

    # dataframe에 컬럼 추가
    df = df.assign(ZL=ZL, TSI=TSI, TSI_signal=TSI_signal)
    df.rename(columns={'TSI': f'TSI({s1},{s2})', 
                       'TSI_signal': f'TSI({s1},{s2},{s3})'}, inplace=True)

    return df


def write_ex_log(position, coin, money, volume, count):
    '''
    date, coin, position='KEEP', count, buy, sell, ex_rate, quantity, remain
    '''
    position = position
    date = time.strftime('%Y-%m-%d %H:%M:%S')
    file_path = "ex_rerult.json"

    with open(file_path) as f:
        js = json.loads(f.read()) ## json 라이브러리 이용
        count = count
        ex_rate = 0
        remain = 0

    if position == "SELL":     
        ex_log = {
            "date":date,
            "coin":coin,
            "position":"SELL",
            "count":count,
            "buy":0,
            "sell":money,
            "ex_rate":ex_rate,
            "quantity":volume,
            "remain":remain
            }
        js.append(ex_log)
        
    elif position == "BUY":
        ex_log = {
            "date":date,
            "coin":coin,
            "position":"BUY",
            "count":count,
            "buy":money,
            "sell":0,
            "ex_rate":ex_rate,
            "quantity":volume,
            "remain":remain
            }      
        js.append(ex_log)  

    return ex_log

# 매도시그널.
# 가격 단기선이 장기선보다 아래에 있고, rsi 시그널선보다 아래에 있으며, 맥디 볼륨이 이전 값보다 낮을 때

# def get_sell_signal(df, coin) -> bool:
#     ma_sig, macd_sig, rsi_sig = False, False, False

#     ma_short = df['ma_short'][-1]
#     ma_long = df['ma_long'][-1]
#     close_prev = df['close'][-2]
#     close = df['close'][-1]

#     macd = df['macd'][-1]
#     macd_signal = df['macd_signal'][-1]
#     macd_osc = df['macd_osc'][-1]
#     macd_osc_prev = df['macd_osc'][-2]

#     rsi_prev = df['RSI'][-2]
#     rsi = df['RSI'][-1]
#     rsi_signal = df['RSI_SIGNAL'][-1]

#     try:
#         if macd_osc > 0 and macd_osc <= macd_osc_prev :
#             macd_sig = True
#         if rsi < rsi_signal and rsi <= rsi_prev and rsi > 50:
#             rsi_sig = True
#         if ma_short < ma_long and close < ma_short and close < close_prev:
#             ma_sig = True

#         if ma_sig and macd_sig and rsi_sig:
#             return [True, [ma_sig, macd_sig, rsi_sig]]
#         else:
#             return [False, [ma_sig, macd_sig, rsi_sig]]        


#     except Exception as e:
#         print(e)