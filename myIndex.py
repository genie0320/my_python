import pandas as pd

def SMA(df, period=30):
    '''
    # 단순 이동 평균(Simple Moving Average, SMA)
    ''' 
    df_sma = df.rolling(window=period).mean()
    return df_sma


def EMA(df, period=30, *column):
    '''
    # 지수 이동 평균(Exponentially-weighted Moving Average, EMA)
    최근의 데이터에 가중치를 두어 이동평균을 계산
    '''
    if column:
        _df = df[column]
    else :
        _df = df

    df_ema = _df.ewm(span=period, adjust=False).mean()
    return df_ema


# 왜인지는 모르지만 자꾸 에러가 난다. rsi 산출시 사용됨.
# def WMA(df, period=30, *column):
#     '''
#     # WMA (Welles Moving Average)
#     EMA와 비슷하지만, 가중치를 2/1+N 대신 1/N을 사용한다고 함.
#     RSI 계산시의 산식.
#     최근의 데이터에 가중치를 두어 이동평균을 계산
#     '''
#     if column:
#         _df = df[column].astype(float)
#     else :
#         _df = df

#     df_wma = _df.ewm(alpha=1/period, min_periods=period).mean()
#     return df_wma

def RSI(df, rsi_period=14, rsi_signal_period=9):
    '''
    # 상대적 강도 지수(RSI) 계산 함수

    :simbol : 'KRW-ETH'
    :interval : 'day', 'minute60'
    :period : RSI 강도계산 기간
    :n : -1 직전값기준, -1 전전값기준

    - 70 이상: 과매수 (매도 신호)
    - 30 이하: 과매도 (매수 신호)
    - 50: 중립
    > 50선 위/아래로 교차하는 지점을 매매신호로 활용할 수 있음.
    '''
    delta = df.diff(1) #Use diff() function to find the discrete difference over the column axis with period value equal to 1
    # delta = delta.dropna() # or delta[1:] / 결측값을 제거
    up =  delta.copy()  # delta 값 복사
    down = delta.copy() # delta 값 복사
    up[up < 0] = 0 
    down[down > 0] = 0 

    df['up'] = up
    df['down'] = down

    AVG_Gain = up.ewm(alpha=1/rsi_period, min_periods=rsi_period).mean()
    AVG_Loss = abs(down.ewm(alpha=1/rsi_period, min_periods=rsi_period).mean())


    RS = AVG_Gain / AVG_Loss
    RSI = 100.0 - (100.0/ (1.0 + RS))
    RSI_SIGNAL = RSI.ewm(span=rsi_signal_period, adjust=False, min_periods=rsi_signal_period).mean()

    df_rsi = pd.concat([RSI, RSI_SIGNAL],axis=1)
    df_rsi.columns = ['rsi', 'rsi_signal']

    return df_rsi

def MACD(df, fastperiod=12, slowperiod=26, signalperiod=9):

    macd = EMA(df, fastperiod) - EMA(df, slowperiod)
    macd_signal = EMA(macd, signalperiod)
    macd_osc = macd - macd_signal

    df_macd = pd.concat([macd, macd_signal, macd_osc],axis=1)
    df_macd.columns = ['macd','macd_signal','macd_osc']

    return df_macd