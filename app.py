from datetime import datetime
import streamlit as st

# ==================== [설정] ====================
CORRECT_PASSWORD = "1234"  # 👈 접속 비밀번호 (원하시는 번호로 변경 가능)

# 테스트용 가상 출입자 명단 (DB 역할)
DB_REGISTRY = {
    "김철수": {
        "구분": "영농인",
        "차량번호": "12가 3456",
        "목적지": "가상리 101-1",
        "구역": "A구역",
    },
    "이영희": {
        "구분": "영농인",
        "차량번호": "34나 5678",
        "목적지": "테스트로 202",
        "구역": "B구역",
    },
    "박민수": {
        "구분": "공사인원",
        "차량번호": "56다 7890",
        "목적지": "시공 현장 3",
        "구역": "C구역",
    },
    "홍길동": {
        "구분": "안보관광",
        "차량번호": "78라 1234",
        "목적지": "관광 안내소",
        "구역": "D구역",
    },
}

# 페이지 기본 설정
st.set_page_title("민통초소 출입 관리 (연습용)", layout="centered")

# 세션 상태 초기화 (로그인 여부 및 방문객 기록)
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

  st.stop()  # 로그인 안 된 상태면 여기서 멈춤

# ==================== [메인 출입 관리 화면] ====================
st.title("🛡️ 민통초소 실시간 출입 관리 (연습용)")

# 상단에 로그아웃 버튼 배치
col_title, col_logout = st.columns([3, 1])
with col_logout:
  if st.button("로그아웃"):
    st.session_state.logged_in = False
    st.rerun()

st.divider()

# 1. 출입자 등록 섹션
st.subheader("📝 출입자 등록 (입영)")

# 이름 입력 (자동완성 기능 연동)
name_input = st.selectbox(
    "성명 선택 또는 직접 입력 (명단에 있으면 자동완성)",
    options=[""] + list(DB_REGISTRY.keys()),
    index=0,
)

# 자동완성 데이터 가져오기
default_type = "영농인"
default_car = ""
default_dest = ""
default_zone = ""

if name_input in DB_REGISTRY:
  data = DB_REGISTRY[name_input]
  default_type = data["구분"]
  default_car = data["차량번호"]
  default_dest = data["목적지"]
  default_zone = data["구역"]

with st.form("entry_form", clear_on_submit=True):
  # 만약 직접 이름을 적고 싶을 때를 위한 텍스트 입력창
  custom_name = st.text_input(
      "이름 (목록에 없으면 직접 입력)", value=name_input if name_input else ""
  )
  v_type = st.selectbox(
      "출입 구분",
      ["영농인", "공사인원", "안보관광", "고정", "성묘객", "민간인"],
      index=0,
  )
  car = st.text_input("차종 및 차량번호", value=default_car)
  dest = st.text_input("목적지", value=default_dest)
  zone = st.text_input("구역", value=default_zone)

  submitted = st.form_submit_button("🚀 입영 처리")

  if submitted:
    final_name = custom_name.strip()
    if not final_name:
      st.warning("⚠️ 성명을 입력해주세요.")
    else:
      time_now = datetime.now().strftime("%H:%M")
      st.session_state.visitors.append({
          "type": v_type,
          "name": final_name,
          "car": car if car else "-",
          "dest": dest if dest else "-",
          "zone": zone if zone else "-",
          "time": time_now,
          "status": "체류중",
      })
      st.success(
          f"🎉 [{final_name}] 님 입영 처리 완료되었습니다! (시간: {time_now})"
      )

st.divider()

# 2. 현재 체류 현황 섹션
st.subheader("📊 현재 체류 중인 출입자 현황")

staying_visitors = [
    (i, v)
    for i, v in enumerate(st.session_state.visitors)
    if v["status"] == "체류중"
]

if not staying_visitors:
  st.info("현재 체류 중인 인원이 없습니다.")
else:
  for idx, v in staying_visitors:
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
      st.markdown(
          f"**[{v['type']}] {v['name']}**  \n차량: {v['car']} | 목적: {v['dest']}"
      )
    with col2:
      st.markdown(f"입영시간: `{v['time']}`")
    with col3:
      if st.button("퇴영", key=f"out_{idx}"):
        st.session_state.visitors[idx]["status"] = "퇴영완료"
        st.rerun()
    st.markdown("---")
