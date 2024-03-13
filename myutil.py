def moving_rate(prev_price:float, current_price:float) -> float:
    return round((current_price - prev_price) / prev_price * 100, 3)

# _price = ohlcv.loc['2024-03-12 08:45:00']['close']
# price = pyupbit.get_current_price("KRW-BTC")

# moving_rate(_price, price)

def calc_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"함수 {func.__name__}의 실행 시간: {end_time - start_time} 초")
        return result
    return wrapper