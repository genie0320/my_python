#%%
import pyupbit    
import pandas as pd
import pickle
import os

'''
# 코인 ohlcv 정보 저장
원화거래가 가능한 ticker들의 ohlcv 데이터를 가져와 pickle 파일로 저장.
1. 새로 추가된 ticker가 있다면(이전 저장파일이 없다면) 해당 파일을 만들어 저장.
2. 이전 저장파일이 있다면, 해당 파일을 불러와 concat하여 중복을 제거하고 저장.
'''
#%%
tickers = pyupbit.get_tickers('KRW')
for ticker in tickers:
    df = pyupbit.get_ohlcv(ticker, interval='minute15')

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

#%%
# ---------------------------------------------------------------------
# 피클파일은 그냥 열어볼 수 없다. 파일검증시 사용. 귀찮아서 주석처리만 해둔다.
# ---------------------------------------------------------------------
data = pd.read_pickle(f'data/KRW-ETH_data.pickle')
# data.drop_duplicates()
data
# %%
