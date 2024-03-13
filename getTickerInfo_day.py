
#%%
# 파이썬 내장
import os
import time
import datetime as dt
import pickle

# 외부 모듈
import pyupbit
import pandas as pd

# 내부 모듈
import myutil

@myutil.time_check
def expand_data(ticker, interval, n, *file_path):
    
    if file_path:
        ohlcv = pd.read_pickle(file_path)
    else:
        ohlcv = pyupbit.get_ohlcv(ticker, interval = interval)
        file_path = f'data/{ticker}_{interval}.pickle'
    
    st_day = dt.datetime.now()

    try:
        calls = 0
        if interval == 'minute15':
            cnt = int(200 // (1440/15))
        elif interval == 'minute60':
            cnt = int(200 // (1440/60))
        elif interval == 'day':
            cnt = int(199 // (1440/1440))
        
        while len(ohlcv) < n and calls < 10:
            calls += 1
            day_delta = (st_day - dt.timedelta(days=cnt))
            st_day = day_delta
            _ohlcv = pyupbit.get_ohlcv(ticker, interval = interval, to = day_delta.strftime('%Y-%m-%d'))
            ohlcv = pd.concat([_ohlcv, ohlcv], axis=0)
            ohlcv = ohlcv.drop_duplicates()
            # print(f'{ticker},{len(ohlcv)}개의 데이터를 수집했습니다.')

            time.sleep(0.5)

        ohlcv.to_pickle(file_path)    

    except Exception as e:
        print('Exception : ', e)
        

#%%
@myutil.time_check
def update_data(ticker, interval, file_path):
    df = pyupbit.get_ohlcv(ticker, interval = interval)
    _df = pd.read_pickle(file_path)
    df = pd.concat([_df, df], axis=0)
    df = df.drop_duplicates()
    df.to_pickle(file_path)

#%%
def main() -> str:
    tickers = pyupbit.get_tickers('KRW')
    interval = 'day'
    Update = 0
    Create = 0

    for ticker in tickers:
        # try:
        time.sleep(0.2)
        file_path = f'data/{ticker}_{interval}.pickle'
        
        if os.path.exists(file_path):
            print(f'{ticker} 파일을 업데이트합니다.')
            update_data(ticker, interval, file_path)
            Update += 1

        else:
            print(f'{ticker} 파일을 생성합니다.')
            expand_data(ticker, interval, 1000)
            Create += 1

        # except Exception as e:
        #     print('Exception : ', ticker, e )

    return f'{Update}개의 코인데이터를 업데이트했습니다. \n {Create}개의 코인데이터를 생성했습니다.'


#%%
if __name__ == '__main__':
    print(main())

#%%
# 파일 체크시 사용
# res = pd.read_pickle('data\KRW-BTC_day.pickle')
# res.to_csv('D:\Devn_src\my_python\your_csv_file.csv', index=True)