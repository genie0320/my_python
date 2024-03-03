# RSI 지수

가상자산 거래에서 RSI 지수는 **상대 강도 지수(Relative Strength Index)**의 약자로, 특정 기간 동안 가격 변동의 강도를 측정하여 과매수 또는 과매도를 파악하는 지표입니다. 쉽게 말하면, 현재의 가격변동이 얼마나 빠른 속도로 상승/하락하고 있는지를 보여주는 지표이다.

## 계산방법
1. 특정기간동안의 상승/하락 평균치를 구한다.
특정기간(14,7,21일)동안의 싱승/하락 변동률을 모두 더한 후 기간으로 나눈다.
2. 상승평균 / 하락평균절대값  
    - 상승 가격 변동률의 평균: +2%  
    - 하락 가격 변동률의 평균: -2%  
    `RS: (+2%) / |-2%| = 1`
3. 100 - ( 100 / ( 1 + RS))
    - RS: 1.5  
    `RSI: 100 - (100 / (1 + 1.5)) = 60` 또는
    `RSI = 상승평균/(상승평균+하락평균) = RS/(1+RS)(*100)`

## 결과해석
RSI 지수는 0에서 100까지의 값을 가지며, 일반적으로 다음과 같이 해석됨.

- 70 이상: 과매수 (매도 신호) 
- 30 이하: 과매도 (매수 신호)
- 50: 중립
> 50선 위/아래로 교차하는 지점을 매매신호로 활용할 수 있음.
> 지지 / 저항선으로 활용

다만, RSI 30 이하에서만 구매할 경우, 장이 상승세인 경우 봇이 활동하지 못하게 되는 경우가 발생할 수 있다. 이때는 기준이 되는 RSI period를 변경하는 등으로 봇이 활동할 수 있는 타이밍을 만들어줄 수 있다. 일반적으로, 짧게 잡으면 좀 더 공격적으로 투자하는 셈이 된다(거래횟수가 많아지므로)

## 코드

```python
import pandas as pd

def GetRSI(ohlcv, period, n): # 일봉/분봉정보, 기간, 기준값:직전값(-1)/전전값(-2)
    ohlcv['close'] = ohlcv['close']
    delta = ohlcv['close'].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    _gain = up.ewm(com=(period -1), min_periods=period).mean()
    _loss = down.abs().ewm(com=(period -1), min_periods=period).mean()
    RS = _gain / _loss
    return pd.Series(100-(100/(1+RS)), name = 'RSI').iloc[n]

# 비트코인의 일봉(캔들) 정보를 가져온다.
# df = pyupbit.get_ohlcv('KRW-ETH', interval = 'day') # 1일기준
df = pyupbit.get_ohlcv('KRW-ETH', interval = 'minute240') # 4시간 기준

# RSI지표를 계산해서 프린트
print(GetRSI(df, 14))

# RSI지표를 계산
print(GetRSI(df, 14, -1)) #오늘(최근 / 마지막 값)
print(GetRSI(df, 14, -2)) #어제(전전값)

rsi14 = float(GetRSI(df, 14, -1))

if rsi14 <=30:
    upbit.buy_market_order('KRW-ETH', 5000)
```