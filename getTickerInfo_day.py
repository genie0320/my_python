
#%%
# 파이썬 내장
import os
import time
import datetime as dt
import pickle
import json

# 외부 모듈
import pyupbit
import pandas as pd

# 내부 모듈
import myutil
import myfunc

from dotenv import load_dotenv
import _myfunc

load_dotenv()

access_key = os.getenv("UPBIT_OPEN_API_ACCESS_KEY")
secret_key = os.getenv("UPBIT_OPEN_API_SECRET_KEY")
upbit = pyupbit.Upbit(access_key, secret_key)
       
#%%
@myutil.time_check
def main() -> None:
    now = dt.datetime.now().strftime('%H:%M')
    if now >= '09:01' and now <= '09:20':
        myfunc.update_ticker_data('day')
        target_coins_day:list = myfunc.get_target_coins('day')
        print('Coins of day :', now, target_coins_day)
        myfunc.sort_coins(target_coins_day, 'day')

    # myfunc.update_ticker_data('minute15')
    target_coins_min:list = myfunc.get_target_coins('minute15')
    print('Coins of 15min :', now, target_coins_min)
    sorted_list:list = myfunc.sort_coins(target_coins_min, 'minute15')
    print('Coins for BUY :', now, sorted_list)

    my_balance = upbit.get_balances()
    my_coin = myfunc.cut_loss(upbit, my_balance)

    # myfunc.order 수정해야 함.
    myfunc.order(upbit, coins:list)

    print(my_coin)
#%%
if __name__ == '__main__':
    main()

#%%
# 파일 체크시 사용
# res = pd.read_pickle('data\KRW-BTC_day.pickle')
# res.to_csv('D:\Devn_src\my_python\your_csv_file.csv', index=True)