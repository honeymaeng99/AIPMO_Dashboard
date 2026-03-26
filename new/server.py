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

DB_PATH = "tasks.db"


# ========== Pydantic 모델 ==========
class TaskCreate(BaseModel):
    title: str
    team: str = ""
    manager: str = ""
    status: str = "PoC"
    goal: str = ""
    ai_area: str = ""
    start_date: str = ""
    end_date: str = ""
    effect: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    team: Optional[str] = None
    manager: Optional[str] = None
    status: Optional[str] = None
    goal: Optional[str] = None
    ai_area: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    effect: Optional[str] = None


class StatusChange(BaseModel):
    status: str
    changed_by: str = "관리자"


# ========== DB 헬퍼 ==========
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            team TEXT DEFAULT '',
            manager TEXT DEFAULT '',
            status TEXT DEFAULT 'PoC',
            goal TEXT DEFAULT '',
            ai_area TEXT DEFAULT '',
            start_date TEXT DEFAULT '',
            end_date TEXT DEFAULT '',
            effect TEXT DEFAULT '',
            created_at TEXT,
            updated_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            before_status TEXT,
            after_status TEXT,
            changed_by TEXT DEFAULT '관리자',
            changed_at TEXT,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)

    # 샘플 데이터 (테이블이 비어있을 때만)
    c.execute("SELECT COUNT(*) as cnt FROM tasks")
    if c.fetchone()["cnt"] == 0:
        now = datetime.now().isoformat()
        samples = [
            ("AIP-001", "설비 이상 감지 AI 모델", "설비팀", "김민수", "Pilot", "설비 고장 사전 예측", "예측 분석", "2025-01-15", "2025-06-30", "설비 가동률 15% 향상"),
            ("AIP-002", "품질 검사 자동화", "품질팀", "이지은", "PoC", "육안 검사 대체", "컴퓨터 비전", "2025-02-01", "2025-08-31", "검사 시간 60% 단축"),
            ("AIP-003", "수요 예측 모델", "물류팀", "박준혁", "현장 적용", "재고 최적화", "시계열 예측", "2024-09-01", "2025-03-31", "재고 비용 20% 절감"),
            ("AIP-004", "문서 자동 분류 시스템", "경영지원팀", "최서연", "개발 완료", "문서 분류 자동화", "NLP", "2024-06-01", "2024-12-31", "업무 효율 30% 향상"),
            ("AIP-005", "공정 최적화 AI", "생산팀", "정우성", "아이디어", "생산 효율 극대화", "강화학습", "2025-04-01", "2025-12-31", "생산성 25% 향상"),
            ("AIP-006", "에너지 소비 예측", "설비팀", "한예슬", "PoC", "에너지 절감", "예측 분석", "2025-03-01", "2025-09-30", "에너지 비용 10% 절감"),
            ("AIP-007", "스마트 물류 배차", "물류팀", "오태석", "Pilot", "배송 효율화", "최적화 알고리즘", "2025-01-20", "2025-07-31", "배송 비용 18% 절감"),
            ("AIP-008", "챗봇 고객 응대", "경영지원팀", "윤하나", "현장 적용", "고객 문의 자동 응대", "대화형 AI", "2024-07-01", "2025-01-31", "응대 시간 50% 감소"),
            ("AIP-009", "용접 품질 실시간 모니터링", "품질팀", "강동원", "보류", "용접 불량 감소", "컴퓨터 비전", "2025-02-15", "2025-10-31", "불량률 40% 감소"),
            ("AIP-010", "AI 기반 채용 스크리닝", "경영지원팀", "임수정", "아이디어", "채용 효율화", "NLP", "2025-05-01", "2025-11-30", "스크리닝 시간 70% 단축"),
            ("AIP-011", "예방 정비 스케줄링", "설비팀", "김민수", "개발 완료", "정비 최적화", "예측 분석", "2024-04-01", "2024-11-30", "정비 비용 22% 절감"),
            ("AIP-012", "원자재 가격 예측", "물류팀", "박준혁", "PoC", "구매 전략 최적화", "시계열 예측", "2025-03-15", "2025-09-30", "구매 비용 8% 절감"),
        ]
        for s in samples:
            c.execute(
                "INSERT INTO tasks (id, title, team, manager, status, goal, ai_area, start_date, end_date, effect, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (*s, now, now),
            )

    conn.commit()
    conn.close()


# ========== 다음 ID 생성 ==========
def next_task_id():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM tasks ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        num = int(row["id"].split("-")[1]) + 1
    else:
        num = 1
    return f"AIP-{num:03d}"


# ========== API 엔드포인트 ==========

# 전체 과제 조회
@app.get("/api/tasks")
def get_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


# 단일 과제 조회
@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다")
    return row_to_dict(row)


# 과제 등록
@app.post("/api/tasks")
def create_task(task: TaskCreate):
    conn = get_db()
    task_id = next_task_id()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO tasks (id, title, team, manager, status, goal, ai_area, start_date, end_date, effect, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (task_id, task.title, task.team, task.manager, task.status, task.goal, task.ai_area, task.start_date, task.end_date, task.effect, now, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


# 과제 수정
@app.put("/api/tasks/{task_id}")
def update_task(task_id: str, task: TaskUpdate):
    conn = get_db()
    existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다")

    updates = {k: v for k, v in task.dict().items() if v is not None}
    if not updates:
        conn.close()
        return row_to_dict(existing)

    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [task_id]
    conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


# 상태 변경 (이력 저장 포함)
@app.patch("/api/tasks/{task_id}/status")
def change_status(task_id: str, body: StatusChange):
    conn = get_db()
    existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다")

    before = existing["status"]
    now = datetime.now().isoformat()

    conn.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?", (body.status, now, task_id))
    conn.execute(
        "INSERT INTO status_history (task_id, before_status, after_status, changed_by, changed_at) VALUES (?,?,?,?,?)",
        (task_id, before, body.status, body.changed_by, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


# 과제 삭제
@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    conn = get_db()
    existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다")
    conn.execute("DELETE FROM status_history WHERE task_id = ?", (task_id,))
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "삭제 완료", "id": task_id}


# 상태 변경 이력 조회
@app.get("/api/tasks/{task_id}/history")
def get_history(task_id: str):
    conn = get_db()
    rows = conn.execute("SELECT * FROM status_history WHERE task_id = ? ORDER BY changed_at DESC", (task_id,)).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


# 요약 통계
@app.get("/api/summary")
def get_summary():
    conn = get_db()
    rows = conn.execute("SELECT status, COUNT(*) as count FROM tasks GROUP BY status").fetchall()
    total = conn.execute("SELECT COUNT(*) as count FROM tasks").fetchone()["count"]
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
