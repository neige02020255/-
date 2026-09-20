from datetime import datetime
import json
import requests
import streamlit as st

# ==================== [설정] ====================
CORRECT_PASSWORD = "1234"  # 접속 비밀번호
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx87WTQj9FLlYWiLivD19-2wHbMVtaQAGqvgPc9MgyLrV2khBcyOORdC4_fsDzbTCHY/exec"

# 페이지 기본 설정
st.set_page_config(page_title="제25보병사단 비룡초소 출입 관리", layout="centered")

# ==================== [커스텀 CSS 디자인 스타일] ====================
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6f5;
    }
    .css-card {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 12px;
        border-left: 5px solid #2d6a4f;
    }
    h1, h2, h3 {
        font-family: 'Malgun Gothic', sans-serif;
        color: #1b4332;
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

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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
        <h2 style='margin: 5px 0 0 0; color: #1b4332;'>민통초소 실시간 출입 관리 시스템</h2>
    </div>
""", unsafe_allow_html=True)

col_space, col_logout = st.columns([4, 1])
with col_logout:
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

# 1. 출입자 등록 섹션
st.subheader("📝 출입자 등록 (입영)")

with st.container():
    with st.form("entry_form", clear_on_submit=True):
        custom_name = st.text_input("성명")
        v_type = st.selectbox("출입 구분", ["영농인", "공사인원", "안보관광", "고정", "성묘객", "민간인"])
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            car = st.text_input("차종 및 차량번호", placeholder="예: 1234 / 아반떼")
            dest = st.text_input("목적지", placeholder="예: 북삼리 영농지")
        with col_f2:
            zone = st.text_input("통제 구역", placeholder="예: A구역")
            st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 입영 및 시스템 등록", use_container_width=True)
        if submitted:
            final_name = custom_name.strip()
            if not final_name:
                st.warning("⚠️ 성명을 입력해주세요.")
            else:
                time_now = datetime.now().strftime("%H:%M")
                # 구글 시트 헤더 컬럼명과 정확히 일치하도록 페이로드 수정 완료
                payload = {
                    "시간": time_now,
                    "소속": v_type,
                    "성명": final_name,
                    "차량": car if car else "-",
                    "목적": dest if dest else "-",
                    "구역": zone if zone else "-",
                    "상태": "체류중"
                }
                
                try:
                    requests.post(APPS_SCRIPT_URL, json=payload, timeout=5)
                except Exception:
                    pass
                
                st.markdown(f"""
                    <div style="background-color: #2d6a4f; color: white; padding: 18px; border-radius: 10px; text-align: center; font-size: 18px; font-weight: bold; margin: 15px 0;">
                        🚨 [입영 완료] {final_name} ({v_type})<br>
                        <span style="font-size: 14px; font-weight: normal;">등록 시간: {time_now} | 구역: {zone if zone else '-'}</span>
                    </div>
                """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 2. 현재 체류 현황 및 검색 섹션
st.subheader("📊 현재 체류 중인 출입자 현황")

visitors_data = []
try:
    res = requests.get(APPS_SCRIPT_URL, timeout=5)
    visitors_data = res.json()
except Exception:
    visitors_data = []

# 체류 중인 항목만 필터링 (행 번호와 함께)
staying_list = [(i+2, row) for i, row in enumerate(visitors_data) if row.get("상태") == "체류중"]

if not staying_list:
    st.info("💡 현재 초소 통제구역 내 체류 중인 인원이 없습니다.")
else:
    # 🔍 400명 대규모 인원에 대비한 실시간 검색 입력창 추가
    search_query = st.text_input("🔍 출입자 검색 (성명 또는 차량번호 입력)", placeholder="이름이나 차량번호를 입력하면 바로 찾아줍니다")
    
    # 검색어가 있으면 필터링
    if search_query:
        filtered_list = []
        for idx, row in staying_list:
            name_val = str(row.get("성명", ""))
            car_val = str(row.get("차량", ""))
            if search_query in name_val or search_query in car_val:
                filtered_list.append((idx, row))
        display_list = filtered_list
    else:
        display_list = staying_list

    st.markdown(f"<p style='color: #666; font-size: 14px;'>총 체류 인원: <b>{len(staying_list)}명</b> (검색 결과: {len(display_list)}명)</p>", unsafe_allow_html=True)

    if not display_list:
        st.warning("🔍 검색 결과가 없습니다.")
    else:
        for row_idx, row in display_list:
            with st.container():
                st.markdown(f"""
                    <div class="css-card">
                        <b>[{row.get('소속', '-')}] {row.get('성명', '-')}</b><br>
                        🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')} &nbsp;|&nbsp; 🛡️ 구역: {row.get('구역', '-')}<br>
                        <span style="color: #6c757d; font-size: 13px;">입영 시각: {row.get('시간', '-')}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # 퇴영 처리 버튼
                if st.button("🏁 퇴영 처리", key=f"out_{row_idx}", use_container_width=True):
                    try:
                        payload = {
                            "시간": row.get('시간', '-'),
                            "소속": row.get('소속', '-'),
                            "성명": row.get('성명', '-'),
                            "차량": row.get('차량', '-'),
                            "목적": row.get('목적', '-'),
                            "구역": row.get('구역', '-'),
                            "상태": "퇴영완료"
                        }
                        requests.post(APPS_SCRIPT_URL, json=payload, timeout=5)
                    except Exception:
                        pass
                    st.rerun()
