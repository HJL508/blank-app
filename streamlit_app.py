# streamlit_app.py
# -------------------------------------------
# 우리반 역할 랜덤 배정 (세션 상태 사용, 파일 저장 없음)
# Python 3.10+ / Streamlit 최신 안정 버전 기준
# -------------------------------------------

import random
import re
from datetime import datetime
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="우리반 역할 랜덤 배정",
    page_icon="🎲",
    layout="centered",
)

# 고정 역할 목록 (요구사항의 8개)
ROLES = ["리더", "발표", "기록", "시간관리", "자료조사", "정리", "격려", "품질관리"]

# 세션 상태 초기화
if "history" not in st.session_state:
    # 이번 세션에서 뽑은 기록을 담는 리스트 (앱 새로고침/재실행 시 사라짐)
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# 제목/설명
st.title("우리반 역할 랜덤 배정")
st.caption("버튼을 누르면 역할이 무작위로 선택됩니다. 학생 이름을 입력하면 **이름도 함께 랜덤으로** 뽑을 수 있어요.")

# 이름 파싱 유틸 (쉼표 또는 줄바꿈 구분)
def parse_names(text: str) -> list[str]:
    """
    입력한 문자열을 쉼표(,) 또는 줄바꿈 기준으로 분리해서
    공백을 제거하고 빈 항목은 제외한 이름 리스트로 반환.
    """
    if not text:
        return []
    parts = re.split(r"[,\n]+", text)
    names = [p.strip() for p in parts if p.strip()]
    return names

# (선택) 학생 이름 입력란
names_raw = st.text_area(
    "학생 이름 목록 (선택 사항)",
    placeholder="예: 김철수, 이영희, 박민준\n또는 줄바꿈으로 한 줄에 한 명씩 입력",
    help="입력하지 않으면 역할만 무작위로 뽑습니다.",
)
names = parse_names(names_raw)

# 버튼 영역
col1, col2 = st.columns(2)
with col1:
    draw_clicked = st.button("🎲 역할 뽑기", use_container_width=True)
with col2:
    clear_clicked = st.button("기록 지우기", use_container_width=True)

# 기록 지우기 처리
if clear_clicked:
    st.session_state.history.clear()
    st.session_state.last_result = None
    st.info("기록을 모두 지웠어요. 새로 뽑아 보세요!")

# 뽑기 버튼 처리
if draw_clicked:
    role = random.choice(ROLES)
    chosen_name = random.choice(names) if names else None

    # 결과를 세션 상태에 저장
    st.session_state.last_result = {
        "role": role,
        "name": chosen_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 기록(최신이 위로 오도록 앞에 추가, 최대 20개 보관)
    st.session_state.history.insert(
        0,
        {
            "시간": st.session_state.last_result["timestamp"],
            "이름": chosen_name or "-",
            "역할": role,
        },
    )
    st.session_state.history = st.session_state.history[:20]

# 현재 결과 표시
st.subheader("결과")
if st.session_state.last_result is None:
    st.info("아직 뽑은 결과가 없습니다. **[역할 뽑기]** 버튼을 눌러 보세요!")
else:
    res = st.session_state.last_result
    if res["name"]:
        st.success(f'🎉 **{res["name"]}** → **{res["role"]}**', icon="🎉")
    else:
        st.success(f'🎉 이번 역할: **{res["role"]}**', icon="🎉")

# 세션 내 기록 표시
st.subheader("이번 세션 배정 기록 (최대 20개)")
if st.session_state.history:
    # Streamlit은 리스트/딕셔너리를 표로 렌더링해 줍니다.
    st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)
else:
    st.write("표시할 기록이 없습니다.")

# 안내 문구
st.caption("✅ 이 앱은 세션 상태만 사용하며, **파일로 저장하지 않습니다.** 페이지 새로고침 시 기록이 초기화됩니다.")
