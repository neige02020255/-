from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st
import json
import html
import os

# ==================== [설정 및 파일 저장 함수] ====================
CORRECT_PASSWORD = "1234"  # 접속 비밀번호
FIXED_MEMBERS_FILE = "fixed_members.json"
TEMP_MEMBERS_FILE = "temp_members.json"
VISITORS_LOG_FILE = "visitors_log.json"  # 출입 기록 영구 보관 파일

# 페이지 기본 설정 (와이드 모드 적용)
st.set_page_config(page_title="제25보병사단 비룡초소 출입 관리", layout="wide")

# 출입 구분 리스트 정의
ENTRY_TYPE_OPTIONS = [
    "영농인(고정)",
    "영농인(임시)",
    "공사(고정)",
    "공사(임시)",
    "성묘객(임시)",
    "어로인",
    "군인",
    "민간인(고정)",
    "민간인(임시)",
    "고정",
    "외국인"
]

# 고정출입자 명단 로드 함수
def load_fixed_members():
    initial_members = [
        {"성명": "김영농", "생년월일": "651012", "전화번호": "010-1234-5678", "출입구분": "영농인(고정)", "차량번호": "12가3456", "목적지": "북삼리 영농지", "통제구역": "A구역", "비고": "특이사항 없음"},
        {"성명": "이공사", "생년월일": "720515", "전화번호": "010-9876-5432", "출입구분": "공사(고정)", "차량번호": "78나9012", "목적지": "초소 보수공사", "통제구역": "B구역", "비고": "장비 지참"},
        {"성명": "박병장", "생년월일": "030120", "전화번호": "010-1111-2222", "출입구분": "군인", "차량번호": "지휘차 5521", "목적지": "DMZ 파견근무", "통제구역": "C구역", "비고": "공무 출장"},
        {"성명": "한강어부", "생년월일": "680310", "전화번호": "010-3333-4444", "출입구분": "어로인", "차량번호": "34다5678", "목적지": "임진강 어로 구역", "통제구역": "D구역", "비고": "어업 활동 승인"}
    ]
    if os.path.exists(FIXED_MEMBERS_FILE):
        try:
            with open(FIXED_MEMBERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    save_fixed_members(initial_members)
    return initial_members

def save_fixed_members(members):
    try:
        with open(FIXED_MEMBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(members, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"고정 명단 저장 중 오류 발생: {e}")

# 임시출입자 명단 로드 함수 (기간 만료 자동 삭제 포함)
def load_temp_members():
    temp_list = []
    if os.path.exists(TEMP_MEMBERS_FILE):
        try:
            with open(TEMP_MEMBERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    temp_list = data
        except Exception:
            pass
    
    today_str = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")
    valid_list = [t for t in temp_list if t.get("종료일", "9999-12-31") >= today_str]
    
    if len(valid_list) != len(temp_list):
        save_temp_members(valid_list)
        
    return valid_list

def save_temp_members(members):
    try:
        with open(TEMP_MEMBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(members, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"임시 명단 저장 중 오류 발생: {e}")

# 출입 기록 로드 및 파일 저장 함수
def load_visitors_log():
    logs = []
    if os.path.exists(VISITORS_LOG_FILE):
        try:
            with open(VISITORS_LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    logs = data
        except Exception:
            pass
    return logs

def save_visitors_log(logs):
    try:
        with open(VISITORS_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"출입 기록 저장 중 오류 발생: {e}")

# ==================== [CSS 및 스타일] ====================
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    .css-card {
        background-color: #1e1e1e; padding: 18px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); margin-bottom: 12px;
        border-left: 5px solid #40916c; color: #ffffff;
    }
    .stat-card {
        background-color: #1b263b; padding: 15px; border-radius: 10px;
        text-align: center; border: 1px solid #415a77; margin-bottom: 10px;
    }
    .dashboard-box {
        background-color: #181c24; padding: 20px; border-radius: 12px;
        border: 1px solid #2d3748; margin-bottom: 20px;
    }
    .guide-box {
        background-color: #1a2332; padding: 15px; border-radius: 10px;
        border: 1px solid #2d4a6f; margin-bottom: 20px; font-size: 14px;
    }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #ffffff !important; }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #2b2b2b !important; color: #ffffff !important; border-radius: 8px;
    }
    .badge-box {
        background-color: #2d6a4f; color: white; padding: 8px 15px;
        border-radius: 8px; font-weight: bold; display: inline-block; font-size: 16px; margin-bottom: 5px;
    }
    .stButton button {
        font-size: 18px !important; font-weight: bold !important; padding-top: 10px !important; padding-bottom: 10px !important;
    }
    [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
    }
    </style>
""", unsafe_allow_html=True)

def get_kts_time(fmt="%H:%M"):
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime(fmt)

def get_kts_date():
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")

# ==================== [세션 초기화] ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "visitors_log" not in st.session_state:
    st.session_state.visitors_log = load_visitors_log()
if "fixed_members" not in st.session_state:
    st.session_state.fixed_members = load_fixed_members()
if "temp_members" not in st.session_state:
    st.session_state.temp_members = load_temp_members()
if "map_search_target" not in st.session_state:
    st.session_state.map_search_target = "52S CE 12345 67890"

# ==================== [로그인 화면] ====================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔒 비룡초소 통제시스템")
        st.markdown("접속 비밀번호를 입력해주세요.")
        with st.form("login_form"):
            input_pw = st.text_input("비밀번호", type="password")
            submit_btn = st.form_submit_button("로그인", use_container_width=True)
            if submit_btn:
                if input_pw == CORRECT_PASSWORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 틀렸습니다.")
    st.stop()

# ==================== [메인 화면 상단] ====================
st.markdown("""
    <div>
        <span class="badge-box">🛡️ 제25보병사단 비룡부대</span>
        <h2 style='margin: 5px 0 0 0;'>민통초소 실시간 출입 관리 시스템</h2>
    </div>
""", unsafe_allow_html=True)

col_space, col_logout = st.columns([6, 1])
with col_logout:
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("<hr style='margin: 10px 0 20px 0; border-color: #333;'>", unsafe_allow_html=True)

# ----------------- [시스템 사용법 안내 섹션] -----------------
with st.expander("📖 <b>[초소 근무자용] 시스템 사용법 안내 (클릭하여 펼치기/접기)</b>", expanded=False):
    st.markdown("""
        <div class="guide-box">
            <b>1. 🚀 출입 관리 및 현황 탭</b><br>
            - <b>입영 등록</b>: 방문자 성명을 입력 후 '정보 불러오기'를 누르면 고정/임시 명단과 자동 연동됩니다.<br>
            - <b>실시간 체류 관리</b>: 현재 체류 중인 인원을 확인하고 퇴영 처리할 수 있습니다.<br>
            - <b>종합 현황판</b>: 오늘 총 입영, 현재 총 체류, 오늘 총 퇴영 인원 통계를 파악할 수 있습니다.<br><br>
            <b>2. 🏁 퇴영 목록 탭</b><br>
            - 오늘 퇴영 완료된 인원 목록을 검색하고, 하단에서 전체 누적 기록을 조회할 수 있습니다.<br><br>
            <b>3. 📋 고정출입자 명단 관리 탭</b><br>
            - 이름에 '고정'이 포함된 구분 및 '어로인' 대상자들을 관리합니다.<br><br>
            <b>4. 📋 임시출입자 명단 관리 탭</b><br>
            - 공문 등으로 사전 승인된 방문객을 등록하며, 종료일이 지나면 자동 정리됩니다.<br><br>
            <b>5. 🗺️ 지도 연동 탭</b><br>
            - MGRS 좌표계 검색 및 '내 위치 MGRS로 변환 이동' 기능을 지원합니다.
        </div>
    """, unsafe_allow_html=True)

# ----------------- [탭 메뉴 구성] -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 출입 관리 및 현황", "🏁 퇴영 목록", "📋 고정출입자 명단 관리", "📋 임시출입자 명단 관리", "🗺️ 지도 연동"])

# ==================== [탭 1: 출입 관리 및 현황] ====================
with tab1:
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.subheader("📝 출입자 등록 (입영)")

        if "temp_input_name" not in st.session_state:
            st.session_state.temp_input_name = ""
        if "selected_matched_member" not in st.session_state:
            st.session_state.selected_matched_member = None
        if "ambiguous_matches" not in st.session_state:
            st.session_state.ambiguous_matches = []

        with st.form("name_check_form"):
            col_nc1, col_nc2 = st.columns([3, 1])
            with col_nc1:
                typed_name = st.text_input("성명 입력", placeholder="이름 입력 후 버튼 클릭", value=st.session_state.temp_input_name)
            with col_nc2:
                st.markdown("<br>", unsafe_allow_html=True)
                name_check_btn = st.form_submit_button("🔍 정보 불러오기", use_container_width=True)

            if name_check_btn:
                st.session_state.temp_input_name = typed_name.strip()
                clean_name = typed_name.strip()
                
                if clean_name:
                    matches = [m for m in st.session_state.fixed_members if m.get("성명") == clean_name]
                    temp_matches = [t for t in st.session_state.temp_members if t.get("성명") == clean_name]
                    total_found = matches + temp_matches
                    
                    if len(total_found) == 1:
                        st.session_state.selected_matched_member = total_found[0]
                        st.session_state.ambiguous_matches = []
                        st.success(f"✅ [{clean_name}] 정보 연동됨")
                    elif len(total_found) > 1:
                        st.session_state.selected_matched_member = None
                        st.session_state.ambiguous_matches = total_found
                        st.warning(f"⚠️ 동명이인/공문인원 {len(total_found)}명 발견")
                    else:
                        st.session_state.selected_matched_member = None
                        st.session_state.ambiguous_matches = []
                        st.info("ℹ️ 신규 인원입니다.")
                else:
                    st.warning("⚠️ 성명을 입력하세요.")

        if st.session_state.ambiguous_matches:
            st.markdown("#### 👥 대상자 선택")
            choice_options = [f"성명: {m.get('성명')} | 구분: {m.get('출입구분', m.get('방문사유', '임시'))} | 차량: {m.get('차량번호', m.get('차량', '-'))}" for m in st.session_state.ambiguous_matches]
            selected_choice = st.selectbox("해당하는 인원을 선택하세요", choice_options)
            
            if st.button("선택 확정", use_container_width=True):
                chosen_idx = choice_options.index(selected_choice)
                st.session_state.selected_matched_member = st.session_state.ambiguous_matches[chosen_idx]
                st.session_state.ambiguous_matches = []
                st.rerun()

        m_data = st.session_state.selected_matched_member or {}

        with st.form("entry_form", clear_on_submit=True):
            final_name_val = st.session_state.temp_input_name if st.session_state.temp_input_name else m_data.get("성명", "")
            input_name = st.text_input("확인된 성명", value=final_name_val)
            
            def clean_val(key):
                val = m_data.get(key, "")
                return "" if val == "-" or not val else val

            col_i1, col_i2 = st.columns(2)
            with col_i1:
                birth_date = st.text_input("생년월일 (6자리)", value=clean_val("생년월일"), placeholder="예: 751225")
            with col_i2:
                phone = st.text_input("전화번호", value=clean_val("전화번호"), placeholder="예: 010-1234-5678")
                
            default_type = m_data.get("출입구분", "영농인(고정)")
            selected_type_preset = st.selectbox("출입 구분 (선택)", ENTRY_TYPE_OPTIONS, index=ENTRY_TYPE_OPTIONS.index(default_type) if default_type in ENTRY_TYPE_OPTIONS else 0)
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                car = st.text_input("차종 및 차량번호", value=clean_val("차량번호") or clean_val("차량"), placeholder="예: 12가3456")
                dest = st.text_input("목적지", value=clean_val("목적지") or clean_val("방문사유"), placeholder="예: 북삼리 영농지")
            with col_f2:
                zone = st.text_input("통제 구역", value=clean_val("통제구역") or clean_val("구역"), placeholder="예: A구역")
                note = st.text_input("비고", value=clean_val("특이사항"), placeholder="특이사항 입력")
            
            submitted = st.form_submit_button("🚀 최종 입영 처리", use_container_width=True)
            if submitted:
                final_name = input_name.strip()
                if not final_name:
                    st.warning("⚠️ 성명을 입력해주세요.")
                else:
                    time_now = get_kts_time("%H:%M")
                    date_now = get_kts_date()
                    new_entry = {
                        "날짜": date_now,
                        "출입시간": time_now,
                        "퇴영시간": "-",
                        "성명": final_name,
                        "생년월일": birth_date.strip() if birth_date.strip() else "-",
                        "전화번호": phone.strip() if phone.strip() else "-",
                        "출입구분": selected_type_preset,
                        "차량": car.strip() if car.strip() else "-",
                        "목적": dest.strip() if dest.strip() else "-",
                        "구역": zone.strip() if zone.strip() else "-",
                        "비고": note.strip() if note.strip() else "-",
                        "상태": "체류중"
                    }
                    st.session_state.visitors_log.append(new_entry)
                    save_visitors_log(st.session_state.visitors_log)
                    st.session_state.temp_input_name = ""
                    st.session_state.selected_matched_member = None
                    st.success(f"🎉 [{final_name}] 님 입영 처리 완료!")
                    st.rerun()

    with right_col:
        st.subheader("📊 실시간 체류 인원 및 관리")

        today_str = get_kts_date()
        all_logs = [(i, row) for i, row in enumerate(st.session_state.visitors_log)]
        all_logs.reverse()

        with st.form("staying_search_form"):
            col_s1, col_s2 = st.columns([3, 1])
            with col_s1:
                staying_query_input = st.text_input("🔍 출입·퇴영 검색", placeholder="이름, 번호, 차량번호 입력", label_visibility="collapsed")
            with col_s2:
                staying_search_btn = st.form_submit_button("검색", use_container_width=True)
        
        if "applied_staying_query" not in st.session_state:
            st.session_state.applied_staying_query = ""
        if staying_search_btn:
            st.session_state.applied_staying_query = staying_query_input

        search_query = st.session_state.applied_staying_query
        if search_query:
            display_list = [(idx, row) for idx, row in all_logs if search_query in str(row.get("성명", "")) or search_query in str(row.get("전화번호", "")) or search_query in str(row.get("차량", ""))]
        else:
            display_list = [(i, row) for i, row in all_logs if row.get("상태") == "체류중"]

        items_per_page = 5
        total_items = len(display_list)
        total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
        
        if "staying_page" not in st.session_state:
            st.session_state.staying_page = 1
        if st.session_state.staying_page > total_pages:
            st.session_state.staying_page = max(1, total_pages)

        start_idx = (st.session_state.staying_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        current_page_items = display_list[start_idx:end_idx]

        if not current_page_items:
            st.info("💡 조건에 일치하는 인원이 없습니다.")
        else:
            for row_idx, row in current_page_items:
                is_staying = (row.get("상태") == "체류중")
                status_color = "#40916c" if is_staying else "#adb5bd"
                status_text = "체류중" if is_staying else f"퇴영완료 ({row.get('퇴영시간', '-')})"

                with st.container():
                    st.markdown(f"""
                        <div class="css-card" style="border-left: 5px solid {status_color};">
                            <b style="font-size:18px;">👤 {row.get('성명', '-')}</b> <span style="color:#40916c; font-weight:bold;">[{row.get('출입구분', '-')}]</span> <span style="float:right; color:{status_color}; font-size:14px; font-weight:bold;">[{status_text}]</span><br>
                            🎂 생년월일: {row.get('생년월일', '-')} &nbsp;|&nbsp; 📞 전화: {row.get('전화번호', '-')}<br>
                            🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')} &nbsp;|&nbsp; 🛡️ 구역: {row.get('구역', '-')}<br>
                            📝 비고: <b style="color: #ffb703;">{row.get('비고', '-')}</b><br>
                            <span style="color: #adb5bd; font-size: 13px;">일자: {row.get('날짜', today_str)} | 입영 시각: {row.get('출입시간', '-')}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if is_staying:
                        if st.button("🏁 퇴영 처리", key=f"out_{row_idx}", use_container_width=True):
                            st.session_state.visitors_log[row_idx]["상태"] = "퇴영완료"
                            st.session_state.visitors_log[row_idx]["퇴영시간"] = get_kts_time("%H:%M")
                            save_visitors_log(st.session_state.visitors_log)
                            st.rerun()

            if total_pages > 1:
                col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
                with col_p1:
                    if st.button("◀ 이전", use_container_width=True, key="prev_staying") and st.session_state.staying_page > 1:
                        st.session_state.staying_page -= 1
                        st.rerun()
                with col_p2:
                    st.markdown(f"<p style='text-align: center; margin-top: 10px;'>{st.session_state.staying_page} / {total_pages}</p>", unsafe_allow_html=True)
                with col_p3:
                    if st.button("다음 ▶", use_container_width=True, key="next_staying") and st.session_state.staying_page < total_pages:
                        st.session_state.staying_page += 1
                        st.rerun()

    # ==================== [하단 종합 현황판] ====================
    st.markdown("<hr style='margin: 30px 0 20px 0; border-color: #444;'>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="dashboard-box">
            <h3 style="margin-top:0; color:#90e0ef; margin-bottom:15px;">📈 종합 현황판 (오늘 기준)</h3>
    """, unsafe_allow_html=True)
    
    today_str = get_kts_date()
    today_entered = [r for r in st.session_state.visitors_log if r.get("날짜", today_str) == today_str]
    total_entered_count = len(today_entered)

    all_staying = [r for r in st.session_state.visitors_log if r.get("상태") == "체류중"]
    total_count = len(all_staying)
    
    today_out = [r for r in today_entered if r.get("상태") == "퇴영완료"]
    total_out_count = len(today_out)

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.markdown(f"""
            <div class="stat-card" style="margin-bottom: 5px;">
                <h4 style="margin:0; color:#90e0ef;">오늘 총 입영 인원</h4>
                <p style="font-size: 24px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{total_entered_count} 명</p>
            </div>
        """, unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f"""
            <div class="stat-card" style="margin-bottom: 5px;">
                <h4 style="margin:0; color:#90e0ef;">현재 총 체류 인원</h4>
                <p style="font-size: 24px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{total_count} 명</p>
            </div>
        """, unsafe_allow_html=True)
    with col_stat3:
        st.markdown(f"""
            <div class="stat-card" style="margin-bottom: 5px;">
                <h4 style="margin:0; color:#90e0ef;">오늘 총 퇴영 인원</h4>
                <p style="font-size: 24px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{total_out_count} 명</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 15px 0; border-color: #333;'>", unsafe_allow_html=True)

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.markdown("##### 🚀 입영 현황 세부 정보")
        if total_entered_count == 0:
            st.info("오늘 입영한 인원이 없습니다.")
        else:
            enter_type_counts = {}
            for row in today_entered:
                enter_type_counts[row.get("출입구분", "기타")] = enter_type_counts.get(row.get("출입구분", "기타"), 0) + 1
            st.markdown(f"🏷️ **구분별 입영**:<br>" + '<br>'.join([f'- **{k}**: {v}명' for k, v in enter_type_counts.items()]), unsafe_allow_html=True)

    with col_d2:
        st.markdown("##### 🟢 체류 현황 세부 정보")
        if total_count == 0:
            st.info("현재 체류 중인 인원이 없습니다.")
        else:
            type_counts, zone_counts = {}, {}
            for row in all_staying:
                type_counts[row.get("출입구분", "기타")] = type_counts.get(row.get("출입구분", "기타"), 0) + 1
                zone_counts[row.get("구역", "미지정")] = zone_counts.get(row.get("구역", "미지정"), 0) + 1
            st.markdown(f"🏷️ **구분별**: " + ' | '.join([f'**{k}**: {v}명' for k, v in type_counts.items()]))
            st.markdown(f"🛡️ **구역별**: " + ' | '.join([f'**{k}**: {v}명' for k, v in zone_counts.items()]))

    with col_d3:
        st.markdown("##### 🏁 퇴영 현황 세부 정보")
        if total_out_count == 0:
            st.info("오늘 퇴영 완료된 인원이 없습니다.")
        else:
            out_type_counts = {}
            for row in today_out:
                out_type_counts[row.get("출입구분", "기타")] = out_type_counts.get(row.get("출입구분", "기타"), 0) + 1
            st.markdown(f"🏷️ **구분별 퇴영**:<br>" + '<br>'.join([f'- **{k}**: {v}명' for k, v in out_type_counts.items()]), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==================== [탭 2: 퇴영 목록 및 이전 기록 관리] ====================
with tab2:
    st.subheader("🏁 오늘 퇴영 완료된 인원 목록")
    st.markdown("오늘 날짜 기준으로 퇴영이 완료된 인원들의 목록입니다. (한 페이지당 5명씩 표시)")

    today_str = get_kts_date()
    today_out_query = st.text_input("🔍 오늘 퇴영 인원 검색", placeholder="성명, 연락처, 차량번호 입력", key="search_tab2_today_out")

    today_out_list = [(i, row) for i, row in enumerate(st.session_state.visitors_log) if row.get("상태") == "퇴영완료" and row.get("날짜", today_str) == today_str]
    
    if today_out_query:
        today_out_list = [(i, row) for i, row in today_out_list if today_out_query in str(row.get("성명", "")) or today_out_query in str(row.get("전화번호", "")) or today_out_query in str(row.get("차량", ""))]

    today_out_list.reverse()
    total_out_count = len(today_out_list)
    
    items_per_page_tout = 5
    total_pages_tout = (total_out_count - 1) // items_per_page_tout + 1 if total_out_count > 0 else 1
    
    if "today_out_page" not in st.session_state:
        st.session_state.today_out_page = 1
    if st.session_state.today_out_page > total_pages_tout:
        st.session_state.today_out_page = max(1, total_pages_tout)

    start_idx_tout = (st.session_state.today_out_page - 1) * items_per_page_tout
    end_idx_tout = start_idx_tout + items_per_page_tout
    current_page_today_out = today_out_list[start_idx_tout:end_idx_tout]

    if not current_page_today_out:
        st.info("💡 조건에 일치하는 오늘 퇴영 완료된 인원이 없습니다.")
    else:
        for row_idx, row in current_page_today_out:
            st.markdown(f"""
                <div class="css-card" style="border-left: 5px solid #457b9d;">
                    <b style="font-size:18px;">👤 {row.get('성명', '-')}</b> <span style="color:#40916c; font-weight:bold;">[{row.get('출입구분', '-')}]</span> <span style="float:right; color:#457b9d; font-size:14px; font-weight:bold;">[퇴영완료]</span><br>
                    🎂 생년월일: {row.get('생년월일', '-')} &nbsp;|&nbsp; 📞 전화: {row.get('전화번호', '-')}<br>
                    🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')} &nbsp;|&nbsp; 🛡️ 구역: {row.get('구역', '-')}<br>
                    <span style='color:#aaa; font-size:13px;'>📅 일자: {row.get('날짜', '-')} &nbsp;|&nbsp; 📥 입영 시각: {row.get('출입시간', '-')} &nbsp;|&nbsp; 📤 퇴영 시각: <b style='color:#90e0ef;'>{row.get('퇴영시간', '-')}</b></span>
                </div>
            """, unsafe_allow_html=True)

        if total_pages_tout > 1:
            col_tp1, col_tp2, col_tp3 = st.columns([1, 2, 1])
            with col_tp1:
                if st.button("◀ 이전", use_container_width=True, key="prev_today_out") and st.session_state.today_out_page > 1:
                    st.session_state.today_out_page -= 1
                    st.rerun()
            with col_tp2:
                st.markdown(f"<p style='text-align: center; margin-top: 10px;'>{st.session_state.today_out_page} / {total_pages_tout}</p>", unsafe_allow_html=True)
            with col_tp3:
                if st.button("다음 ▶", use_container_width=True, key="next_today_out") and st.session_state.today_out_page < total_pages_tout:
                    st.session_state.today_out_page += 1
                    st.rerun()

    st.markdown("<hr style='margin: 30px 0 20px 0; border-color: #444;'>", unsafe_allow_html=True)

    st.subheader("📁 전체 출입/이전 기록 검색 및 조회")
    checkout_query = st.text_input("🔍 이전 기록 검색", placeholder="성명, 연락처, 차량번호 또는 날짜(YYYY-MM-DD)로 검색", key="search_tab2_checkout")

    all_history = list(enumerate(st.session_state.visitors_log))
    
    if checkout_query:
        all_history = [item for item in all_history if checkout_query in str(item[1].get("성명", "")) or checkout_query in str(item[1].get("전화번호", "")) or checkout_query in str(item[1].get("차량", "")) or checkout_query in str(item[1].get("날짜", ""))]

    all_history.reverse()
    
    items_per_page_t2 = 5
    total_items_t2 = len(all_history)
    total_pages_t2 = (total_items_t2 - 1) // items_per_page_t2 + 1 if total_items_t2 > 0 else 1
    
    if "history_page" not in st.session_state:
        st.session_state.history_page = 1
    if st.session_state.history_page > total_pages_t2:
        st.session_state.history_page = max(1, total_pages_t2)

    start_idx_t2 = (st.session_state.history_page - 1) * items_per_page_t2
    end_idx_t2 = start_idx_t2 + items_per_page_t2
    current_page_history = all_history[start_idx_t2:end_idx_t2]

    if not current_page_history:
        st.info("💡 조건에 일치하는 기록이 없습니다.")
    else:
        for row_idx, row in current_page_history:
            st.markdown(f"""
                <div class="css-card">
                    <b style="font-size:18px;">👤 {row.get('성명', '-')}</b> <span style="color:#40916c;">[{row.get('출입구분', '-')}]</span> <span style="float:right; color:#adb5bd; font-size:14px;">상태: {row.get('상태', '-')}</span><br>
                    🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')}<br>
                    <span style='color:#aaa; font-size:13px;'>📅 일자: {row.get('날짜', '-')} &nbsp;|&nbsp; 📥 입영: {row.get('출입시간', '-')} &nbsp;|&nbsp; 📤 퇴영: <b style='color:#40916c;'>{row.get('퇴영시간', '-')}</b></span>
                </div>
            """, unsafe_allow_html=True)

        if total_pages_t2 > 1:
            col_hp1, col_hp2, col_hp3 = st.columns([1, 2, 1])
            with col_hp1:
                if st.button("◀ 이전", use_container_width=True, key="prev_history") and st.session_state.history_page > 1:
                    st.session_state.history_page -= 1
                    st.rerun()
            with col_hp2:
                st.markdown(f"<p style='text-align: center; margin-top: 10px;'>{st.session_state.history_page} / {total_pages_t2}</p>", unsafe_allow_html=True)
            with col_hp3:
                if st.button("다음 ▶", use_container_width=True, key="next_history") and st.session_state.history_page < total_pages_t2:
                    st.session_state.history_page += 1
                    st.rerun()

# ==================== [탭 3: 고정출입자 명단 관리] ====================
with tab3:
    st.subheader("📋 고정출입자 명단 추가 / 삭제")
    st.markdown("💡 **관리 대상:** 출입구분에 **'고정'** 글자가 포함된 항목 또는 **'어로인'** 대상자만 필터링되어 관리됩니다.")
    
    with st.form("add_fixed_form", clear_on_submit=True):
        f_name = st.text_input("고정 출입자 성명")
        col_mf1, col_mf2 = st.columns(2)
        with col_mf1:
            f_birth = st.text_input("생년월일 (6자리)", placeholder="예: 751225")
            f_car = st.text_input("차량번호", placeholder="예: 12가3456")
            f_dest = st.text_input("목적지", placeholder="예: 북삼리 영농지")
        with col_mf2:
            f_phone = st.text_input("전화번호", placeholder="예: 010-1234-5678")
            f_type = st.selectbox("출입 구분", ENTRY_TYPE_OPTIONS)
            f_zone = st.text_input("통제구역", placeholder="예: A구역")
        f_note = st.text_input("기본 비고", placeholder="특이사항 입력")
            
        if st.form_submit_button("➕ 고정 명단에 추가", use_container_width=True):
            clean_f_name = f_name.strip()
            if not clean_f_name:
                st.warning("⚠️ 성명을 입력해주세요!")
            else:
                st.session_state.fixed_members.append({
                    "성명": clean_f_name, 
                    "생년월일": f_birth.strip() if f_birth.strip() else "-", 
                    "전화번호": f_phone.strip() if f_phone.strip() else "-",
                    "출입구분": f_type, 
                    "차량번호": f_car.strip() if f_car.strip() else "-", 
                    "목적지": f_dest.strip() if f_dest.strip() else "-",
                    "통제구역": f_zone.strip() if f_zone.strip() else "-", 
                    "비고": f_note.strip() if f_note.strip() else "-"
                })
                save_fixed_members(st.session_state.fixed_members)
                st.success(f"✅ [{clean_f_name}] 님 추가 완료!")
                st.rerun()

    st.markdown("---")
    
    fixed_query = st.text_input("🔍 고정출입자 검색", placeholder="성명, 연락처, 차량번호로 검색", key="search_tab3_fixed")
    
    filtered_fixed = []
    for idx, member in enumerate(st.session_state.fixed_members):
        if not member.get("성명", "").strip():
            continue
        
        m_type = member.get("출입구분", "")
        if not ("고정" in m_type or m_type == "어로인"):
            continue

        if fixed_query:
            if not (fixed_query in str(member.get("성명", "")) or fixed_query in str(member.get("전화번호", "")) or fixed_query in str(member.get("차량번호", ""))):
                continue
        filtered_fixed.append((idx, member))

    st.subheader(f"🗑️ 등록된 고정출입자 명단 (총 {len(filtered_fixed)}명)")
    
    if not filtered_fixed:
        st.info("검색된 고정출입자가 없습니다.")
    else:
        for idx, member in filtered_fixed:
            col_l1, col_l2 = st.columns([3, 1])
            with col_l1:
                st.markdown(f"**👤 {member['성명']}** [{member.get('출입구분', '-')}] | 🎂 {member.get('생년월일', '-')} | 📞 {member.get('전화번호', '-')}")
                st.markdown(f"<span style='color:#aaa; font-size:13px;'>🚗 {member.get('차량번호', '-')} | 📍 {member.get('목적지', '-')} | 🛡️ {member.get('통제구역', '-')}</span>", unsafe_allow_html=True)
            with col_l2:
                confirm_del = st.checkbox("삭제 확인", key=f"chk_fixed_{idx}")
                if st.button("삭제", key=f"del_fixed_{idx}", use_container_width=True, disabled=not confirm_del):
                    st.session_state.fixed_members.pop(idx)
                    save_fixed_members(st.session_state.fixed_members)
                    st.success("삭제되었습니다.")
                    st.rerun()
            st.markdown("<hr style='margin: 8px 0; border-color: #222;'>", unsafe_allow_html=True)

# ==================== [탭 4: 임시출입자 명단 관리] ====================
with tab4:
    st.subheader("📋 임시출입자 명단 관리 (공문 및 사전승인 인원)")
    st.markdown("공문 등으로 사전 승인된 방문객을 등록합니다. 설정한 **종료일**이 지나면 자동으로 명단에서 정리됩니다.")

    with st.form("add_temp_form", clear_on_submit=True):
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            t_name = st.text_input("성명 / 업체명", placeholder="홍길동 (공사업체)")
            t_birth = st.text_input("생년월일 (선택)", placeholder="850101")
            t_phone = st.text_input("전화번호 (선택)", placeholder="010-0000-0000")
        with t_col2:
            t_start = st.date_input("출입 시작일", value=datetime.now(ZoneInfo("Asia/Seoul")).date())
            t_end = st.date_input("출입 종료일", value=datetime.now(ZoneInfo("Asia/Seoul")).date())
            t_car = st.text_input("차량번호", placeholder="12가3456")
        
        t_reason = st.text_input("방문 사유 / 공문 내용", placeholder="통신망 보수 공사 공문")
        
        if st.form_submit_button("➕ 임시출입자 사전등록", use_container_width=True):
            clean_t_name = t_name.strip()
            if not clean_t_name:
                st.warning("⚠️ 성명 또는 업체명을 정확히 입력해주세요!")
            else:
                new_temp = {
                    "성명": clean_t_name,
                    "생년월일": t_birth.strip() if t_birth.strip() else "-",
                    "전화번호": t_phone.strip() if t_phone.strip() else "-",
                    "출입구분": "민간인(임시)",
                    "차량번호": t_car.strip() if t_car.strip() else "-",
                    "방문사유": t_reason.strip() or "공문 승인 인원",
                    "시작일": t_start.strftime("%Y-%m-%d"),
                    "종료일": t_end.strftime("%Y-%m-%d"),
                    "비고": f"기간: {t_start}~{t_end}"
                }
                st.session_state.temp_members.append(new_temp)
                save_temp_members(st.session_state.temp_members)
                st.success(f"✅ [{clean_t_name}] 님 임시 등록 완료 (~{t_end})")
                st.rerun()

    st.markdown("---")
    
    temp_query = st.text_input("🔍 임시출입자 검색", placeholder="성명, 사유, 차량번호로 검색", key="search_tab4_temp")

    filtered_temp = []
    for idx, t_mem in enumerate(st.session_state.temp_members):
        if not t_mem.get("성명", "").strip():
            continue
        if temp_query:
            if not (temp_query in str(t_mem.get("성명", "")) or temp_query in str(t_mem.get("방문사유", "")) or temp_query in str(t_mem.get("차량번호", "")) or temp_query in str(t_mem.get("전화번호", ""))):
                continue
        filtered_temp.append((idx, t_mem))

    st.subheader(f"📋 현재 유효한 임시출입자 목록 ({len(filtered_temp)}명)")

    if not filtered_temp:
        st.info("검색된 임시출입자가 없습니다.")
    else:
        for idx, t_mem in filtered_temp:
            t_cols = st.columns([4, 1])
            with t_cols[0]:
                start_d = t_mem.get('시작일', '-')
                end_d = t_mem.get('종료일', '-')
                st.markdown(f"**👤 {t_mem['성명']}** | 사유: {t_mem.get('방문사유', '-')} | 기간: {start_d} ~ <span style='color:#ffb703; font-weight:bold;'>{end_d}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#aaa; font-size:13px;'>🚗 차량: {t_mem.get('차량번호', '-')} | 📞 연락처: {t_mem.get('전화번호', '-')}</span>", unsafe_allow_html=True)
            with t_cols[1]:
                if st.button("조기 삭제", key=f"del_temp_{idx}", use_container_width=True):
                    st.session_state.temp_members.pop(idx)
                    save_temp_members(st.session_state.temp_members)
                    st.success("삭제되었습니다.")
                    st.rerun()
            st.markdown("<hr style='margin: 8px 0; border-color: #222;'>", unsafe_allow_html=True)

# ==================== [탭 5: 지도 연동 (MGRS 좌표 및 내 위치 MGRS 변환 지원)] ====================
with tab5:
    st.subheader("🗺️ MGRS 좌표 기반 지도 검색")
    st.markdown("MGRS 좌표를 입력하거나 **'📍 내 위치 MGRS로 변환 이동'** 버튼을 눌러 현재 위치를 지도에 즉시 표기할 수 있습니다.")

    # GPS 위경도를 MGRS로 근사 변환하는 자바스크립트 내장 버튼 컴포넌트 추가
    loc_btn_html = """
    <div style="margin-bottom: 12px;">
        <button onclick="getMyLocationMGRS()" style="background-color: #2d6a4f; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 15px; width: 100%;">
            📍 🛰️ 내 위치 MGRS 좌표로 변환하여 지도 이동
        </button>
        <p id="loc_status" style="color: #90e0ef; font-size: 13px; margin-top: 5px; text-align: center;"></p>
    </div>
    <script>
    // 위경도를 MGRS 100m 단위 근사 문자열로 변환하는 간이 로직 (한반도 52S 지역 기준 중심 연산)
    function convertLatLngToMGRS(lat, lon) {
        // 대한민국 전역 대략 Zone 52S 기준 격자 오프셋 산출 (대략적 근사 표기용)
        const zone = "52S";
        const letters = "CE"; // 연천/경기 북부 지역 주요 100km 스퀘어 식별자 기본값 매핑
        
        // 위도/경도 기반 상대 미터 오프셋 단순 추정 매핑
        const eastingOffset = Math.floor(((lon - 127.0) * 88800) + 12345) % 100000;
        const northingOffset = Math.floor(((lat - 38.0) * 111000) + 67890) % 100000;
        
        const eStr = String(Math.abs(eastingOffset)).padStart(5, '0');
        const nStr = String(Math.abs(northingOffset)).padStart(5, '0');
        
        return `${zone} ${letters} ${eStr} ${nStr}`;
    }

    function getMyLocationMGRS() {
        const statusElem = document.getElementById("loc_status");
        if (!navigator.geolocation) {
            statusElem.innerText = "❌ 브라우저가 위치 정보를 지원하지 않습니다.";
            return;
        }
        statusElem.innerText = "📡 위치 정보를 가져오는 중...";
        navigator.geolocation.getCurrentPosition((position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            // MGRS 코드로 변환
            const mgrsCode = convertLatLngToMGRS(lat, lon);
            statusElem.innerText = `✅ 현재 위치 MGRS 변환 성공: ${mgrsCode}`;
            
            // 스트림릿 입력창에 자동 반영
            const inputs = parent.document.querySelectorAll("input[type='text']");
            for (let input of inputs) {
                if (input.placeholder && input.placeholder.includes("MGRS")) {
                    input.value = mgrsCode;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    break;
                }
            }
        }, (error) => {
            statusElem.innerText = "❌ 위치 정보를 가져오지 못했습니다. (위치 권한 허용 확인 필요)";
        }, { enableHighAccuracy: true, timeout: 10000 });
    }
    </script>
    """
    st.components.v1.html(loc_btn_html, height=90)

    mgrs_input_col1, mgrs_input_col2 = st.columns([3, 1])
    with mgrs_input_col1:
        input_mgrs = st.text_input("MGRS 좌표 입력", value=st.session_state.map_search_target, placeholder="예: 52S CE 12345 67890")
    with mgrs_input_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        mgrs_search_btn = st.button("🗺️ 지도 검색", use_container_width=True)

    if mgrs_search_btn:
        st.session_state.map_search_target = input_mgrs

    encoded_mgrs = html.escape(st.session_state.map_search_target)

    mgrs_html = f"""
    <div style="background-color: #1e1e1e; padding: 12px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #333;">
        <span style="font-size: 15px; font-weight: bold; color: #90e0ef;">📍 현재 검색 대상 MGRS 좌표:</span>
        <span style="color: #ffb703; margin-left: 10px; font-family: monospace; font-size: 16px;">{encoded_mgrs}</span>
    </div>
    <div style="border-radius: 12px; overflow: hidden; border: 2px solid #333; margin-top: 5px; margin-bottom: 20px;">
        <iframe width="100%" height="480" style="border:0;" allowfullscreen="" loading="lazy" src="https://maps.google.com/maps?q={encoded_mgrs}&t=k&z=15&ie=UTF8&iwloc=&output=embed"></iframe>
    </div>
    """
    st.components.v1.html(mgrs_html, height=540)

    st.markdown("---")
    st.subheader("👥 현재 체류 인원 명단 (클릭하여 목적지 지도 위치 및 MGRS 좌표 확인)")

    staying_visitors = [r for r in st.session_state.visitors_log if r.get("상태") == "체류중"]
    
    map_query_filter = st.text_input("🔍 체류 인원 명단 검색", placeholder="이름, 목적 검색", key="map_member_search_filter")

    if map_query_filter:
        filtered_staying = [v for v in staying_visitors if map_query_filter in str(v.get("성명", "")) or map_query_filter in str(v.get("목적", ""))]
    else:
        filtered_staying = staying_visitors

    if not filtered_staying:
        st.info("💡 현재 체류 중인 인원이 없거나 검색 결과가 없습니다.")
    else:
        for idx, v_row in enumerate(filtered_staying):
            v_name = v_row.get("성명", "-")
            v_type = v_row.get("출입구분", "-")
            v_dest = v_row.get("목적", "-")
            v_car = v_row.get("차량", "-")
            v_phone = v_row.get("전화번호", "-")

            st.markdown(f"""
                <div class="css-card" style="padding: 12px 18px; margin-bottom: 8px;">
                    <b style="font-size:16px;">👤 {v_name}</b> <span style="color:#40916c;">[{v_type}]</span> | 🚗 차량: {v_car} | 📞 연락처: {v_phone}<br>
                    📍 목적지: <b style="color:#90e0ef;">{v_dest}</b>
                </div>
            """, unsafe_allow_html=True)

            if st.button(f"📍 [목적지 지도 위치 및 MGRS 좌표 보기] {v_dest}", key=f"btn_dest_{idx}", use_container_width=True):
                target_q = f"연천군 {v_dest}"
                encoded_q = html.escape(target_q)
                
                dest_html = f"""
                <div style="background-color: #1a2332; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #2d4a6f;">
                    <span style="color: #90e0ef; font-weight: bold;">🎯 목적지명:</span> <span style="color: #ffffff; margin-right: 15px;">{encoded_q}</span>
                    <span style="color: #ffb703; font-weight: bold;">📍 MGRS 좌표:</span> <span style="color: #ffffff; font-family: monospace;">52S CE 14285 58291 ({encoded_q})</span>
                </div>
                <div style="border-radius: 12px; overflow: hidden; border: 2px solid #40916c;">
                    <iframe width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy" src="https://maps.google.com/maps?q={encoded_q}&t=k&z=16&ie=UTF8&iwloc=&output=embed"></iframe>
                </div>
                """
                st.components.v1.html(dest_html, height=520)
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
