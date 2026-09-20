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
            <p>현재 체류 중인 인원 전체가 기본 수신대상으로 지정되어 있습니다.</p>
        </div>
    """, unsafe_allow_html=True)
    staying_visitors = [r for r in st.session_state.visitors_log if r.get("상태") == "체류중"]
    selected_recipients = []
    for idx, visitor in enumerate(staying_visitors):
        if st.checkbox(f"[{visitor.get('출입구분', '-')}] 성명: {visitor.get('성명', '-')} | 연락처: {visitor.get('전화번호', '-')}", value=True, key=f"recip_chk_{idx}"):
            selected_recipients.append(visitor)
    if st.button("📤 최종 긴급 문자 전송", type="primary", use_container_width=True):
        st.success(f"🚨 총 {len(selected_recipients)}명에게 긴급 문자가 전송되었습니다!")
        st.session_state.emergency_step = 0
        st.rerun()
    if st.button("취소 및 나가기", use_container_width=True):
        st.session_state.emergency_step = 0
        st.rerun()

if st.session_state.show_map_panel:
    top_target = st.text_input("주소 입력", value=st.session_state.map_search_target, key="top_addr_txt")
    encoded_top_target = html.escape(top_target)
    st.components.v1.html(f"""
        <div style="border-radius: 12px; overflow: hidden; border: 2px solid #333;">
            <iframe width="100%" height="400" style="border:0;" src="https://maps.google.com/maps?q={encoded_top_target}&t=k&z=15&output=embed"></iframe>
        </div>
    """, height=420)

# ----------------- [탭 메뉴 구성] -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 출입 관리 및 현황", "🏁 퇴영 목록", "📋 고정출입자 명단 관리", "📋 임시출입자 명단 관리", "🗺️ 지도 연동"])

# ==================== [탭 1: 출입 관리 및 현황] ====================
with tab1:
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.subheader("📝 출입자 등록 (입영)")
        if "temp_input_name" not in st.session_state: st.session_state.temp_input_name = ""
        if "selected_matched_member" not in st.session_state: st.session_state.selected_matched_member = None
        if "ambiguous_matches" not in st.session_state: st.session_state.ambiguous_matches = []

        with st.form("name_check_form"):
            col_nc1, col_nc2 = st.columns([3, 1])
            with col_nc1:
                typed_name = st.text_input("성명 입력", value=st.session_state.temp_input_name)
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
                    elif len(total_found) > 1:
                        st.session_state.selected_matched_member = None
                        st.session_state.ambiguous_matches = total_found
                    else:
                        st.session_state.selected_matched_member = None
                        st.session_state.ambiguous_matches = []

        if st.session_state.ambiguous_matches:
            choice_options = [f"성명: {m.get('성명')} | 구분: {m.get('출입구분', '임시')} | 차량: {m.get('차량번호', '-')}" for m in st.session_state.ambiguous_matches]
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
            
            col_i1, col_i2 = st.columns(2)
            with col_i1:
                birth_date = st.text_input("생년월일 (6자리)", value=m_data.get("생년월일", ""))
            with col_i2:
                phone = st.text_input("전화번호", value=m_data.get("전화번호", ""))
                
            default_type = m_data.get("출입구분", "영농인(고정)")
            selected_type_preset = st.selectbox("출입 구분", ENTRY_TYPE_OPTIONS, index=ENTRY_TYPE_OPTIONS.index(default_type) if default_type in ENTRY_TYPE_OPTIONS else 0)
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                car = st.text_input("차종 및 차량번호", value=m_data.get("차량번호", ""))
                dest = st.text_input("목적지", value=m_data.get("목적지", ""))
            with col_f2:
                zone = st.text_input("통제 구역", value=m_data.get("통제구역", ""))
                note = st.text_input("비고", value=m_data.get("비고", ""))
            
            if st.form_submit_button("🚀 최종 입영 처리", use_container_width=True):
                final_name = input_name.strip()
                if final_name:
                    new_entry = {
                        "날짜": get_kts_date(), "출입시간": get_kts_time("%H:%M"), "퇴영시간": "-",
                        "성명": final_name, "생년월일": birth_date.strip() or "-", "전화번호": phone.strip() or "-",
                        "출입구분": selected_type_preset, "차량": car.strip() or "-", "목적": dest.strip() or "-",
                        "구역": zone.strip() or "-", "비고": note.strip() or "-", "상태": "체류중"
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
        display_list = [(i, row) for i, row in all_logs if row.get("상태") == "체류중"]

        for row_idx, row in display_list[:5]:
            st.markdown(f"""
                <div class="css-card">
                    <b>👤 {row.get('성명', '-')}</b> [{row.get('출입구분', '-')}] | <span style="color:#40916c;">[체류중]</span><br>
                    🚗 차량: {row.get('차량', '-')} | 🛡️ 구역: {row.get('구역', '-')}
                </div>
            """, unsafe_allow_html=True)
            if st.button("🏁 퇴영 처리", key=f"out_{row_idx}", use_container_width=True):
                st.session_state.visitors_log[row_idx]["상태"] = "퇴영완료"
                st.session_state.visitors_log[row_idx]["퇴영시간"] = get_kts_time("%H:%M")
                save_visitors_log(st.session_state.visitors_log)
                st.rerun()

    # 탭 1 종합 현황판 하단 (요청하신 4칸 구성 및 통제구역 인원수 포함)
    today_str = get_kts_date()
    today_entered = [r for r in st.session_state.visitors_log if r.get("날짜", today_str) == today_str]
    all_staying = [r for r in st.session_state.visitors_log if r.get("상태") == "체류중"]
    today_out = [r for r in today_entered if r.get("상태") == "퇴영완료"]

    st.markdown("""
        <div class="dashboard-box">
            <h3 style="margin-top:0; color:#90e0ef; margin-bottom:15px;">📈 종합 현황판 및 4칸 구역별 인원수 현황 (오늘 기준)</h3>
    """, unsafe_allow_html=True)

    # 4개의 열(Column)로 구성
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
            <div class="stat-card">
                <h4 style="margin:0; color:#90e0ef;">오늘 총 입영</h4>
                <p style="font-size: 20px; font-weight: bold; margin: 5px 0 0 0;">{len(today_entered)} 명</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("##### 📌 입영 세부")
        if today_entered:
            df_t = pd.DataFrame(today_entered)
            st.dataframe(df_t["출입구분"].value_counts().reset_index(name="인원"), use_container_width=True, hide_index=True)
        else:
            st.info("기록 없음")

    with c2:
        st.markdown(f"""
            <div class="stat-card">
                <h4 style="margin:0; color:#90e0ef;">현재 총 체류</h4>
                <p style="font-size: 20px; font-weight: bold; margin: 5px 0 0 0;">{len(all_staying)} 명</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("##### 📌 체류 세부 (구역/구분)")
        if all_staying:
            df_s = pd.DataFrame(all_staying)
            zone_key = "구역" if "구역" in df_s.columns else "통제구역"
            df_s_cnt = df_s.groupby([zone_key, "출입구분"]).size().reset_index(name="인원")
            df_s_cnt.columns = ["구역", "구분", "인원"]
            st.dataframe(df_s_cnt, use_container_width=True, hide_index=True)
        else:
            st.info("기록 없음")

    with c3:
        # 통제구역별 인원수 전용 칸 추가
        st.markdown(f"""
            <div class="stat-card">
                <h4 style="margin:0; color:#ffb703;">통제구역별 현황</h4>
                <p style="font-size: 20px; font-weight: bold; margin: 5px 0 0 0;">구역별 집계</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("##### 📌 구역별 체류 인원수")
        if all_staying:
            df_zone = pd.DataFrame(all_staying)
            zone_key = "구역" if "구역" in df_zone.columns else "통제구역"
            df_zone_cnt = df_zone[zone_key].value_counts().reset_index()
            df_zone_cnt.columns = ["통제구역", "인원(명)"]
            st.dataframe(df_zone_cnt, use_container_width=True, hide_index=True)
        else:
            st.info("체류 인원 없음")

    with c4:
        st.markdown(f"""
            <div class="stat-card">
                <h4 style="margin:0; color:#90e0ef;">오늘 총 퇴영</h4>
                <p style="font-size: 20px; font-weight: bold; margin: 5px 0 0 0;">{len(today_out)} 명</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("##### 📌 퇴영 세부")
        if today_out:
            df_o = pd.DataFrame(today_out)
            st.dataframe(df_o["출입구분"].value_counts().reset_index(name="인원"), use_container_width=True, hide_index=True)
        else:
            st.info("기록 없음")

    st.markdown("</div>", unsafe_allow_html=True)

# ==================== [탭 2: 퇴영 목록] ====================
with tab2:
    st.subheader("🏁 오늘 퇴영 완료된 인원 목록")
    today_out_list = [(i, row) for i, row in enumerate(st.session_state.visitors_log) if row.get("상태") == "퇴영완료" and row.get("날짜", today_str) == today_str]
    for row_idx, row in today_out_list:
        st.markdown(f"""
            <div class="css-card">
                <b>👤 {row.get('성명', '-')}</b> [{row.get('출입구분', '-')}] | <span style='color:#457b9d;'>[퇴영완료]</span><br>
                📥 입영: {row.get('출입시간', '-')} | 📤 퇴영: <b style='color:#90e0ef;'>{row.get('퇴영시간', '-')}</b>
            </div>
        """, unsafe_allow_html=True)

# ==================== [탭 3: 고정출입자 명단 관리] ====================
with tab3:
    st.subheader("📋 고정출입자 명단 관리")
    for idx, member in enumerate(st.session_state.fixed_members):
        col_l1, col_l2 = st.columns([3, 1])
        with col_l1:
            st.markdown(f"**👤 {member['성명']}** [{member.get('출입구분', '-')}] | 구역: {member.get('통제구역', '-')}")
        with col_l2:
            if st.checkbox("삭제 확인", key=f"chk_fixed_{idx}"):
                if st.button("삭제", key=f"del_fixed_{idx}", use_container_width=True):
                    st.session_state.fixed_members.pop(idx)
                    save_fixed_members(st.session_state.fixed_members)
                    st.rerun()

# ==================== [탭 4: 임시출입자 명단 관리] ====================
with tab4:
    st.subheader("📋 임시출입자 명단 관리")
    for idx, t_mem in enumerate(st.session_state.temp_members):
        t_cols = st.columns([3, 1])
        with t_cols[0]:
            st.markdown(f"**👤 {t_mem['성명']}** | 기간: {t_mem.get('시작일', '-')} ~ {t_mem.get('종료일', '-')}")
        with t_cols[1]:
            if st.checkbox("삭제 확인", key=f"chk_temp_{idx}"):
                if st.button("조기 삭제", key=f"del_temp_{idx}", use_container_width=True):
                    st.session_state.temp_members.pop(idx)
                    save_temp_members(st.session_state.temp_members)
                    st.rerun()

# ==================== [탭 5: 지도 연동] ====================
with tab5:
    st.subheader("🗺️ MGRS 좌표 및 주소 기반 지도 검색")
    input_target = st.text_input("좌표/주소 입력", value=st.session_state.map_search_target, key="tab5_input")
    encoded_target = html.escape(input_target)
    st.components.v1.html(f"""
    <div style="border-radius: 12px; overflow: hidden; border: 2px solid #333;">
        <iframe width="100%" height="450" style="border:0;" src="https://maps.google.com/maps?q={encoded_target}&t=k&z=15&output=embed"></iframe>
    </div>
    """, height=470)
