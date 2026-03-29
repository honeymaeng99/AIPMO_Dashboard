<template>
    <!-- ==================== 헤더 영역: 로고, 엑셀 다운로드, 다크모드 토글, 과제 추가 버튼 ==================== -->
    <header class="header">
      <div class="header-inner">
        <div class="logo">
          <div class="logo-icon">⚡</div>
          <div>
            <h1>MTC AI 과제 관리 플랫폼</h1>
            <div class="sub">MTC AI Project Management Platform</div>
          </div>
        </div>
        <div style="display:flex;gap:10px;align-items:center">
          <button class="btn-add"
            style="background:linear-gradient(135deg,#2B8A3E,#20C997);box-shadow:0 4px 15px rgba(43,138,62,.35)"
            @click="exportExcel">
            <span style="font-size:16px;line-height:1">📥</span> 엑셀 다운로드
          </button>

          <button class="btn-add"
            :style="{background: darkMode ? 'linear-gradient(135deg,#F59F00,#FF922B)' : 'linear-gradient(135deg,#343A40,#212529)', boxShadow: darkMode ? '0 4px 15px rgba(245,159,0,.35)' : '0 4px 15px rgba(33,37,41,.35)'}"
            @click="darkMode = !darkMode">
            <span style="font-size:16px;line-height:1">{{ darkMode ? '☀️' : '🌙' }}</span> {{ darkMode ? '라이트 모드' : '다크 모드' }}
          </button>

          <button class="btn-add" @click="showAdd = true">
            <span style="font-size:18px;line-height:1">+</span> 과제 추가
          </button>
        </div>
      </div>
    </header>

    <!-- ==================== 메인 콘텐츠 영역 ==================== -->
    <div class="main">

      <!-- 로딩 스피너 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <div>데이터를 불러오는 중...</div>
      </div>

      <template v-else>

        <!-- 상태별 요약 카드: 전체/기획/Data 확보/PoC 등 건수 표시, 클릭 시 필터 적용 -->
        <div class="summary">
          <div class="s-card" :class="{active: !filterStatuses.length}"
            :style="!filterStatuses.length ? 'background:#343A40;box-shadow:0 8px 25px #343A4044' : ''"
            @click="filterStatuses = []">
            <div class="num">{{ projects.length }}</div>
            <div class="lbl">전체 과제</div>
          </div>
          <div v-for="(s, i) in statuses" :key="s" class="s-card" :class="{active: filterStatuses.includes(s)}"
            :style="filterStatuses.includes(s) ? `background:${summaryColors[i+1]};box-shadow:0 8px 25px ${summaryColors[i+1]}44` : ''"
            @click="toggleFilter('status', s)">
            <div class="num">{{ countByStatus(s) }}</div>
            <div class="lbl">{{ s }}</div>
          </div>
        </div>

        <!-- 필터 바: 상태/도메인/실행팀 다중 선택 + 키워드 검색 -->
        <div class="filter-bar" @click.self="openFilter = null">
          <div class="f-label">필터</div>

          <!-- 상태 -->
          <div class="multi-select">
            <div class="ms-btn" @click.stop="openFilter = openFilter==='status' ? null : 'status'">
              {{ filterStatuses.length ? '상태' : '전체 상태' }}
              <span v-if="filterStatuses.length" class="ms-count">{{ filterStatuses.length }}</span>
              <span class="ms-arrow">▼</span>
            </div>
            <div v-if="openFilter==='status'" class="ms-dropdown" @click.stop>
              <div v-for="s in statuses" :key="s" class="ms-item" :class="{checked: filterStatuses.includes(s)}"
                @click="toggleFilter('status', s)">
                <div class="ms-check">{{ filterStatuses.includes(s) ? '✓' : '' }}</div>
                {{ s }}
              </div>
            </div>
          </div>

          <!-- 도메인 -->
          <div class="multi-select">
            <div class="ms-btn" @click.stop="openFilter = openFilter==='domain' ? null : 'domain'">
              {{ filterDomains.length ? '도메인' : '전체 도메인' }}
              <span v-if="filterDomains.length" class="ms-count">{{ filterDomains.length }}</span>
              <span class="ms-arrow">▼</span>
            </div>
            <div v-if="openFilter==='domain'" class="ms-dropdown" @click.stop>
              <div v-for="d in domains" :key="d" class="ms-item" :class="{checked: filterDomains.includes(d)}"
                @click="toggleFilter('domain', d)">
                <div class="ms-check">{{ filterDomains.includes(d) ? '✓' : '' }}</div>
                {{ d }}
              </div>
            </div>
          </div>

          <!-- 실행/대표팀 -->
          <div class="multi-select">
            <div class="ms-btn" @click.stop="openFilter = openFilter==='team' ? null : 'team'">
              {{ filterTeams.length ? '실행/대표팀' : '전체 실행/대표팀' }}
              <span v-if="filterTeams.length" class="ms-count">{{ filterTeams.length }}</span>
              <span class="ms-arrow">▼</span>
            </div>
            <div v-if="openFilter==='team'" class="ms-dropdown" @click.stop>
              <div v-for="d in teams" :key="d" class="ms-item" :class="{checked: filterTeams.includes(d)}"
                @click="toggleFilter('team', d)">
                <div class="ms-check">{{ filterTeams.includes(d) ? '✓' : '' }}</div>
                {{ d }}
              </div>
            </div>
          </div>

          <div class="search-wrap">
            <span class="ico">🔍</span>
            <input v-model="keyword" placeholder="과제명, ID, 키워드 검색..." @click.stop>
          </div>
          <button v-if="hasFilter" class="btn-reset" @click="clearFilters">초기화</button>
        </div>

        <!-- 결과 건수 표시 및 컬럼 편집 버튼 -->
        <div class="table-toolbar">
          <div class="result-count" style="margin-bottom:0">총 <span>{{ filtered.length }}</span>건</div>
          <button class="btn-col-edit" @click="showColPicker = true">⚙️ Column 수정</button>
        </div>

        <!-- 컬럼 선택 모달: 테이블에 표시할 컬럼을 사용자가 선택 -->
        <div v-if="showColPicker" class="col-picker-overlay" @click.self="showColPicker = false">
          <div class="col-picker-bg" @click="showColPicker = false"></div>
          <div class="col-picker">
            <h3>표시할 컬럼 선택</h3>
            <div class="col-picker-grid">
              <div v-for="col in allColumns" :key="col.key" class="col-picker-item"
                :class="{active: visibleCols.includes(col.key)}"
                :style="fixedCols.includes(col.key) ? {opacity:0.6, cursor:'default'} : {}" @click="toggleCol(col.key)">
                <div class="cp-check"
                  :style="fixedCols.includes(col.key) ? {background:'#ADB5BD',borderColor:'#ADB5BD'} : {}">
                  {{ visibleCols.includes(col.key) ? '✓' : '' }}</div>
                {{ col.label }}
              </div>
            </div>
            <div class="col-picker-footer">
              <button class="btn-cancel" style="padding:8px 16px;font-size:13px" @click="toggleAllCols">전체 선택</button>
              <button class="btn-submit" style="padding:8px 20px;font-size:13px"
                @click="showColPicker = false">확인</button>
            </div>
          </div>
        </div>

        <!-- 과제 목록 테이블: 좌우 스크롤 지원, 정렬/클릭 상세보기 -->
        <div class="table-outer">
          <div class="table-scroll-side left" @click="scrollTable(-300)" @mousemove="moveArrow($event, 'left')" @mouseleave="hideArrow('left')">
            <div class="arrow" ref="arrowLeft">&lt;</div>
          </div>
          <div class="table-scroll-side right" @click="scrollTable(300)" @mousemove="moveArrow($event, 'right')" @mouseleave="hideArrow('right')">
            <div class="arrow" ref="arrowRight">&gt;</div>
          </div>
        <div class="table-wrap">
          <div class="table-scroll" ref="tableScrollRef">
            <table :style="{minWidth: visibleCols.length > 7 ? visibleCols.length * 130 + 'px' : ''}">
              <thead>
                <tr>
                  <th v-for="col in activeColumns" :key="col.key" :style="{width: col.width||'', whiteSpace:'nowrap'}"
                    @click="toggleSort(col.key)">
                    {{ col.label }} <span class="si"
                      :style="{color: sortCol===col.key?'#3B5BDB':'', opacity: sortCol===col.key?1:0.25}">{{ sortIcon(col.key) }}</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filtered.length === 0">
                  <td :colspan="activeColumns.length">
                    <div class="empty">
                      <div class="icon">📋</div>
                      <div class="t">결과가 없습니다</div>
                      <div class="d">필터 조건을 변경해 보세요</div>
                    </div>
                  </td>
                </tr>
                <tr v-for="(p, i) in filtered" :key="p.id" @click="openDetail(p)"
                  :style="{animation: `slideRow .3s ease ${i*0.03}s both`}">
                  <td v-for="col in activeColumns" :key="col.key" :class="col.tdClass || ''">
                    <span v-if="col.key==='current_status'" class="badge"
                      :style="{background: sc(p.current_status).bg, color: sc(p.current_status).text}"><span class="dot"
                        :style="{background: sc(p.current_status).dot}"></span>{{ p.current_status }}</span>
                    <template v-else-if="col.bool">{{ p[col.key] ? 'YES' : 'NO' }}</template>
                    <template v-else>{{ p[col.key] ?? '-' }}</template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        </div><!-- table-outer -->

      </template>
    </div>

    <!-- ==================== 새 과제 등록 모달 ==================== -->
    <div v-if="showAdd" class="modal-overlay" @click.self="showAdd = false">
      <div class="modal-bg" @click="showAdd = false"></div>
      <div class="modal-box wide">
        <div class="modal-header">
          <h2>새 과제 등록</h2>
          <button class="btn-close" @click="showAdd = false">✕</button>
        </div>
        <div class="form-grid">

          <!-- ── 기본 정보 ── -->
          <div class="form-section-card sec-basic">
            <div class="form-section-title">
              <div class="sec-icon" style="background:#DCE4FF;color:#3B5BDB">📋</div>
              <span class="sec-text">기본 정보</span>
            </div>
            <div class="form-grid-inner">
              <div class="full f-item">
                <label>과제명 *</label>
                <input v-model="form.project_name" :class="{err: errors.project_name}" placeholder="과제명을 입력하세요">
                <div v-if="errors.project_name" class="err-msg">필수 입력</div>
              </div>
              <div class="f-item">
                <label>도메인 *</label>
                <select v-model="form.domain" :class="{err: errors.domain}">
                  <option value="">선택하세요</option>
                  <option v-for="d in domains" :key="d" :value="d">{{ d }}</option>
                </select>
                <div v-if="errors.domain" class="err-msg">필수 입력</div>
              </div>
              <div class="f-item">
                <label>과제 유형</label>
                <input v-model="form.projects_type" placeholder="예: 예측 분석, 컴퓨터 비전">
              </div>
              <div class="f-item">
                <label>현재 상태</label>
                <select v-model="form.current_status">
                  <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
                </select>
              </div>
              <div class="f-item">
                <label>협업 부서</label>
                <input v-model="form.collaboration_dept" placeholder="협업 부서">
              </div>
              <div class="full f-item">
                <label>과제 설명</label>
                <textarea v-model="form.project_description" placeholder="과제에 대한 설명"></textarea>
              </div>
            </div>
          </div>

          <!-- ── 조직 정보 ── -->
          <div class="form-section-card sec-org">
            <div class="form-section-title">
              <div class="sec-icon" style="background:#EDE5FF;color:#7048E8">👥</div>
              <span class="sec-text">조직 정보</span>
            </div>
            <div class="form-grid-inner" style="grid-template-columns:1fr 1fr 1fr">
              <div class="f-item">
                <label>실행/대표팀 *</label>
                <input v-model="form.owner_team" :class="{err: errors.owner_team}" placeholder="실행/대표팀">
                <div v-if="errors.owner_team" class="err-msg">필수 입력</div>
              </div>
              <div class="f-item">
                <label>대표 임원 *</label>
                <input v-model="form.executive_owner" :class="{err: errors.executive_owner}" placeholder="대표 임원">
                <div v-if="errors.executive_owner" class="err-msg">필수 입력</div>
              </div>
              <div class="f-item">
                <label>과제 리더 *</label>
                <input v-model="form.project_leader" :class="{err: errors.project_leader}" placeholder="과제 리더">
                <div v-if="errors.project_leader" class="err-msg">필수 입력</div>
              </div>
            </div>
          </div>

          <!-- ── 일정 ── -->
          <div class="form-section-card sec-schedule">
            <div class="form-section-title">
              <div class="sec-icon" style="background:#FFE0C2;color:#E8590C">📅</div>
              <span class="sec-text">일정</span>
            </div>
            <div class="form-grid-inner" style="grid-template-columns:1fr 1fr 1fr">
              <div class="f-item">
                <label>기획일</label>
                <input type="date" v-model="form.planning_date">
              </div>
              <div class="f-item">
                <label>Data 확보일</label>
                <input type="date" v-model="form.data_ready_date">
              </div>
              <div class="f-item">
                <label>PoC 일자</label>
                <input type="date" v-model="form.poc_date">
              </div>
              <div class="f-item">
                <label>MVP/Pilot 일자</label>
                <input type="date" v-model="form.mvp_pilot_date">
              </div>
              <div class="f-item">
                <label>전면적용일</label>
                <input type="date" v-model="form.full_deployment_date">
              </div>
            </div>
          </div>

          <!-- ── 성과 지표 ── -->
          <div class="form-section-card sec-perf">
            <div class="form-section-title">
              <div class="sec-icon" style="background:#C3E6CB;color:#2B8A3E">📊</div>
              <span class="sec-text">성과 지표</span>
            </div>
            <div class="form-grid-inner" style="grid-template-columns:repeat(4,1fr)">
              <div class="f-item">
                <label>성과지표 Y1</label>
                <input type="text" inputmode="decimal" v-model="form.performance_y1" placeholder="숫자 입력">
              </div>
              <div class="f-item">
                <label>성과지표 Y2</label>
                <input type="text" inputmode="decimal" v-model="form.performance_y2" placeholder="숫자 입력">
              </div>
              <div class="f-item">
                <label>성과지표 X1</label>
                <input type="text" inputmode="decimal" v-model="form.performance_x1" placeholder="숫자 입력">
              </div>
              <div class="f-item">
                <label>성과지표 X2</label>
                <input type="text" inputmode="decimal" v-model="form.performance_x2" placeholder="숫자 입력">
              </div>
            </div>
            <div class="form-grid-inner" style="margin-top:10px">
              <div class="full f-item">
                <label>기대효과</label>
                <input v-model="form.expected_impact" placeholder="기대효과">
              </div>
              <div class="f-item">
                <label>KPI</label>
                <input v-model="form.kpi" placeholder="KPI">
              </div>
              <div class="f-item">
                <label>재무 성과 (억 원)</label>
                <input type="text" inputmode="decimal" v-model="form.financial_performance" placeholder="예: 1.5">
              </div>
              <div class="full f-item">
                <label>프로세스 지표</label>
                <input v-model="form.process_metric" placeholder="프로세스 지표">
              </div>
            </div>
          </div>

          <!-- ── 전략 과제 ── -->
          <div class="form-section-card sec-strategy">
            <div class="form-section-title">
              <div class="sec-icon" style="background:#FDE68A;color:#B45309">⭐</div>
              <span class="sec-text">전략 과제 여부</span>
            </div>
            <div class="form-grid-inner" style="grid-template-columns:1fr 1fr 1fr">
              <label class="form-strategy-chip"
                style="margin:0;display:flex;align-items:center;justify-content:center;height:100%">
                <span class="chip-dot" :style="{background: form.mtc_strategic_project ? '#2B8A3E' : '#CED4DA'}"></span>
                <input type="checkbox" class="toggle-check" v-model="form.mtc_strategic_project" :true-value="1"
                  :false-value="0" style="display:none">
                MTC 전략 과제
                <span class="chip-status"
                  :style="{color: form.mtc_strategic_project ? '#2B8A3E' : '#ADB5BD'}">{{ form.mtc_strategic_project ? 'YES' : 'NO' }}</span>
              </label>
              <label class="form-strategy-chip"
                style="margin:0;display:flex;align-items:center;justify-content:center;height:100%">
                <span class="chip-dot" :style="{background: form.aic_strategic_project ? '#2B8A3E' : '#CED4DA'}"></span>
                <input type="checkbox" class="toggle-check" v-model="form.aic_strategic_project" :true-value="1"
                  :false-value="0" style="display:none">
                AIC 전략 과제
                <span class="chip-status"
                  :style="{color: form.aic_strategic_project ? '#2B8A3E' : '#ADB5BD'}">{{ form.aic_strategic_project ? 'YES' : 'NO' }}</span>
              </label>
              <label class="form-strategy-chip"
                style="margin:0;display:flex;align-items:center;justify-content:center;height:100%">
                <span class="chip-dot" :style="{background: form.dtc_strategic_project ? '#2B8A3E' : '#CED4DA'}"></span>
                <input type="checkbox" class="toggle-check" v-model="form.dtc_strategic_project" :true-value="1"
                  :false-value="0" style="display:none">
                DTC 전략 과제
                <span class="chip-status"
                  :style="{color: form.dtc_strategic_project ? '#2B8A3E' : '#ADB5BD'}">{{ form.dtc_strategic_project ? 'YES' : 'NO' }}</span>
              </label>
            </div>
          </div>

          <!-- ── GPU 자원 ── -->
          <div class="form-section-card sec-gpu">
            <div class="form-section-title">
              <div class="sec-icon" style="background:#D5D8DC;color:#495057">🖥️</div>
              <span class="sec-text">GPU 자원</span>
            </div>
            <div class="form-grid-inner" style="grid-template-columns:1fr 1fr 1fr">
              <div class="f-item">
                <label>현재 GPU 수량</label>
                <input type="text" inputmode="numeric" v-model="form.current_gpu_count" placeholder="숫자 입력">
              </div>
              <div class="f-item">
                <label>현재 GPU 사양</label>
                <input v-model="form.current_gpu_spec" placeholder="예: A100, H100">
              </div>
              <div class="f-item">
                <label>필요 GPU 수량</label>
                <input type="text" inputmode="numeric" v-model="form.required_gpu_count" placeholder="숫자 입력">
              </div>
              <div class="f-item">
                <label>필요 GPU 사양</label>
                <input v-model="form.required_gpu_spec" placeholder="예: B300">
              </div>
              <div class="f-item">
                <label>GPU 요청 B300 환산</label>
                <input type="text" inputmode="decimal" v-model="form.gpu_request_b300_equivalent" placeholder="숫자 입력">
              </div>
              <label class="f-item" style="cursor:pointer">
                <div class="lb" style="text-transform:uppercase">GPU 요청 승인</div>
                <input type="checkbox" v-model="form.gpu_request_approved" :true-value="1" :false-value="0"
                  style="display:none">
                <div style="display:flex;align-items:center;gap:6px;margin-top:8px">
                  <span
                    :style="{width:'10px',height:'10px',borderRadius:'50%',display:'inline-block',background: form.gpu_request_approved ? '#2B8A3E' : '#CED4DA'}"></span>
                  <span
                    :style="{color: form.gpu_request_approved ? '#2B8A3E' : '#ADB5BD', fontWeight:700, fontSize:'14px'}">{{ form.gpu_request_approved ? 'YES' : 'NO' }}</span>
                </div>
              </label>
            </div>
          </div>

          <!-- ── 기타 ── -->
          <div class="form-section-card sec-etc">
            <div class="form-section-title">
              <div class="sec-icon" style="background:#BAE0FF;color:#1C7ED6">💬</div>
              <span class="sec-text">기타</span>
            </div>
            <div class="f-item">
              <label>추가 지원 요청 사항</label>
              <textarea v-model="form.additional_support_request" placeholder="추가 지원이 필요한 사항을 입력하세요"></textarea>
            </div>
          </div>

        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showAdd = false">취소</button>
          <button class="btn-submit" @click="submitProject">등록</button>
        </div>
      </div>
    </div>

    <!-- ==================== 과제 상세보기/수정 모달 ==================== -->
    <div v-if="detail" class="modal-overlay" @click.self="detail = null">
      <div class="modal-bg" @click="detail = null"></div>
      <div class="modal-box wide" style="padding-top:20px">
        <!-- 헤더 바 -->
        <div class="detail-header-bar" style="position:relative">
          <span class="badge"
            :style="{background: sc(detail.current_status).bg, color: sc(detail.current_status).text, padding:'6px 14px', fontSize:'13px'}">
            <span class="dot" :style="{background: sc(detail.current_status).dot}"></span>{{ detail.current_status }}
          </span>
          <div style="flex:1">
            <div class="dh-id">{{ detail.id }}</div>
            <div class="dh-name">{{ editing ? '' : detail.project_name }}</div>
            <input v-if="editing" v-model="editForm.project_name" class="edit-input"
              style="font-size:18px;font-weight:800;margin-top:4px">
          </div>
          <div style="display:flex;gap:8px;align-items:center">
            <button v-if="!editing" class="btn-edit" @click="startEdit">✏️ 수정</button>
            <template v-if="editing">
              <button class="btn-save" @click="updateProject">💾 저장</button>
              <button class="btn-edit-cancel" @click="cancelEdit">취소</button>
            </template>
            <button class="btn-close" style="background:#495057;color:#fff;flex-shrink:0"
              @click="detail = null; editing = false">✕</button>
          </div>
        </div>

        <!-- ── 기본 정보 ── -->
        <div class="form-section-card sec-basic" style="margin-bottom:12px">
          <div class="form-section-title">
            <div class="sec-icon" style="background:#DCE4FF;color:#3B5BDB">📋</div>
            <span class="sec-text">기본 정보</span>
          </div>
          <div class="detail-grid">
            <div class="d-item">
              <div class="lb">도메인</div>
              <div v-if="!editing" class="vl">{{ detail.domain || '-' }}</div>
              <select v-else v-model="editForm.domain" class="edit-select">
                <option v-for="d in domains" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
            <div class="d-item">
              <div class="lb">과제 유형</div>
              <div v-if="!editing" class="vl">{{ detail.projects_type || '-' }}</div>
              <input v-else v-model="editForm.projects_type" class="edit-input" placeholder="과제 유형">
            </div>
            <div class="d-item">
              <div class="lb">현재 상태</div>
              <div class="vl">{{ detail.current_status || '-' }}</div>
            </div>
            <div class="d-item">
              <div class="lb">협업 부서</div>
              <div v-if="!editing" class="vl">{{ detail.collaboration_dept || '-' }}</div>
              <input v-else v-model="editForm.collaboration_dept" class="edit-input" placeholder="협업 부서">
            </div>
            <div class="d-item">
              <div class="lb">등록일</div>
              <div class="vl">{{ detail.created_at?.split('T')[0] || '-' }}</div>
            </div>
          </div>
          <div class="detail-sec" style="margin-top:4px">
            <div class="d-item">
              <div class="lb">과제 설명</div>
              <div v-if="!editing" class="vl" style="white-space:pre-line">{{ detail.project_description || '-' }}</div>
              <textarea v-else v-model="editForm.project_description" class="edit-textarea"
                placeholder="과제 설명"></textarea>
            </div>
          </div>
        </div>

        <!-- ── 조직 정보 ── -->
        <div class="form-section-card sec-org" style="margin-bottom:12px">
          <div class="form-section-title">
            <div class="sec-icon" style="background:#EDE5FF;color:#7048E8">👥</div>
            <span class="sec-text">조직 정보</span>
          </div>
          <div class="detail-grid" style="grid-template-columns:1fr 1fr 1fr">
            <div class="d-item">
              <div class="lb">실행/대표팀</div>
              <div v-if="!editing" class="vl">{{ detail.owner_team || '-' }}</div>
              <input v-else v-model="editForm.owner_team" class="edit-input" placeholder="실행/대표팀">
            </div>
            <div class="d-item">
              <div class="lb">대표 임원</div>
              <div v-if="!editing" class="vl">{{ detail.executive_owner || '-' }}</div>
              <input v-else v-model="editForm.executive_owner" class="edit-input" placeholder="대표 임원">
            </div>
            <div class="d-item">
              <div class="lb">과제 리더</div>
              <div v-if="!editing" class="vl">{{ detail.project_leader || '-' }}</div>
              <input v-else v-model="editForm.project_leader" class="edit-input" placeholder="과제 리더">
            </div>
          </div>
        </div>

        <!-- ── 일정 ── -->
        <div class="form-section-card sec-schedule" style="margin-bottom:12px">
          <div class="form-section-title">
            <div class="sec-icon" style="background:#FFE0C2;color:#E8590C">📅</div>
            <span class="sec-text">일정 목표</span>
          </div>
          <div class="detail-grid" style="grid-template-columns:repeat(3,1fr)">
            <div class="d-item">
              <div class="lb">기획일</div>
              <div v-if="!editing" class="vl">{{ detail.planning_date || '-' }}</div>
              <input v-else type="date" v-model="editForm.planning_date" class="edit-input">
            </div>
            <div class="d-item">
              <div class="lb">Data 확보일</div>
              <div v-if="!editing" class="vl">{{ detail.data_ready_date || '-' }}</div>
              <input v-else type="date" v-model="editForm.data_ready_date" class="edit-input">
            </div>
            <div class="d-item">
              <div class="lb">PoC 일자</div>
              <div v-if="!editing" class="vl">{{ detail.poc_date || '-' }}</div>
              <input v-else type="date" v-model="editForm.poc_date" class="edit-input">
            </div>
            <div class="d-item">
              <div class="lb">MVP/Pilot 일자</div>
              <div v-if="!editing" class="vl">{{ detail.mvp_pilot_date || '-' }}</div>
              <input v-else type="date" v-model="editForm.mvp_pilot_date" class="edit-input">
            </div>
            <div class="d-item">
              <div class="lb">전면적용일</div>
              <div v-if="!editing" class="vl">{{ detail.full_deployment_date || '-' }}</div>
              <input v-else type="date" v-model="editForm.full_deployment_date" class="edit-input">
            </div>
          </div>
        </div>

        <!-- ── 성과 지표 ── -->
        <div class="form-section-card sec-perf" style="margin-bottom:12px">
          <div class="form-section-title">
            <div class="sec-icon" style="background:#C3E6CB;color:#2B8A3E">📊</div>
            <span class="sec-text">성과 지표</span>
          </div>
          <div class="detail-grid" style="grid-template-columns:repeat(4,1fr)">
            <div class="d-item">
              <div class="lb">성과지표 Y1</div>
              <div v-if="!editing" class="vl">{{ detail.performance_y1 ?? '-' }}</div>
              <input v-else type="text" inputmode="decimal" v-model="editForm.performance_y1" class="edit-input"
                placeholder="숫자 입력">
            </div>
            <div class="d-item">
              <div class="lb">성과지표 Y2</div>
              <div v-if="!editing" class="vl">{{ detail.performance_y2 ?? '-' }}</div>
              <input v-else type="text" inputmode="decimal" v-model="editForm.performance_y2" class="edit-input"
                placeholder="숫자 입력">
            </div>
            <div class="d-item">
              <div class="lb">성과지표 X1</div>
              <div v-if="!editing" class="vl">{{ detail.performance_x1 ?? '-' }}</div>
              <input v-else type="text" inputmode="decimal" v-model="editForm.performance_x1" class="edit-input"
                placeholder="숫자 입력">
            </div>
            <div class="d-item">
              <div class="lb">성과지표 X2</div>
              <div v-if="!editing" class="vl">{{ detail.performance_x2 ?? '-' }}</div>
              <input v-else type="text" inputmode="decimal" v-model="editForm.performance_x2" class="edit-input"
                placeholder="숫자 입력">
            </div>
          </div>
          <div class="detail-grid" style="margin-top:8px">
            <div class="d-item">
              <div class="lb">KPI</div>
              <div v-if="!editing" class="vl">{{ detail.kpi || '-' }}</div>
              <input v-else v-model="editForm.kpi" class="edit-input" placeholder="KPI">
            </div>
            <div class="d-item">
              <div class="lb">재무 성과 (억 원)</div>
              <div v-if="!editing" class="vl">{{ detail.financial_performance ?? '-' }}</div>
              <input v-else type="text" inputmode="decimal" v-model="editForm.financial_performance" class="edit-input"
                placeholder="예: 1.5">
            </div>
          </div>
          <div class="detail-sec" style="margin-top:8px">
            <div class="d-item">
              <div class="lb">기대효과</div>
              <div v-if="!editing" class="vl">{{ detail.expected_impact || '-' }}</div>
              <input v-else v-model="editForm.expected_impact" class="edit-input" placeholder="기대효과">
            </div>
          </div>
          <div class="detail-sec">
            <div class="d-item">
              <div class="lb">프로세스 지표</div>
              <div v-if="!editing" class="vl">{{ detail.process_metric || '-' }}</div>
              <input v-else v-model="editForm.process_metric" class="edit-input" placeholder="프로세스 지표">
            </div>
          </div>
        </div>

        <!-- ── 전략 과제 ── -->
        <div class="form-section-card sec-strategy" style="margin-bottom:12px">
          <div class="form-section-title">
            <div class="sec-icon" style="background:#FDE68A;color:#B45309">⭐</div>
            <span class="sec-text">전략 과제 여부</span>
          </div>
          <div class="detail-strategy-inline">
            <label v-if="editing" class="form-strategy-chip" style="margin:0;cursor:pointer">
              <span class="chip-dot"
                :style="{background: editForm.mtc_strategic_project ? '#2B8A3E' : '#CED4DA'}"></span>
              <input type="checkbox" v-model="editForm.mtc_strategic_project" :true-value="1" :false-value="0"
                style="display:none">
              MTC 전략 과제
              <span class="chip-status"
                :style="{color: editForm.mtc_strategic_project ? '#2B8A3E' : '#ADB5BD'}">{{ editForm.mtc_strategic_project ? 'YES' : 'NO' }}</span>
            </label>
            <div v-else class="detail-strategy-chip">
              <span class="chip-dot" :style="{background: detail.mtc_strategic_project ? '#2B8A3E' : '#CED4DA'}"></span>
              MTC 전략 과제
              <strong
                :style="{marginLeft:'auto', color: detail.mtc_strategic_project ? '#2B8A3E' : '#ADB5BD'}">{{ detail.mtc_strategic_project ? 'YES' : 'NO' }}</strong>
            </div>
            <label v-if="editing" class="form-strategy-chip" style="margin:0;cursor:pointer">
              <span class="chip-dot"
                :style="{background: editForm.aic_strategic_project ? '#2B8A3E' : '#CED4DA'}"></span>
              <input type="checkbox" v-model="editForm.aic_strategic_project" :true-value="1" :false-value="0"
                style="display:none">
              AIC 전략 과제
              <span class="chip-status"
                :style="{color: editForm.aic_strategic_project ? '#2B8A3E' : '#ADB5BD'}">{{ editForm.aic_strategic_project ? 'YES' : 'NO' }}</span>
            </label>
            <div v-else class="detail-strategy-chip">
              <span class="chip-dot" :style="{background: detail.aic_strategic_project ? '#2B8A3E' : '#CED4DA'}"></span>
              AIC 전략 과제
              <strong
                :style="{marginLeft:'auto', color: detail.aic_strategic_project ? '#2B8A3E' : '#ADB5BD'}">{{ detail.aic_strategic_project ? 'YES' : 'NO' }}</strong>
            </div>
            <label v-if="editing" class="form-strategy-chip" style="margin:0;cursor:pointer">
              <span class="chip-dot"
                :style="{background: editForm.dtc_strategic_project ? '#2B8A3E' : '#CED4DA'}"></span>
              <input type="checkbox" v-model="editForm.dtc_strategic_project" :true-value="1" :false-value="0"
                style="display:none">
              DTC 전략 과제
              <span class="chip-status"
                :style="{color: editForm.dtc_strategic_project ? '#2B8A3E' : '#ADB5BD'}">{{ editForm.dtc_strategic_project ? 'YES' : 'NO' }}</span>
            </label>
            <div v-else class="detail-strategy-chip">
              <span class="chip-dot" :style="{background: detail.dtc_strategic_project ? '#2B8A3E' : '#CED4DA'}"></span>
              DTC 전략 과제
              <strong
                :style="{marginLeft:'auto', color: detail.dtc_strategic_project ? '#2B8A3E' : '#ADB5BD'}">{{ detail.dtc_strategic_project ? 'YES' : 'NO' }}</strong>
            </div>
          </div>
        </div>

        <!-- ── GPU 자원 ── -->
        <div class="form-section-card sec-gpu" style="margin-bottom:12px">
          <div class="form-section-title">
            <div class="sec-icon" style="background:#D5D8DC;color:#495057">🖥️</div>
            <span class="sec-text">GPU 자원</span>
          </div>
          <div class="detail-grid" style="grid-template-columns:repeat(3,1fr)">
            <div class="d-item">
              <div class="lb">현재 GPU 수량</div>
              <div v-if="!editing" class="vl">{{ detail.current_gpu_count ?? '-' }}</div>
              <input v-else type="text" inputmode="numeric" v-model="editForm.current_gpu_count" class="edit-input"
                placeholder="숫자 입력">
            </div>
            <div class="d-item">
              <div class="lb">현재 GPU 사양</div>
              <div v-if="!editing" class="vl">{{ detail.current_gpu_spec || '-' }}</div>
              <input v-else v-model="editForm.current_gpu_spec" class="edit-input" placeholder="예: A100, H100">
            </div>
            <div class="d-item">
              <div class="lb">필요 GPU 수량</div>
              <div v-if="!editing" class="vl">{{ detail.required_gpu_count ?? '-' }}</div>
              <input v-else type="text" inputmode="numeric" v-model="editForm.required_gpu_count" class="edit-input"
                placeholder="숫자 입력">
            </div>
            <div class="d-item">
              <div class="lb">필요 GPU 사양</div>
              <div v-if="!editing" class="vl">{{ detail.required_gpu_spec || '-' }}</div>
              <input v-else v-model="editForm.required_gpu_spec" class="edit-input" placeholder="예: B300">
            </div>
            <div class="d-item">
              <div class="lb">GPU 요청 B300 환산</div>
              <div v-if="!editing" class="vl">{{ detail.gpu_request_b300_equivalent ?? '-' }}</div>
              <input v-else type="text" inputmode="decimal" v-model="editForm.gpu_request_b300_equivalent"
                class="edit-input" placeholder="숫자 입력">
            </div>
            <div class="d-item">
              <div class="lb">GPU 요청 승인</div>
              <div v-if="!editing" class="vl" style="display:flex;align-items:center;gap:6px">
                <span
                  :style="{width:'10px',height:'10px',borderRadius:'50%',display:'inline-block',background: detail.gpu_request_approved ? '#2B8A3E' : '#CED4DA'}"></span>
                <span
                  :style="{color: detail.gpu_request_approved ? '#2B8A3E' : '#ADB5BD', fontWeight:700}">{{ detail.gpu_request_approved ? 'YES' : 'NO' }}</span>
              </div>
              <label v-else class="edit-checkbox-wrap">
                <input type="checkbox" v-model="editForm.gpu_request_approved" :true-value="1" :false-value="0"
                  style="display:none">
                <span
                  :style="{width:'10px',height:'10px',borderRadius:'50%',display:'inline-block',background: editForm.gpu_request_approved ? '#2B8A3E' : '#CED4DA'}"></span>
                <span
                  :style="{color: editForm.gpu_request_approved ? '#2B8A3E' : '#ADB5BD', fontWeight:700, fontSize:'14px'}">{{ editForm.gpu_request_approved ? 'YES' : 'NO' }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- ── 기타 ── -->
        <div class="form-section-card sec-etc" style="margin-bottom:12px">
          <div class="form-section-title">
            <div class="sec-icon" style="background:#BAE0FF;color:#1C7ED6">💬</div>
            <span class="sec-text">기타</span>
          </div>
          <div class="detail-sec">
            <div class="d-item">
              <div class="lb">추가 지원 요청 사항</div>
              <div v-if="!editing" class="vl" style="white-space:pre-line">{{ detail.additional_support_request || '-' }}</div>
              <textarea v-else v-model="editForm.additional_support_request" class="edit-textarea"
                placeholder="추가 지원 요청 사항"></textarea>
            </div>
          </div>
        </div>

        <!-- ── 상태 변경 ── -->
        <div class="status-bar">
          <span class="tit">상태 변경</span>
          <div class="status-btns">
            <button v-for="s in statuses" :key="s" class="s-btn"
              :style="{border: s===detail.current_status ? '2px solid '+sc(s).dot : '1px solid #DEE2E6', background: s===detail.current_status ? sc(s).bg : '#fff', color: s===detail.current_status ? sc(s).text : '#868E96'}"
              @click="changeStatus(detail, s)">{{ s }}</button>
          </div>
        </div>

        <!-- 변경 이력 -->
        <div v-if="history.length" class="history-section">
          <h4>변경 이력</h4>
          <div v-for="h in history" :key="h.id" class="history-item">
            <span class="badge"
              :style="{background: sc(h.before_status).bg, color: sc(h.before_status).text, padding:'2px 8px', fontSize:'11px'}"><span
                class="dot"
                :style="{background: sc(h.before_status).dot, width:'5px',height:'5px'}"></span>{{ h.before_status }}</span>
            <span class="arrow">→</span>
            <span class="badge"
              :style="{background: sc(h.after_status).bg, color: sc(h.after_status).text, padding:'2px 8px', fontSize:'11px'}"><span
                class="dot"
                :style="{background: sc(h.after_status).dot, width:'5px',height:'5px'}"></span>{{ h.after_status }}</span>
            <span style="font-size:11px;color:#868E96">{{ h.changed_by }}</span>
            <span class="time">{{ h.changed_at?.split('T')[0] }}</span>
          </div>
        </div>

        <div class="modal-footer" style="margin-top:24px">
          <button class="btn-delete" @click="deleteProject(detail.id)">삭제</button>
          <button class="btn-cancel" @click="detail = null">닫기</button>
        </div>
      </div>
    </div>

    <!-- AI 채팅 플로팅 버튼 (FAB) -->
    <button class="chat-fab" @click="showChat = !showChat" :title="showChat ? '채팅 닫기' : 'AI 어시스턴트'">
      {{ showChat ? '✕' : '🤖' }}
    </button>

    <!-- AI 채팅 윈도우: 사용자 질문 입력 및 응답 표시 -->
    <div v-if="showChat" class="chat-window">
      <div class="chat-header">
        <div class="ch-icon">🤖</div>
        <div>
          <div class="ch-title">AI 어시스턴트</div>
          <div class="ch-sub">과제에 대해 물어보세요</div>
        </div>
        <button class="ch-close" @click="showChat = false">✕</button>
      </div>
      <div class="chat-body" ref="chatBodyRef">
        <div v-for="(m, i) in chatMessages" :key="i" class="chat-msg" :class="m.role">{{ m.text }}</div>
      </div>
      <div class="chat-input-wrap">
        <input v-model="chatInput" placeholder="질문을 입력하세요..." @keyup.enter="sendChat">
        <button class="chat-send" @click="sendChat">➤</button>
      </div>
    </div>

    <!-- 알림 토스트 메시지 (성공/오류) -->
    <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.msg }}</div>
</template>

<script setup>
/**
 * App.vue - 메인 컴포넌트 (Composition API + script setup)
 * 과제 CRUD, 필터링, 정렬, 엑셀 다운로드, AI 채팅 등 전체 기능을 담당한다.
 */
import { ref, computed, onMounted, watch } from 'vue'
import * as XLSX from 'xlsx'  // 엑셀 파일 생성 라이브러리

// API 기본 경로 (Vite 프록시를 통해 백엔드로 전달)
const API = '/api'

// 상태별 색상 매핑 (배지 표시용)
const STATUS_COLORS = {
  "기획": { bg: "#F0F4FF", text: "#3B5BDB", dot: "#3B5BDB" },
  "Data 확보": { bg: "#FFF9DB", text: "#E67700", dot: "#E67700" },
  "PoC": { bg: "#FFF4E6", text: "#E8590C", dot: "#E8590C" },
  "MVP/Pilot": { bg: "#F3F0FF", text: "#7048E8", dot: "#7048E8" },
  "전면적용": { bg: "#EBFBEE", text: "#2B8A3E", dot: "#2B8A3E" },
  "Pending/Drop": { bg: "#F1F3F5", text: "#868E96", dot: "#868E96" },
}

// 상수 정의: 과제 상태 목록, 도메인 목록, 요약 카드 색상
const statuses = ["기획", "Data 확보", "PoC", "MVP/Pilot", "전면적용", "Pending/Drop"]
const domains = ["생산", "설비", "수율/품질"]
const summaryColors = ["#343A40", "#3B5BDB", "#E67700", "#E8590C", "#7048E8", "#2B8A3E", "#868E96"]

// ===== 다크 모드 =====
const darkMode = ref(false)
watch(darkMode, (v) => {
  document.documentElement.classList.toggle('dark', v)
})

// ===== 반응형 상태 변수 =====
const projects = ref([])           // 전체 과제 목록
const loading = ref(true)          // 데이터 로딩 상태
const filterStatuses = ref([])     // 상태 필터 (다중 선택)
const filterDomains = ref([])      // 도메인 필터 (다중 선택)
const filterTeams = ref([])        // 실행/대표팀 필터 (다중 선택)
const keyword = ref("")            // 검색 키워드
const openFilter = ref(null)       // 현재 열린 필터 드롭다운
const sortCol = ref(null)          // 정렬 기준 컬럼
const sortDir = ref("asc")        // 정렬 방향 (asc/desc)

// ===== 테이블 컬럼 설정: key(DB 필드명), label(표시명), width, tdClass(셀 스타일) =====
const allColumns = [
  { key: 'id', label: 'ID', width: '90px', tdClass: 'td-id' },
  { key: 'current_status', label: '상태', width: '130px' },
  { key: 'project_name', label: '과제명', width: '220px', tdClass: 'td-title' },
  { key: 'domain', label: '도메인', width: '100px', tdClass: 'td-text' },
  { key: 'projects_type', label: '과제 유형', width: '120px', tdClass: 'td-sub' },
  { key: 'owner_team', label: '실행/대표팀', width: '110px', tdClass: 'td-text' },
  { key: 'executive_owner', label: '대표 임원', width: '90px', tdClass: 'td-text' },
  { key: 'project_leader', label: '실무 리더', width: '90px', tdClass: 'td-text' },
  { key: 'collaboration_dept', label: '협업 부서', width: '100px', tdClass: 'td-text' },
  { key: 'planning_date', label: '기획일', width: '100px', tdClass: 'td-date' },
  { key: 'data_ready_date', label: 'Data 확보일', width: '110px', tdClass: 'td-date' },
  { key: 'poc_date', label: 'PoC 일자', width: '100px', tdClass: 'td-date' },
  { key: 'mvp_pilot_date', label: 'MVP/Pilot 일자', width: '120px', tdClass: 'td-date' },
  { key: 'full_deployment_date', label: '전면적용일', width: '110px', tdClass: 'td-date' },
  { key: 'performance_y1', label: '성과지표 Y1', width: '100px', tdClass: 'td-text' },
  { key: 'performance_y2', label: '성과지표 Y2', width: '100px', tdClass: 'td-text' },
  { key: 'performance_x1', label: '성과지표 X1', width: '100px', tdClass: 'td-text' },
  { key: 'performance_x2', label: '성과지표 X2', width: '100px', tdClass: 'td-text' },
  { key: 'expected_impact', label: '기대효과', width: '140px', tdClass: 'td-text' },
  { key: 'kpi', label: 'KPI', width: '100px', tdClass: 'td-text' },
  { key: 'financial_performance', label: '재무 성과 (억 원)', width: '140px', tdClass: 'td-text' },
  { key: 'process_metric', label: '프로세스 지표', width: '120px', tdClass: 'td-text' },
  { key: 'mtc_strategic_project', label: 'MTC 전략 과제', width: '120px', tdClass: 'td-text', bool: true },
  { key: 'aic_strategic_project', label: 'AIC 전략 과제', width: '120px', tdClass: 'td-text', bool: true },
  { key: 'dtc_strategic_project', label: 'DTC 전략 과제', width: '120px', tdClass: 'td-text', bool: true },
  { key: 'current_gpu_count', label: '현재 GPU 수량', width: '120px', tdClass: 'td-text' },
  { key: 'current_gpu_spec', label: '현재 GPU 사양', width: '120px', tdClass: 'td-text' },
  { key: 'required_gpu_count', label: '필요 GPU 수량', width: '120px', tdClass: 'td-text' },
  { key: 'required_gpu_spec', label: '필요 GPU 사양', width: '120px', tdClass: 'td-text' },
  { key: 'gpu_request_approved', label: 'GPU 요청 승인', width: '120px', tdClass: 'td-text', bool: true },
  { key: 'gpu_request_b300_equivalent', label: 'GPU B300 환산', width: '120px', tdClass: 'td-text' },
  { key: 'additional_support_request', label: '추가 지원 요청', width: '140px', tdClass: 'td-text' },
  { key: 'created_at', label: '등록일', width: '100px', tdClass: 'td-date' },
  { key: 'updated_at', label: '수정일', width: '100px', tdClass: 'td-date' },
]
// 기본으로 표시할 컬럼 목록
const defaultVisibleCols = ['id', 'current_status', 'project_name', 'domain', 'owner_team',
  'executive_owner', 'project_leader', 'projects_type', 'planning_date'
]
const showColPicker = ref(false)
const visibleCols = ref([...defaultVisibleCols])
// 현재 표시 중인 컬럼 객체 배열 (computed)
const activeColumns = computed(() => allColumns.filter(c => visibleCols.value.includes(c.key)))

// 항상 표시되는 고정 컬럼 (숨길 수 없음)
const fixedCols = ['id', 'current_status', 'project_name']

// 컬럼 표시/숨김 토글
function toggleCol(key) {
  if (fixedCols.includes(key)) return
  const idx = visibleCols.value.indexOf(key)
  if (idx !== -1) visibleCols.value.splice(idx, 1)
  else visibleCols.value.push(key)
}

// 전체 컬럼 선택/해제 토글
function toggleAllCols() {
  const optional = allColumns.filter(c => !fixedCols.includes(c.key)).map(c => c.key)
  const allOn = optional.every(k => visibleCols.value.includes(k))
  if (allOn) visibleCols.value = [...fixedCols]
  else visibleCols.value = allColumns.map(c => c.key)
}

// ===== 과제 등록 폼 =====
const showAdd = ref(false)
// 폼 초기값 생성 함수
const defaultForm = () => ({
  project_name: "",
  domain: "",
  projects_type: "",
  owner_team: "",
  executive_owner: "",
  project_leader: "",
  project_description: "",
  current_status: "기획",
  performance_y1: "",
  performance_y2: "",
  performance_x1: "",
  performance_x2: "",
  planning_date: "",
  data_ready_date: "",
  poc_date: "",
  mvp_pilot_date: "",
  full_deployment_date: "",
  collaboration_dept: "",
  mtc_strategic_project: 0,
  aic_strategic_project: 0,
  dtc_strategic_project: 0,
  current_gpu_count: "",
  current_gpu_spec: "",
  required_gpu_count: "",
  required_gpu_spec: "",
  gpu_request_approved: 0,
  gpu_request_b300_equivalent: "",
  additional_support_request: "",
  expected_impact: "",
  kpi: "",
  financial_performance: "",
  process_metric: ""
})
const form = ref(defaultForm())
const errors = ref({})

// ===== 상세보기/수정 관련 상태 =====
const detail = ref(null)           // 현재 선택된 과제 상세 정보
const history = ref([])            // 상태 변경 이력
const editing = ref(false)         // 수정 모드 여부
const editForm = ref({})           // 수정 폼 데이터

// 토스트 알림 상태
const toast = ref({ show: false, msg: "", type: "success" })

// ===== AI 채팅 및 테이블 스크롤 관련 =====
const showChat = ref(false)
const chatInput = ref("")
const tableScrollRef = ref(null)
const arrowLeft = ref(null)
const arrowRight = ref(null)
// 테이블 좌우 스크롤 이동
function scrollTable(amount) {
  if (tableScrollRef.value) {
    tableScrollRef.value.scrollLeft += amount
  }
}
// 스크롤 화살표 위치를 마우스 커서에 맞춰 이동
function moveArrow(e, side) {
  const arrow = side === 'left' ? arrowLeft.value : arrowRight.value
  const outer = e.currentTarget.parentElement
  if (arrow && outer) {
    const rect = outer.getBoundingClientRect()
    arrow.style.opacity = '1'
    arrow.style.top = (e.clientY - 11) + 'px'
    if (side === 'left') {
      arrow.style.left = (rect.left + 16) + 'px'
      arrow.style.right = ''
    } else {
      arrow.style.right = (window.innerWidth - rect.right + 16) + 'px'
      arrow.style.left = ''
    }
  }
}
function hideArrow(side) {
  const arrow = side === 'left' ? arrowLeft.value : arrowRight.value
  if (arrow) {
    arrow.style.opacity = '0'
  }
}

const chatBodyRef = ref(null)
const chatMessages = ref([{
  role: "ai",
  text: "안녕하세요! AI 어시스턴트입니다. 과제에 대해 궁금한 점을 물어보세요."
}])

// 토스트 알림 표시 (2.5초 후 자동 사라짐)
function showToast(msg, type = "success") {
  toast.value = { show: true, msg, type }
  setTimeout(() => toast.value.show = false, 2500)
}

// ===== API 호출 함수 =====
// 전체 과제 목록 조회
async function fetchProjects() {
  try {
    const res = await fetch(`${API}/projects`)
    projects.value = await res.json()
  } catch (e) {
    showToast("서버 연결 실패. server.py가 실행 중인지 확인하세요.", "error")
  } finally {
    loading.value = false
  }
}

// 특정 과제의 상태 변경 이력 조회
async function fetchHistory(projectId) {
  try {
    const res = await fetch(`${API}/projects/${projectId}/history`)
    history.value = await res.json()
  } catch (e) {
    history.value = []
  }
}

// ===== Computed (파생 상태) =====
const teams = computed(() => [...new Set(projects.value.map(p => p.owner_team).filter(Boolean))])     // 실행/대표팀 목록 (중복 제거)
const leaders = computed(() => [...new Set(projects.value.map(p => p.project_leader).filter(Boolean))]) // 과제 리더 목록
const hasFilter = computed(() => !!(filterStatuses.value.length || filterDomains.value.length || filterTeams.value.length || keyword.value))

// 필터 + 키워드 + 정렬이 적용된 과제 목록
const filtered = computed(() => {
  let r = [...projects.value]
  if (filterStatuses.value.length) r = r.filter(p => filterStatuses.value.includes(p.current_status))
  if (filterDomains.value.length) r = r.filter(p => filterDomains.value.includes(p.domain))
  if (filterTeams.value.length) r = r.filter(p => filterTeams.value.includes(p.owner_team))
  if (keyword.value) {
    const kw = keyword.value
    r = r.filter(p =>
      (p.project_name || '').includes(kw) ||
      (p.id || '').includes(kw) ||
      (p.project_description || '').includes(kw) ||
      (p.projects_type || '').includes(kw) ||
      (p.expected_impact || '').includes(kw) ||
      (p.owner_team || '').includes(kw) ||
      (p.executive_owner || '').includes(kw) ||
      (p.project_leader || '').includes(kw)
    )
  }
  if (sortCol.value) {
    const statusOrder = {
      "기획": 0,
      "Data 확보": 1,
      "PoC": 2,
      "MVP/Pilot": 3,
      "전면적용": 4,
      "Pending/Drop": 5
    }
    r.sort((a, b) => {
      let av, bv
      if (sortCol.value === 'current_status') {
        av = statusOrder[a.current_status] ?? 99
        bv = statusOrder[b.current_status] ?? 99
        return sortDir.value === "asc" ? av - bv : bv - av
      }
      av = (a[sortCol.value] || "").toString()
      bv = (b[sortCol.value] || "").toString()
      return sortDir.value === "asc" ? av.localeCompare(bv) : bv.localeCompare(av)
    })
  }
  return r
})

// 특정 상태의 과제 수 반환
function countByStatus(s) {
  return projects.value.filter(p => p.current_status === s).length
}

// 상태에 해당하는 색상 객체 반환
function sc(status) {
  return STATUS_COLORS[status] || STATUS_COLORS["Pending/Drop"]
}

// 모든 필터 초기화
function clearFilters() {
  filterStatuses.value = []
  filterDomains.value = []
  filterTeams.value = []
  keyword.value = ""
  openFilter.value = null
}

// 필터 값 토글 (선택/해제)
function toggleFilter(type, val) {
  const map = {
    status: filterStatuses,
    domain: filterDomains,
    team: filterTeams
  }
  const arr = map[type]
  const idx = arr.value.indexOf(val)
  if (idx !== -1) arr.value.splice(idx, 1)
  else arr.value.push(val)
}

// 테이블 컬럼 정렬 토글 (오름차순 <-> 내림차순)
function toggleSort(col) {
  if (sortCol.value === col) sortDir.value = sortDir.value === "asc" ? "desc" : "asc"
  else {
    sortCol.value = col
    sortDir.value = "asc"
  }
}

// 정렬 방향 아이콘 반환
function sortIcon(col) {
  return sortCol.value === col ? (sortDir.value === "asc" ? "↑" : "↓") : "↕"
}

// ===== 과제 등록: 유효성 검사 후 POST 요청 =====
async function submitProject() {
  const errs = {}
  if (!form.value.project_name.trim()) errs.project_name = true
  if (!form.value.domain) errs.domain = true
  if (!form.value.owner_team?.trim()) errs.owner_team = true
  if (!form.value.executive_owner?.trim()) errs.executive_owner = true
  if (!form.value.project_leader?.trim()) errs.project_leader = true
  errors.value = errs
  if (Object.keys(errs).length) return

  // 숫자 필드 검증
  const numericFields = {
    performance_y1: '성과 Y1', performance_y2: '성과 Y2',
    performance_x1: '성과 X1', performance_x2: '성과 X2',
    financial_performance: '재무 성과',
    gpu_request_b300_equivalent: 'B300 환산',
    current_gpu_count: '현재 GPU 수', required_gpu_count: '필요 GPU 수'
  }
  for (const [k, label] of Object.entries(numericFields)) {
    const v = form.value[k]
    if (v !== "" && v !== null && v !== undefined && isNaN(Number(v))) {
      showToast(`"${label}" 항목에는 숫자만 입력할 수 있습니다.`, "error")
      return
    }
  }

  // null 처리: 빈 문자열은 null로 변환
  const payload = {}
  for (const [k, v] of Object.entries(form.value)) {
    payload[k] = (v === "" || v === null) ? null : v
  }
  // 숫자 필드 변환 (REAL)
  ;['financial_performance', 'performance_y1', 'performance_y2', 'performance_x1', 'performance_x2',
    'gpu_request_b300_equivalent'
  ].forEach(k => {
    if (payload[k] != null) payload[k] = parseFloat(payload[k]) || null
  })
  // 정수 필드 변환 (INTEGER)
  ;['current_gpu_count', 'required_gpu_count'].forEach(k => {
    if (payload[k] != null) payload[k] = parseInt(payload[k]) || null
  })
  // domain과 project_name은 반드시 포함
  payload.domain = form.value.domain
  payload.project_name = form.value.project_name

  try {
    const res = await fetch(`${API}/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error()
    await fetchProjects()
    showAdd.value = false
    form.value = defaultForm()
    errors.value = {}
    showToast("과제가 등록되었습니다")
  } catch (e) {
    showToast("등록 실패", "error")
  }
}

// ===== 상태 변경: 확인 후 PATCH 요청, 이력 자동 기록 =====
async function changeStatus(project, newStatus) {
  if (project.current_status === newStatus) return
  const ok = confirm(`과제 상태를 "${project.current_status}" → "${newStatus}"(으)로 변경하시겠습니까?`)
  if (!ok) return
  try {
    const res = await fetch(`${API}/projects/${project.id}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus, changed_by: "관리자" })
    })
    if (!res.ok) throw new Error()
    const updated = await res.json()
    const idx = projects.value.findIndex(p => p.id === project.id)
    if (idx !== -1) projects.value[idx] = updated
    if (detail.value && detail.value.id === project.id) {
      detail.value = updated
      fetchHistory(project.id)
    }
    showToast(`상태 변경: ${newStatus}`)
  } catch (e) {
    showToast("상태 변경 실패", "error")
  }
}

// ===== AI 채팅: 메시지 전송 (현재 목업, 추후 AI API 연동 예정) =====
function sendChat() {
  const msg = chatInput.value.trim()
  if (!msg) return
  chatMessages.value.push({ role: "user", text: msg })
  chatInput.value = ""
  // TODO: 실제 AI API 연동
  setTimeout(() => {
    chatMessages.value.push({
      role: "ai",
      text: "AI 기능은 현재 준비 중입니다. 곧 과제에 대한 질문에 답변할 수 있도록 업데이트될 예정입니다."
    })
    if (chatBodyRef.value) chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }, 500)
  setTimeout(() => {
    if (chatBodyRef.value) chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }, 50)
}

// ===== 엑셀 다운로드: 현재 필터된 목록을 .xlsx 파일로 내보내기 =====
function exportExcel() {
  const headers = {
    id: 'ID',
    current_status: '상태',
    project_name: '과제명',
    domain: '도메인',
    projects_type: '과제 유형',
    owner_team: '실행/대표팀',
    executive_owner: '대표 임원',
    project_leader: '실무 리더',
    project_description: '과제 설명',
    collaboration_dept: '협업 부서',
    planning_date: '기획일',
    data_ready_date: 'Data 확보일',
    poc_date: 'PoC 일자',
    mvp_pilot_date: 'MVP/Pilot 일자',
    full_deployment_date: '전면적용일',
    performance_y1: '성과지표 Y1',
    performance_y2: '성과지표 Y2',
    performance_x1: '성과지표 X1',
    performance_x2: '성과지표 X2',
    expected_impact: '기대효과',
    kpi: 'KPI',
    financial_performance: '재무 성과 (억 원)',
    process_metric: '프로세스 지표',
    mtc_strategic_project: 'MTC 전략 과제',
    aic_strategic_project: 'AIC 전략 과제',
    dtc_strategic_project: 'DTC 전략 과제',
    current_gpu_count: '현재 GPU 수량',
    current_gpu_spec: '현재 GPU 사양',
    required_gpu_count: '필요 GPU 수량',
    required_gpu_spec: '필요 GPU 사양',
    gpu_request_approved: 'GPU 요청 승인',
    gpu_request_b300_equivalent: 'GPU 요청 B300 환산',
    additional_support_request: '추가 지원 요청 사항',
    created_at: '등록일',
    updated_at: '수정일'
  }
  const cols = Object.keys(headers)
  const rows = filtered.value.map(p => {
    const row = {}
    cols.forEach(k => {
      let v = p[k]
      if (['mtc_strategic_project', 'aic_strategic_project', 'dtc_strategic_project',
          'gpu_request_approved'
        ].includes(k)) v = v ? 'YES' : 'NO'
      row[headers[k]] = v ?? ''
    })
    return row
  })
  const ws = XLSX.utils.json_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '과제 목록')
  XLSX.writeFile(wb, `MTC AI 과제 목록_${new Date().toISOString().slice(0,10)}.xlsx`)
  showToast(`${rows.length}건 엑셀 다운로드 완료`)
}

// ===== 상세 보기: 과제 클릭 시 상세 모달 열기 =====
function openDetail(project) {
  detail.value = { ...project }
  editing.value = false
  editForm.value = {}
  fetchHistory(project.id)
}

// ===== 수정: 관리자 코드 검증 후 수정 모드 진입 =====
async function startEdit() {
  const code = prompt("수정하려면 관리자 코드를 입력하세요:")
  if (!code) return
  try {
    const res = await fetch(`${API}/verify-admin`, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ admin_code: code }) })
    if (!res.ok) { showToast("관리자 코드가 올바르지 않습니다", "error"); return }
  } catch(e) { showToast("서버 연결 실패", "error"); return }
  editForm.value = { ...detail.value }
  editing.value = true
}

// 수정 취소
function cancelEdit() {
  editing.value = false
  editForm.value = {}
}

// 수정 내용 저장 (PUT 요청)
async function updateProject() {
  // 숫자 필드 검증
  const numericFields = {
    performance_y1: '성과 Y1', performance_y2: '성과 Y2',
    performance_x1: '성과 X1', performance_x2: '성과 X2',
    financial_performance: '재무 성과',
    gpu_request_b300_equivalent: 'B300 환산',
    current_gpu_count: '현재 GPU 수', required_gpu_count: '필요 GPU 수'
  }
  for (const [k, label] of Object.entries(numericFields)) {
    const v = editForm.value[k]
    if (v !== "" && v !== null && v !== undefined && isNaN(Number(v))) {
      showToast(`"${label}" 항목에는 숫자만 입력할 수 있습니다.`, "error")
      return
    }
  }

  const payload = {}
  for (const [k, v] of Object.entries(editForm.value)) {
    if (k === 'id' || k === 'created_at' || k === 'updated_at') continue
    payload[k] = (v === "" || v === null) ? null : v
  }
  ;['financial_performance', 'performance_y1', 'performance_y2', 'performance_x1', 'performance_x2',
    'gpu_request_b300_equivalent'
  ].forEach(k => {
    if (payload[k] != null) payload[k] = parseFloat(payload[k]) || null
  })
  ;['current_gpu_count', 'required_gpu_count'].forEach(k => {
    if (payload[k] != null) payload[k] = parseInt(payload[k]) || null
  })
  try {
    const res = await fetch(`${API}/projects/${detail.value.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error()
    const updated = await res.json()
    detail.value = updated
    const idx = projects.value.findIndex(p => p.id === updated.id)
    if (idx !== -1) projects.value[idx] = updated
    editing.value = false
    editForm.value = {}
    showToast("과제가 수정되었습니다")
  } catch (e) {
    showToast("수정 실패", "error")
  }
}

// ===== 삭제: 관리자 코드 검증 + 확인 후 소프트 삭제 (DELETE 요청) =====
async function deleteProject(projectId) {
  const code = prompt("삭제하려면 관리자 코드를 입력하세요:")
  if (!code) return
  try {
    const res = await fetch(`${API}/verify-admin`, { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ admin_code: code }) })
    if (!res.ok) { showToast("관리자 코드가 올바르지 않습니다", "error"); return }
  } catch(e) { showToast("서버 연결 실패", "error"); return }
  if (!confirm("정말 삭제하시겠습니까?")) return
  try {
    const res = await fetch(`${API}/projects/${projectId}`, { method: "DELETE" })
    if (!res.ok) throw new Error()
    await fetchProjects()
    detail.value = null
    showToast("삭제 완료")
  } catch (e) {
    showToast("삭제 실패", "error")
  }
}

// ===== 컴포넌트 마운트 시 초기화 =====
onMounted(() => {
  fetchProjects()  // 과제 목록 최초 로딩
  // 필터 드롭다운 외부 클릭 시 닫기
  document.addEventListener('click', () => {
    openFilter.value = null
  })
})
</script>
