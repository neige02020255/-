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
    .stTextInput input {
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

# 고정 출입자 명단 기본값 (전화번호, 목적지, 구역 추가)
if "fixed_members" not in st.session_state:
    st.session_state.fixed_members = [
        {"성명": "김영농", "전화번호": "010-1234-5678", "차량번호": "12가3456", "목적지": "북삼리 영농지", "통제구역": "A구역"},
        {"성명": "이공사", "전화번호": "010-9876-5432", "차량번호": "78나9012", "목적지": "초소 보수공사 현장", "통제구역": "B구역"}
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

    # 성명을 입력받아 실시간으로 고정명단 매칭
    input_name = st.text_input("성명 (입력 시 고정명단 자동 매칭)", key="entry_name_input")
    
    # 기본값 세팅
    default_phone = ""
    default_car = ""
    default_dest = ""
    default_zone = ""

    # 성명이 고정 명단에 있는지 체크하여 정보 자동 가져오기
    if input_name.strip():
        matched_member = next((m for m in st.session_state.fixed_members if m["성명"] == input_name.strip()), None)
        if matched_member:
            default_phone = matched_member.get("전화번호", "")
            default_car = matched_member.get("차량번호", "")
            default_dest = matched_member.get("목적지", "")
            default_zone = matched_member.get("통제구역", "")

    with st.form("entry_form", clear_on_submit=True):
        phone = st.text_input("전화번호", value=default_phone, placeholder="예: 010-1234-5678")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            car = st.text_input("차종 및 차량번호", value=default_car, placeholder="예: 1234 / 아반떼")
            dest = st.text_input("목적지", value=default_dest, placeholder="예: 북삼리 영농지")
        with col_f2:
            zone = st.text_input("통제 구역", value=default_zone, placeholder="예: A구역")
            st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 입영 처리", use_container_width=True)
        if submitted:
            final_name = input_name.strip()
            if not final_name:
                st.warning("⚠️ 성명을 입력해주세요.")
            else:
                time_now = datetime.now().strftime("%H:%M")
                new_entry = {
                    "시간": time_now,
                    "성명": final_name,
                    "전화번호": phone if phone else "-",
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
        search_query = st.text_input("🔍 출입자 검색 (성명, 전화번호, 차량번호 입력)", placeholder="이름, 번호, 차량번호 검색")
        
        if search_query:
            filtered_list = []
            for idx, row in staying_list:
                if (search_query in str(row.get("성명", "")) or 
                    search_query in str(row.get("전화번호", "")) or 
                    search_query in str(row.get("차량", ""))):
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
                            <b style="font-size:18px;">👤 {row.get('성명', '-')}</b> &nbsp; <span style="color:#aaa;">(📞 {row.get('전화번호', '-')})</span><br>
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
    st.markdown("자주 출입하는 인원의 인적사항을 사전에 입력해 두면, 입영 등록 시 이름만 입력해도 정보가 자동 완성됩니다.")

    with st.form("add_fixed_form", clear_on_submit=True):
        f_name = st.text_input("고정 출입자 성명")
        f_phone = st.text_input("전화번호", placeholder="예: 010-1234-5678")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            f_car = st.text_input("차량번호", placeholder="예: 12가3456")
            f_dest = st.text_input("자주 방문하는 목적지", placeholder="예: 북삼리 영농지")
        with col_m2:
            f_zone = st.text_input("주 통제구역", placeholder="예: A구역")
            st.markdown("<br>", unsafe_allow_html=True)
            
        f_submitted = st.form_submit_button("➕ 고정 명단에 추가", use_container_width=True)
        if f_submitted:
            if f_name.strip():
                st.session_state.fixed_members.append({
                    "성명": f_name.strip(),
                    "전화번호": f_phone.strip() if f_phone.strip() else "-",
                    "차량번호": f_car.strip() if f_car.strip() else "-",
                    "목적지": f_dest.strip() if f_dest.strip() else "-",
                    "통제구역": f_zone.strip() if f_zone.strip() else "-"
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
            col_list1, col_list2 = st.columns([4, 1])
            with col_list1:
                st.markdown(f"**👤 {member['성명']}** (📞 {member.get('전화번호', '-')})")
                st.markdown(f"<span style='color:#aaa; font-size:13px;'>🚗 차량: {member.get('차량번호', '-')} | 📍 목적지: {member.get('목적지', '-')} | 🛡️ 구역: {member.get('통제구역', '-')}</span>", unsafe_allow_html=True)
            with col_list2:
                if st.button("삭제", key=f"del_fixed_{m_idx}", use_container_width=True):
                    st.session_state.fixed_members.pop(m_idx)
                    st.rerun()
            st.markdown("<hr style='margin: 8px 0; border-color: #222;'>", unsafe_allow_html=True)
