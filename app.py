from datetime import datetime
import json
import requests
import streamlit as st

# ==================== [설정] ====================
CORRECT_PASSWORD = "1234"  # 접속 비밀번호
# 방금 발급받으신 웹 앱 URL 연동 완료
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw9jhKVfSOLNJMI3i0e6E-aV0VvrmbXS4abQ2XxpOlEnn4T3KsG3kwdnBX-7e4CfjROnA/exec"

# 페이지 기본 설정
st.set_page_config(page_title="민통초소 실시간 출입 관리", layout="centered")

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==================== [로그인 화면] ====================
if not st.session_state.logged_in:
    st.title("🔒 초소 출입 관리 로그인")
    st.markdown("접속하려면 비밀번호를 입력하세요. (기본 비밀번호: 1234)")
    with st.form("login_form"):
        input_pw = st.text_input("비밀번호", type="password")
        submit_btn = st.form_submit_button("로그인")
        if submit_btn:
            if input_pw == CORRECT_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ 비밀번호가 틀렸습니다.")
    st.stop()

# ==================== [메인 출입 관리 화면] ====================
st.title("🛡️ 민통초소 실시간 출입 관리")

col_title, col_logout = st.columns([3, 1])
with col_logout:
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.rerun()

st.divider()

# 1. 출입자 등록 섹션
st.subheader("📝 출입자 등록 (입영)")

with st.form("entry_form", clear_on_submit=True):
    custom_name = st.text_input("성명 입력")
    v_type = st.selectbox("출입 구분", ["영농인", "공사인원", "안보관광", "고정", "성묘객", "민간인"])
    car = st.text_input("차종 및 차량번호")
    dest = st.text_input("목적지")
    zone = st.text_input("구역")
    
    submitted = st.form_submit_button("🚀 입영 처리")
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
            
            # 대문짝만한 화면 경고 팝업 띄우기
            st.markdown(f"""
                <div style="background-color: #ff4b4b; color: white; padding: 20px; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">
                    🚨 [긴급 알림] 새로운 출입자 등록!<br>
                    성명: {final_name} ({v_type})<br>
                    시간: {time_now}
                </div>
            """, unsafe_allow_html=True)
            
            st.success(f"🎉 [{final_name}] 님 입영 처리 및 구글 시트 저장 완료!")

st.divider()

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
    st.info("현재 체류 중인 인원이 없습니다.")
else:
    for row_idx, row in staying_list:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"**[{row.get('소속', '-')}] {row.get('성명', '-')}**  \n차량: {row.get('차량', '-')} | 목적: {row.get('목적', '-')}")
        with col2:
            st.markdown(f"입영시간: `{row.get('시간', '-')}`")
        with col3:
            if st.button("퇴영", key=f"out_{row_idx}"):
                # 퇴영 처리 전송
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
        st.markdown("---")
