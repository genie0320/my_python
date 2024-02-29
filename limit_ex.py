from dotenv import load_dotenv
import os 
import pyupbit

load_dotenv()

access_key = os.environ.get('UPBIT_OPEN_API_ACCESS_KEY')
secret_key = os.environ.get('UPBIT_OPEN_API_SECRET_KEY')
upbit = pyupbit.Upbit(access_key, secret_key)

# Upbit login 확인
my_balance = upbit.get_balances()

for coin in my_balance:
    ticker = coin['currency']
    ticker_set = f'KRW-{ticker}'
    locked = float(coin['locked'])

    # 매수/매도 호가정보조회
    # pyupbit.get_orderbook(ticker=ticker_set)

    if ticker == 'KRW' :
        print(f"현재 계좌의 원화 잔고는 {coin['balance']} 입니다.")
        if locked :
            print(f"- Locked : {locked}")
    else :
        current_price = pyupbit.get_current_price(ticker_set)
        return_rate =  (current_price - float(coin['avg_buy_price'])) / float(coin['avg_buy_price']) * 100.0
        
        print(f"- {ticker} : {coin['balance']}, {coin['avg_buy_price']}, {return_rate}")
        
        if return_rate >= 1.2:
            ticker_balance = upbit.get_balance(ticker_set)

            # 시장가 전량판매
            # upbit.sell_market_order(ticker_set, ticker_balance)

            # 지정가 전량판매 걸어 넣기
            upbit.sell_limit_order(ticker_set, pyupbit.get_tick_size(current_price * 1.002), ticker_balance) 
            print(f'----------------- {ticker_set} 판매완료 -----------------')
        else :
            print(f'----------------- {ticker_set} 계속보유 ------------------')


# ---------- 지정가 구매걸기 --------------------------------
# current_price = pyupbit.get_current_price('KRW-ETH')
# target_price = pyupbit.get_tick_size(current_price * 0.998)
# my_balance = upbit.get_balance("KRW")-1000 # 수수료만큼은 남겨놔야 주문이 들어간다.
# amount = my_balance / target_price

# # won = 10000

# print(upbit.buy_limit_order('KRW-ETH', pyupbit.get_tick_size(target_price), my_balance/target_price))
