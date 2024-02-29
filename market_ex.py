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

    # 시장가 호가정보조회
    # pyupbit.get_orderbook(ticker=ticker_set)

    # 시장가 매수
    # print(upbit.buy_market_order("KRW-ETH", 5000))

    if ticker == 'KRW' :
        print(f"현재 계좌의 원화 잔고는 {coin['balance']} 입니다.")
        if locked :
            print(f"- Locked : {locked}")
    else :
        current_price = pyupbit.get_current_price(ticker_set)
        return_rate =  (current_price - float(coin['avg_buy_price'])) / float(coin['avg_buy_price']) * 100.0
        
        print(f"- {ticker} : {coin['balance']}, {coin['avg_buy_price']}, {return_rate}")
        
        # 시장가 매도 : 일정 수익률을 넘는 경우 전량판매진행.
        if return_rate >= 1.2:
            ticker_balance = upbit.get_balance(ticker_set)
            upbit.sell_market_order(ticker_set, ticker_balance)
            print(f'----------------- {ticker_set} 판매완료 -----------------')
        else :
            print(f'----------------- {ticker_set} 계속보유 ------------------')