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

# ==================== [초기 고정출입자 대량 생성] ====================
if "fixed_members" not in st.session_state:
    initial_members = [
        {"성명": "김영농", "생년월일": "651012", "전화번호": "010-1234-5678", "출입구분": "영농인", "차량번호": "12가3456", "목적지": "북삼리 영농지", "통제구역": "A구역"},
        {"성명": "이공사", "생년월일": "720515", "전화번호": "010-9876-5432", "출입구분": "공사인원", "차량번호": "78나9012", "목적지": "초소 보수공사", "통제구역": "B구역"},
        {"성명": "박병장", "생년월일": "030120", "전화번호": "010-1111-2222", "출입구분": "군인", "차량번호": "지휘차 5521", "목적지": "DMZ 파견근무", "통제구역": "C구역"},
        {"성명": "김영농", "생년월일": "800101", "전화번호": "010-5555-6666", "출입구분": "영농인", "차량번호": "33다5555", "목적지": "남방한계선 영농지", "통제구역": "A구역"}
    ]
    
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", "전", "홍"]
    first_names = ["민준", "서준", "도윤", "예준", "시우", "하준", "주원", "지호", "준우", "도현", "서연", "서윤", "지우", "서현", "민서", "하윤", "지민", "채원", "지유", "지안", "영수", "영철", "정호", "상훈", "성진"]
    types_pool = ["영농인", "공사인원", "안보관광", "군인", "고정", "성묘객"]
    zones_pool = ["A구역", "B구역", "C구역", "DMZ통로", "영농단지"]
    
    import random
    random.seed(42)
    
    for i in range(1, 180):
        l_name = random.choice(last_names)
        f_name = random.choice(first_names)
        full_name = f"{l_name}{f_name}{i}" if i > 25 else f"{l_name}{f_name}"
        
        birth_year = random.choice(range(50, 95))
        birth_date = f"{birth_year}{random.choice(range(1, 13)):02d}{random.choice(range(1, 29)):02d}"
        phone_num = f"010-{random.choice(range(1000, 10000))}-{random.choice(range(1000, 10000))}"
        car_num = f"{random.choice(range(10, 100))}{random.choice(['가','나','다','라','마','바','사','아'])}{random.choice(range(1000, 10000))}"
        v_type = random.choice(types_pool)
        zone = random.choice(zones_pool)
        
        initial_members.append({
            "성명": full_name,
            "생년월일": birth_date,
            "전화번호": phone_num,
            "출입구분": v_type,
            "차량번호": car_num,
            "목적지": f"{zone} 일대 영농/작업",
            "통제구역": zone
        })
        
    st.session_state.fixed_members = initial_members

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

    # 1단계: 고정출입자 명단 검색 기능 추가
    if "applied_entry_search" not in st.session_state:
        st.session_state.applied_entry_search = ""

    with st.form("entry_member_search_form"):
        col_es1, col_es2 = st.columns([3, 1])
        with col_es1:
            entry_search_input = st.text_input("🔍 명단 검색 (성명 또는 차량번호)", placeholder="이름이나 차량번호 입력", label_visibility="collapsed")
        with col_es2:
            entry_search_btn = st.form_submit_button("명단검색", use_container_width=True)

    if entry_search_btn:
        st.session_state.applied_entry_search = entry_search_input

    current_search_term = st.session_state.applied_entry_search

    # 검색어에 따른 고정명단 필터링
    if current_search_term.strip():
        filtered_fixed_members = [
            m for m in st.session_state.fixed_members 
            if current_search_term in m["성명"] or current_search_term in m["차량번호"]
        ]
    else:
        filtered_fixed_members = st.session_state.fixed_members

    member_options = ["직접 입력 / 신규 등록"] + [f"{m['성명']} (생년: {m['생년월일']}, 전화: {m['전화번호']}, 차량: {m['차량번호']})" for m in filtered_fixed_members]
    
    selected_member_str = st.selectbox(f"고정출입자 선택 (검색 결과: {len(filtered_fixed_members)}명)", member_options)

    default_name = ""
    default_birth = ""
    default_phone = ""
    default_type = "영농인"
    default_car = ""
    default_dest = ""
    default_zone = ""
    types_list = ["영농인", "공사인원", "군인", "안보관광", "고정", "성묘객", "민간인"]
    default_type_index = 0

    if selected_member_str != "직접 입력 / 신규 등록":
        # 선택된 인원을 필터링된 목록에서 찾기
        selected_idx = member_options.index(selected_member_str) - 1
        matched_member = filtered_fixed_members[selected_idx]
        default_name = matched_member.get("성명", "")
        default_birth = matched_member.get("생년월일", "")
        default_phone = matched_member.get("전화번호", "")
        default_type = matched_member.get("출입구분", "영농인")
        default_car = matched_member.get("차량번호", "")
        default_dest = matched_member.get("목적지", "")
        default_zone = matched_member.get("통제구역", "")
        if default_type in types_list:
            default_type_index = types_list.index(default_type)

    with st.form("entry_form", clear_on_submit=True):
        input_name = st.text_input("성명", value=default_name)
        
        col_i1, col_i2 = st.columns(2)
        with col_i1:
            birth_date = st.text_input("생년월일 (6자리)", value=default_birth, placeholder="예: 751225")
        with col_i2:
            phone = st.text_input("전화번호", value=default_phone, placeholder="예: 010-1234-5678")
            
        v_type = st.selectbox("출입 구분", types_list, index=default_type_index)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            car = st.text_input("차종 및 차량번호", value=default_car, placeholder="예: 12가3456")
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
                    "출입시간": time_now,
                    "퇴영시간": "-",
                    "성명": final_name,
                    "생년월일": birth_date if birth_date else "-",
                    "전화번호": phone if phone else "-",
                    "출입구분": v_type,
                    "차량": car if car else "-",
                    "목적": dest if dest else "-",
                    "구역": zone if zone else "-",
                    "상태": "체류중"
                }
                st.session_state.visitors_log.append(new_entry)
                st.success(f"🎉 [{final_name}] 님 입영 처리 완료!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================== [배너 1: 현재 체류 중인 출입자 현황] ====================
    st.markdown("---")
    st.markdown("### 📊 [출입 현황] 현재 통제구역 내 체류 인원")

    staying_list = [(i, row) for i, row in enumerate(st.session_state.visitors_log) if row.get("상태") == "체류중"]

    if not staying_list:
        st.info("💡 현재 초소 통제구역 내 체류 중인 인원이 없습니다.")
    else:
        with st.form("staying_search_form"):
            col_s1, col_s2 = st.columns([3, 1])
            with col_s1:
                staying_query_input = st.text_input("🔍 출입자 검색어", placeholder="이름, 번호, 차량번호 입력", label_visibility="collapsed")
            with col_s2:
                staying_search_btn = st.form_submit_button("검색", use_container_width=True)
        
        if "applied_staying_query" not in st.session_state:
            st.session_state.applied_staying_query = ""

        if staying_search_btn:
            st.session_state.applied_staying_query = staying_query_input

        search_query = st.session_state.applied_staying_query

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

        st.markdown(f"<p style='color: #aaa; font-size: 14px;'>체류 인원: <b>{len(staying_list)}명</b> (검색 결과: {len(display_list)}명)</p>", unsafe_allow_html=True)

        if not display_list:
            st.warning("🔍 검색 결과가 없습니다.")
        else:
            for row_idx, row in display_list:
                with st.container():
                    st.markdown(f"""
                        <div class="css-card">
                            <b style="font-size:18px;">👤 {row.get('성명', '-')}</b> <span style="color:#aaa;">({row.get('출입구분', '-')})</span><br>
                            🎂 생년월일: {row.get('생년월일', '-')} &nbsp;|&nbsp; 📞 전화: {row.get('전화번호', '-')}<br>
                            🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')} &nbsp;|&nbsp; 🛡️ 구역: {row.get('구역', '-')}<br>
                            <span style="color: #40916c; font-size: 13px; font-weight: bold;">입영 시각: {row.get('출입시간', '-')}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🏁 퇴영 처리", key=f"out_{row_idx}", use_container_width=True):
                        st.session_state.visitors_log[row_idx]["상태"] = "퇴영완료"
                        st.session_state.visitors_log[row_idx]["퇴영시간"] = datetime.now().strftime("%H:%M")
                        st.rerun()

    # ==================== [배너 2: 퇴영 목록] ====================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🏁 [퇴영 목록] 초소 통과 완료된 기록")

    out_list = [(i, row) for i, row in enumerate(st.session_state.visitors_log) if row.get("상태") == "퇴영완료"]

    if not out_list:
        st.info("💡 오늘 퇴영 완료된 기록이 없습니다.")
    else:
        with st.form("out_search_form"):
            col_os1, col_os2 = st.columns([3, 1])
            with col_os1:
                out_query_input = st.text_input("🔍 퇴영자 검색어", placeholder="이름이나 차량번호 검색", label_visibility="collapsed")
            with col_os2:
                out_search_btn = st.form_submit_button("검색", use_container_width=True)

        if "applied_out_query" not in st.session_state:
            st.session_state.applied_out_query = ""

        if out_search_btn:
            st.session_state.applied_out_query = out_query_input

        out_search = st.session_state.applied_out_query

        if out_search:
            filtered_out = []
            for idx, row in out_list:
                if out_search in str(row.get("성명", "")) or out_search in str(row.get("차량", "")):
                    filtered_out.append((idx, row))
            display_out_list = filtered_out
        else:
            display_out_list = out_list

        st.markdown(f"<p style='color: #aaa; font-size: 13px;'>총 퇴영 기록: <b>{len(out_list)}명</b> (검색 결과: {len(display_out_list)}명)</p>", unsafe_allow_html=True)

        for row_idx, row in display_out_list:
            st.markdown(f"**👤 {row.get('성명', '-')}** ({row.get('출입구분', '-')}) &nbsp;|&nbsp; 🚗 {row.get('차량', '-')} &nbsp;|&nbsp; 📍 {row.get('목적', '-')}")
            st.markdown(f"<span style='color:#aaa; font-size:13px;'>📥 출입 시간: {row.get('출입시간', '-')} &nbsp;|&nbsp; 📤 퇴영 시간: <b style='color:#adb5bd;'>{row.get('퇴영시간', '-')}</b></span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 8px 0; border-color: #333;'>", unsafe_allow_html=True)

# ==================== [탭 2: 고정출입자 명단 관리] ====================
with tab2:
    st.subheader("📋 고정출입자 명단 추가 / 삭제")
    st.markdown("자주 출입하는 인원의 인적사항을 관리합니다.")

    with st.form("add_fixed_form", clear_on_submit=True):
        f_name = st.text_input("고정 출입자 성명")
        
        col_mf1, col_mf2 = st.columns(2)
        with col_mf1:
            f_birth = st.text_input("생년월일 (6자리)", placeholder="예: 751225")
            f_car = st.text_input("차량번호", placeholder="예: 12가3456")
            f_dest = st.text_input("목적지", placeholder="예: 북삼리 영농지")
        with col_mf2:
            f_phone = st.text_input("전화번호", placeholder="예: 010-1234-5678")
            f_type = st.selectbox("출입 구분", ["영농인", "공사인원", "군인", "안보관광", "고정", "성묘객"], key="new_fixed_type")
            f_zone = st.text_input("통제구역", placeholder="예: A구역")
            
        f_submitted = st.form_submit_button("➕ 고정 명단에 추가", use_container_width=True)
        if f_submitted:
            if f_name.strip():
                st.session_state.fixed_members.append({
                    "성명": f_name.strip(),
                    "생년월일": f_birth.strip() if f_birth.strip() else "-",
                    "전화번호": f_phone.strip() if f_phone.strip() else "-",
                    "출입구분": f_type,
                    "차량번호": f_car.strip() if f_car.strip() else "-",
                    "목적지": f_dest.strip() if f_dest.strip() else "-",
                    "통제구역": f_zone.strip() if f_zone.strip() else "-"
                })
                st.success(f"✅ [{f_name.strip()}] 님이 고정명단에 추가되었습니다!")
                st.rerun()
            else:
                st.warning("⚠️ 성명을 입력해주세요.")

    st.markdown("---")
    st.subheader(f"🗑️ 등록된 고정출입자 목록 (현재 {len(st.session_state.fixed_members)}명)")

    with st.form("fixed_search_form"):
        col_fs1, col_fs2 = st.columns([3, 1])
        with col_fs1:
            fixed_query_input = st.text_input("🔍 고정명단 검색어", placeholder="이름이나 차량번호 검색", label_visibility="collapsed")
        with col_fs2:
            fixed_search_btn = st.form_submit_button("검색", use_container_width=True)

    if "applied_fixed_query" not in st.session_state:
        st.session_state.applied_fixed_query = ""

    if fixed_search_btn:
        st.session_state.applied_fixed_query = fixed_query_input

    fixed_search = st.session_state.applied_fixed_query

    if not st.session_state.fixed_members:
        st.info("등록된 고정출입자가 없습니다.")
    else:
        display_fixed = st.session_state.fixed_members
        if fixed_search:
            display_fixed = [m for m in st.session_state.fixed_members if fixed_search in m["성명"] or fixed_search in m["차량번호"]]

        st.markdown(f"<p style='color: #aaa; font-size: 13px;'>검색 결과: 총 {len(display_fixed)}명</p>", unsafe_allow_html=True)

        for m_idx, member in enumerate(display_fixed):
            col_list1, col_list2 = st.columns([4, 1])
            with col_list1:
                st.markdown(f"**👤 {member['성명']}** ({member.get('출입구분', '-')}) &nbsp;|&nbsp; 🎂 {member.get('생년월일', '-')} &nbsp;|&nbsp; 📞 {member.get('전화번호', '-')}")
                st.markdown(f"<span style='color:#aaa; font-size:13px;'>🚗 차량: {member.get('차량번호', '-')} | 📍 목적: {member.get('목적지', '-')} | 🛡️ 구역: {member.get('통제구역', '-')}</span>", unsafe_allow_html=True)
            with col_list2:
                real_idx = st.session_state.fixed_members.index(member)
                if st.button("삭제", key=f"del_fixed_{real_idx}", use_container_width=True):
                    st.session_state.fixed_members.pop(real_idx)
                    st.rerun()
            st.markdown("<hr style='margin: 8px 0; border-color: #222;'>", unsafe_allow_html=True)
