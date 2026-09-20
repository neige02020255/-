from datetime import datetime
import streamlit as st

# ==================== [설정] ====================
CORRECT_PASSWORD = "1234"  # 접속 비밀번호

# 페이지 기본 설정
st.set_page_config(page_title="제25보병사단 비룡초소 출입 관리", layout="centered")

# ==================== [다크모드 CSS 디자인 스타일] ====================
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    .css-card {
        background-color: #1e1e1e;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 12px;
        border-left: 5px solid #40916c;
        color: #ffffff;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #ffffff !important;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #2b2b2b !important;
        color: #ffffff !important;
        border-radius: 8px;
    }
    .badge-box {
        background-color: #2d6a4f;
        color: white;
        padding: 8px 15px;
        border-radius: 8px;
        font-weight: bold;
        display: inline-block;
        font-size: 16px;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== [세션 상태 초기화] ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 체류 중인 출입자 목록 메모리 저장소
if "visitors_log" not in st.session_state:
    st.session_state.visitors_log = []

# 고정 출입자 명단 기본값
if "fixed_members" not in st.session_state:
    st.session_state.fixed_members = [
        {"성명": "김영농", "소속구분": "영농인", "차량번호": "1234"},
        {"성명": "이공사", "소속구분": "공사인원", "차량번호": "5678"}
    ]

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

# ==================== [메인 출입 관리 화면] ====================

st.markdown("""
    <div>
        <span class="badge-box">🛡️ 제25보병사단 비룡부대</span>
        <h2 style='margin: 5px 0 0 0;'>민통초소 실시간 출입 관리 시스템</h2>
    </div>
""", unsafe_allow_html=True)

col_space, col_logout = st.columns([4, 1])
with col_logout:
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("<hr style='margin: 10px 0 20px 0; border-color: #333;'>", unsafe_allow_html=True)

# ----------------- [탭 메뉴 구성] -----------------
tab1, tab2 = st.tabs(["🚀 출입 관리 및 현황", "📋 고정출입자 명단 관리"])

# ==================== [탭 1: 출입 관리 및 현황] ====================
with tab1:
    st.subheader("📝 출입자 등록 (입영)")

    # 1. 고정 명단 선택 (selectbox는 form 바깥에 배치하여 선택 즉시 값이 반영되도록 함)
    fixed_options = ["직접 입력"] + [f"{m['성명']} ({m['소속구분']})" for m in st.session_state.fixed_members]
    chosen = st.selectbox("📋 등록된 고정출입자 불러오기 (선택 시 자동완성)", fixed_options)

    # 선택된 값에 따라 기본 정보 세팅
    default_name = ""
    default_type = "영농인"
    default_car = "-"
    
    types_list = ["영농인", "공사인원", "안보관광", "고정", "성묘객", "민간인"]
    default_type_index = 0

    if chosen != "직접 입력":
        idx = fixed_options.index(chosen) - 1
        matched = st.session_state.fixed_members[idx]
        default_name = matched["성명"]
        default_type = matched["소속구분"]
        default_car = matched["차량번호"]
        if default_type in types_list:
            default_type_index = types_list.index(default_type)

    with st.form("entry_form", clear_on_submit=True):
        custom_name = st.text_input("성명", value=default_name)
        v_type = st.selectbox("출입 구분", types_list, index=default_type_index)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            car = st.text_input("차종 및 차량번호", value=default_car, placeholder="예: 1234 / 아반떼")
            dest = st.text_input("목적지", placeholder="예: 북삼리 영농지")
        with col_f2:
            zone = st.text_input("통제 구역", placeholder="예: A구역")
            st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 입영 처리", use_container_width=True)
        if submitted:
            final_name = custom_name.strip()
            if not final_name:
                st.warning("⚠️ 성명을 입력해주세요.")
            else:
                time_now = datetime.now().strftime("%H:%M")
                new_entry = {
                    "시간": time_now,
                    "소속": v_type,
                    "성명": final_name,
                    "차량": car if car else "-",
                    "목적": dest if dest else "-",
                    "구역": zone if zone else "-",
                    "상태": "체류중"
                }
                st.session_state.visitors_log.append(new_entry)
                st.success(f"🎉 [{final_name}] 님 입영 처리 완료!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 현재 체류 현황 및 검색 섹션
    st.subheader("📊 현재 체류 중인 출입자 현황")

    staying_list = [(i, row) for i, row in enumerate(st.session_state.visitors_log) if row.get("상태") == "체류중"]

    if not staying_list:
        st.info("💡 현재 초소 통제구역 내 체류 중인 인원이 없습니다.")
    else:
        search_query = st.text_input("🔍 출입자 검색 (성명 또는 차량번호 입력)", placeholder="이름이나 차량번호를 입력하세요")
        
        if search_query:
            filtered_list = []
            for idx, row in staying_list:
                if search_query in str(row.get("성명", "")) or search_query in str(row.get("차량", "")):
                    filtered_list.append((idx, row))
            display_list = filtered_list
        else:
            display_list = staying_list

        st.markdown(f"<p style='color: #aaa; font-size: 14px;'>총 체류 인원: <b>{len(staying_list)}명</b> (검색 결과: {len(display_list)}명)</p>", unsafe_allow_html=True)

        if not display_list:
            st.warning("🔍 검색 결과가 없습니다.")
        else:
            for row_idx, row in display_list:
                with st.container():
                    st.markdown(f"""
                        <div class="css-card">
                            <b>[{row.get('소속', '-')}] {row.get('성명', '-')}</b><br>
                            🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')} &nbsp;|&nbsp; 🛡️ 구역: {row.get('구역', '-')}<br>
                            <span style="color: #aaaaaa; font-size: 13px;">입영 시각: {row.get('시간', '-')}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🏁 퇴영 처리", key=f"out_{row_idx}", use_container_width=True):
                        st.session_state.visitors_log[row_idx]["상태"] = "퇴영완료"
                        st.rerun()

# ==================== [탭 2: 고정출입자 명단 관리] ====================
with tab2:
    st.subheader("📋 고정출입자 명단 추가 / 삭제")
    st.markdown("자주 출입하는 영농인이나 공사인원을 여기서 직접 등록하고 관리할 수 있습니다.")

    with st.form("add_fixed_form", clear_on_submit=True):
        f_name = st.text_input("고정 출입자 성명")
        f_type = st.selectbox("출입 구분", ["영농인", "공사인원", "고정"], key="f_type_box")
        f_car = st.text_input("차량번호", placeholder="예: 1234")
        
        f_submitted = st.form_submit_button("➕ 고정 명단에 추가", use_container_width=True)
        if f_submitted:
            if f_name.strip():
                st.session_state.fixed_members.append({
                    "성명": f_name.strip(),
                    "소속구분": f_type,
                    "차량번호": f_car.strip() if f_car.strip() else "-"
                })
                st.success(f"✅ [{f_name.strip()}] 님이 고정명단에 추가되었습니다!")
                st.rerun()
            else:
                st.warning("⚠️ 성명을 입력해주세요.")

    st.markdown("---")
    st.subheader("🗑️ 등록된 고정출입자 목록")

    if not st.session_state.fixed_members:
        st.info("등록된 고정출입자가 없습니다.")
    else:
        for m_idx, member in enumerate(st.session_state.fixed_members):
            col_m1, col_m2 = st.columns([4, 1])
            with col_m1:
                st.markdown(f"**{member['성명']}** ({member['소속구분']}) — 차량: `{member['차량번호']}`")
            with col_m2:
                if st.button("삭제", key=f"del_fixed_{m_idx}", use_container_width=True):
                    st.session_state.fixed_members.pop(m_idx)
                    st.rerun()
