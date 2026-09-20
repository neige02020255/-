from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import json
import os

# ==================== [설정 및 파일 저장 함수] ====================
CORRECT_PASSWORD = "1234"  # 접속 비밀번호
FIXED_MEMBERS_FILE = "fixed_members.json"

# 페이지 기본 설정 (와이드 모드 적용)
st.set_page_config(page_title="제25보병사단 비룡초소 출입 관리", layout="wide")

# 고정출입자 명단 로드 함수 (서버 파일에서 읽기)
def load_fixed_members():
    initial_members = [
        {"성명": "김영농", "생년월일": "651012", "전화번호": "010-1234-5678", "출입구분": "영농인", "차량번호": "12가3456", "목적지": "북삼리 영농지", "통제구역": "A구역", "비고": "특이사항 없음"},
        {"성명": "이공사", "생년월일": "720515", "전화번호": "010-9876-5432", "출입구분": "공사인원", "차량번호": "78나9012", "목적지": "초소 보수공사", "통제구역": "B구역", "비고": "장비 지참"},
        {"성명": "박병장", "생년월일": "030120", "전화번호": "010-1111-2222", "출입구분": "군인", "차량번호": "지휘차 5521", "목적지": "DMZ 파견근무", "통제구역": "C구역", "비고": "공무 출장"}
    ]
    
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", "전", "홍"]
    first_names = ["민준", "서준", "도윤", "예준", "시우", "하준", "주원", "지호", "준우", "도현", "서연", "서윤", "지우", "서현", "민서", "하윤", "지민", "채원", "지유", "지안"]
    types_pool = ["영농인", "공사인원", "안보관광", "군인", "고정", "성묘객"]
    zones_pool = ["A구역", "B구역", "C구역", "DMZ통로", "영농단지"]
    
    import random
    random.seed(42)
    
    for i in range(1, 40):
        l_name = random.choice(last_names)
        f_name = random.choice(first_names)
        full_name = f"{l_name}{f_name}"
        
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
            "통제구역": zone,
            "비고": "-"
        })

    if os.path.exists(FIXED_MEMBERS_FILE):
        try:
            with open(FIXED_MEMBERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass
            
    # 파일이 없거나 읽기 실패 시 초기 기본값 저장 후 반환
    save_fixed_members(initial_members)
    return initial_members

# 고정출입자 명단 저장 함수 (서버 파일에 기록)
def save_fixed_members(members):
    try:
        with open(FIXED_MEMBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(members, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"고정 명단 저장 중 오류 발생: {e}")

# ==================== [다크모드 CSS 및 버튼 글자 크기 확대 스타일] ====================
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
    .stat-card {
        background-color: #1b263b;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #415a77;
        margin-bottom: 10px;
    }
    .guide-box {
        background-color: #1a1a2e;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #16213e;
        margin-top: 30px;
        margin-bottom: 20px;
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
    /* 버튼 글자 크기 키우기 및 터치 영역 확보 */
    .stButton button {
        font-size: 18px !important;
        font-weight: bold !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== [한국 시간 헬퍼 함수] ====================
def get_kts_time(fmt="%H:%M"):
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime(fmt)

# ==================== [세션 상태 초기화] ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "visitors_log" not in st.session_state:
    st.session_state.visitors_log = []

# 고정출입자 명단 세션 연동 (파일에서 불러오기)
if "fixed_members" not in st.session_state:
    st.session_state.fixed_members = load_fixed_members()

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

# ----------------- [탭 메뉴 구성] -----------------
tab1, tab2, tab3 = st.tabs(["🚀 출입 관리 및 현황", "🏁 퇴영 목록", "📋 고정출입자 명단 관리"])

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
                    matches = [m for m in st.session_state.fixed_members if m["성명"] == clean_name]
                    if len(matches) == 1:
                        st.session_state.selected_matched_member = matches[0]
                        st.session_state.ambiguous_matches = []
                        st.success(f"✅ [{clean_name}] 정보 연동됨")
                    elif len(matches) > 1:
                        st.session_state.selected_matched_member = None
                        st.session_state.ambiguous_matches = matches
                        st.warning(f"⚠️ 동명이인 {len(matches)}명 발견")
                    else:
                        st.session_state.selected_matched_member = None
                        st.session_state.ambiguous_matches = []
                        st.info("ℹ️ 신규 인원입니다.")
                else:
                    st.warning("⚠️ 성명을 입력하세요.")

        if st.session_state.ambiguous_matches:
            st.markdown("#### 👥 동명이인 선택")
            choice_options = [f"성명: {m['성명']} | 생년: {m['생년월일']} | 전화: {m['전화번호']} | 차량: {m['차량번호']}" for m in st.session_state.ambiguous_matches]
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
                birth_date = st.text_input("생년월일 (6자리)", value=m_data.get("생년월일", ""), placeholder="예: 751225")
            with col_i2:
                phone = st.text_input("전화번호", value=m_data.get("전화번호", ""), placeholder="예: 010-1234-5678")
                
            default_type = m_data.get("출입구분", "영농인")
            preset_types = ["영농인", "공사인원", "군인", "안보관광", "고정", "성묘객", "기타"]
            
            selected_type_preset = st.selectbox("출입 구분", preset_types, index=preset_types.index(default_type) if default_type in preset_types else 0)
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                car = st.text_input("차종 및 차량번호", value=m_data.get("차량번호", ""), placeholder="예: 12가3456")
                dest = st.text_input("목적지", value=m_data.get("목적지", ""), placeholder="예: 북삼리 영농지")
            with col_f2:
                zone = st.text_input("통제 구역", value=m_data.get("통제구역", ""), placeholder="예: A구역")
                note = st.text_input("비고", value=m_data.get("비고", ""), placeholder="특이사항 입력")
            
            submitted = st.form_submit_button("🚀 최종 입영 처리", use_container_width=True)
            if submitted:
                final_name = input_name.strip()
                if not final_name:
                    st.warning("⚠️ 성명을 입력해주세요.")
                else:
                    time_now = get_kts_time("%H:%M")
                    new_entry = {
                        "출입시간": time_now,
                        "퇴영시간": "-",
                        "성명": final_name,
                        "생년월일": birth_date if birth_date else "-",
                        "전화번호": phone if phone else "-",
                        "출입구분": selected_type_preset,
                        "차량": car if car else "-",
                        "목적": dest if dest else "-",
                        "구역": zone if zone else "-",
                        "비고": note if note else "-",
                        "상태": "체류중"
                    }
                    st.session_state.visitors_log.append(new_entry)
                    st.session_state.temp_input_name = ""
                    st.session_state.selected_matched_member = None
                    st.success(f"🎉 [{final_name}] 님 입영 처리 완료!")
                    st.rerun()

    with right_col:
        st.subheader("📊 체류 인원 목록 (최신순)")

        all_logs = [(i, row) for i, row in enumerate(st.session_state.visitors_log)]
        all_logs.reverse()

        with st.form("staying_search_form"):
            col_s1, col_s2 = st.columns([3, 1])
            with col_s1:
                staying_query_input = st.text_input("🔍 통합 검색어", placeholder="이름, 번호, 차량번호 입력 (퇴영자 포함)", label_visibility="collapsed")
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

        # --- 5명씩 페이지네이션 적용 ---
        items_per_page = 5
        total_items = len(display_list)
        total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
        
        if "staying_page" not in st.session_state:
            st.session_state.staying_page = 1
        
        if st.session_state.staying_page > total_pages:
            st.session_state.staying_page = max(1, total_pages)

        if search_query:
            st.markdown(f"<p style='color: #ffb703; font-size: 14px;'>검색 결과 (퇴영자 포함): <b>{total_items}건</b> (페이지 {st.session_state.staying_page}/{total_pages})</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color: #aaa; font-size: 14px;'>현재 체류: <b>{total_items}명</b> (페이지 {st.session_state.staying_page}/{total_pages})</p>", unsafe_allow_html=True)

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
                            <span style="color: #adb5bd; font-size: 13px;">입영 시각: {row.get('출입시간', '-')}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if is_staying:
                        if st.button("🏁 퇴영 처리", key=f"out_{row_idx}", use_container_width=True):
                            st.session_state.visitors_log[row_idx]["상태"] = "퇴영완료"
                            st.session_state.visitors_log[row_idx]["퇴영시간"] = get_kts_time("%H:%M")
                            st.rerun()

            # 페이지 이동 버튼 컨트롤
            if total_pages > 1:
                col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
                with col_p1:
                    if st.button("◀ 이전", use_container_width=True, key="prev_staying"):
                        if st.session_state.staying_page > 1:
                            st.session_state.staying_page -= 1
                            st.rerun()
                with col_p2:
                    st.markdown(f"<p style='text-align: center; margin-top: 10px;'>{st.session_state.staying_page} / {total_pages}</p>", unsafe_allow_html=True)
                with col_p3:
                    if st.button("다음 ▶", use_container_width=True, key="next_staying"):
                        if st.session_state.staying_page < total_pages:
                            st.session_state.staying_page += 1
                            st.rerun()

    # ==================== [종합 현황판: 가장 아래쪽 배치] ====================
    st.markdown("<hr style='margin: 30px 0 20px 0; border-color: #444;'>", unsafe_allow_html=True)
    st.subheader("📈 종합 현황판 (현재 체류 인원)")
    
    all_staying = []
    for item in st.session_state.visitors_log:
        r = item[1] if isinstance(item, tuple) else item
        if isinstance(r, dict) and r.get("상태") == "체류중":
            all_staying.append(r)
            
    total_count = len(all_staying)

    col_stat1, col_stat2 = st.columns([1, 2])
    with col_stat1:
        st.markdown(f"""
            <div class="stat-card">
                <h4 style="margin:0; color:#90e0ef;">현재 총 체류 인원</h4>
                <p style="font-size: 32px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{total_count} 명</p>
            </div>
        """, unsafe_allow_html=True)
    with col_stat2:
        if total_count == 0:
            st.info("현재 체류 중인 인원이 없습니다.")
        else:
            type_counts = {}
            zone_counts = {}
            for row in all_staying:
                v_t = row.get("출입구분", "기타")
                zone = row.get("구역", "미지정")
                type_counts[v_t] = type_counts.get(v_t, 0) + 1
                zone_counts[zone] = zone_counts.get(zone, 0) + 1
            
            t_str = " | ".join([f"**{k}**: {v}명" for k, v in type_counts.items()])
            z_str = " | ".join([f"**{k}**: {v}명" for k, v in zone_counts.items()])
            st.markdown(f"🏷️ **구분별**: {t_str}")
            st.markdown(f"🛡️ **구역별**: {z_str}")

# ==================== [탭 2: 퇴영 목록] ====================
with tab2:
    out_list = [(i, row) for i, row in enumerate(st.session_state.visitors_log) if row.get("상태") == "퇴영완료"]
    out_list.reverse()
    total_out_count = len(out_list)
    
    current_staying_count = 0
    for item in st.session_state.visitors_log:
        r = item[1] if isinstance(item, tuple) else item
        if isinstance(r, dict) and r.get("상태") == "체류중":
            current_staying_count += 1

    st.subheader("🏁 퇴영 완료된 기록 목록")

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
        display_out_list = out_list
        if out_search:
            display_out_list = [(idx, row) for idx, row in out_list if out_search in str(row.get("성명", "")) or out_search in str(row.get("차량", ""))]

        # --- 퇴영 목록 5명씩 페이지네이션 적용 ---
        out_items_per_page = 5
        total_out_items = len(display_out_list)
        total_out_pages = (total_out_items - 1) // out_items_per_page + 1 if total_out_items > 0 else 1
        
        if "out_page" not in st.session_state:
            st.session_state.out_page = 1
        
        if st.session_state.out_page > total_out_pages:
            st.session_state.out_page = max(1, total_out_pages)

        st.markdown(f"<p style='color: #aaa; font-size: 14px;'>총 퇴영 기록: <b>{total_out_items}명</b> (페이지 {st.session_state.out_page}/{total_out_pages})</p>", unsafe_allow_html=True)

        out_start_idx = (st.session_state.out_page - 1) * out_items_per_page
        out_end_idx = out_start_idx + out_items_per_page
        current_page_out_items = display_out_list[out_start_idx:out_end_idx]

        for row_idx, row in current_page_out_items:
            st.markdown(f"""
                <div class="css-card">
                    <b style="font-size:18px;">👤 {row.get('성명', '-')}</b> <span style="color:#40916c;">[{row.get('출입구분', '-')}]</span><br>
                    🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')}<br>
                    📝 비고: <b style="color: #ffb703;">{row.get('비고', '-')}</b><br>
                    <span style='color:#aaa; font-size:13px;'>📥 입영 시간: {row.get('출입시간', '-')} &nbsp;|&nbsp; 📤 퇴영 시간: <b style='color:#40916c;'>{row.get('퇴영시간', '-')}</b></span>
                </div>
            """, unsafe_allow_html=True)

        # 퇴영 목록 페이지 이동 버튼 컨트롤
        if total_out_pages > 1:
            col_op1, col_op2, col_op3 = st.columns([1, 2, 1])
            with col_op1:
                if st.button("◀ 이전", use_container_width=True, key="prev_out"):
                    if st.session_state.out_page > 1:
                        st.session_state.out_page -= 1
                        st.rerun()
            with col_op2:
                st.markdown(f"<p style='text-align: center; margin-top: 10px;'>{st.session_state.out_page} / {total_out_pages}</p>", unsafe_allow_html=True)
            with col_op3:
                if st.button("다음 ▶", use_container_width=True, key="next_out"):
                    if st.session_state.out_page < total_out_pages:
                        st.session_state.out_page += 1
                        st.rerun()

    # ==================== [종합 현황판: 가장 아래쪽 배치] ====================
    st.markdown("<hr style='margin: 30px 0 20px 0; border-color: #444;'>", unsafe_allow_html=True)
    st.subheader("📈 종합 현황판 (퇴영 완료 및 남은 체류 인원)")

    col_osat1, col_osat2, col_osat3 = st.columns([1, 1, 2])
    with col_osat1:
        st.markdown(f"""
            <div class="stat-card">
                <h4 style="margin:0; color:#90e0ef;">총 퇴영 완료</h4>
                <p style="font-size: 28px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{total_out_count} 명</p>
            </div>
        """, unsafe_allow_html=True)
    with col_osat2:
        st.markdown(f"""
            <div class="stat-card">
                <h4 style="margin:0; color:#ffb703;">현재 남은 체류</h4>
                <p style="font-size: 28px; font-weight: bold; margin: 5px 0 0 0; color: #ffffff;">{current_staying_count} 명</p>
            </div>
        """, unsafe_allow_html=True)
    with col_osat3:
        if total_out_count == 0:
            st.info("오늘 퇴영 완료된 인원이 없습니다.")
        else:
            out_type_counts = {}
            for item in out_list:
                row = item[1] if isinstance(item, tuple) else item
                if isinstance(row, dict):
                    v_t = row.get("출입구분", "기타")
                    out_type_counts[v_t] = out_type_counts.get(v_t, 0) + 1
            
            ot_str = " | ".join([f"**{k}**: {v}명" for k, v in out_type_counts.items()])
            st.markdown(f"<br>🏷️ **퇴영 구분별 통계**: {ot_str}", unsafe_allow_html=True)

# ==================== [탭 3: 고정출입자 명단 관리] ====================
with tab3:
    st.subheader("📋 고정출입자 명단 추가 / 삭제")
    st.markdown("자주 출입하는 인원의 인적사항을 관리합니다. (추가/삭제 시 서버에 영구 반영됩니다)")

    with st.form("add_fixed_form", clear_on_submit=True):
        f_name = st.text_input("고정 출입자 성명")
        
        col_mf1, col_mf2 = st.columns(2)
        with col_mf1:
            f_birth = st.text_input("생년월일 (6자리)", placeholder="예: 751225")
            f_car = st.text_input("차량번호", placeholder="예: 12가3456")
            f_dest = st.text_input("목적지", placeholder="예: 북삼리 영농지")
        with col_mf2:
            f_phone = st.text_input("전화번호", placeholder="예: 010-1234-5678")
            f_type = st.selectbox("출입 구분", ["영농인", "공사인원", "군인", "안보관광", "고정", "성묘객", "기타"])
            f_zone = st.text_input("통제구역", placeholder="예: A구역")
            
        f_note = st.text_input("기본 비고", placeholder="특이사항 입력")
            
        f_submitted = st.form_submit_button("➕ 고정 명단에 추가", use_container_width=True)
        if f_submitted:
            if f_name.strip():
                new_member = {
                    "성명": f_name.strip(),
                    "생년월일": f_birth.strip() if f_birth.strip() else "-",
                    "전화번호": f_phone.strip() if f_phone.strip() else "-",
                    "출입구분": f_type,
                    "차량번호": f_car.strip() if f_car.strip() else "-",
                    "목적지": f_dest.strip() if f_dest.strip() else "-",
                    "통제구역": f_zone.strip() if f_zone.strip() else "-",
                    "비고": f_note.strip() if f_note.strip() else "-"
                }
                st.session_state.fixed_members.append(new_member)
                save_fixed_members(st.session_state.fixed_members)  # 파일에 즉시 저장
                st.success(f"✅ [{f_name.strip()}] 님이 고정명단에 추가되었습니다!")
                st.rerun()
            else:
                st.warning("⚠️ 성명을 입력해주세요.")

    st.markdown("---")
    st.subheader(f"🗑️ 등록된 고정출입자 목록 (현재 {len(st.session_state.fixed_members)}명)")

    with st.form("fixed_search_form"):
        col_fs1, col_fs2 = st.columns([3, 1])
        with col_fs1:
            fixed_query_input = st.text_input("🔍 검색어", placeholder="이름이나 차량번호 검색", label_visibility="collapsed")
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

        for member in display_fixed:
            col_list1, col_list2 = st.columns([4, 1])
            with col_list1:
                st.markdown(f"**👤 {member['성명']}** <span style='color:#40916c;'>[{member.get('출입구분', '-')}]</span> &nbsp;|&nbsp; 🎂 {member.get('생년월일', '-')} &nbsp;|&nbsp; 📞 {member.get('전화번호', '-')}", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#aaa; font-size:13px;'>🚗 차량: {member.get('차량번호', '-')} | 📍 목적: {member.get('목적지', '-')} | 🛡️ 구역: {member.get('통제구역', '-')} | 📝 비고: {member.get('비고', '-')}</span>", unsafe_allow_html=True)
            with col_list2:
                real_idx = st.session_state.fixed_members.index(member)
                if st.button("삭제", key=f"del_fixed_{real_idx}", use_container_width=True):
                    st.session_state.fixed_members.pop(real_idx)
                    save_fixed_members(st.session_state.fixed_members)  # 삭제된 내용도 파일에 반영
                    st.rerun()
            st.markdown("<hr style='margin: 8px 0; border-color: #222;'>", unsafe_allow_html=True)

# ==================== [초소 근무자 사용 방법 안내] ====================
st.markdown("""
    <div class="guide-box">
        <h3>📖 비룡초소 출입통제 시스템 사용 방법</h3>
        <ol style="line-height: 1.8; color: #ddd;">
            <li><b>출입자 등록 (입영)</b>: 
                <ul>
                    <li>[출입 관리 및 현황] 탭 좌측에서 성명을 입력하고 <b>[정보 불러오기]</b>를 누르면 고정출입자 명단과 자동으로 연동됩니다.</li>
                    <li>신규 인원이거나 정보 확인 후 하단의 <b>[최종 입영 처리]</b> 버튼을 누르면 즉시 체류 목록에 추가됩니다.</li>
                </ul>
            </li>
            <li><b>퇴영 처리</b>: 
                <ul>
                    <li>[출입 관리 및 현황] 탭 우측의 체류 인원 카드 하단에 있는 <b>[퇴영 처리]</b> 버튼을 누르면 즉시 퇴영 완료 처리되며 [퇴영 목록] 탭으로 이동합니다.</li>
                </ul>
            </li>
            <li><b>통합 검색 활용</b>: 
                <ul>
                    <li>체류 인원 목록 검색창에 이름을 입력하면, 현재 체류 중인 인원뿐만 아니라 이미 퇴영 완료된 인원까지 모두 포함하여 통합 검색할 수 있습니다.</li>
                </ul>
            </li>
            <li><b>고정출입자 관리</b>: 
                <ul>
                    <li>[고정출입자 명단 관리] 탭에서 자주 출입하는 영농인, 공사인원 등을 미리 등록하거나 삭제할 수 있습니다. <b>(수정 내용이 서버 파일에 저장되어 새로고침해도 유지됩니다.)</b></li>
                </ul>
            </li>
        </ol>
    </div>
""", unsafe_allow_html=True)
