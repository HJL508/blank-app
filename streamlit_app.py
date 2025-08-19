# streamlit_app.py
# ---------------------------------------------------------
# 우리반 역할 랜덤 배정 (세션 상태 사용, 파일 저장 없음)
# 피드백 반영:
#  - 여러 학생을 입력하면 "모든" 학생에게 역할을 배정
#  - 이름을 무작위로 뽑는 기능/안내 제거
# Python 3.10+ / Streamlit 최신 안정 버전 기준
# ---------------------------------------------------------

import math
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
    # 이번 세션에서 배정한 누적 기록(최근이 위). 각 항목은 {"시간","이름","역할"}
    st.session_state.history = []
if "last_batch" not in st.session_state:
    # 직전 배정 결과(여러 명일 수 있음). 리스트[{"이름","역할"}] 또는 단일 역할 문자열
    st.session_state.last_batch = None

# 제목/설명
st.title("우리반 역할 랜덤 배정")
st.caption("학생 이름을 여러 명 입력하면 **입력된 모든 학생에게** 역할이 무작위로 배정됩니다. (세션 상태만 사용, 파일 저장 없음)")

# 유틸: 이름 파싱 (쉼표 또는 줄바꿈 구분)
def parse_names(text: str) -> list[str]:
    """
    쉼표(,) 또는 줄바꿈 기준으로 분리 → 공백 제거 → 빈 항목 제외
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
    help="입력하지 않으면 역할만 하나 무작위로 출력합니다.",
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
    st.session_state.last_batch = None
    st.info("기록을 모두 지웠어요. 새로 배정해 보세요!")

# 배정 로직
def assign_roles_to_all(input_names: list[str]) -> list[dict]:
    """
    입력된 모든 학생에게 역할을 하나씩 배정해서 반환.
    - 학생 수가 역할 수(8개)보다 많으면 역할을 반복해서 채움(중복 허용).
    - 매번 섞어서 공정하게 분배.
    반환 형식: [{"이름": str, "역할": str}, ...]
    """
    n = len(input_names)
    if n == 0:
        return []

    # 필요한 최소 반복 횟수만큼 역할 풀을 늘리고 섞기
    repeats = math.ceil(n / len(ROLES))
    pool = ROLES * repeats
    random.shuffle(pool)

    # 이름도 섞어서 특정 순서 편향 방지(원치 않으면 이 줄 제거)
    shuffled_names = input_names[:]  # 원본 보존
    random.shuffle(shuffled_names)

    # 앞에서 n개를 짝지어 반환
    batch = [{"이름": nm, "역할": role} for nm, role in zip(shuffled_names, pool[:n])]
    return batch

# 뽑기 버튼 처리
if draw_clicked:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if names:  # 여러 학생 모두에게 배정
        batch = assign_roles_to_all(names)
        st.session_state.last_batch = batch

        # 세션 기록에 앞쪽에 추가 (최신이 위), 최대 100개까지만 유지
        for row in batch:
            st.session_state.history.insert(0, {"시간": timestamp, "이름": row["이름"], "역할": row["역할"]})
        st.session_state.history = st.session_state.history[:100]
    else:
        # 이름이 없으면 역할만 하나 무작위 출력
        role = random.choice(ROLES)
        st.session_state.last_batch = role
        st.session_state.history.insert(0, {"시간": timestamp, "이름": "-", "역할": role})
        st.session_state.history = st.session_state.history[:100]

# 결과 표시
st.subheader("결과")
if st.session_state.last_batch is None:
    st.info("아직 배정 결과가 없습니다. **[역할 뽑기]** 버튼을 눌러 보세요!")
else:
    last = st.session_state.last_batch
    if isinstance(last, list):
        st.success("🎉 모든 학생에게 역할이 배정되었습니다!")
        # 표로 보기 좋게 출력
        st.dataframe(last, use_container_width=True, hide_index=True)
        # 안내: 학생 수가 역할 수를 초과하면 중복 가능
        if len(names) > len(ROLES):
            st.caption("ℹ️ 학생 수가 역할 수(8개)보다 많아 **일부 역할은 중복**될 수 있어요.")
    else:
        st.success(f"🎉 이번 역할: **{last}**")

# 세션 누적 기록
st.subheader("이번 세션 배정 기록")
if st.session_state.history:
    st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)
else:
    st.write("표시할 기록이 없습니다.")

# 하단 고정 안내
st.caption("✅ 이 앱은 세션 상태만 사용하며, 페이지 새로고침 시 기록이 초기화됩니다.")
