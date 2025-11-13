# 1. HTTP

## 1-1. 정의
- 클라이언트와 서버간의 통신을 위한 프로토콜이다.

## 1-2. HTTP Method
- GET, POST, PATCH, PUT, DELETE, OPTIONS 가 있다.
- 일반적으로 데이터를 조회하거나 paramter 받아 웹데이터의 리소스를 접근하다.
- POST HTTP body 데이터를 보내는 방식으로 일반적으로 데이터의 생성이 주 목적이며 파일업로드 등..
- PATCH는 업데이트 요청을 처리한다 PATCH 는 전체 데이터중 일부분만 수정하지만 PUT 은 전체 데이터를 수정하기 때문에 일부 데이터를 누락하게 되면 해당 값이 없는 상태로 업데이트 된다.
- DELETE는 리소스의 삭제를 요청한다.

## 1-3. HTTP Status
- 200 요청이 성공
- 201 리소스 생성
- 204 요청을 성공 적으로 처리했으나 응답할 내용이 없는경우 (게시글 삭제, 회원탈퇴)
- 400 서버에 잘못된 데이터를 요청한경우
- 401 인증되지 않은 접근
- 403 인가되지 않은 접근
- 429 너무 많은 리소스 요청
- 404 리소스가 존재하지 않는다.
- 500 서버에러
- 503 현재 서버가 준비되지 않은 상태
- 501 서버가 해당 요청을 수행할 기능이 없는경우 (METHOD)

## 1-4. HTTP 와 REST의 차이

HTTP API 설계방식과 REST API설계는 차이는
과거 클라이언트와 서버간의 통신을 할때로 거슬러 올라가본다.
기존에는 서버가 클라이언트와 결속되어 클라이언트에 맞는 데이터를 제공해야했었다.
반면 REST 클라이언트에 결속되어 설계되는 것이 아닌 독립적으로 리소스의 요청에 따른 데이터를 주고 받는다.
REST의 특징은 URL만으로 리소스를 이해할 수 있고 또한 API 문서를 통해 원하는 정보를 제공 받을 수 있다.
더 나아가 HAETOS 를 이용하여 다음 액션을 알 수 있도록 설계하는 방식도 있기에 RESTAPI 와 HTTP API는 차이가 명확하다.

# 2. router, controller

[feat/task2](https://github.com/study-python-ai/week9/tree/feat/task2)


# 4. router, controller, model

[feat/task4](https://github.com/study-python-ai/week9/tree/feat/task4)