from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import streamlit as st

# ==================== [설정] ====================
CORRECT_PASSWORD = "1234"  # 접속 비밀번호

# 페이지 기본 설정
st.set_page_config(page_title="민통초소 실시간 출입 관리", layout="centered")

# 구글 시트 연결 생성
conn = st.connection("gsheets", type=GSheetsConnection)

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "latest_alert" not in st.session_state:
    st.session_state.latest_alert = None

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

# 구글 시트에서 최신 데이터 불러오기 (캐시 없이 실시간 조회)
try:
    df = conn.read(ttl=0)
except Exception as e:
    df = None

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
            
            # 구글 시트에 기록할 데이터 행 구성 (시트 열 순서: Time, Affiliation, Name, Contact, Purpose, Vehicle, Status 등에 맞춤)
            import pandas as pd
            new_row = pd.DataFrame([{
                "Time": time_now,
                "Affiliation": v_type,
                "Name": final_name,
                "Contact": car if car else "-",
                "Purpose": dest if dest else "-",
                "Vehicle": zone if zone else "-",
                "Status": "체류중"
            }])
            
            # 기존 데이터에 새 행 추가 후 구글 시트에 업로드
            if df is not None and not df.empty:
                updated_df = pd.concat([df, new_row], ignore_index=True)
            else:
                updated_df = new_row
                
            conn.update(data=updated_df)
            
            # 대문짝만한 화면 경고창 띄우기
            st.markdown(f"""
                <div style="background-color: #ff4b4b; color: white; padding: 20px; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">
                    🚨 [긴급 알림] 새로운 출입자 등록!<br>
                    성명: {final_name} ({v_type})<br>
                    시간: {time_now}
                </div>
            """, unsafe_allow_html=True)
            
            st.success(f"🎉 [{final_name}] 님 입영 처리 및 구글 시트 동기화 완료!")
            st.rerun()

st.divider()

# 2. 현재 체류 현황 섹션
st.subheader("📊 현재 체류 중인 출입자 현황")

if df is not None and not df.empty and "Name" in df.columns:
    # 체류중인 목록 필터링
    staying_df = df[df["Status"] == "체류중"] if "Status" in df.columns else df
    
    if staying_df.empty:
        st.info("현재 체류 중인 인원이 없습니다.")
    else:
        for idx, row in staying_df.iterrows():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                v_t = row.get("Affiliation", "-")
                v_n = row.get("Name", "-")
                v_c = row.get("Contact", "-")
                v_d = row.get("Purpose", "-")
                st.markdown(f"**[{v_t}] {v_n}**  \n차량: {v_c} | 목적: {v_d}")
            with col2:
                st.markdown(f"입영시간: `{row.get('Time', '-')}`")
            with col3:
                if st.button("퇴영", key=f"out_{idx}"):
                    df.loc[idx, "Status"] = "퇴영완료"
                    conn.update(data=df)
                    st.rerun()
            st.markdown("---")
else:
    st.info("구글 시트에 기록된 데이터가 없거나 형식을 불러오는 중입니다.")
