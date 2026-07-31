import json
import os
import uuid
from datetime import datetime

import streamlit as st
from streamlit_calendar import calendar

DATA_FILE = "tasks.json"

LABEL_COLORS = {
    "A": "#e74c3c",  # red
    "P": "#3498db",  # blue
    "B": "#2ecc71",  # green
}

st.set_page_config(page_title="My Calendar", layout="wide")


def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

st.title("📅 My Calendar")

with st.sidebar:
    st.header("Add a task")
    with st.form("add_task", clear_on_submit=True):
        title = st.text_input("Title")
        date = st.date_input("Date", format="DD/MM/YYYY")
        time = st.time_input("Time", step=300)
        label = st.selectbox("Label", options=["A", "P", "B"])
        submitted = st.form_submit_button("Add")
        if submitted and title.strip():
            start_dt = datetime.combine(date, time)
            st.session_state.tasks.append(
                {
                    "id": str(uuid.uuid4()),
                    "title": title.strip(),
                    "start": start_dt.isoformat(),
                    "label": label,
                    "color": LABEL_COLORS[label],
                }
            )
            save_tasks(st.session_state.tasks)
            st.rerun()

    st.divider()
    st.caption("Legend")
    for lbl, color in LABEL_COLORS.items():
        st.markdown(
            f"<span style='display:inline-block;width:12px;height:12px;"
            f"background:{color};border-radius:2px;margin-right:6px'></span>{lbl}",
            unsafe_allow_html=True,
        )

    st.divider()
    if st.session_state.tasks:
        st.subheader("Delete a task")
        options = {
            f"{datetime.fromisoformat(t['start']).strftime('%d/%m/%Y %H:%M')} — "
            f"{t['title']} ({t['label']})": t["id"]
            for t in st.session_state.tasks
        }
        choice = st.selectbox("Select task", options=list(options.keys()))
        if st.button("Delete"):
            task_id = options[choice]
            st.session_state.tasks = [
                t for t in st.session_state.tasks if t["id"] != task_id
            ]
            save_tasks(st.session_state.tasks)
            st.rerun()

view_choice = st.radio("View", ["Month", "Week"], horizontal=True)
initial_view = "dayGridMonth" if view_choice == "Month" else "timeGridWeek"

events = [
    {
        "title": f"[{t['label']}] {t['title']}",
        "start": t["start"],
        "color": t["color"],
    }
    for t in st.session_state.tasks
]

calendar_options = {
    "initialView": initial_view,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "",
    },
    "height": 700,
    "slotLabelFormat": {
        "hour": "2-digit",
        "minute": "2-digit",
        "hour12": False,
    },
    "eventTimeFormat": {
        "hour": "2-digit",
        "minute": "2-digit",
        "hour12": False,
    },
    "dayHeaderFormat": {"day": "2-digit", "month": "2-digit", "weekday": "short"},
    "titleFormat": {"day": "2-digit", "month": "2-digit", "year": "numeric"},
}

calendar(events=events, options=calendar_options, key=view_choice)
