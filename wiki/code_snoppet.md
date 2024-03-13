##### 현재시간 구하기
```python
# from time import time, localtime
from datetime import datetime
import pytz

now = datetime.now()
now.strftime("%Y-%m-%d %H:%M:%S")

KST = pytz.timezone('Asia/Seoul')
now_kst = datetime.now(KST)
now_kst.strftime("%Y-%m-%d %H:%M:%S") # '2024-03-12 18:38:24'
now_kst.strftime("%Y-%m-%d")+' 09:00:00' # '2024-03-12 09:00:00'
```

##### 실행시간 계산 데코레이터.
```python
def calc_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"함수 {func.__name__}의 실행 시간: {end_time - start_time} 초")
        return result
    return wrapper

@calc_time
def example_function():
    print("함수 실행 중...")
    time.sleep(2)

example_function()
```

##### title
```python

```