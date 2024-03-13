'''
# 시간계산
방법이 여러가지가 있다. datetime.datetime이라는 객체가 생성되고 이걸 조작해서 계산을 하는 방식이다.
초~주간단위 계산은 그냥 datetime을 쓰면 될 것 같지만, 월단위 계산이 필요하다면 pandas를 쓰는게 낫다.


## 현재시간
```python
import datetime as dt

now = dt.datetime.now() 
today = dt.datetime.today()
now # datetime.datetime(2024, 3, 13, 1, 46, 22, 273469)
today # datetime.datetime(2024, 3, 13, 1, 46, 54, 449217)
type(now) # datetime.datetime
```

## 시간계산 (일반)
```python
now_str = dt.datetime.now().strftime("%Y-%m-%d") 
# '2024-03-13' (str)

now_dt = dt.datetime.strptime(now_str, "%Y-%m-%d") 
# datetime.datetime(2024, 3, 13, 0, 0)

now_add = now_dt + dt.timedelta(hours=32) 
# datetime.datetime(2024, 3, 14, 8, 0) : 32시간 뒤

now_minus = now_dt - dt.timedelta(hours=32) 
# datetime.datetime(2024, 3, 11, 16, 0) : 32시간 전

time_delta = now + dt.timedelta(seconds=32) 
# seconds, minutes, hours, days, weeks 사용가능. 
```

## 시간계산 (pandas)
```python
import pandas as pd

# Create a datetime object
now = pd.Timestamp.now()
# Timestamp('2024-03-13 02:15:34.679195')

# Add 3 months to the current date
three_months_later = now + pd.DateOffset(months=3)
# Timestamp('2024-06-13 02:16:36.436542')

# Subtract 1 year from the current date
one_year_earlier = now - pd.DateOffset(years=1)
# Timestamp('2023-03-13 02:16:55.251894')

# Add 2 weeks and 3 days to the current date
two_weeks_three_days_later = now + pd.DateOffset(weeks=2) + pd.DateOffset(days=3)
# Timestamp('2024-03-30 02:17:22.875524')
```