"""
AI 과제 관리 프로그램 - FastAPI 서버

실행 방법:
  1. pip install fastapi uvicorn
  2. python server.py
  3. 브라우저에서 http://localhost:8000 접속
"""

import sqlite3
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="AI 과제 관리 API")

# CORS 설정 – 프론트엔드와 다른 포트에서 호출 가능하도록 허용
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # 모든 도메인 허용 (개발 단계)
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, PATCH, DELETE 등 모든 메서드 허용
    allow_headers=["*"],            # 모든 헤더 허용
)

DB_PATH = "projects.db"
 
# ========== Pydantic 모델 ==========
# 데이터 타입 검사, 자동 검증 , Json <-> Python 변환
class ProjectCreate(BaseModel):
    domain: str
    projects_type: Optional[str] = None
    owner_team: Optional[str] = None
    executive_owner: Optional[str] = None
    project_leader: Optional[str] = None
    project_name: str
    project_description: Optional[str] = None
    performance_y1: Optional[float] = None
    performance_y2: Optional[float] = None
    performance_x1: Optional[float] = None
    performance_x2: Optional[float] = None
    current_status: Optional[str] = "기획"
    planning_date: Optional[str] = None
    data_ready_date: Optional[str] = None
    poc_date: Optional[str] = None
    mvp_pilot_date: Optional[str] = None
    full_deployment_date: Optional[str] = None
    collaboration_dept: Optional[str] = None
    mtc_strategic_project: Optional[int] = 0
    aic_strategic_project: Optional[int] = 0
    dtc_strategic_project: Optional[int] = 0
    current_gpu_count: Optional[int] = 0
    current_gpu_spec: Optional[str] = None
    required_gpu_count: Optional[int] = 0
    required_gpu_spec: Optional[str] = None
    gpu_request_approved: Optional[int] = 0
    gpu_request_b300_equivalent: Optional[float] = None
    additional_support_request: Optional[str] = None
    expected_impact: Optional[str] = None
    kpi: Optional[str] = None
    financial_performance: Optional[float] = None
    process_metric: Optional[str] = None

# 과제 업데이트 시 필요
class ProjectUpdate(BaseModel):
    domain: Optional[str] = None
    projects_type: Optional[str] = None
    owner_team: Optional[str] = None
    executive_owner: Optional[str] = None
    project_leader: Optional[str] = None
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    performance_y1: Optional[float] = None
    performance_y2: Optional[float] = None
    performance_x1: Optional[float] = None
    performance_x2: Optional[float] = None
    current_status: Optional[str] = None
    planning_date: Optional[str] = None
    data_ready_date: Optional[str] = None
    poc_date: Optional[str] = None
    mvp_pilot_date: Optional[str] = None
    full_deployment_date: Optional[str] = None
    collaboration_dept: Optional[str] = None
    mtc_strategic_project: Optional[int] = None
    aic_strategic_project: Optional[int] = None
    dtc_strategic_project: Optional[int] = None
    current_gpu_count: Optional[int] = None
    current_gpu_spec: Optional[str] = None
    required_gpu_count: Optional[int] = None
    required_gpu_spec: Optional[str] = None
    gpu_request_approved: Optional[int] = None
    gpu_request_b300_equivalent: Optional[float] = None
    additional_support_request: Optional[str] = None
    expected_impact: Optional[str] = None
    kpi: Optional[str] = None
    financial_performance: Optional[float] = None
    process_metric: Optional[str] = None

# 상태 변경 전용
class StatusChange(BaseModel):
    status: str
    changed_by: str = "관리자"


# 관리자 코드 검증용
class AdminVerify(BaseModel):
    admin_code: str

ADMIN_CODE = "AIPMO980306"

# ========== DB 헬퍼 ==========
# DB 연결 -> 테이블 생성 -> 데이터 다루기 준비
def get_db():
    conn = sqlite3.connect(DB_PATH) #.db파일에 연결
    conn.row_factory = sqlite3.Row # 결과를 딕셔너리처럼 사용 가능하게 변경 (ex. row["title"] 이런식으로 사용가능)
    return conn

# DB에서 가져온 데이터를 Dict로 변환
def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

# 프로그램 실행 시 DB 테이블을 자동 생성하는 함수
def init_db():
    conn = get_db()
    c = conn.cursor()

    # 0은 없다 or 안했다, 1은 있다 or 했다. 날짜는 text로 관리
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        domain TEXT CHECK(domain IN ('생산', '설비', '수율/품질')),
        projects_type TEXT,
        owner_team TEXT,
        executive_owner TEXT,
        project_leader TEXT,
        project_name TEXT NOT NULL,
        project_description TEXT,
        performance_y1 REAL,
        performance_y2 REAL,
        performance_x1 REAL,
        performance_x2 REAL,
        current_status TEXT CHECK(current_status IN ('기획','Data 확보','PoC','MVP/Pilot','전면적용','Pending/Drop')),
        planning_date TEXT,
        data_ready_date TEXT,
        poc_date TEXT,
        mvp_pilot_date TEXT,
        full_deployment_date TEXT,
        collaboration_dept TEXT,
        mtc_strategic_project INTEGER,
        aic_strategic_project INTEGER,
        dtc_strategic_project INTEGER,
        current_gpu_count INTEGER,
        current_gpu_spec TEXT,
        required_gpu_count INTEGER,
        required_gpu_spec TEXT,
        gpu_request_approved INTEGER,
        gpu_request_b300_equivalent REAL,
        additional_support_request TEXT,
        expected_impact TEXT,
        kpi TEXT,
        financial_performance REAL,
        process_metric TEXT,
        created_at TEXT,
        updated_at TEXT,
        is_deleted INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            before_status TEXT,
            after_status TEXT CHECK(after_status IN ('기획','Data 확보','PoC','MVP/Pilot','전면적용','Pending/Drop')),
            changed_by TEXT DEFAULT '관리자',
            changed_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # 기존 DB에 is_deleted 컬럼이 없으면 추가
    try:
        c.execute("SELECT is_deleted FROM projects LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE projects ADD COLUMN is_deleted INTEGER DEFAULT 0")

    # 샘플 데이터 (테이블이 비어있을 때만)
    c.execute("SELECT COUNT(*) as cnt FROM projects")
    if c.fetchone()["cnt"] == 0:
        now = datetime.now().isoformat()
        samples = [
            ("AIP-001", "설비", "설비 이상 감지 AI 모델", "설비팀", "김민수", "MVP/Pilot", "설비 고장 사전 예측", "예측 분석", "2025-01-15", "2025-06-30", "설비 가동률 15% 향상"),
            ("AIP-002", "수율/품질", "품질 검사 자동화", "품질팀", "이지은", "PoC", "육안 검사 대체", "컴퓨터 비전", "2025-02-01", "2025-08-31", "검사 시간 60% 단축"),
            ("AIP-003", "생산", "수요 예측 모델", "물류팀", "박준혁", "전면적용", "재고 최적화", "시계열 예측", "2024-09-01", "2025-03-31", "재고 비용 20% 절감"),
            ("AIP-004", "생산", "문서 자동 분류 시스템", "경영지원팀", "최서연", "전면적용", "문서 분류 자동화", "NLP", "2024-06-01", "2024-12-31", "업무 효율 30% 향상"),
            ("AIP-005", "생산", "공정 최적화 AI", "생산팀", "정우성", "기획", "생산 효율 극대화", "강화학습", "2025-04-01", "2025-12-31", "생산성 25% 향상"),
            ("AIP-006", "설비", "에너지 소비 예측", "설비팀", "한예슬", "PoC", "에너지 절감", "예측 분석", "2025-03-01", "2025-09-30", "에너지 비용 10% 절감"),
            ("AIP-007", "생산", "스마트 물류 배차", "물류팀", "오태석", "MVP/Pilot", "배송 효율화", "최적화 알고리즘", "2025-01-20", "2025-07-31", "배송 비용 18% 절감"),
            ("AIP-008", "생산", "챗봇 고객 응대", "경영지원팀", "윤하나", "전면적용", "고객 문의 자동 응대", "대화형 AI", "2024-07-01", "2025-01-31", "응대 시간 50% 감소"),
            ("AIP-009", "수율/품질", "용접 품질 실시간 모니터링", "품질팀", "강동원", "Pending/Drop", "용접 불량 감소", "컴퓨터 비전", "2025-02-15", "2025-10-31", "불량률 40% 감소"),
            ("AIP-010", "생산", "AI 기반 채용 스크리닝", "경영지원팀", "임수정", "기획", "채용 효율화", "NLP", "2025-05-01", "2025-11-30", "스크리닝 시간 70% 단축"),
            ("AIP-011", "설비", "예방 정비 스케줄링", "설비팀", "김민수", "전면적용", "정비 최적화", "예측 분석", "2024-04-01", "2024-11-30", "정비 비용 22% 절감"),
            ("AIP-012", "생산", "원자재 가격 예측", "물류팀", "박준혁", "PoC", "구매 전략 최적화", "시계열 예측", "2025-03-15", "2025-09-30", "구매 비용 8% 절감"),
        ]

        for s in samples:
            c.execute("""
                INSERT INTO projects (
                    id,
                    domain,
                    project_name,
                    owner_team,
                    project_leader,
                    current_status,
                    project_description,
                    projects_type,
                    planning_date,
                    full_deployment_date,
                    expected_impact,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (*s, now, now))

    conn.commit()
    conn.close()

# ========== 다음 ID 생성 ==========
def next_project_id():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM projects ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        num = int(row["id"].split("-")[1]) + 1
    else:
        num = 1
    return f"AIP-{num:03d}"


# ========== API 엔드포인트 ==========

# 관리자 코드 검증
@app.post("/api/verify-admin")
def verify_admin(body: AdminVerify):
    if body.admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="관리자 코드가 올바르지 않습니다")
    return {"verified": True}

# 전체 과제 조회
@app.get("/api/projects")
def get_projects():
    conn = get_db()
    rows = conn.execute("SELECT * FROM projects WHERE is_deleted = 0 ORDER BY created_at DESC").fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


# 단일 과제 조회
@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM projects WHERE id = ? AND is_deleted = 0", (project_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다")
    return row_to_dict(row)


# 과제 등록
@app.post("/api/projects")
def create_project(project: ProjectCreate):
    conn = get_db()
    project_id = next_project_id()
    now = datetime.now().isoformat()

    conn.execute("""
        INSERT INTO projects (
            id,
            domain,
            projects_type,
            owner_team,
            executive_owner,
            project_leader,
            project_name,
            project_description,
            performance_y1,
            performance_y2,
            performance_x1,
            performance_x2,
            current_status,
            planning_date,
            data_ready_date,
            poc_date,
            mvp_pilot_date,
            full_deployment_date,
            collaboration_dept,
            mtc_strategic_project,
            aic_strategic_project,
            dtc_strategic_project,
            current_gpu_count,
            current_gpu_spec,
            required_gpu_count,
            required_gpu_spec,
            gpu_request_approved,
            gpu_request_b300_equivalent,
            additional_support_request,
            expected_impact,
            kpi,
            financial_performance,
            process_metric,
            created_at,
            updated_at
        )
        VALUES (
            ?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?
        )
    """, (
        project_id,
        project.domain,
        project.projects_type,
        project.owner_team,
        project.executive_owner,
        project.project_leader,
        project.project_name,
        project.project_description,
        project.performance_y1,
        project.performance_y2,
        project.performance_x1,
        project.performance_x2,
        project.current_status,
        project.planning_date,
        project.data_ready_date,
        project.poc_date,
        project.mvp_pilot_date,
        project.full_deployment_date,
        project.collaboration_dept,
        project.mtc_strategic_project,
        project.aic_strategic_project,
        project.dtc_strategic_project,
        project.current_gpu_count,
        project.current_gpu_spec,
        project.required_gpu_count,
        project.required_gpu_spec,
        project.gpu_request_approved,
        project.gpu_request_b300_equivalent,
        project.additional_support_request,
        project.expected_impact,
        project.kpi,
        project.financial_performance,
        project.process_metric,
        now,
        now
    ))

    conn.commit()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return row_to_dict(row)

# 과제 수정
@app.put("/api/projects/{project_id}")
def update_project(project_id: str, project: ProjectUpdate):
    conn = get_db()
    existing = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다")

    updates = {k: v for k, v in project.dict().items() if v is not None}
    if not updates:
        conn.close()
        return row_to_dict(existing)

    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [project_id]

    conn.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)
    conn.commit()

    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return row_to_dict(row)

# 상태 변경 (이력 저장 포함)
@app.patch("/api/projects/{project_id}/status")
def change_status(project_id: str, body: StatusChange):
    conn = get_db()
    existing = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다")

    before = existing["current_status"]
    now = datetime.now().isoformat()

    conn.execute(
        "UPDATE projects SET current_status = ?, updated_at = ? WHERE id = ?",
        (body.status, now, project_id)
    )

    conn.execute("""
        INSERT INTO status_history (
            project_id, before_status, after_status, changed_by, changed_at
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        project_id,
        before,
        body.status,
        body.changed_by,
        now
    ))

    conn.commit()

    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return row_to_dict(row)

# 과제 삭제 (소프트 삭제 - DB에서 실제 삭제하지 않고 숨김 처리)
@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):
    conn = get_db()
    existing = conn.execute("SELECT * FROM projects WHERE id = ? AND is_deleted = 0", (project_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다")
    now = datetime.now().isoformat()
    conn.execute("UPDATE projects SET is_deleted = 1, updated_at = ? WHERE id = ?", (now, project_id))
    conn.commit()
    conn.close()
    return {"message": "삭제 완료", "id": project_id}


# 상태 변경 이력 조회
@app.get("/api/projects/{project_id}/history")
def get_history(project_id: str):
    conn = get_db()
    rows = conn.execute("SELECT * FROM status_history WHERE project_id = ? ORDER BY changed_at DESC", (project_id,)).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


# 요약 통계
@app.get("/api/summary")
def get_summary():
    conn = get_db()
    rows = conn.execute("SELECT status, COUNT(*) as count FROM projects WHERE is_deleted = 0 GROUP BY status").fetchall()
    total = conn.execute("SELECT COUNT(*) as count FROM projects WHERE is_deleted = 0").fetchone()["count"]
    conn.close()
    counts = {r["status"]: r["count"] for r in rows}
    counts["전체"] = total
    return counts


# ========== 프론트엔드 서빙 ==========
@app.get("/")
def serve_index():
    return FileResponse("index.html")


# ========== 서버 시작 ==========
if __name__ == "__main__":
    init_db()
    print("\n" + "=" * 50)
    print("  AI 과제 관리 서버 시작!")
    print("  브라우저에서 http://localhost:8000 접속")
    print("=" * 50 + "\n")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
