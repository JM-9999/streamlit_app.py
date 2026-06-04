import streamlit as st
import json
from datetime import date
from collections import defaultdict
import calendar as cal

FILE_NAME = "tasks.json"

# ------------------
# 데이터 처리
# ------------------

def load_tasks():
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# ------------------
# 초기 로드 (중요: 항상 최신 상태 기준)
# ------------------

if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

tasks = st.session_state.tasks

# ------------------
# 페이지 상태
# ------------------

if "year" not in st.session_state:
    st.session_state.year = date.today().year
if "month" not in st.session_state:
    st.session_state.month = date.today().month

# ------------------
# UI
# ------------------

st.title("📚 과제 관리 시스템")

# ------------------
# 과제 추가
# ------------------

st.subheader("➕ 과제 추가")

col1, col2 = st.columns(2)

with col1:
    subject = st.text_input("과목명")

with col2:
    title_input = st.text_input("과제명")

priority = st.selectbox("우선순위", ["높음", "보통", "낮음"])
due_date = st.date_input("마감일")

if st.button("추가"):
    if subject and title_input:
        st.session_state.tasks.append({
            "subject": subject,
            "title": title_input,
            "priority": priority,
            "due_date": str(due_date),
            "completed": False
        })
        save_tasks(st.session_state.tasks)
        st.rerun()

# ------------------
# 진행 현황
# ------------------

st.subheader("📊 진행 현황")

total = len(tasks)
done = sum(t["completed"] for t in tasks)
rate = done / total if total else 0

st.write(f"전체 {total}개 | 완료 {done}개 | 완료율 {rate*100:.0f}%")
st.progress(rate)

# ------------------
# 월 이동
# ------------------

col_prev, col_title, col_next = st.columns([1, 2, 1])

with col_prev:
    if st.button("◀ 이전달"):
        st.session_state.month -= 1
        if st.session_state.month == 0:
            st.session_state.month = 12
            st.session_state.year -= 1

with col_title:
    st.markdown(f"### {st.session_state.year}년 {st.session_state.month}월")

with col_next:
    if st.button("다음달 ▶"):
        st.session_state.month += 1
        if st.session_state.month == 13:
            st.session_state.month = 1
            st.session_state.year += 1

# ------------------
# 캘린더
# ------------------

st.subheader("📅 월간 캘린더")

weekday_map = ["월", "화", "수", "목", "금", "토", "일"]

calendar_dict = defaultdict(list)
for t in tasks:
    calendar_dict[t["due_date"]].append(t)

month_calendar = cal.monthcalendar(st.session_state.year, st.session_state.month)

for week in month_calendar:
    cols = st.columns(7)

    for i, day in enumerate(week):

        with cols[i]:

            if day == 0:
                st.markdown(
                    "<div style='height:120px;border:1px solid #eee;border-radius:6px'></div>",
                    unsafe_allow_html=True
                )
                continue

            date_str = f"{st.session_state.year}-{st.session_state.month:02d}-{day:02d}"
            day_tasks = calendar_dict.get(date_str, [])

            wd = weekday_map[date(st.session_state.year, st.session_state.month, day).weekday()]

            html = f"""
            <div style="
                height:120px;
                overflow-y:auto;
                border:1px solid #ddd;
                border-radius:8px;
                padding:6px;
                background:#fafafa;
            ">
                <div style="font-weight:600;font-size:13px;">
                    {day}({wd})
                </div>
            """

            for t in day_tasks:
                icon = "🔴" if t["priority"] == "높음" else "🟡" if t["priority"] == "보통" else "🟢"
                text = f"{icon} {t['title']}"

                if t["completed"]:
                    text = f"<s>{text}</s>"

                html += f"<div style='font-size:11px'>{text}</div>"

            html += "</div>"

            st.markdown(html, unsafe_allow_html=True)

# ------------------
# 전체 목록
# ------------------

st.subheader("📋 전체 과제 목록")

today = date.today()

with st.container(height=300, border=True):

    for i, task in enumerate(tasks):

        due = date.fromisoformat(task["due_date"])
        dday = (due - today).days

        icon = "🔴" if task["priority"] == "높음" else "🟡" if task["priority"] == "보통" else "🟢"

        cols = st.columns([8, 1, 1])

        with cols[0]:
            title = f"{icon} {task['subject']} - {task['title']}"

            if task["completed"]:
                st.markdown(f"~~**{title}**~~")
            else:
                st.markdown(f"**{title}**")

            if dday < 0:
                st.caption(f"❌ {abs(dday)}일 지남")
            elif dday == 0:
                st.caption("🔥 오늘 마감")
            else:
                st.caption(f"D-{dday}")

        with cols[1]:
            if st.button("✔" if not task["completed"] else "↩", key=f"toggle_{i}"):
                st.session_state.tasks[i]["completed"] = not st.session_state.tasks[i]["completed"]
                save_tasks(st.session_state.tasks)
                st.rerun()

        with cols[2]:
            if st.button("🗑️", key=f"delete_{i}"):
                st.session_state.tasks.pop(i)
                save_tasks(st.session_state.tasks)
                st.rerun()

# ------------------
# 저장 (보험용)
# ------------------

save_tasks(st.session_state.tasks)