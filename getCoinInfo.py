import os
import time
import json

import pickle
import pyupbit
import pandas as pd

import myfunc

'''
# 거래량 상위종목 산출.
원화거래 가능한 코인과 그 거래볼륨을 산출.

:period = 'day', 'minute60'
'''
tickers = pyupbit.get_tickers('KRW')
ex_vols = dict()
coin_data = pd.DataFrame()
print(f'거래가능한 코인의 수 : ', len(tickers))

for ticker in tickers:
    try:
        df = pyupbit.get_ohlcv(ticker,'minute15') # 거래량기준으로 거래량*종가

        ex_vol = (df['close'].iloc[-1] * df['volume'].iloc[-1]) \
            + (df['close'].iloc[-2] * df['volume'].iloc[-2]) \
            + (df['close'].iloc[-3] * df['volume'].iloc[-3]) \
            + (df['close'].iloc[-4] * df['volume'].iloc[-4]) \
            + (df['close'].iloc[-5] * df['volume'].iloc[-5]) \
            + (df['close'].iloc[-6] * df['volume'].iloc[-6]) \
        
        ex_vols[ticker] = ex_vol

        # 읽어온 코인데이터를 히스토리삼아 저장
        try:
            file_path = f'data/{ticker}_data.pickle'
            
            if os.path.exists(file_path):
                _df = pd.read_pickle(file_path)
                df = pd.concat([_df, df], axis=0)
                df = df.drop_duplicates()
                df.to_pickle(file_path, protocol=4)
            else:
                df.to_pickle(file_path, protocol=4)
                
        except Exception as e:
            print('Exception : ', e)

        print(f'{myfunc.get_time()}{ticker} 데이터 저장이 완료되었습니다.')
        time.sleep(0.002)

    except Exception as e:
        print('Exception :', e)

sorted_coin = (sorted(ex_vols.items(), key=lambda x: x[1], reverse=True)) # sorted를 하는 순간 dict > (Tuple들의) list가 된다.

with open("sorted_coin.json", "w") as file:
# Dump the Python data into the file as a JSON string
    json.dump(sorted_coin, file)    
    print('구매대상 코인 선별이 완료되었습니다.')