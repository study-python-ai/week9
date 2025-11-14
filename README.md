## 실행방법

### 1. 의존성 설치

```bash
uv sync
```

### 2. 서버 실행

#### 방법 1: Python 스크립트로 실행
```bash
uv run python main.py
```

#### 방법 2: uvicorn으로 직접 실행
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. API 접근

서버 실행 후 다음 URL로 접근할 수 있습니다:

| URL | 설명 |
|-----|------|
| http://localhost:8000/ | 기본 API 엔드포인트 |
| http://localhost:8000/redoc | ReDoc API 문서 |
