import time
from datetime import datetime
import pytz

def moving_rate(prev_price:float, current_price:float) -> float:
    return round((current_price - prev_price) / prev_price * 100, 3)

# _price = ohlcv.loc['2024-03-12 08:45:00']['close']
# price = pyupbit.get_current_price("KRW-BTC")

# moving_rate(_price, price)

def time_check(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"함수 {func.__name__}의 실행 시간: {end_time - start_time} 초")
        return result
    return wrapper


def get_time(type:str):

    KST = pytz.timezone('Asia/Seoul')
    
    if type == 'ch':
        now_kst = datetime.now(KST)
        res = now_kst.strftime("%Y-%m-%d %H:%M:%S")
    else:
        now_kst = datetime.now(KST)

    return now_kst
