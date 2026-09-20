from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st
import json
import html
import os
import pandas as pd

# ==================== [설정 및 파일 저장 함수] ====================
CORRECT_PASSWORD = "1234"  # 접속 비밀번호
FIXED_MEMBERS_FILE = "fixed_members.json"
TEMP_MEMBERS_FILE = "temp_members.json"
VISITORS_LOG_FILE = "visitors_log.json"

# 페이지 기본 설정 (와이드 모드 적용)
st.set_page_config(page_title="제25보병사단 비룡초소 출입 관리", layout="wide")

ENTRY_TYPE_OPTIONS = [
    "영농인(고정)", "영농인(임시)", "공사(고정)", "공사(임시)", 
    "성묘객(임시)", "어로인", "군인", "민간인(고정)", "민간인(임시)", "고정", "외국인"
]

def load_fixed_members():
    initial_members = [
        {"성명": "김영농", "생년월일": "651012", "전화번호": "010-1234-5678", "출입구분": "영농인(고정)", "차량번호": "12가3456", "목적지": "비룡부대 인근 북삼리 영농지", "통제구역": "A구역", "비고": "특이사항 없음"},
        {"성명": "이공사", "생년월일": "720515", "전화번호": "010-9876-5432", "출입구분": "공사(고정)", "차량번호": "78나9012", "목적지": "비룡부대 초소 보수공사", "통제구역": "B구역", "비고": "장비 지참"},
        {"성명": "박병장", "생년월일": "030120", "전화번호": "010-1111-2222", "출입구분": "군인", "차량번호": "지휘차 5521", "목적지": "비룡부대 본부 파견근무", "통제구역": "C구역", "비고": "공무 출장"},
        {"성명": "한강어부", "생년월일": "680310", "전화번호": "010-3333-4444", "출입구분": "어로인", "차량번호": "34다5678", "목적지": "비룡부대 인근 임진강 어로 구역", "통제구역": "D구역", "비고": "어업 활동 승인"}
    ]
    if os.path.exists(FIXED_MEMBERS_FILE):
        try:
            with open(FIXED_MEMBERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list): return data
        except Exception: pass
    save_fixed_members(initial_members)
    return initial_members

def save_fixed_members(members):
    try:
        with open(FIXED_MEMBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(members, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"고정 명단 저장 중 오류 발생: {e}")

def load_temp_members():
    temp_list = []
    if os.path.exists(TEMP_MEMBERS_FILE):
        try:
            with open(TEMP_MEMBERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list): temp_list = data
        except Exception: pass
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

def load_visitors_log():
    logs = []
    if os.path.exists(VISITORS_LOG_FILE):
        try:
            with open(VISITORS_LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list): logs = data
        except Exception: pass
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
        border: 1px solid #2d3748; margin-top: 25px; margin-bottom: 20px;
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
    [data-baseweb="tab-list"] { overflow-x: auto !important; flex-wrap: nowrap !important; }
    </style>
""", unsafe_allow_html=True)

def get_kts_time(fmt="%H:%M"):
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime(fmt)

def get_kts_date():
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")

# ==================== [세션 초기화] ====================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "visitors_log" not in st.session_state: st.session_state.visitors_log = load_visitors_log()
if "fixed_members" not in st.session_state: st.session_state.fixed_members = load_fixed_members()
if "temp_members" not in st.session_state: st.session_state.temp_members = load_temp_members()
if "map_search_target" not in st.session_state: st.session_state.map_search_target = "제25보병사단 비룡부대"
if "emergency_step" not in st.session_state: st.session_state.emergency_step = 0
if "show_map_panel" not in st.session_state: st.session_state.show_map_panel = False

# ==================== [로그인 화면] ====================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔒 비룡부대 초소 통제시스템")
        st.markdown("접속 비밀번호를 입력해주세요.")
        with st.form("login_form"):
            input_pw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인", use_container_width=True):
                if input_pw == CORRECT_PASSWORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 틀렸습니다.")
    st.stop()

# ==================== [메인 화면 상단] ====================
col_title, col_btns = st.columns([4, 2])

with col_title:
    st.markdown("""
        <div>
            <span class="badge-box">🛡️ 제25보병사단 비룡부대</span>
            <h2 style='margin: 5px 0 0 0;'>비룡부대 초소 실시간 출입 관리 시스템</h2>
        </div>
    """, unsafe_allow_html=True)

with col_btns:
    if st.button("🚨 긴급문자", use_container_width=True, type="primary"):
        st.session_state.emergency_step = 1
        st.rerun()
    if st.button("🗺️ 지도연동", use_container_width=True):
        st.session_state.show_map_panel = not st.session_state.show_map_panel
        st.rerun()

st.markdown("<hr style='margin: 15px 0 20px 0; border-color: #333;'>", unsafe_allow_html=True)

# ==================== [긴급 문자 3중 경고 팝업 및 서식 화면] ====================
@st.dialog("🚨 [긴급 경고 1단계] 발송 확인")
def step_1_warning():
    st.error("정말로 긴급 문자를 발송하시겠습니까?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("취소", use_container_width=True):
            st.session_state.emergency_step = 0
            st.rerun()
    with c2:
        if st.button("확인 (다음)", use_container_width=True, type="primary"):
            st.session_state.emergency_step = 2
            st.rerun()

@st.dialog("⚠️ [긴급 경고 2단계] 대상 확인")
def step_2_warning():
    staying_visitors = [r for r in st.session_state.visitors_log if r.get("상태") == "체류중"]
    st.warning(f"⚠️ 경고: 현재 비룡부대 인근 체류 중인 모든 인원 ({len(staying_visitors)}명) 대상 긴급 상황입니다. 계속 진행하시겠습니까?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("취소", use_container_width=True, key="c2"):
            st.session_state.emergency_step = 0
            st.rerun()
    with c2:
        if st.button("확인 (다음)", use_container_width=True, type="primary", key="o2"):
            st.session_state.emergency_step = 3
            st.rerun()

@st.dialog("🚨 [긴급 경고 3단계] 최종 이동")
def step_3_warning():
    st.error("🚨 마지막 경고: 문자 작성 서식 화면으로 이동합니다. 이동하시겠습니까?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("취소", use_container_width=True, key="c3"):
            st.session_state.emergency_step = 0
            st.rerun()
    with c2:
        if st.button("이동하기", use_container_width=True, type="primary", key="o3"):
            st.session_state.emergency_step = 4
            st.rerun()

if st.session_state.emergency_step == 1:
    step_1_warning()
elif st.session_state.emergency_step == 2:
    step_2_warning()
elif st.session_state.emergency_step == 3:
    step_3_warning()

if st.session_state.emergency_step == 4:
    st.markdown("""
        <div style="background-color: #2b1d1d; padding: 20px; border-radius: 10px; border: 2px solid #ff4b4b; margin-bottom: 20px;">
            <h3 style="color: #ff4b4b; margin-top: 0;">🚨 비룡부대 긴급 상황 문자 작성 서식</h3>
            <p>현재 체류 중인 인원 전체가 기본 수신대상으로 지정되어 있습니다. 필요한 경우 아래 목록에서 수신 여부를 체크하여 조정할 수 있습니다.</p>
        </div>
    """, unsafe_allow_html=True)

    staying_visitors = [r for r in st.session_state.visitors_log if r.get("상태") == "체류중"]
    
    st.markdown("#### 📋 수신 대상 선택 및 확인 목록")
    selected_recipients = []
    
    if not staying_visitors:
        st.info("현재 체류 중인 인원이 없습니다.")
    else:
        for idx, visitor in enumerate(staying_visitors):
            v_name = visitor.get("성명", "-")
            v_phone = visitor.get("전화번호", "-")
            v_type = visitor.get("출입구분", "-")
            v_dest = visitor.get("목적", "-")
            
            is_checked = st.checkbox(f"[{v_type}] 성명: {v_name} | 연락처: {v_phone} | 목적: {v_dest}", value=True, key=f"recip_chk_{idx}")
            if is_checked:
                selected_recipients.append(visitor)

    st.markdown("<br>", unsafe_allow_html=True)
    emergency_msg_content = st.text_area("긴급 전파 내용 입력", placeholder="예: [비상] 비룡부대 초소 인근 비상 상황 발생. 즉시 안전 지역으로 대피 또는 복귀 바랍니다.", height=120)

    col_es1, col_es2 = st.columns(2)
    with col_es1:
        if st.button("📤 최종 긴급 문자 전송", type="primary", use_container_width=True):
            @st.dialog("🔥 [최종 전송 확인]")
            def final_send_dialog():
                st.error(f"선택된 총 {len(selected_recipients)}명에게 긴급 문자를 정말로 전송하시겠습니까?")
                confirm_check = st.checkbox("⚠️ 내용을 최종 확인했으며 발송에 동의합니다.")
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("취소", use_container_width=True, key="fin_cancel"):
                        st.rerun()
                with c_btn2:
                    if st.button("🚀 네, 즉시 발송", use_container_width=True, type="primary", key="fin_send", disabled=not confirm_check):
                        st.success(f"🚨 총 {len(selected_recipients)}명에게 긴급 문자가 성공적으로 전송되었습니다!")
                        st.session_state.emergency_step = 0
                        st.rerun()
            final_send_dialog()
            
    with col_es2:
        if st.button("취소 및 나가기", use_container_width=True):
            st.session_state.emergency_step = 0
            st.rerun()
            
    st.markdown("<hr style='margin: 30px 0; border-color: #444;'>", unsafe_allow_html=True)

if st.session_state.show_map_panel:
    st.markdown("""
        <div style="background-color: #1a2332; padding: 20px; border-radius: 10px; border: 2px solid #415a77; margin-bottom: 20px;">
            <h3 style="color: #90e0ef; margin-top: 0;">🗺️ 비룡부대 인근 빠른 지도 및 MGRS 좌표 검색</h3>
        </div>
    """, unsafe_allow_html=True)
    
    s_mode = st.radio("검색 방식 선택", ["MGRS 좌표", "주소 입력"], horizontal=True, key="top_map_radio")
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        if s_mode == "MGRS 좌표":
            top_target = st.text_input("MGRS 좌표 입력", value=st.session_state.map_search_target, key="top_mgrs_txt")
        else:
            top_target = st.text_input("주소 입력", value="제25보병사단 비룡부대", key="top_addr_txt")
    with sc2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("지도 갱신", use_container_width=True, key="top_map_btn"):
            st.session_state.map_search_target = top_target

    encoded_top_target = html.escape(st.session_state.map_search_target)
    st.components.v1.html(f"""
        <div style="border-radius: 12px; overflow: hidden; border: 2px solid #333;">
            <iframe width="100%" height="400" style="border:0;" allowfullscreen="" loading="lazy" src="https://maps.google.com/maps?q={encoded_top_target}&t=k&z=15&ie=UTF8&iwloc=&output=embed"></iframe>
        </div>
    """, height=420)
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

# ----------------- [탭 메뉴 구성] -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 출입 관리 및 현황", "🏁 퇴영 목록 및 세부 내역", "📋 고정출입자 명단 관리", "📋 임시출입자 명단 관리", "🗺️ 지도 연동"])

# ==================== [탭 1: 출입 관리 및 현황] ====================
with tab1:
    with st.expander("📖 [사용법 안내] 출입 관리 및 현황", expanded=False):
        st.markdown("""
            - **입영 등록**: 방문자 성명 입력 후 '정보 불러오기' 시 동명이인이나 공문 인원이 있을 경우 선택 창이 활성화됩니다.<br>
            - **실시간 체류 관리**: 현재 비룡부대 인근 체류 중인 인원을 확인하고 퇴영 처리할 수 있습니다.<br>
            - **종합 현황판**: 화면 하단에서 오늘 총 입영, 현재 총 체류, 오늘 총 퇴영 인원 통계 및 **출입 구분별·구역별 상세 표**를 파악할 수 있습니다.
        """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.subheader("📝 출입자 등록 (입영)")

        if "temp_input_name" not in st.session_state: st.session_state.temp_input_name = ""
        if "selected_matched_member" not in st.session_state: st.session_state.selected_matched_member = None
        if "ambiguous_matches" not in st.session_state: st.session_state.ambiguous_matches = []

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
                dest = st.text_input("목적지", value=clean_val("목적지") or clean_val("방문사유"), placeholder="예: 비룡부대 인근 영농지")
            with col_f2:
                zone = st.text_input("통제 구역", value=clean_val("통제구역") or clean_val("구역"), placeholder="예: A구역")
                note = st.text_input("비고", value=clean_val("특이사항"), placeholder="특이사항 입력")
            
            if st.form_submit_button("🚀 최종 입영 처리", use_container_width=True):
                final_name = input_name.strip()
                if not final_name:
                    st.warning("⚠️ 성명을 입력해주세요.")
                else:
                    new_entry = {
                        "날짜": get_kts_date(),
                        "출입시간": get_kts_time("%H:%M"),
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

        all_logs = [(i, row) for i, row in enumerate(st.session_state.visitors_log)]
        all_logs.reverse()

        with st.form("staying_search_form"):
            col_s1, col_s2 = st.columns([3, 1])
            with col_s1:
                staying_query_input = st.text_input("🔍 출입·퇴영 검색", placeholder="이름, 번호, 차량번호 입력", label_visibility="collapsed")
            with col_s2:
                staying_search_btn = st.form_submit_button("검색", use_container_width=True)
        
        if "applied_staying_query" not in st.session_state: st.session_state.applied_staying_query = ""
        if staying_search_btn: st.session_state.applied_staying_query = staying_query_input

        search_query = st.session_state.applied_staying_query
        if search_query:
            display_list = [(idx, row) for idx, row in all_logs if search_query in str(row.get("성명", "")) or search_query in str(row.get("전화번호", "")) or search_query in str(row.get("차량", ""))]
        else:
            display_list = [(i, row) for i, row in all_logs if row.get("상태") == "체류중"]

        items_per_page = 5
        total_items = len(display_list)
        total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
        
        if "staying_page" not in st.session_state: st.session_state.staying_page = 1
        if st.session_state.staying_page > total_pages: st.session_state.staying_page = max(1, total_pages)

        start_idx = (st.session_state.staying_page - 1) * items_per_page
        current_page_items = display_list[start_idx:start_idx + items_per_page]

        if not current_page_items:
            st.info("💡 조건에 일치하는 인원이 없습니다.")
        else:
            for row_idx, row in current_page_items:
                is_staying = (row.get("상태") == "체류중")
                status_color = "#40916c" if is_staying else "#adb5bd"
                status_text = "체류중" if is_staying else f"퇴영완료 ({row.get('퇴영시간', '-')})"

                st.markdown(f"""
                    <div class="css-card" style="border-left: 5px solid {status_color};">
                        <b style="font-size:18px;">👤 {row.get('성명', '-')}</b> <span style="color:#40916c; font-weight:bold;">[{row.get('출입구분', '-')}]</span> <span style="float:right; color:{status_color}; font-size:14px; font-weight:bold;">[{status_text}]</span><br>
                        🎂 생년월일: {row.get('생년월일', '-')} &nbsp;|&nbsp; 📞 전화: {row.get('전화번호', '-')}<br>
                        🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')} &nbsp;|&nbsp; 🛡️ 구역: {row.get('구역', '-')}<br>
                        📝 비고: <b style="color: #ffb703;">{row.get('비고', '-')}</b><br>
                        <span style="color: #adb5bd; font-size: 13px;">일자: {row.get('날짜', get_kts_date())} | 입영 시각: {row.get('출입시간', '-')}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                if is_staying:
                    if st.button("🏁 퇴영 처리", key=f"out_{row_idx}", use_container_width=True):
                        st.session_state.visitors_log[row_idx]["상태"] = "퇴영완료"
                        st.session_state.visitors_log[row_idx]["퇴영시간"] = get_kts_time("%H:%M")
                        save_visitors_log(st.session_state.visitors_log)
                        st.rerun()

            if total_pages > 1:
                cp1, cp2, cp3 = st.columns([1, 2, 1])
                with cp1:
                    if st.button("◀ 이전", use_container_width=True, key="prev_staying") and st.session_state.staying_page > 1:
                        st.session_state.staying_page -= 1; st.rerun()
                with cp2:
                    st.markdown(f"<p style='text-align: center; margin-top: 10px;'>{st.session_state.staying_page} / {total_pages}</p>", unsafe_allow_html=True)
                with cp3:
                    if st.button("다음 ▶", use_container_width=True, key="next_staying") and st.session_state.staying_page < total_pages:
                        st.session_state.staying_page += 1; st.rerun()

    # 탭 1 종합 현황판 하단
    today_str = get_kts_date()
    today_entered = [r for r in st.session_state.visitors_log if r.get("날짜", today_str) == today_str]
    all_staying = [r for r in st.session_state.visitors_log if r.get("상태") == "체류중"]
    today_out = [r for r in today_entered if r.get("상태") == "퇴영완료"]

    st.markdown("""
        <div class="dashboard-box">
            <h3 style="margin-top:0; color:#90e0ef; margin-bottom:15px;">📈 종합 현황판 (오늘 기준)</h3>
    """, unsafe_allow_html=True)

    cs1, cs2, cs3 = st.columns(3)
    with cs1:
        st.markdown(f"""
            <div class="stat-card" style="margin-bottom: 5px;">
                <h4 style="margin:0; color:#90e0ef;">오늘 총 입영 인원</h4>
                <p style="font-size: 24px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{len(today_entered)} 명</p>
            </div>
        """, unsafe_allow_html=True)
    with cs2:
        st.markdown(f"""
            <div class="stat-card" style="margin-bottom: 5px;">
                <h4 style="margin:0; color:#90e0ef;">현재 총 체류 인원</h4>
                <p style="font-size: 24px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{len(all_staying)} 명</p>
            </div>
        """, unsafe_allow_html=True)
    with cs3:
        st.markdown(f"""
            <div class="stat-card" style="margin-bottom: 5px;">
                <h4 style="margin:0; color:#90e0ef;">오늘 총 퇴영 인원</h4>
                <p style="font-size: 24px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{len(today_out)} 명</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown("#### 👤 출입 구분별 인원 현황")
        if today_entered:
            df_today = pd.DataFrame(today_entered)
            if "출입구분" in df_today.columns:
                df_type_cnt = df_today["출입구분"].value_counts().reset_index()
                df_type_cnt.columns = ["출입 구분", "인원(명)"]
                st.dataframe(df_type_cnt, use_container_width=True, hide_index=True)
            else:
                st.info("출입구분 데이터가 없습니다.")
        else:
            st.info("오늘 출입 기록이 없습니다.")
            
    with t_col2:
        st.markdown("#### 🛡️ 통제 구역별 체류 인원 현황")
        if all_staying:
            df_staying = pd.DataFrame(all_staying)
            zone_col = "구역" if "구역" in df_staying.columns else ("통제구역" if "통제구역" in df_staying.columns else None)
            if zone_col:
                df_zone_cnt = df_staying[zone_col].value_counts().reset_index()
                df_zone_cnt.columns = ["통제 구역", "체류 인원(명)"]
                st.dataframe(df_zone_cnt, use_container_width=True, hide_index=True)
            else:
                st.info("구역 데이터가 없습니다.")
        else:
            st.info("현재 체류 중인 인원이 없습니다.")

    st.markdown("</div>", unsafe_allow_html=True)

# ==================== [탭 2: 퇴영 목록 및 세부 내역] ====================
with tab2:
    with st.expander("📖 [사용법 안내] 퇴영 목록 및 세부 내역", expanded=False):
        st.markdown("""
            - **입영·체류·퇴영 세부 내역**: 오늘 날짜 기준으로 입영, 체류, 퇴영 인원 통계 지표와 **출입 구분별·통제 구역별 상세 표**를 확인할 수 있습니다.<br>
            - **퇴영 완료 목록 및 이전 기록 조회**: 오늘 퇴영 완료된 인원 목록과 전체 출입/이전 기록을 검색할 수 있습니다.
        """, unsafe_allow_html=True)

    today_str = get_kts_date()
    today_entered_t2 = [r for r in st.session_state.visitors_log if r.get("날짜", today_str) == today_str]
    all_staying_t2 = [r for r in st.session_state.visitors_log if r.get("상태") == "체류중"]
    today_out_t2 = [r for r in today_entered_t2 if r.get("상태") == "퇴영완료"]

    st.markdown("""
        <div class="dashboard-box" style="margin-top: 5px; margin-bottom: 25px;">
            <h3 style="margin-top:0; color:#90e0ef; margin-bottom:15px;">📊 입영·체류·퇴영 세부 내역 및 통계 (오늘 기준)</h3>
    """, unsafe_allow_html=True)

    ts1, ts2, ts3 = st.columns(3)
    with ts1:
        st.markdown(f"""
            <div class="stat-card" style="margin-bottom: 5px;">
                <h4 style="margin:0; color:#90e0ef;">오늘 총 입영 내역</h4>
                <p style="font-size: 22px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{len(today_entered_t2)} 명</p>
            </div>
        """, unsafe_allow_html=True)
    with ts2:
        st.markdown(f"""
            <div class="stat-card" style="margin-bottom: 5px;">
                <h4 style="margin:0; color:#90e0ef;">현재 체류 내역</h4>
                <p style="font-size: 22px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{len(all_staying_t2)} 명</p>
            </div>
        """, unsafe_allow_html=True)
    with ts3:
        st.markdown(f"""
            <div class="stat-card" style="margin-bottom: 5px;">
                <h4 style="margin:0; color:#90e0ef;">오늘 퇴영 내역</h4>
                <p style="font-size: 22px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{len(today_out_t2)} 명</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    tt_col1, tt_col2 = st.columns(2)
    with tt_col1:
        st.markdown("#### 👤 출입 구분별 인원 상세 표")
        if today_entered_t2:
            df_today_t2 = pd.DataFrame(today_entered_t2)
            if "출입구분" in df_today_t2.columns:
                df_type_cnt_t2 = df_today_t2["출입구분"].value_counts().reset_index()
                df_type_cnt_t2.columns = ["출입 구분", "인원(명)"]
                st.dataframe(df_type_cnt_t2, use_container_width=True, hide_index=True)
            else:
                st.info("출입구분 데이터가 없습니다.")
        else:
            st.info("오늘 출입 기록이 없습니다.")
            
    with tt_col2:
        st.markdown("#### 🛡️ 통제 구역별 체류 인원 상세 표")
        if all_staying_t2:
            df_staying_t2 = pd.DataFrame(all_staying_t2)
            zone_col_t2 = "구역" if "구역" in df_staying_t2.columns else ("통제구역" if "통제구역" in df_staying_t2.columns else None)
            if zone_col_t2:
                df_zone_cnt_t2 = df_staying_t2[zone_col_t2].value_counts().reset_index()
                df_zone_cnt_t2.columns = ["통제 구역", "체류 인원(명)"]
                st.dataframe(df_zone_cnt_t2, use_container_width=True, hide_index=True)
            else:
                st.info("구역 데이터가 없습니다.")
        else:
            st.info("현재 체류 중인 인원이 없습니다.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("🏁 오늘 퇴영 완료된 인원 목록")
    today_out_query = st.text_input("🔍 오늘 퇴영 인원 검색", placeholder="성명, 연락처, 차량번호 입력", key="search_tab2_today_out")

    today_out_list = [(i, row) for i, row in enumerate(st.session_state.visitors_log) if row.get("상태") == "퇴영완료" and row.get("날짜", today_str) == today_str]
    if today_out_query:
        today_out_list = [(i, row) for i, row in today_out_list if today_out_query in str(row.get("성명", "")) or today_out_query in str(row.get("전화번호", "")) or today_out_query in str(row.get("차량", ""))]
    today_out_list.reverse()

    for row_idx, row in today_out_list:
        st.markdown(f"""
            <div class="css-card" style="border-left: 5px solid #457b9d;">
                <b style="font-size:18px;">👤 {row.get('성명', '-')}</b> <span style="color:#40916c; font-weight:bold;">[{row.get('출입구분', '-')}]</span> <span style="float:right; color:#457b9d; font-size:14px; font-weight:bold;">[퇴영완료]</span><br>
                🎂 생년월일: {row.get('생년월일', '-')} &nbsp;|&nbsp; 📞 전화: {row.get('전화번호', '-')}<br>
                🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')} &nbsp;|&nbsp; 🛡️ 구역: {row.get('구역', '-')}<br>
                <span style='color:#aaa; font-size:13px;'>📅 일자: {row.get('날짜', '-')} &nbsp;|&nbsp; 📥 입영 시각: {row.get('출입시간', '-')} &nbsp;|&nbsp; 📤 퇴영 시각: <b style='color:#90e0ef;'>{row.get('퇴영시간', '-')}</b></span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 30px 0 20px 0; border-color: #444;'>", unsafe_allow_html=True)
    st.subheader("📁 전체 출입/이전 기록 검색 및 조회")
    checkout_query = st.text_input("🔍 이전 기록 검색", placeholder="성명, 연락처, 차량번호 또는 날짜(YYYY-MM-DD)로 검색", key="search_tab2_checkout")

    all_history = list(enumerate(st.session_state.visitors_log))
    if checkout_query:
        all_history = [item for item in all_history if checkout_query in str(item[1].get("성명", "")) or checkout_query in str(item[1].get("전화번호", "")) or checkout_query in str(item[1].get("차량", "")) or checkout_query in str(item[1].get("날짜", ""))]
    all_history.reverse()

    for row_idx, row in all_history[:10]:
        st.markdown(f"""
            <div class="css-card">
                <b style="font-size:18px;">👤 {row.get('성명', '-')}</b> <span style="color:#40916c;">[{row.get('출입구분', '-')}]</span> <span style="float:right; color:#adb5bd; font-size:14px;">상태: {row.get('상태', '-')}</span><br>
                🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')}<br>
                <span style='color:#aaa; font-size:13px;'>📅 일자: {row.get('날짜', '-')} &nbsp;|&nbsp; 📥 입영: {row.get('출입시간', '-')} &nbsp;|&nbsp; 📤 퇴영: <b style='color:#40916c;'>{row.get('퇴영시간', '-')}</b></span>
            </div>
        """, unsafe_allow_html=True)

# ==================== [탭 3: 고정출입자 명단 관리] ====================
with tab3:
    with st.expander("📖 [사용법 안내] 고정출입자 명단 관리", expanded=False):
        st.markdown("""
            - 고정출입자(어로인 포함) 명단을 등록 및 관리합니다.<br>
            - 삭제 시 반드시 **'삭제 확인'** 체크박스를 체크한 후 삭제 버튼을 눌러야 안전하게 삭제됩니다.
        """, unsafe_allow_html=True)

    st.subheader("📋 고정출입자 명단 추가 / 삭제")
    with st.form("add_fixed_form", clear_on_submit=True):
        f_name = st.text_input("고정 출입자 성명")
        col_mf1, col_mf2 = st.columns(2)
        with col_mf1:
            f_birth = st.text_input("생년월일 (6자리)", placeholder="예: 751225")
            f_car = st.text_input("차량번호", placeholder="예: 12가3456")
            f_dest = st.text_input("목적지", placeholder="예: 비룡부대 인근 영농지")
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
                    "성명": clean_f_name, "생년월일": f_birth.strip() or "-", "전화번호": f_phone.strip() or "-",
                    "출입구분": f_type, "차량번호": f_car.strip() or "-", "목적지": f_dest.strip() or "-",
                    "통제구역": f_zone.strip() or "-", "비고": f_note.strip() or "-"
                })
                save_fixed_members(st.session_state.fixed_members)
                st.success(f"✅ [{clean_f_name}] 님 추가 완료!")
                st.rerun()

    st.markdown("---")
    fixed_query = st.text_input("🔍 고정출입자 검색", placeholder="성명, 연락처, 차량번호로 검색", key="search_tab3_fixed")
    
    for idx, member in enumerate(st.session_state.fixed_members):
        if fixed_query and not (fixed_query in member.get("성명", "") or fixed_query in member.get("전화번호", "") or fixed_query in member.get("차량번호", "")):
            continue
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
    with st.expander("📖 [사용법 안내] 임시출입자 명단 관리", expanded=False):
        st.markdown("""
            - 공문 및 사전 승인된 임시출입자를 등록합니다.<br>
            - 기간 만료 시 자동으로 정리되며, 조기 삭제 시 **'삭제 확인'** 체크 후 삭제할 수 있습니다.
        """, unsafe_allow_html=True)

    st.subheader("📋 임시출입자 명단 관리 (공문 및 사전승인 인원)")
    with st.form("add_temp_form", clear_on_submit=True):
        t1, t2 = st.columns(2)
        with t1:
            t_name = st.text_input("성명 / 업체명", placeholder="홍길동 (공사업체)")
            t_birth = st.text_input("생년월일 (선택)", placeholder="850101")
            t_phone = st.text_input("전화번호 (선택)", placeholder="010-0000-0000")
        with t2:
            t_start = st.date_input("출입 시작일", value=datetime.now(ZoneInfo("Asia/Seoul")).date())
            t_end = st.date_input("출입 종료일", value=datetime.now(ZoneInfo("Asia/Seoul")).date())
            t_car = st.text_input("차량번호", placeholder="12가3456")
        t_reason = st.text_input("방문 사유 / 공문 내용", placeholder="비룡부대 통신망 보수 공사 공문")
        
        if st.form_submit_button("➕ 임시출입자 사전등록", use_container_width=True):
            clean_t_name = t_name.strip()
            if not clean_t_name:
                st.warning("⚠️ 성명 또는 업체명을 정확히 입력해주세요!")
            else:
                new_temp = {
                    "성명": clean_t_name, "생년월일": t_birth.strip() or "-", "전화번호": t_phone.strip() or "-",
                    "출입구분": "민간인(임시)", "차량번호": t_car.strip() or "-",
                    "방문사유": t_reason.strip() or "공문 승인 인원",
                    "시작일": t_start.strftime("%Y-%m-%d"), "종료일": t_end.strftime("%Y-%m-%d"),
                    "비고": f"기간: {t_start}~{t_end}"
                }
                st.session_state.temp_members.append(new_temp)
                save_temp_members(st.session_state.temp_members)
                st.success(f"✅ [{clean_t_name}] 님 임시 등록 완료 (~{t_end})")
                st.rerun()

    st.markdown("---")
    temp_query = st.text_input("🔍 임시출입자 검색", placeholder="성명, 사유, 차량번호로 검색", key="search_tab4_temp")

    for idx, t_mem in enumerate(st.session_state.temp_members):
        if temp_query and not (temp_query in t_mem.get("성명", "") or temp_query in t_mem.get("방문사유", "") or temp_query in t_mem.get("차량번호", "")):
            continue
        t_cols = st.columns([3, 1])
        with t_cols[0]:
            st.markdown(f"**👤 {t_mem['성명']}** | 사유: {t_mem.get('방문사유', '-')} | 기간: {t_mem.get('시작일', '-')} ~ <span style='color:#ffb703; font-weight:bold;'>{t_mem.get('종료일', '-')}</span>", unsafe_allow_html=True)
            st.markdown(f"<span style='color:#aaa; font-size:13px;'>🚗 차량: {t_mem.get('차량번호', '-')} | 📞 연락처: {t_mem.get('전화번호', '-')}</span>", unsafe_allow_html=True)
        with t_cols[1]:
            confirm_del_temp = st.checkbox("삭제 확인", key=f"chk_temp_{idx}")
            if st.button("조기 삭제", key=f"del_temp_{idx}", use_container_width=True, disabled=not confirm_del_temp):
                st.session_state.temp_members.pop(idx)
                save_temp_members(st.session_state.temp_members)
                st.success("삭제되었습니다.")
                st.rerun()
        st.markdown("<hr style='margin: 8px 0; border-color: #222;'>", unsafe_allow_html=True)

# ==================== [탭 5: 지도 연동] ====================
with tab5:
    with st.expander("📖 [사용법 안내] 지도 연동 및 MGRS 검색", expanded=False):
        st.markdown("""
            - 체류 인원의 목적지 지도 위치 및 MGRS 좌표를 실시간으로 확인할 수 있습니다.<br>
            - MGRS 좌표 또는 주소를 직접 입력하여 비룡부대 인근 지도를 검색할 수 있습니다.
        """, unsafe_allow_html=True)

    st.subheader("👥 현재 체류 인원 목적지 위치 확인")
    staying_visitors = [r for r in st.session_state.visitors_log if r.get("상태") == "체류중"]

    for idx, v_row in enumerate(staying_visitors):
        v_name, v_dest = v_row.get("성명", "-"), v_row.get("목적", "-")
        st.markdown(f"""
            <div class="css-card" style="padding: 12px 18px; margin-bottom: 8px;">
                <b style="font-size:16px;">👤 {v_name}</b> | 📍 목적지: <b style="color:#90e0ef;">{v_dest}</b>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"📍 [지도 및 MGRS 좌표 보기] {v_dest}", key=f"btn_dest_{idx}", use_container_width=True):
            encoded_q = html.escape(f"비룡부대 {v_dest}")
            st.components.v1.html(f"""
            <div style="background-color: #1a2332; padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #2d4a6f;">
                <span style="color: #ffb703; font-weight: bold;">📍 MGRS 좌표:</span> <span style="color: #ffffff; font-family: monospace;">52S CE 14285 58291</span>
            </div>
            <div style="border-radius: 12px; overflow: hidden; border: 2px solid #40916c;">
                <iframe width="100%" height="400" style="border:0;" allowfullscreen="" loading="lazy" src="https://maps.google.com/maps?q={encoded_q}&t=k&z=16&ie=UTF8&iwloc=&output=embed"></iframe>
            </div>
            """, height=470)

    st.markdown("<hr style='margin: 30px 0 20px 0; border-color: #444;'>", unsafe_allow_html=True)
    st.subheader("🗺️ MGRS 좌표 및 주소 기반 지도 검색")
    
    search_mode = st.radio("검색 방식 선택", ["MGRS 좌표", "주소 입력"], horizontal=True, key="tab5_search_mode")
    mc1, mc2 = st.columns([3, 1])
    with mc1:
        input_target = st.text_input("좌표/주소 입력", value=st.session_state.map_search_target, placeholder="예: 52S CE 12345 67890 또는 비룡부대", key="tab5_input")
    with mc2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗺️ 지도 검색", use_container_width=True, key="tab5_btn"):
            st.session_state.map_search_target = input_target

    encoded_target = html.escape(st.session_state.map_search_target)
    st.components.v1.html(f"""
    <div style="border-radius: 12px; overflow: hidden; border: 2px solid #333; margin-top: 10px;">
        <iframe width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy" src="https://maps.google.com/maps?q={encoded_target}&t=k&z=15&ie=UTF8&iwloc=&output=embed"></iframe>
    </div>
    """, height=470)
