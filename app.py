import datetime
import json
import os
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="비룡초소 출입통제 시스템", page_icon="🛡️", layout="wide"
)

# -------------------------------------------------------------------------
# 파일 저장 및 불러오기 함수 (서버 JSON 연동)
# -------------------------------------------------------------------------
FIXED_FILE = "fixed_members.json"
TEMP_FILE = "temp_members.json"
LOG_FILE = "logs.json"


def load_json(filename, default_data):
  if os.path.exists(filename):
    try:
      with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return default_data
  return default_data


def save_json(filename, data):
  with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# 초기 데이터 로드
if "fixed_members" not in st.session_state:
  st.session_state.fixed_members = load_json(
      FIXED_FILE,
      [
        {"군번": "12-345678", "계급": "병장", "이름": "김철수", "소속": "1중대"},
        {"군번": "23-456789", "계급": "상병", "이름": "박영희", "소속": "2중대"},
      ],
  )

if "temp_members" not in st.session_state:
  loaded_temp = load_json(TEMP_FILE, [])
  today_str = datetime.date.today().strftime("%Y-%m-%d")
  valid_temp = []
  for t in loaded_temp:
    if t.get("종료일", "9999-12-31") >= today_str:
      valid_temp.append(t)
  st.session_state.temp_members = valid_temp
  save_json(TEMP_FILE, st.session_state.temp_members)

if "logs" not in st.session_state:
  st.session_state.logs = load_json(LOG_FILE, [])


# -------------------------------------------------------------------------
# 로그인 세션 관리
# -------------------------------------------------------------------------
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if not st.session_state.logged_in:
  st.title("🛡️ 비룡초소 출입통제 시스템 (보안 로그인)")
  with st.form("login_form"):
    password = st.text_input("비밀번호를 입력하세요", type="password")
    submit_btn = st.form_submit_button("로그인")
    if submit_btn:
      if password == "1234":
        st.session_state.logged_in = True
        st.rerun()
      else:
        st.error("비밀번호가 틀렸습니다.")
  st.stop()


# -------------------------------------------------------------------------
# 메인 시스템 UI
# -------------------------------------------------------------------------
st.title("🛡️ 비룡초소 출입통제 시스템")
st.sidebar.markdown(f"**현재 접속일자:** {datetime.date.today()}")

# 탭 구성 (아카이브 및 임시출입자 관리 포함)
tab1, tab2, tab3, tab4 = st.tabs([
    "🚪 출입 관리",
    "👥 고정출입자 관리",
    "📋 임시출입자 관리",
    "📦 아카이브 (지난 기록)",
])

# -------------------------------------------------------------------------
# [탭 1] 출입 관리 (입영/출영 및 임시출입자 연동)
# -------------------------------------------------------------------------
with tab1:
  st.subheader("🚪 실시간 출입 관리")

  # 고정 + 유효한 임시출입자 통합 선택 리스트 구성 (안전하게 .get 사용)
  all_available_options = []
  for f in st.session_state.fixed_members:
    rank = f.get("계급", "")
    name = f.get("이름", "")
    f_id = f.get("군번", "")
    unit = f.get("소속", "")
    all_available_options.append(f"[고정] {rank} {name} ({f_id}, {unit})")

  for t in st.session_state.temp_members:
    t_name = t.get("이름", "")
    t_start = t.get("시작일", "")
    t_end = t.get("종료일", "")
    t_reason = t.get("방문사유", "")
    all_available_options.append(
        f"[임시] {t_name} (기간: {t_start}~{t_end}, 사유: {t_reason})"
    )

  with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      selected_person = st.selectbox(
          "대상자 선택 (고정/임시 통합 검색)",
          options=["직접 입력"] + all_available_options,
      )
      manual_name = st.text_input(
          "이름 (직접 입력 시)",
          placeholder="선택 안 함 또는 직접 입력 시 작성",
      )
    with col2:
      direction = st.radio("구분", ["입영 (들어옴)", "출영 (나감)"], horizontal=True)
      purpose = st.text_input("방문/이동 목적", value="근무 및 용무")

    submit_entry = st.form_submit_button("출입 기록 등록")
    if submit_entry:
      name_to_log = ""
      category_to_log = "일반"

      if selected_person != "직접 입력":
        name_to_log = selected_person
        if "[고정]" in selected_person:
          category_to_log = "고정출입자"
        elif "[임시]" in selected_person:
          category_to_log = "임시출입자"
      else:
        if not manual_name:
          name_to_log = "미확인 인원"
        else:
          name_to_log = manual_name
        category_to_log = "기타/직접입력"

      now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      new_log = {
          "시간": now_time,
          "날짜": datetime.date.today().strftime("%Y-%m-%d"),
          "대상": name_to_log,
          "구분": direction,
          "목적": purpose,
          "분류": category_to_log,
      }

      st.session_state.logs.insert(0, new_log)
      save_json(LOG_FILE, st.session_state.logs)
      st.success(f"[{direction}] 기록되었습니다: {name_to_log}")
      st.rerun()

  st.markdown("---")
  st.subheader("📋 최근 7일 출입 현황 (메인)")

  today_date = datetime.date.today()
  seven_days_ago = today_date - datetime.timedelta(days=7)

  recent_logs = []
  for log in st.session_state.logs:
    log_date_str = log.get("날짜", log.get("시간", "2026-01-01")[:10])
    try:
      log_date = datetime.datetime.strptime(log_date_str, "%Y-%m-%d").date()
    except:
      log_date = today_date

    if log_date >= seven_days_ago:
      recent_logs.append(log)

  if recent_logs:
    st.dataframe(
        recent_logs,
        column_order=["시간", "대상", "구분", "목적", "분류"],
        use_container_width=True,
    )
  else:
    st.info("최근 7일 이내의 출입 기록이 없습니다.")

# -------------------------------------------------------------------------
# [탭 2] 고정출입자 관리 (삭제 안전장치 추가)
# -------------------------------------------------------------------------
with tab2:
  st.subheader("👥 부대 고정출입자 관리")

  with st.form("add_fixed_form", clear_on_submit=True):
    st.markdown("##### 새 고정출입자 등록")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
      f_id = st.text_input("군번", placeholder="12-345678")
    with f_col2:
      f_rank = st.text_input("계급", placeholder="병장")
    with f_col3:
      f_name = st.text_input("이름", placeholder="홍길동")
    with f_col4:
      f_unit = st.text_input("소속", placeholder="본부중대")

    f_submit = st.form_submit_button("고정출입자 등록")
    if f_submit:
      if f_id and f_name:
        st.session_state.fixed_members.append({
            "군번": f_id,
            "계급": f_rank,
            "이름": f_name,
            "소속": f_unit,
        })
        save_json(FIXED_FILE, st.session_state.fixed_members)
        st.success(f"고정출입자 등록 완료: {f_rank} {f_name}")
        st.rerun()
      else:
        st.warning("군번과 이름은 필수 입력입니다.")

  st.markdown("---")
  st.markdown("##### 등록된 고정출입자 목록 (삭제 안전장치 적용)")

  for idx, member in enumerate(st.session_state.fixed_members):
    cols = st.columns([3, 1])
    with cols[0]:
      st.write(
          f"🔹 **{member.get('계급', '')} {member.get('이름', '')}** (군번:"
          f" {member.get('군번', '')}, 소속: {member.get('소속', '')})"
      )
    with cols[1]:
      confirm_del = st.checkbox("삭제 확인", key=f"chk_fixed_{idx}")
      if st.button("삭제", key=f"del_fixed_{idx}", disabled=not confirm_del):
        st.session_state.fixed_members.pop(idx)
        save_json(FIXED_FILE, st.session_state.fixed_members)
        st.success("삭제되었습니다.")
        st.rerun()

# -------------------------------------------------------------------------
# [탭 3] 임시출입자 관리 (기간 설정 및 자동 만료 기능)
# -------------------------------------------------------------------------
with tab3:
  st.subheader("📋 임시출입자 관리 (공문 및 사전승인 인원)")

  with st.form("add_temp_form", clear_on_submit=True):
    st.markdown("##### 새 임시출입자 등록")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
      t_name = st.text_input("성명 / 업체명", placeholder="김민수 (공사업체)")
      t_reason = st.text_input("방문 사유 / 공문번호", placeholder="통신망 보수 공문")
    with t_col2:
      t_start = st.date_input("출입 시작일", value=datetime.date.today())
      t_end = st.date_input(
          "출입 종료일",
          value=datetime.date.today() + datetime.timedelta(days=3),
      )

    t_submit = st.form_submit_button("임시출입자 등록")
    if t_submit:
      if t_name:
        new_temp = {
            "이름": t_name,
            "방문사유": t_reason,
            "시작일": t_start.strftime("%Y-%m-%d"),
            "종료일": t_end.strftime("%Y-%m-%d"),
        }
        st.session_state.temp_members.append(new_temp)
        save_json(TEMP_FILE, st.session_state.temp_members)
        st.success(f"임시출입자 등록 완료: {t_name} (~{t_end})")
        st.rerun()
      else:
        st.warning("이름/업체명은 필수 입력입니다.")

  st.markdown("---")
  st.markdown("##### 현재 유효한 임시출입자 목록")

  if st.session_state.temp_members:
    for idx, t_mem in enumerate(st.session_state.temp_members):
      t_cols = st.columns([4, 1])
      with t_cols[0]:
        st.write(
            f"🔸 **{t_mem.get('이름', '')}** | 사유:"
            f" {t_mem.get('방문사유', '')} | 기간: {t_mem.get('시작일', '')} ~"
            f" {t_mem.get('종료일', '')}"
        )
      with t_cols[1]:
        if st.button("조기 삭제", key=f"del_temp_{idx}"):
          st.session_state.temp_members.pop(idx)
          save_json(TEMP_FILE, st.session_state.temp_members)
          st.success("제거되었습니다.")
          st.rerun()
  else:
    st.info("등록된 임시출입자가 없습니다.")

# -------------------------------------------------------------------------
# [탭 4] 아카이브 (7일이 지난 지난 기록)
# -------------------------------------------------------------------------
with tab4:
  st.subheader("📦 아카이브 (일주일 경과 지난 기록 보관함)")
  st.markdown(
      "메인 화면에서 7일이 지난 과거 출입 기록들은 자동으로 이 공간에"
      " 보관되어 시스템 속도를 쾌적하게 유지합니다."
  )

  old_logs = []
  today_date = datetime.date.today()
  seven_days_ago = today_date - datetime.timedelta(days=7)

  for log in st.session_state.logs:
    log_date_str = log.get("날짜", log.get("시간", "2026-01-01")[:10])
    try:
      log_date = datetime.datetime.strptime(log_date_str, "%Y-%m-%d").date()
    except:
      log_date = today_date

    if log_date < seven_days_ago:
      old_logs.append(log)

  if old_logs:
    st.dataframe(
        old_logs,
        column_order=["시간", "대상", "구분", "목적", "분류"],
        use_container_width=True,
    )
  else:
    st.info("7일이 지난 아카이브 기록이 없습니다.")
