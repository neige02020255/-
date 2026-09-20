from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import json
import os

# ==================== [설정 및 파일 저장 함수] ====================
CORRECT_PASSWORD = "1234"  # 접속 비밀번호
FIXED_MEMBERS_FILE = "fixed_members.json"
TEMP_MEMBERS_FILE = "temp_members.json"

# 페이지 기본 설정 (와이드 모드 적용)
st.set_page_config(page_title="제25보병사단 비룡초소 출입 관리", layout="wide")

# 고정출입자 명단 로드 함수
def load_fixed_members():
    initial_members = [
        {"성명": "김영농", "생년월일": "651012", "전화번호": "010-1234-5678", "출입구분": "영농인", "차량번호": "12가3456", "목적지": "북삼리 영농지", "통제구역": "A구역", "비고": "특이사항 없음"},
        {"성명": "이공사", "생년월일": "720515", "전화번호": "010-9876-5432", "출입구분": "공사인원", "차량번호": "78나9012", "목적지": "초소 보수공사", "통제구역": "B구역", "비고": "장비 지참"},
        {"성명": "박병장", "생년월일": "030120", "전화번호": "010-1111-2222", "출입구분": "군인", "차량번호": "지휘차 5521", "목적지": "DMZ 파견근무", "통제구역": "C구역", "비고": "공무 출장"}
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
    
    # 오늘 날짜와 비교하여 기간이 지나지 않은 유효한 임시출입자만 남김
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
    .guide-box {
        background-color: #1a1a2e; padding: 20px; border-radius: 10px;
        border: 1px solid #16213e; margin-top: 30px; margin-bottom: 20px;
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
    </style>
""", unsafe_allow_html=True)

def get_kts_time(fmt="%H:%M"):
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime(fmt)

# ==================== [세션 초기화] ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "visitors_log" not in st.session_state:
    st.session_state.visitors_log = []
if "fixed_members" not in st.session_state:
    st.session_state.fixed_members = load_fixed_members()
if "temp_members" not in st.session_state:
    st.session_state.temp_members = load_temp_members()

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
tab1, tab2, tab3, tab4 = st.tabs(["🚀 출입 관리 및 현황", "🏁 퇴영 목록", "📋 고정출입자 명단 관리", "📋 임시출입자 명단 관리"])

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
            
            col_i1, col_i2 = st.columns(2)
            with col_i1:
                birth_date = st.text_input("생년월일 (6자리)", value=m_data.get("생년월일", "-"), placeholder="예: 751225")
            with col_i2:
                phone = st.text_input("전화번호", value=m_data.get("전화번호", "-"), placeholder="예: 010-1234-5678")
                
            default_type = m_data.get("출입구분", "영농인")
            preset_types = ["영농인", "공사인원", "군인", "안보관광", "고정", "성묘객", "임시방문", "기타"]
            selected_type_preset = st.selectbox("출입 구분", preset_types, index=preset_types.index(default_type) if default_type in preset_types else 0)
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                car = st.text_input("차종 및 차량번호", value=m_data.get("차량번호", m_data.get("차량", "")), placeholder="예: 12가3456")
                dest = st.text_input("목적지", value=m_data.get("목적지", m_data.get("방문사유", "")), placeholder="예: 북삼리 영농지")
            with col_f2:
                zone = st.text_input("통제 구역", value=m_data.get("통제구역", "-"), placeholder="예: A구역")
                note = st.text_input("비고", value=m_data.get("비고", "-"), placeholder="특이사항 입력")
            
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
                staying_query_input = st.text_input("🔍 통합 검색어", placeholder="이름, 번호, 차량번호 입력", label_visibility="collapsed")
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
                            <span style="color: #adb5bd; font-size: 13px;">입영 시각: {row.get('출입시간', '-')}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if is_staying:
                        if st.button("🏁 퇴영 처리", key=f"out_{row_idx}", use_container_width=True):
                            st.session_state.visitors_log[row_idx]["상태"] = "퇴영완료"
                            st.session_state.visitors_log[row_idx]["퇴영시간"] = get_kts_time("%H:%M")
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

    st.markdown("<hr style='margin: 30px 0 20px 0; border-color: #444;'>", unsafe_allow_html=True)
    st.subheader("📈 종합 현황판 (현재 체류 인원)")
    
    all_staying = [r[1] if isinstance(r, tuple) else r for r in st.session_state.visitors_log if (r[1] if isinstance(r, tuple) else r).get("상태") == "체류중"]
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
            type_counts, zone_counts = {}, {}
            for row in all_staying:
                type_counts[row.get("출입구분", "기타")] = type_counts.get(row.get("출입구분", "기타"), 0) + 1
                zone_counts[row.get("구역", "미지정")] = zone_counts.get(row.get("구역", "미지정"), 0) + 1
            st.markdown(f"🏷️ **구분별**: {' | '.join([f'**{k}**: {v}명' for k, v in type_counts.items()])}")
            st.markdown(f"🛡️ **구역별**: {' | '.join([f'**{k}**: {v}명' for k, v in zone_counts.items()])}")

# ==================== [탭 2: 퇴영 목록] ====================
with tab2:
    out_list = [(i, row) for i, row in enumerate(st.session_state.visitors_log) if row.get("상태") == "퇴영완료"]
    out_list.reverse()
    st.subheader("🏁 퇴영 완료된 기록 목록")
    if not out_list:
        st.info("💡 오늘 퇴영 완료된 기록이 없습니다.")
    else:
        for row_idx, row in out_list[:10]:
            st.markdown(f"""
                <div class="css-card">
                    <b style="font-size:18px;">👤 {row.get('성명', '-')}</b> <span style="color:#40916c;">[{row.get('출입구분', '-')}]</span><br>
                    🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')}<br>
                    <span style='color:#aaa; font-size:13px;'>📥 입영: {row.get('출입시간', '-')} &nbsp;|&nbsp; 📤 퇴영: <b style='color:#40916c;'>{row.get('퇴영시간', '-')}</b></span>
                </div>
            """, unsafe_allow_html=True)

# ==================== [탭 3: 고정출입자 명단 관리] ====================
with tab3:
    st.subheader("📋 고정출입자 명단 추가 / 삭제")
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
            
        if st.form_submit_button("➕ 고정 명단에 추가", use_container_width=True):
            if f_name.strip():
                st.session_state.fixed_members.append({
                    "성명": f_name.strip(), "생년월일": f_birth.strip() or "-", "전화번호": f_phone.strip() or "-",
                    "출입구분": f_type, "차량번호": f_car.strip() or "-", "목적지": f_dest.strip() or "-",
                    "통제구역": f_zone.strip() or "-", "비고": f_note.strip() or "-"
                })
                save_fixed_members(st.session_state.fixed_members)
                st.success(f"✅ [{f_name.strip()}] 님 추가 완료!")
                st.rerun()

    st.markdown("---")
    st.subheader(f"🗑️ 등록된 고정출입자 목록 (총 {len(st.session_state.fixed_members)}명)")
    
    for idx, member in enumerate(st.session_state.fixed_members):
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
            if clean_t_name:
                new_temp = {
                    "성명": clean_t_name,
                    "생년월일": t_birth.strip() or "-",
                    "전화번호": t_phone.strip() or "-",
                    "출입구분": "임시방문",
                    "차량번호": t_car.strip() or "-",
                    "방문사유": t_reason.strip() or "공문 승인 인원",
                    "시작일": t_start.strftime("%Y-%m-%d"),
                    "종료일": t_end.strftime("%Y-%m-%d"),
                    "비고": f"기간: {t_start}~{t_end}"
                }
                st.session_state.temp_members.append(new_temp)
                save_temp_members(st.session_state.temp_members)
                st.success(f"✅ [{clean_t_name}] 님 임시 등록 완료 (~{t_end})")
                st.rerun()
            else:
                st.warning("⚠️ 성명 또는 업체명은 필수입니다.")

    st.markdown("---")
    st.subheader(f"📋 현재 유효한 임시출입자 목록 ({len(st.session_state.temp_members)}명)")

    if not st.session_state.temp_members:
        st.info("등록된 임시출입자가 없습니다.")
    else:
        for idx, t_mem in enumerate(st.session_state.temp_members):
            t_cols = st.columns([4, 1])
            with t_cols[0]:
                st.markdown(f"**👤 {t_mem['성명']}** | 사유: {t_mem.get('방문사유', '-')} | 기간: {t_mem.get('시작일')} ~ <b style='color:#ffb703;'>{t_mem.get('종료일')}</b>")
                st.markdown(f"<span style='color:#aaa; font-size:13px;'>🚗 차량: {t_mem.get('차량번호', '-')} | 📞 연락처: {t_mem.get('전화번호', '-')}</span>", unsafe_allow_html=True)
            with t_cols[1]:
                if st.button("조기 삭제", key=f"del_temp_{idx}", use_container_width=True):
                    st.session_state.temp_members.pop(idx)
                    save_temp_members(st.session_state.temp_members)
                    st.success("삭제되었습니다.")
                    st.rerun()
            st.markdown("<hr style='margin: 8px 0; border-color: #222;'>", unsafe_allow_html=True)
