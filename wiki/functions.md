# Ultimate Function Guide
Rule 1. Do one thing, and do it well.
- 결합도, 의존도 낮추기

Rule 2. Separate commands from queries.
- 데이터배정 등의 낮은 레벨과 '체크로직'등의 상위레벨은 분리해서 작성하고,
- 굳이 변수만들어 리턴할 생각하지 말고 바로 리턴해라.bool 등으로.

Rule 3. Only request information you actually need
- 만약 유효기간 체크를 위한 함수라면, 체크할 번호와 유효기간만 넘겨주면 되지, 해당 customer 전체를 넘겨줄 필요는 없다.

Rule 4. Keep the number of parameters minimal
- 매개변수가 많다는 것은 그 함수가 많은 걸 하고 있다는 뜻. 따라서 1, 2번 원칙에 어긋날 수 있다.

Rule 5. Don't create and use an object in the same place.
- 그 함수 내에서 생성하지 말고, 생성해서 매개변수로 필요한 부분만 떼서 넘겨라.

Rule 6. Don't use flag parameters
- Bool을 써야하면 차라리... 함수를 분리해서 간략하게 만들어라.

Rule 7. Remember functions are Objects.
- callable, partial (from functools) 을 활용하면 한결 간결한 코드를 사용할 수 있다.
