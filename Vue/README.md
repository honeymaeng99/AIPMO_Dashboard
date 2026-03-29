# MTC AI 과제 관리 플랫폼 (Vue 버전)

MTC AI Project Management Platform - Vue 3 + Vite + FastAPI

## 프로젝트 구조

```
Vue/
├── start.bat              # 프로덕션 실행 (빌드 + 서버)
├── dev.bat                # 개발 모드 실행 (핫리로드)
├── backend/
│   ├── server.py          # FastAPI 백엔드 서버
│   ├── requirements.txt   # Python 패키지 목록
│   ├── projects.db        # SQLite DB (자동 생성)
│   └── venv/              # Python 가상환경
└── frontend/
    ├── package.json       # Node.js 패키지 설정
    ├── vite.config.js     # Vite 설정 (API 프록시 포함)
    ├── index.html         # HTML 엔트리
    ├── dist/              # 빌드 결과물 (npm run build)
    └── src/
        ├── main.js        # Vue 앱 초기화
        ├── App.vue        # 메인 컴포넌트 (SFC)
        └── assets/
            └── style.css  # 전역 스타일
```

## 기술 스택

| 구분 | 기술 |
|------|------|
| 프론트엔드 | Vue 3 (Composition API, `<script setup>`), Vite |
| 백엔드 | Python, FastAPI, SQLite |
| 엑셀 | SheetJS (xlsx) |

## 시작하기

### 사전 요구사항

- **Node.js** v18 이상
- **Python** 3.10 이상

### 1. 최초 설치

```bash
# 프론트엔드 패키지 설치
cd frontend
npm install

# 백엔드 가상환경 생성 및 패키지 설치
cd ../backend
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

### 2. 실행

#### 개발 모드 (핫리로드)

`dev.bat`을 더블클릭하거나 아래 명령어를 각각 실행:

```bash
# 터미널 1 - 백엔드
cd backend
venv\Scripts\python server.py
# http://localhost:8000

# 터미널 2 - 프론트엔드
cd frontend
npm run dev
# http://localhost:5173
```

개발 모드에서는 `http://localhost:5173`으로 접속합니다.
Vite 프록시가 `/api` 요청을 백엔드(8000)로 자동 전달합니다.

#### 프로덕션 모드

`start.bat`을 더블클릭하거나:

```bash
# 빌드
cd frontend
npm run build

# 서버 시작 (빌드 결과물 자동 서빙)
cd ../backend
venv\Scripts\python server.py
# http://localhost:8000
```

## 주요 기능

- 과제 등록 / 수정 / 삭제 (소프트 삭제)
- 과제 상태 관리 (기획 → Data 확보 → PoC → MVP/Pilot → 전면적용 → Pending/Drop)
- 상태 변경 시 확인 다이얼로그
- 수정 모드에서 상태 변경 제한 (하단 상태 변경 버튼으로만 변경 가능)
- 멀티 필터 (상태, 도메인, 실행/대표팀)
- 키워드 검색 (과제명, ID, 실행/대표팀, 대표 임원, 실무 리더)
- 테이블 컬럼 커스터마이징 (ID, 상태, 과제명은 고정)
- 컬럼 정렬 (상태는 파이프라인 순서대로)
- 엑셀 다운로드
- 과제 수정/삭제 시 관리자 코드 검증 (서버측)
- 변경 이력 조회
- AI 어시스턴트 채팅 UI (추후 연동 예정)

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/projects` | 전체 과제 조회 |
| GET | `/api/projects/{id}` | 단일 과제 조회 |
| POST | `/api/projects` | 과제 등록 |
| PUT | `/api/projects/{id}` | 과제 수정 |
| PATCH | `/api/projects/{id}/status` | 상태 변경 |
| DELETE | `/api/projects/{id}` | 과제 삭제 (소프트) |
| GET | `/api/projects/{id}/history` | 변경 이력 조회 |
| POST | `/api/verify-admin` | 관리자 코드 검증 |
| GET | `/api/summary` | 요약 통계 |
