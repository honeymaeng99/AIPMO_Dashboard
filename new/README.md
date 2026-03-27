# AI 과제 관리 프로그램

## 구성
```
📁 프로젝트 폴더
├── server.py      ← FastAPI 백엔드 (SQLite 연동)
├── index.html     ← Vue 3 프론트엔드
├── tasks.db       ← (자동 생성) SQLite 데이터베이스
└── README.md
```

## 실행 방법

### 1단계: 패키지 설치 (최초 1회)
```bash
pip install fastapi uvicorn
```

### 2단계: 서버 실행
```bash
python server.py
```

### 3단계: 브라우저 접속
```
http://localhost:8000
```

끝! 이게 전부입니다.

## API 목록

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /api/tasks | 전체 과제 조회 |
| GET | /api/tasks/{id} | 단일 과제 조회 |
| POST | /api/tasks | 과제 등록 |
| PUT | /api/tasks/{id} | 과제 수정 |
| PATCH | /api/tasks/{id}/status | 상태 변경 (이력 저장) |
| DELETE | /api/tasks/{id} | 과제 삭제 |
| GET | /api/tasks/{id}/history | 상태 변경 이력 조회 |
| GET | /api/summary | 상태별 요약 통계 |

## 참고
- 최초 실행 시 `tasks.db` 파일이 자동 생성되고 샘플 데이터 12건이 들어갑니다
- DB 파일을 삭제하면 초기화됩니다
- API 문서: http://localhost:8000/docs (Swagger UI 자동 제공)
