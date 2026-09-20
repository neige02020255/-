from datetime import datetime
import streamlit as st

# ==================== [설정] ====================
CORRECT_PASSWORD = "1234"  # 접속 비밀번호

# 페이지 기본 설정
st.set_page_config(page_title="민통초소 실시간 출입 관리", layout="centered")

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "visitors" not in st.session_state:
    st.session_state.visitors = []

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
            # 새로운 방문자 추가 및 팝업 알림 효과
            st.session_state.visitors.append({
                "type": v_type, 
                "name": final_name, 
                "car": car if car else "-", 
                "dest": dest if dest else "-", 
                "zone": zone if zone else "-", 
                "time": time_now, 
                "status": "체류중"
            })
            # 팝업 알림 메시지 출력
            st.toast(f"🚨 새로운 출입자 등록! [{final_name}] 님 ({v_type})", icon="📢")
            st.success(f"🎉 [{final_name}] 님 입영 처리 완료되었습니다! (시간: {time_now})")

st.divider()

# 2. 현재 체류 현황 섹션
st.subheader("📊 현재 체류 중인 출입자 현황")

staying_visitors = [(i, v) for i, v in enumerate(st.session_state.visitors) if v["status"] == "체류중"]

if not staying_visitors:
    st.info("현재 체류 중인 인원이 없습니다.")
else:
    for idx, v in staying_visitors:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"**[{v['type']}] {v['name']}**  \n차량: {v['car']} | 목적: {v['dest']}")
        with col2:
            st.markdown(f"입영시간: `{v['time']}`")
        with col3:
            if st.button("퇴영", key=f"out_{idx}"):
                st.session_state.visitors[idx]["status"] = "퇴영완료"
                st.toast(f"👋 [{v['name']}] 님 퇴영 처리되었습니다.", icon="✅")
                st.rerun()
        st.markdown("---")
