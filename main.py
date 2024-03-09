import os
import time
import json
import pyupbit

# Optional
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning) # FutureWarning 제거
from dotenv import load_dotenv
import myfunc as myfunc

load_dotenv()

access_key = os.getenv("UPBIT_OPEN_API_ACCESS_KEY")
secret_key = os.getenv("UPBIT_OPEN_API_SECRET_KEY")
upbit = pyupbit.Upbit(access_key, secret_key)

def my_strategy(df, coin) -> list:

    ma_sig, macd_sig, rsi_sig = False, False, False

    ma_short = df['ma_short'][-1]
    ma_long = df['ma_long'][-1]
    close_prev = df['close'][-2]
    close = df['close'][-1]

    macd = df['macd'][-1]
    macd_signal = df['macd_signal'][-1]
    macd_osc = df['macd_osc'][-1]
    macd_osc_prev = df['macd_osc'][-2]

    rsi_prev = df['RSI'][-2]
    rsi = df['RSI'][-1]
    rsi_signal = df['RSI_SIGNAL'][-1]

    try:
        if ma_short > ma_long and close > ma_short and close > close_prev:
            ma_sig = True
        if macd > macd_signal and macd_osc > 0 and macd_osc > macd_osc_prev:
            macd_sig = True
        if rsi > rsi_signal and rsi > rsi_prev:
            if rsi > 30 and rsi < 70:
                rsi_sig = True

        if ma_sig and macd_sig and rsi_sig:
            return ['BUY']
        else:
            return ['KEEP', [ma_sig, macd_sig, rsi_sig]]
   
    except Exception as e:
        print(e)

def order(coin, position) -> str:

    try:
        if position == 'BUY':
            # 스프레드매매는 일단 생각하지 않기로. 
            # 코인 구매시에, 익절가격을 미리 정해서 동일 물량을 지정가로 걸어두기.
            # cash = upbit.get_balance('KRW')
            cash = 5100
            current_price = pyupbit.get_current_price(coin)

            volume = current_price / cash
            bid = upbit.buy_market_order(coin, cash)
            
            ask_price = pyupbit.get_tick_size(current_price * 1.05)
            ask = upbit.sell_limit_order(coin, ask_price, volume)

            with open('spread_cnt.json', 'a') as f:
                json.dump({bid, ask}, f)

            return (f'{coin} 구매완료 / {volume}')
        
        elif position == 'SELL':
            # 팔려면 lock 걸려 있는 애를 풀어줘야 한다. uuid 필요.
            volume = upbit.get_balance(coin)
            ask = upbit.sell_market_order(coin, volume)

            coin_acc = get_coin_acc(coin)
            avg_buy_price = coin_acc['avg_buy_price']
            current_price = pyupbit.get_current_price(coin)
            earning_rate = ((current_price - avg_buy_price) / avg_buy_price) * 100

            return (f'{coin}을 매각완료. {round(earning_rate,2)}%')
        
        elif position == 'KEEP':
            return (f'{coin} 관망')

    except Exception as e:
        print('Exception From order() - ', e)

def get_coin_acc(coin):
    my_balance = upbit.get_balances()
    for i in range(1, len(my_balance)):
        if my_balance[i]['currency'] == coin:
            return my_balance[i]

def cut_loss(my_balance) -> list:
    my_coin = []

    for i in range(1, len(my_balance)):
        try:
            coin = f"KRW-{my_balance[i]['currency']}"
            avg_buy_price = float(my_balance[i]['avg_buy_price'])
            current_price = pyupbit.get_current_price(coin)
            cut_line = avg_buy_price* (1.0 - 0.15)
            earn_line = avg_buy_price* (1.0 + 0.23)

            if current_price >= earn_line:
                upbit.sell_market_order(coin, my_balance[i]['balance'])
                earning_rate = ((avg_buy_price - current_price) / avg_buy_price) * 100
                print(f'{coin}을 익절했습니다. {round(earning_rate,2)}%')
            elif current_price <= cut_line:
                upbit.sell_market_order(coin, my_balance[i]['balance'])
                loss_rate = ((avg_buy_price - current_price) / avg_buy_price) * 100
                print(f'{coin}을 손절했습니다. {round(loss_rate,2)}%')
            else :
                my_coin.append(coin)

        except Exception as e:
            print('Exception cut_loss():', e)

    return my_coin

def main() -> None:
    # myfunc.get_ex_vols("minute15")
    print(f'거래를 시작합니다. {now}')

    my_balance = upbit.get_balances()
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    ex_history = [now]

    if len(my_balance) > 1:
        # 가지고 있는 코인에 대해서 손익절체크.(손익절비율 = 1:1.5)
        # 손익절에 해당하지 않는 코인을 돌려준다.
        remain_coin = cut_loss(my_balance)    
    else:
        remain_coin = []

    # 만약 현금이 남아 있다면 다음을 진행.
    if upbit.get_balance('KRW-KRW') > 5000:

        # 안전한 코인을 구해와서
        safe_coin = myfunc.get_safe_coin()
        target_coin = set(remain_coin + safe_coin)
        print(target_coin)

        for coin in target_coin:
            # 데이터셋을 마련하고
            df = myfunc.get_all_df(coin)

            # 포지션을 정한다. 
            position = my_strategy(df, coin)
            # print(coin, position)

            orders = order(coin, position[0])            
            ex_history.append(orders)

    with open('ex_rerult.json', 'a', encoding='utf-8') as file:
        json.dump(ex_history, file, ensure_ascii=False)
    
    _now = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f'정상적으로 처리가 완료되었습니다. {_now-now} 소요')

if __name__ == "__main__":
    # 관련 세팅은 myIndex.py의 get_all_df 함수에서 진행할 것. 귀찮다...    
    main()
