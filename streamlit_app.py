"""
Streamlit Calendar App
----------------------
Week and Month views. All dates are shown as dd/mm/yyyy and all times as 24-hour HH:MM.

Run with:
    streamlit run calendar_app.py
"""

import streamlit as st
import calendar
from datetime import datetime, date, timedelta

# ---------------------------------------------------------------------------
# Config / constants
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Calendar", layout="wide")

DATE_FMT = "%d/%m/%Y"   # European date format: dd/mm/yyyy
TIME_FMT = "%H:%M"      # 24-hour time format

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Calendar module: weeks start on Monday (European convention)
calendar.setfirstweekday(calendar.MONDAY)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "events" not in st.session_state:
    # Each event: {"date": date, "start": "HH:MM", "end": "HH:MM", "title": str, "notes": str}
    st.session_state.events = []

if "current_date" not in st.session_state:
    st.session_state.current_date = date.today()

if "view" not in st.session_state:
    st.session_state.view = "Month"


def fmt_date(d: date) -> str:
    """Format a date object as dd/mm/yyyy."""
    return d.strftime(DATE_FMT)


def parse_time_str(t) -> str:
    """Ensure a time value is displayed as HH:MM (24-hour)."""
    if isinstance(t, str):
        return t
    return t.strftime(TIME_FMT)


def get_events_for_day(d: date):
    return sorted(
        [e for e in st.session_state.events if e["date"] == d],
        key=lambda e: e["start"]
    )


def week_bounds(d: date):
    """Return (monday, sunday) of the week containing d."""
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


# ---------------------------------------------------------------------------
# Sidebar: navigation + add event form
# ---------------------------------------------------------------------------

st.sidebar.title("📅 Calendar")

view = st.sidebar.radio("View", ["Month", "Week"], index=0 if st.session_state.view == "Month" else 1)
st.session_state.view = view

st.sidebar.markdown("---")

col_prev, col_today, col_next = st.sidebar.columns(3)
if col_prev.button("◀ Prev", use_container_width=True):
    if view == "Month":
        d = st.session_state.current_date
        first_of_month = d.replace(day=1)
        prev_month_last_day = first_of_month - timedelta(days=1)
        st.session_state.current_date = prev_month_last_day.replace(day=1)
    else:
        st.session_state.current_date -= timedelta(weeks=1)

if col_today.button("Today", use_container_width=True):
    st.session_state.current_date = date.today()

if col_next.button("Next ▶", use_container_width=True):
    if view == "Month":
        d = st.session_state.current_date
        days_in_month = calendar.monthrange(d.year, d.month)[1]
        first_of_next = d.replace(day=1) + timedelta(days=days_in_month)
        st.session_state.current_date = first_of_next
    else:
        st.session_state.current_date += timedelta(weeks=1)

st.sidebar.markdown("---")
st.sidebar.subheader("Add event")

with st.sidebar.form("add_event_form", clear_on_submit=True):
    ev_date = st.date_input(
        "Date (dd/mm/yyyy)",
        value=st.session_state.current_date,
        format="DD/MM/YYYY",
    )
    ev_title = st.text_input("Title")
    c1, c2 = st.columns(2)
    ev_start = c1.time_input("Start", value=datetime.strptime("09:00", "%H:%M").time(), step=timedelta(minutes=15))
    ev_end = c2.time_input("End", value=datetime.strptime("10:00", "%H:%M").time(), step=timedelta(minutes=15))
    ev_notes = st.text_area("Notes", height=68)
    submitted = st.form_submit_button("Add event", use_container_width=True)

    if submitted:
        if not ev_title.strip():
            st.sidebar.error("Please enter a title for the event.")
        elif ev_end <= ev_start:
            st.sidebar.error("End time must be after start time.")
        else:
            st.session_state.events.append({
                "date": ev_date,
                "start": ev_start.strftime(TIME_FMT),
                "end": ev_end.strftime(TIME_FMT),
                "title": ev_title.strip(),
                "notes": ev_notes.strip(),
            })
            st.sidebar.success(f"Added '{ev_title.strip()}' on {fmt_date(ev_date)}")

# Manage / delete events
if st.session_state.events:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Manage events")
    sorted_events = sorted(
        enumerate(st.session_state.events),
        key=lambda x: (x[1]["date"], x[1]["start"])
    )
    for idx, ev in sorted_events:
        label = f"{fmt_date(ev['date'])} {ev['start']}–{ev['end']} · {ev['title']}"
        c1, c2 = st.sidebar.columns([4, 1])
        c1.write(label)
        if c2.button("🗑️", key=f"del_{idx}"):
            st.session_state.events.pop(idx)
            st.rerun()

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.title("📅 My Calendar")

today = date.today()

# --- MONTH VIEW -------------------------------------------------------------
if view == "Month":
    d = st.session_state.current_date
    year, month = d.year, d.month

    st.subheader(f"{MONTH_NAMES[month - 1]} {year}")

    # Header row with weekday names (Mon-Sun)
    header_cols = st.columns(7)
    for i, name in enumerate(WEEKDAY_NAMES):
        header_cols[i].markdown(f"**{name}**")

    month_calendar = calendar.monthcalendar(year, month)  # weeks, each a list of 7 day-ints (0 = outside month)

    for week in month_calendar:
        cols = st.columns(7)
        for i, day_num in enumerate(week):
            with cols[i]:
                if day_num == 0:
                    st.markdown("&nbsp;")
                    continue
                day_date = date(year, month, day_num)
                is_today = day_date == today

                day_label = f"**{day_num:02d}**" if not is_today else f"**🔵 {day_num:02d}**"
                st.markdown(day_label)

                day_events = get_events_for_day(day_date)
                if day_events:
                    for ev in day_events[:3]:
                        st.caption(f"{ev['start']}–{ev['end']} {ev['title']}")
                    if len(day_events) > 3:
                        st.caption(f"+{len(day_events) - 3} more")
                else:
                    st.caption(" ")

    st.markdown("---")
    st.caption(f"Today: {fmt_date(today)}")

# --- WEEK VIEW ---------------------------------------------------------------
else:
    monday, sunday = week_bounds(st.session_state.current_date)
    st.subheader(f"Week of {fmt_date(monday)} – {fmt_date(sunday)}")

    cols = st.columns(7)
    for i in range(7):
        day_date = monday + timedelta(days=i)
        is_today = day_date == today
        with cols[i]:
            header = f"**{WEEKDAY_NAMES[i]}**\n\n{fmt_date(day_date)}"
            if is_today:
                header = "🔵 " + header
            st.markdown(header)
            st.markdown("---")

            day_events = get_events_for_day(day_date)
            if day_events:
                for ev in day_events:
                    with st.container(border=True):
                        st.markdown(f"**{ev['start']} – {ev['end']}**")
                        st.write(ev["title"])
                        if ev["notes"]:
                            st.caption(ev["notes"])
            else:
                st.caption("No events")

    st.markdown("---")
    st.caption(f"Today: {fmt_date(today)}")
