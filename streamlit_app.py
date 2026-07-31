import streamlit as st
from streamlit_calendar import calendar

st.set_page_config(page_title="My Calendar", layout="wide")

st.title("📅 My Calendar")

view_choice = st.radio("View", ["Month", "Week"], horizontal=True)
initial_view = "dayGridMonth" if view_choice == "Month" else "timeGridWeek"

calendar_options = {
    "initialView": initial_view,
    "locale": "en-gb",
    "firstDay": 1,  # weeks start on Monday, European style
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
    "slotLabelInterval": "01:00",
}

calendar(events=[], options=calendar_options, key="calendar")
