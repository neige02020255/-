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
    /* 전체 배경 및 폰트 부드러운 느낌 부여 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 카드 박스 스타일 */
    .css-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        border-left: 5px solid #2d6a4f;
    }
    
    /* 헤더 타이틀 강조 */
    h1, h2, h3 {
        font-family: 'Malgun Gothic', sans-serif;
        color: #1b4332;
    }
    
    /* 버튼 디자인 예쁘게 */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
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

# 상단 헤더 (25사단 부대마크 이미지와 타이틀 배치)[span_0](start_span)[span_0](end_span)
col_logo, col_header = st.columns([1, 6])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/ROKA_25th_Infantry_Division_Insignia.svg/200px-ROKA_25th_Infantry_Division_Insignia.svg.png", width=65)
with col_header:
    st.markdown("### **제25보병사단 비룡초소**")
    st.markdown("<p style='color: #555; margin-top: -15px; font-size: 14px;'>민통선 출입통제 실시간 통합 시스템</p>", unsafe_allow_html=True)

# 로그아웃 버튼
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
                payload = {
                    "time": time_now,
                    "type": v_type,
                    "name": final_name,
                    "car": car if car else "-",
                    "dest": dest if dest else "-",
                    "zone": zone if zone else "-",
                    "status": "체류중"
                }
                
                # 구글 시트로 데이터 전송
                try:
                    requests.post(APPS_SCRIPT_URL, json=payload, timeout=5)
                except Exception:
                    pass
                
                # 강조 팝업 알림
                st.markdown(f"""
                    <div style="background-color: #2d6a4f; color: white; padding: 18px; border-radius: 10px; text-align: center; font-size: 18px; font-weight: bold; margin: 15px 0;">
                        🚨 [입영 완료] {final_name} ({v_type})<br>
                        <span style="font-size: 14px; font-weight: normal;">등록 시간: {time_now} | 구역: {zone if zone else '-'}</span>
                    </div>
                """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 2. 현재 체류 현황 섹션
st.subheader("📊 현재 체류 중인 출입자 현황")

visitors_data = []
try:
    res = requests.get(APPS_SCRIPT_URL, timeout=5)
    visitors_data = res.json()
except Exception:
    visitors_data = []

staying_list = [(i+2, row) for i, row in enumerate(visitors_data) if row.get("상태") == "체류중"]

if not staying_list:
    st.info("💡 현재 초소 통제구역 내 체류 중인 인원이 없습니다.")
else:
    for row_idx, row in staying_list:
        with st.container():
            st.markdown(f"""
                <div class="css-card">
                    <b>[{row.get('소속', '-')}] {row.get('성명', '-')}</b><br>
                    🚗 차량: {row.get('차량', '-')} &nbsp;|&nbsp; 📍 목적: {row.get('목적', '-')} &nbsp;|&nbsp; 🛡️ 구역: {row.get('구역', '-')}<br>
                    <span style="color: #6c757d; font-size: 13px;">입영 시각: {row.get('시간', '-')}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # 퇴영 버튼
            if st.button("🏁 퇴영 처리", key=f"out_{row_idx}", use_container_width=True):
                try:
                    payload = {
                        "time": row.get('시간', '-'),
                        "type": row.get('소속', '-'),
                        "name": row.get('성명', '-'),
                        "car": row.get('차량', '-'),
                        "dest": row.get('목적', '-'),
                        "zone": row.get('구역', '-'),
                        "status": "퇴영완료"
                    }
                    requests.post(APPS_SCRIPT_URL, json=payload, timeout=5)
                except Exception:
                    pass
                st.rerun()

