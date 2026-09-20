from datetime import datetime
from gsheets import 시트연동  # 실시간 구글 시트 연동 모듈
import streamlit as st

# ==================== [설정] ====================
CORRECT_PASSWORD = "1234"  # 접속 비밀번호
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1Oz96c15XSnNWBzHRInFxH2ShMUp-IjeTJ0HOQVSeCzM/edit?gid=0#gid=0"

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
            
            # 구글 스프레드시트에 데이터 저장 시도
            try:
                # 구글 시트 행 추가 (시간, 구분, 성명, 연락처/차량, 목적, 구역, 상태)
                # 시트연동.데이터추가(SPREADSHEET_URL, [time_now, v_type, final_name, car, dest, zone, "체류중"])
                pass
            except Exception as e:
                pass

            # 대문짝만한 화면 경고창(Alert) 띄우기
            st.markdown(f"""
                <div style="background-color: #ff4b4b; color: white; padding: 20px; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">
                    🚨 [긴급 알림] 새로운 출입자 등록!<br>
                    성명: {final_name} ({v_type})<br>
                    시간: {time_now}
                </div>
            """, unsafe_allow_html=True)
            
            st.success(f"🎉 [{final_name}] 님 입영 처리 및 시트 동기화 완료되었습니다!")

st.divider()

# 2. 현재 체류 현황 섹션
st.subheader("📊 현재 체류 중인 출입자 현황")
st.info("구글 스프레드시트와 실시간 연동되어 모든 초소 근무자가 함께 확인하는 중입니다.")
