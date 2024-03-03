from dotenv import load_dotenv
import os 
import pyupbit

load_dotenv()

access_key = os.environ.get('UPBIT_OPEN_API_ACCESS_KEY')
secret_key = os.environ.get('UPBIT_OPEN_API_SECRET_KEY')
upbit = pyupbit.Upbit(access_key, secret_key)


my_balance = upbit.get_balance("KRW")

# 원화거래가능한 코인들을 불러와라.
tickers = pyupbit.get_tickers('KRW')

# 그 코인들 중에 ETH에 해당하는게 있다면, 그놈의 일봉데이터를 불러와서, 종가를 찍어라.
for ticker in tickers:
    if ticker == 'KRW-ETH':
        df = pyupbit.get_ohlcv(ticker, interval='day')
        # print(df)
        print(df['close'])
        # print(df['close'].iloc[-2])
        break