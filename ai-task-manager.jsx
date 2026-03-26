import { useState, useMemo, useEffect, useRef } from "react";

const STATUSES = ["아이디어", "PoC", "Pilot", "현장 적용", "개발 완료", "보류"];
const DEPARTMENTS = ["AI혁신팀", "설비팀", "품질팀", "생산팀", "물류팀", "경영지원팀"];
const STATUS_COLORS = {
  "아이디어": { bg: "#F0F4FF", text: "#3B5BDB", dot: "#3B5BDB" },
  "PoC": { bg: "#FFF4E6", text: "#E8590C", dot: "#E8590C" },
  "Pilot": { bg: "#F3F0FF", text: "#7048E8", dot: "#7048E8" },
  "현장 적용": { bg: "#E6FCF5", text: "#0CA678", dot: "#0CA678" },
  "개발 완료": { bg: "#EBFBEE", text: "#2B8A3E", dot: "#2B8A3E" },
  "보류": { bg: "#F1F3F5", text: "#868E96", dot: "#868E96" },
};

const INITIAL_TASKS = [
  { id: "AIP-001", title: "설비 이상 감지 AI 모델", team: "설비팀", manager: "김민수", status: "Pilot", goal: "설비 고장 사전 예측", aiArea: "예측 분석", startDate: "2025-01-15", endDate: "2025-06-30", effect: "설비 가동률 15% 향상", createdAt: "2025-01-10" },
  { id: "AIP-002", title: "품질 검사 자동화", team: "품질팀", manager: "이지은", status: "PoC", goal: "육안 검사 대체", aiArea: "컴퓨터 비전", startDate: "2025-02-01", endDate: "2025-08-31", effect: "검사 시간 60% 단축", createdAt: "2025-01-20" },
  { id: "AIP-003", title: "수요 예측 모델", team: "물류팀", manager: "박준혁", status: "현장 적용", goal: "재고 최적화", aiArea: "시계열 예측", startDate: "2024-09-01", endDate: "2025-03-31", effect: "재고 비용 20% 절감", createdAt: "2024-08-15" },
  { id: "AIP-004", title: "문서 자동 분류 시스템", team: "경영지원팀", manager: "최서연", status: "개발 완료", goal: "문서 분류 자동화", aiArea: "NLP", startDate: "2024-06-01", endDate: "2024-12-31", effect: "업무 효율 30% 향상", createdAt: "2024-05-20" },
  { id: "AIP-005", title: "공정 최적화 AI", team: "생산팀", manager: "정우성", status: "아이디어", goal: "생산 효율 극대화", aiArea: "강화학습", startDate: "2025-04-01", endDate: "2025-12-31", effect: "생산성 25% 향상", createdAt: "2025-03-01" },
  { id: "AIP-006", title: "에너지 소비 예측", team: "설비팀", manager: "한예슬", status: "PoC", goal: "에너지 절감", aiArea: "예측 분석", startDate: "2025-03-01", endDate: "2025-09-30", effect: "에너지 비용 10% 절감", createdAt: "2025-02-15" },
  { id: "AIP-007", title: "스마트 물류 배차", team: "물류팀", manager: "오태석", status: "Pilot", goal: "배송 효율화", aiArea: "최적화 알고리즘", startDate: "2025-01-20", endDate: "2025-07-31", effect: "배송 비용 18% 절감", createdAt: "2025-01-05" },
  { id: "AIP-008", title: "챗봇 고객 응대", team: "경영지원팀", manager: "윤하나", status: "현장 적용", goal: "고객 문의 자동 응대", aiArea: "대화형 AI", startDate: "2024-07-01", endDate: "2025-01-31", effect: "응대 시간 50% 감소", createdAt: "2024-06-10" },
  { id: "AIP-009", title: "용접 품질 실시간 모니터링", team: "품질팀", manager: "강동원", status: "보류", goal: "용접 불량 감소", aiArea: "컴퓨터 비전", startDate: "2025-02-15", endDate: "2025-10-31", effect: "불량률 40% 감소", createdAt: "2025-02-01" },
  { id: "AIP-010", title: "AI 기반 채용 스크리닝", team: "경영지원팀", manager: "임수정", status: "아이디어", goal: "채용 효율화", aiArea: "NLP", startDate: "2025-05-01", endDate: "2025-11-30", effect: "스크리닝 시간 70% 단축", createdAt: "2025-03-20" },
  { id: "AIP-011", title: "예방 정비 스케줄링", team: "설비팀", manager: "김민수", status: "개발 완료", goal: "정비 최적화", aiArea: "예측 분석", startDate: "2024-04-01", endDate: "2024-11-30", effect: "정비 비용 22% 절감", createdAt: "2024-03-15" },
  { id: "AIP-012", title: "원자재 가격 예측", team: "물류팀", manager: "박준혁", status: "PoC", goal: "구매 전략 최적화", aiArea: "시계열 예측", startDate: "2025-03-15", endDate: "2025-09-30", effect: "구매 비용 8% 절감", createdAt: "2025-03-01" },
];

function StatusBadge({ status }) {
  const c = STATUS_COLORS[status] || STATUS_COLORS["보류"];
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 12px", borderRadius: 20, background: c.bg, color: c.text, fontSize: 12, fontWeight: 600, letterSpacing: "-0.02em", whiteSpace: "nowrap" }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: c.dot }} />
      {status}
    </span>
  );
}

function SummaryCard({ label, count, active, onClick, color }) {
  return (
    <button onClick={onClick} style={{
      flex: "1 1 0", minWidth: 100, padding: "20px 16px", background: active ? color : "#FFFFFF",
      border: active ? "none" : "1px solid #E9ECEF", borderRadius: 14, cursor: "pointer",
      transition: "all 0.25s cubic-bezier(.4,0,.2,1)", transform: active ? "translateY(-2px)" : "none",
      boxShadow: active ? `0 8px 25px ${color}44` : "0 1px 3px rgba(0,0,0,0.04)",
    }}>
      <div style={{ fontSize: 28, fontWeight: 800, color: active ? "#fff" : "#212529", letterSpacing: "-0.03em", fontFamily: "'Outfit', sans-serif" }}>{count}</div>
      <div style={{ fontSize: 12, fontWeight: 600, color: active ? "rgba(255,255,255,0.85)" : "#868E96", marginTop: 4, letterSpacing: "-0.01em" }}>{label}</div>
    </button>
  );
}

function Modal({ open, onClose, children }) {
  if (!open) return null;
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }} onClick={onClose}>
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.45)", backdropFilter: "blur(4px)" }} />
      <div onClick={e => e.stopPropagation()} style={{
        position: "relative", background: "#fff", borderRadius: 20, padding: "36px 32px 28px",
        width: "min(560px, 92vw)", maxHeight: "88vh", overflowY: "auto",
        boxShadow: "0 25px 60px rgba(0,0,0,0.2)", animation: "modalIn 0.3s ease"
      }}>
        {children}
      </div>
    </div>
  );
}

function DetailModal({ task, open, onClose, onStatusChange }) {
  if (!task) return null;
  const c = STATUS_COLORS[task.status];
  return (
    <Modal open={open} onClose={onClose}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, color: "#ADB5BD", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 6 }}>{task.id}</div>
          <h2 style={{ margin: 0, fontSize: 22, fontWeight: 800, color: "#212529", letterSpacing: "-0.03em" }}>{task.title}</h2>
        </div>
        <button onClick={onClose} style={{ background: "#F1F3F5", border: "none", borderRadius: 10, width: 36, height: 36, cursor: "pointer", fontSize: 18, color: "#868E96", display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px 24px", marginBottom: 24 }}>
        {[
          ["부서", task.team], ["담당자", task.manager],
          ["시작일", task.startDate], ["완료 예정일", task.endDate],
          ["AI 적용 영역", task.aiArea], ["등록일", task.createdAt],
        ].map(([l, v]) => (
          <div key={l}>
            <div style={{ fontSize: 11, fontWeight: 700, color: "#ADB5BD", marginBottom: 4, letterSpacing: "0.04em" }}>{l}</div>
            <div style={{ fontSize: 14, fontWeight: 600, color: "#495057" }}>{v}</div>
          </div>
        ))}
      </div>
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: "#ADB5BD", marginBottom: 4, letterSpacing: "0.04em" }}>목표</div>
        <div style={{ fontSize: 14, color: "#495057", lineHeight: 1.6 }}>{task.goal}</div>
      </div>
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: "#ADB5BD", marginBottom: 4, letterSpacing: "0.04em" }}>기대효과</div>
        <div style={{ fontSize: 14, color: "#495057", lineHeight: 1.6 }}>{task.effect}</div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "16px 0", borderTop: "1px solid #F1F3F5" }}>
        <span style={{ fontSize: 12, fontWeight: 700, color: "#868E96" }}>상태 변경</span>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {STATUSES.map(s => {
            const sc = STATUS_COLORS[s];
            const active = s === task.status;
            return (
              <button key={s} onClick={() => onStatusChange(task.id, s)} style={{
                padding: "6px 14px", borderRadius: 20, border: active ? "2px solid " + sc.dot : "1px solid #DEE2E6",
                background: active ? sc.bg : "#fff", color: active ? sc.text : "#868E96",
                fontSize: 12, fontWeight: 600, cursor: "pointer", transition: "all 0.2s"
              }}>{s}</button>
            );
          })}
        </div>
      </div>
    </Modal>
  );
}

export default function App() {
  const [tasks, setTasks] = useState(INITIAL_TASKS);
  const [filterStatus, setFilterStatus] = useState(null);
  const [filterTeam, setFilterTeam] = useState("");
  const [filterManager, setFilterManager] = useState("");
  const [keyword, setKeyword] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [detailTask, setDetailTask] = useState(null);
  const [sortCol, setSortCol] = useState(null);
  const [sortDir, setSortDir] = useState("asc");
  const [newTask, setNewTask] = useState({ title: "", team: DEPARTMENTS[0], manager: "", goal: "", aiArea: "", startDate: "", endDate: "", effect: "", status: "PoC" });
  const [errors, setErrors] = useState({});
  const tableRef = useRef(null);

  const statusCounts = useMemo(() => {
    const counts = { "전체": tasks.length };
    STATUSES.forEach(s => counts[s] = tasks.filter(t => t.status === s).length);
    return counts;
  }, [tasks]);

  const filtered = useMemo(() => {
    let r = [...tasks];
    if (filterStatus) r = r.filter(t => t.status === filterStatus);
    if (filterTeam) r = r.filter(t => t.team === filterTeam);
    if (filterManager) r = r.filter(t => t.manager.includes(filterManager));
    if (keyword) r = r.filter(t => t.title.includes(keyword) || t.id.includes(keyword) || t.goal.includes(keyword) || t.aiArea.includes(keyword));
    if (sortCol) {
      r.sort((a, b) => {
        const av = a[sortCol] || "", bv = b[sortCol] || "";
        return sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
      });
    }
    return r;
  }, [tasks, filterStatus, filterTeam, filterManager, keyword, sortCol, sortDir]);

  const managers = useMemo(() => [...new Set(tasks.map(t => t.manager))], [tasks]);

  function handleSort(col) {
    if (sortCol === col) { setSortDir(d => d === "asc" ? "desc" : "asc"); }
    else { setSortCol(col); setSortDir("asc"); }
  }

  function handleStatusChange(id, newStatus) {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, status: newStatus } : t));
    if (detailTask && detailTask.id === id) setDetailTask(prev => ({ ...prev, status: newStatus }));
  }

  function handleAddTask() {
    const errs = {};
    if (!newTask.title.trim()) errs.title = true;
    if (!newTask.manager.trim()) errs.manager = true;
    if (!newTask.startDate) errs.startDate = true;
    if (Object.keys(errs).length) { setErrors(errs); return; }
    const id = `AIP-${String(tasks.length + 1).padStart(3, "0")}`;
    const created = new Date().toISOString().split("T")[0];
    setTasks(prev => [{ ...newTask, id, createdAt: created }, ...prev]);
    setNewTask({ title: "", team: DEPARTMENTS[0], manager: "", goal: "", aiArea: "", startDate: "", endDate: "", effect: "", status: "PoC" });
    setErrors({});
    setShowAddModal(false);
  }

  function clearFilters() { setFilterStatus(null); setFilterTeam(""); setFilterManager(""); setKeyword(""); }

  const SortIcon = ({ col }) => {
    if (sortCol !== col) return <span style={{ opacity: 0.25, marginLeft: 4 }}>↕</span>;
    return <span style={{ marginLeft: 4, color: "#3B5BDB" }}>{sortDir === "asc" ? "↑" : "↓"}</span>;
  };

  const summaryColors = ["#343A40", "#3B5BDB", "#E8590C", "#7048E8", "#0CA678", "#2B8A3E", "#868E96"];

  return (
    <div style={{ minHeight: "100vh", background: "#F8F9FA", fontFamily: "'Pretendard', 'Outfit', -apple-system, sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap');
        @keyframes modalIn { from { opacity:0; transform: translateY(20px) scale(0.97); } to { opacity:1; transform: none; } }
        @keyframes fadeUp { from { opacity:0; transform: translateY(12px); } to { opacity:1; transform: none; } }
        @keyframes slideDown { from { opacity:0; transform: translateY(-8px); } to { opacity:1; transform: none; } }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: #CED4DA; border-radius: 3px; }
        input, select { font-family: inherit; }
        button { font-family: inherit; }
        tr { transition: background 0.15s; }
        tbody tr:hover { background: #F1F3F5 !important; }
      `}</style>

      {/* Header */}
      <header style={{
        background: "linear-gradient(135deg, #1A1B2E 0%, #2D2B55 50%, #1A1B2E 100%)",
        padding: "28px 40px 24px", borderBottom: "1px solid rgba(255,255,255,0.06)"
      }}>
        <div style={{ maxWidth: 1320, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{
              width: 40, height: 40, borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center",
              background: "linear-gradient(135deg, #748FFC, #7048E8)", fontSize: 20, boxShadow: "0 4px 15px rgba(112,72,232,0.4)"
            }}>⚡</div>
            <div>
              <h1 style={{ margin: 0, color: "#fff", fontSize: 20, fontWeight: 800, letterSpacing: "-0.03em", fontFamily: "'Outfit', sans-serif" }}>AI 과제 관리</h1>
              <div style={{ color: "rgba(255,255,255,0.45)", fontSize: 12, fontWeight: 500, marginTop: 1 }}>Task Management Platform</div>
            </div>
          </div>
          <button onClick={() => setShowAddModal(true)} style={{
            display: "flex", alignItems: "center", gap: 8, padding: "10px 22px", background: "linear-gradient(135deg, #748FFC, #7048E8)",
            color: "#fff", border: "none", borderRadius: 12, fontSize: 14, fontWeight: 700, cursor: "pointer",
            boxShadow: "0 4px 15px rgba(112,72,232,0.35)", transition: "all 0.2s", letterSpacing: "-0.01em"
          }}>
            <span style={{ fontSize: 18, lineHeight: 1 }}>+</span> 과제 추가
          </button>
        </div>
      </header>

      <main style={{ maxWidth: 1320, margin: "0 auto", padding: "28px 40px 60px" }}>
        {/* Summary Cards */}
        <div style={{ display: "flex", gap: 10, marginBottom: 24, flexWrap: "wrap", animation: "fadeUp 0.5s ease" }}>
          <SummaryCard label="전체 과제" count={statusCounts["전체"]} active={!filterStatus} onClick={() => setFilterStatus(null)} color={summaryColors[0]} />
          {STATUSES.map((s, i) => (
            <SummaryCard key={s} label={s} count={statusCounts[s]} active={filterStatus === s} onClick={() => setFilterStatus(filterStatus === s ? null : s)} color={summaryColors[i + 1]} />
          ))}
        </div>

        {/* Filters */}
        <div style={{
          background: "#fff", borderRadius: 16, padding: "18px 24px", marginBottom: 20,
          border: "1px solid #E9ECEF", display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap",
          animation: "fadeUp 0.5s ease 0.1s both"
        }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: "#495057", marginRight: 4 }}>필터</div>
          <select value={filterTeam} onChange={e => setFilterTeam(e.target.value)} style={{
            padding: "8px 14px", borderRadius: 10, border: "1px solid #DEE2E6", fontSize: 13, color: "#495057",
            background: "#fff", outline: "none", cursor: "pointer", minWidth: 120
          }}>
            <option value="">전체 부서</option>
            {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
          <select value={filterManager} onChange={e => setFilterManager(e.target.value)} style={{
            padding: "8px 14px", borderRadius: 10, border: "1px solid #DEE2E6", fontSize: 13, color: "#495057",
            background: "#fff", outline: "none", cursor: "pointer", minWidth: 120
          }}>
            <option value="">전체 담당자</option>
            {managers.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
          <div style={{ flex: 1, minWidth: 200, position: "relative" }}>
            <span style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", fontSize: 14, color: "#ADB5BD" }}>🔍</span>
            <input value={keyword} onChange={e => setKeyword(e.target.value)} placeholder="과제명, ID, 키워드 검색..."
              style={{ width: "100%", padding: "8px 14px 8px 34px", borderRadius: 10, border: "1px solid #DEE2E6", fontSize: 13, outline: "none" }} />
          </div>
          {(filterStatus || filterTeam || filterManager || keyword) && (
            <button onClick={clearFilters} style={{
              padding: "8px 16px", borderRadius: 10, border: "1px solid #DEE2E6", background: "#F8F9FA",
              fontSize: 12, fontWeight: 600, color: "#868E96", cursor: "pointer"
            }}>초기화</button>
          )}
        </div>

        {/* Results count */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12, padding: "0 4px" }}>
          <div style={{ fontSize: 13, color: "#868E96", fontWeight: 600 }}>
            총 <span style={{ color: "#3B5BDB", fontWeight: 800 }}>{filtered.length}</span>건
          </div>
        </div>

        {/* Table */}
        <div ref={tableRef} style={{
          background: "#fff", borderRadius: 16, border: "1px solid #E9ECEF", overflow: "hidden",
          animation: "fadeUp 0.5s ease 0.2s both", boxShadow: "0 1px 3px rgba(0,0,0,0.03)"
        }}>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ background: "#F8F9FB" }}>
                  {[
                    { key: "id", label: "ID", w: 90 },
                    { key: "title", label: "과제명", w: null },
                    { key: "team", label: "부서", w: 110 },
                    { key: "manager", label: "담당자", w: 90 },
                    { key: "status", label: "상태", w: 120 },
                    { key: "aiArea", label: "AI 영역", w: 120 },
                    { key: "startDate", label: "시작일", w: 100 },
                    { key: "endDate", label: "완료 예정일", w: 110 },
                  ].map(col => (
                    <th key={col.key} onClick={() => handleSort(col.key)} style={{
                      padding: "14px 16px", textAlign: "left", fontWeight: 700, color: "#868E96",
                      fontSize: 11, letterSpacing: "0.04em", textTransform: "uppercase", cursor: "pointer",
                      borderBottom: "1px solid #E9ECEF", whiteSpace: "nowrap", width: col.w || "auto",
                      userSelect: "none"
                    }}>
                      {col.label}<SortIcon col={col.key} />
                    </th>
                  ))}
                  <th style={{ padding: "14px 16px", borderBottom: "1px solid #E9ECEF", width: 80 }}></th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr><td colSpan={9} style={{ padding: 60, textAlign: "center", color: "#ADB5BD" }}>
                    <div style={{ fontSize: 36, marginBottom: 12 }}>📋</div>
                    <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>결과가 없습니다</div>
                    <div style={{ fontSize: 13 }}>필터 조건을 변경해 보세요</div>
                  </td></tr>
                ) : filtered.map((task, i) => (
                  <tr key={task.id} onClick={() => setDetailTask(task)}
                    style={{ cursor: "pointer", borderBottom: "1px solid #F1F3F5", animation: `slideDown 0.3s ease ${i * 0.03}s both` }}>
                    <td style={{ padding: "14px 16px", fontWeight: 700, color: "#ADB5BD", fontSize: 12, fontFamily: "'Outfit', monospace" }}>{task.id}</td>
                    <td style={{ padding: "14px 16px", fontWeight: 700, color: "#212529", letterSpacing: "-0.02em" }}>{task.title}</td>
                    <td style={{ padding: "14px 16px", color: "#495057", fontWeight: 500 }}>{task.team}</td>
                    <td style={{ padding: "14px 16px", color: "#495057", fontWeight: 500 }}>{task.manager}</td>
                    <td style={{ padding: "14px 16px" }}><StatusBadge status={task.status} /></td>
                    <td style={{ padding: "14px 16px", color: "#868E96", fontSize: 12, fontWeight: 500 }}>{task.aiArea}</td>
                    <td style={{ padding: "14px 16px", color: "#868E96", fontSize: 12, fontFamily: "'Outfit', monospace" }}>{task.startDate}</td>
                    <td style={{ padding: "14px 16px", color: "#868E96", fontSize: 12, fontFamily: "'Outfit', monospace" }}>{task.endDate}</td>
                    <td style={{ padding: "14px 16px" }}>
                      <select
                        value={task.status}
                        onClick={e => e.stopPropagation()}
                        onChange={e => handleStatusChange(task.id, e.target.value)}
                        style={{
                          padding: "4px 8px", borderRadius: 8, border: "1px solid #DEE2E6", fontSize: 11,
                          color: "#495057", background: "#F8F9FA", cursor: "pointer", outline: "none"
                        }}>
                        {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Add Task Modal */}
      <Modal open={showAddModal} onClose={() => { setShowAddModal(false); setErrors({}); }}>
        <h2 style={{ margin: "0 0 24px", fontSize: 22, fontWeight: 800, color: "#212529", letterSpacing: "-0.03em" }}>새 과제 등록</h2>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px 20px" }}>
          {[
            { key: "title", label: "과제명 *", type: "text", span: 2 },
            { key: "team", label: "부서", type: "select", options: DEPARTMENTS },
            { key: "manager", label: "담당자 *", type: "text" },
            { key: "aiArea", label: "AI 적용 영역", type: "text" },
            { key: "status", label: "현재 상태", type: "select", options: STATUSES },
            { key: "startDate", label: "시작일 *", type: "date" },
            { key: "endDate", label: "완료 예정일", type: "date" },
            { key: "goal", label: "목표", type: "text", span: 2 },
            { key: "effect", label: "기대효과", type: "text", span: 2 },
          ].map(field => (
            <div key={field.key} style={{ gridColumn: field.span === 2 ? "1 / -1" : "auto" }}>
              <label style={{ display: "block", fontSize: 11, fontWeight: 700, color: "#868E96", marginBottom: 6, letterSpacing: "0.04em" }}>{field.label}</label>
              {field.type === "select" ? (
                <select value={newTask[field.key]} onChange={e => setNewTask(p => ({ ...p, [field.key]: e.target.value }))}
                  style={{ width: "100%", padding: "10px 14px", borderRadius: 10, border: errors[field.key] ? "2px solid #FF6B6B" : "1px solid #DEE2E6", fontSize: 14, outline: "none", background: "#fff" }}>
                  {field.options.map(o => <option key={o} value={o}>{o}</option>)}
                </select>
              ) : (
                <input type={field.type} value={newTask[field.key]} onChange={e => { setNewTask(p => ({ ...p, [field.key]: e.target.value })); setErrors(p => ({ ...p, [field.key]: false })); }}
                  style={{ width: "100%", padding: "10px 14px", borderRadius: 10, border: errors[field.key] ? "2px solid #FF6B6B" : "1px solid #DEE2E6", fontSize: 14, outline: "none" }}
                  placeholder={field.label.replace(" *", "")} />
              )}
              {errors[field.key] && <div style={{ fontSize: 11, color: "#FF6B6B", marginTop: 4, fontWeight: 600 }}>필수 입력 항목입니다</div>}
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 28 }}>
          <button onClick={() => { setShowAddModal(false); setErrors({}); }} style={{
            padding: "10px 24px", borderRadius: 10, border: "1px solid #DEE2E6", background: "#fff",
            fontSize: 14, fontWeight: 600, color: "#868E96", cursor: "pointer"
          }}>취소</button>
          <button onClick={handleAddTask} style={{
            padding: "10px 28px", borderRadius: 10, border: "none",
            background: "linear-gradient(135deg, #748FFC, #7048E8)", color: "#fff",
            fontSize: 14, fontWeight: 700, cursor: "pointer", boxShadow: "0 4px 15px rgba(112,72,232,0.3)"
          }}>등록</button>
        </div>
      </Modal>

      {/* Detail Modal */}
      <DetailModal task={detailTask} open={!!detailTask} onClose={() => setDetailTask(null)} onStatusChange={handleStatusChange} />
    </div>
  );
}
