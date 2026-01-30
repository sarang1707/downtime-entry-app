import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --------------------------------------------------
# App configuration
# --------------------------------------------------
st.set_page_config(page_title="Downtime Entry App", layout="centered")
st.title("🛠️ Downtime Entry Application")

# --------------------------------------------------
# Initialize session state
# --------------------------------------------------
if "data" not in st.session_state:
    st.session_state.data = []

# --------------------------------------------------
# Fault options
# --------------------------------------------------
faults = [
    "Morning Startup",
    "Idle Time",
    "Startup Issue",
    "Repositioning Fingers Error",
    "Safety Curtain Error",
    "Operator Error (Training)"
]

st.subheader("Enter Downtime Details")

# --------------------------------------------------
# User inputs
# --------------------------------------------------
selected_date = st.date_input("Select Date", value=datetime.today())

fault = st.selectbox("Select Fault Type", faults)

start_time = st.time_input("Start Time")

downtime_minutes = st.number_input(
    "Downtime Duration (minutes)",
    min_value=1,
    step=1
)

# --------------------------------------------------
# Time calculations
# --------------------------------------------------
start_datetime = datetime.combine(selected_date, start_time)
end_datetime = start_datetime + timedelta(minutes=downtime_minutes)

st.info(f"🕒 End Time: {end_datetime.time().strftime('%H:%M')}")

# --------------------------------------------------
# Add entry
# --------------------------------------------------
if st.button("➕ Add Downtime Entry"):
    st.session_state.data.append({
        "Date": selected_date.strftime("%Y-%m-%d"),
        "Fault": fault,
        "Start Time": start_datetime.time().strftime("%H:%M"),
        "Downtime (min)": downtime_minutes,
        "End Time": end_datetime.time().strftime("%H:%M")
    })
    st.success("Downtime entry added!")
    st.rerun()

# --------------------------------------------------
# Display records + delete
# --------------------------------------------------
if st.session_state.data:
    st.subheader("📊 Downtime Records")

    df = pd.DataFrame(st.session_state.data)

    col0, col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 2, 1])
    col0.markdown("**Date**")
    col1.markdown("**Fault**")
    col2.markdown("**Start**")
    col3.markdown("**Minutes**")
    col4.markdown("**End**")
    col5.markdown("**Delete**")

    for i, row in df.iterrows():
        c0, c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 2, 1])
        c0.write(row["Date"])
        c1.write(row["Fault"])
        c2.write(row["Start Time"])
        c3.write(row["Downtime (min)"])
        c4.write(row["End Time"])

        if c5.button("🗑️", key=f"delete_{i}"):
            st.session_state.data.pop(i)
            st.rerun()

    # --------------------------------------------------
    # Download CSV
    # --------------------------------------------------
    csv = pd.DataFrame(st.session_state.data).to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Downtime Records (CSV)",
        csv,
        "downtime_records.csv",
        "text/csv"
    )
