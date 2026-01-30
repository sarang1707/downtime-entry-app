import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ------------------------------
# App Configuration
# ------------------------------
st.set_page_config(
    page_title="🛠️ Downtime Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# Paths & Machines
# ------------------------------
DATA_DIR = r"S:\Monitor Åstorp\Maskiner & underhåll\Förebyggande underhåll (Preventive Maintenance)\Underhåll maintenance\Downtime report data\Automatic downtime reports"
os.makedirs(DATA_DIR, exist_ok=True)

MACHINES = {
    "LVD": "🛠️",
    "Euromac 1": "🏗️",
    "Euromac 2": "🏗️"
}

DATA_FILES = {
    m: os.path.join(DATA_DIR, f"{m.replace(' ', '_')}_downtime.csv")
    for m in MACHINES
}

FAULT_FILES = {
    m: os.path.join(DATA_DIR, f"{m.replace(' ', '_')}_faults.csv")
    for m in MACHINES
}

# ------------------------------
# Load Functions
# ------------------------------
def load_data(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(
        columns=["Date", "Fault", "Start Time", "Downtime (min)", "End Time"]
    )

def load_faults(path):
    if os.path.exists(path):
        return pd.read_csv(path)["Fault"].tolist()

    default_faults = [
        "Idle time (800)",
        "Suction cups (801)",
        "Faulty sensor (802)",
        "Thickness measurement (803)",
        "Tool change (804)",
        "Compensator (805)",
        "Press control unit (806)",
        "Tool Sync (807)",
        "Preload fail (808)",
        "Tool Broken (809)",
        "Overtravel (810)"
    ]
    pd.DataFrame({"Fault": default_faults}).to_csv(path, index=False)
    return default_faults

# ------------------------------
# Session State Init
# ------------------------------
if "data_dfs" not in st.session_state:
    st.session_state.data_dfs = {
        m: load_data(DATA_FILES[m]) for m in MACHINES
    }

if "fault_lists" not in st.session_state:
    st.session_state.fault_lists = {
        m: load_faults(FAULT_FILES[m]) for m in MACHINES
    }

if "selected_machine" not in st.session_state:
    st.session_state.selected_machine = None

if "new_fault_inputs" not in st.session_state:
    st.session_state.new_fault_inputs = {m: "" for m in MACHINES}

# ------------------------------
# UI – Machine Selection
# ------------------------------
st.title("🛠️ Multi-Machine Downtime Tracker")
st.markdown("Select a machine to manage downtime and faults:")

cols = st.columns(len(MACHINES))
for i, (machine, icon) in enumerate(MACHINES.items()):
    if cols[i].button(f"{icon}\n{machine}", key=f"select_{machine}"):
        st.session_state.selected_machine = machine

selected_machine = st.session_state.selected_machine

# ------------------------------
# Main Machine View
# ------------------------------
if selected_machine:
    st.success(f"Selected Machine: {selected_machine}")

    data_df = st.session_state.data_dfs[selected_machine]
    fault_list = st.session_state.fault_lists[selected_machine]

    tab_entry, tab_faults = st.tabs(
        ["📌 Downtime Entry", "⚙️ Fault Management"]
    )

    # ------------------------------
    # TAB 1 – Downtime Entry
    # ------------------------------
    with tab_entry:
        st.subheader("➕ Record Downtime")

        col1, col2, col3 = st.columns(3)

        selected_date = col1.date_input(
            "📅 Date",
            datetime.today()
        )

        fault = col2.selectbox(
            "⚠️ Fault Type",
            fault_list
        )

        start_time = col3.time_input(
            "⏱️ Start Time",
            datetime.now().time()
        )

        downtime_minutes = st.number_input(
            "🕒 Downtime Duration (minutes)",
            min_value=1,
            step=1,
            value=1
        )

        start_dt = datetime.combine(selected_date, start_time)
        end_dt = start_dt + timedelta(minutes=downtime_minutes)

        st.info(f"Estimated End Time: **{end_dt.strftime('%H:%M')}**")

        if st.button("✅ Add Downtime Entry"):
            new_entry = {
                "Date": selected_date.strftime("%Y-%m-%d"),
                "Fault": fault,
                "Start Time": start_dt.strftime("%H:%M"),
                "Downtime (min)": int(downtime_minutes),
                "End Time": end_dt.strftime("%H:%M")
            }

            st.session_state.data_dfs[selected_machine] = pd.concat(
                [data_df, pd.DataFrame([new_entry])],
                ignore_index=True
            )

            st.session_state.data_dfs[selected_machine].to_csv(
                DATA_FILES[selected_machine],
                index=False
            )

            st.success("✅ Downtime entry added!")

        # ------------------------------
        # Display Records
        # ------------------------------
        if not st.session_state.data_dfs[selected_machine].empty:
            st.subheader("📊 Downtime Records")

            df_display = st.session_state.data_dfs[selected_machine].copy()
            df_display.index = range(1, len(df_display) + 1)
            df_display.index.name = "No."

            st.dataframe(df_display, use_container_width=True)

            delete_rows = st.multiselect(
                "Select rows to delete",
                options=df_display.index.tolist(),
                format_func=lambda i: (
                    f"{i} | {df_display.loc[i, 'Date']} | "
                    f"{df_display.loc[i, 'Fault']} | "
                    f"{df_display.loc[i, 'Start Time']}"
                )
            )

            if st.button("🗑️ Delete Selected Rows") and delete_rows:
                st.session_state.data_dfs[selected_machine].drop(
                    [i - 1 for i in delete_rows],
                    inplace=True
                )
                st.session_state.data_dfs[selected_machine].reset_index(
                    drop=True,
                    inplace=True
                )
                st.session_state.data_dfs[selected_machine].to_csv(
                    DATA_FILES[selected_machine],
                    index=False
                )
                st.success(f"Deleted {len(delete_rows)} row(s).")

            st.download_button(
                "⬇️ Download Records as CSV",
                st.session_state.data_dfs[selected_machine]
                .to_csv(index=False)
                .encode("utf-8"),
                file_name=f"{selected_machine.replace(' ', '_')}_downtime_records.csv",
                mime="text/csv"
            )
        else:
            st.info("No downtime entries yet.")

    # ------------------------------
    # TAB 2 – Fault Management
    # ------------------------------
    with tab_faults:
        st.subheader("⚙️ Fault Management")

        col_add, col_delete = st.columns(2)

        new_fault = col_add.text_input(
            "➕ New Fault Type",
            value=st.session_state.new_fault_inputs[selected_machine]
        )

        if col_add.button("➕ Add Fault"):
            new_fault = new_fault.strip()
            if new_fault and new_fault not in fault_list:
                st.session_state.fault_lists[selected_machine].append(new_fault)
                pd.DataFrame(
                    {"Fault": st.session_state.fault_lists[selected_machine]}
                ).to_csv(FAULT_FILES[selected_machine], index=False)
                st.success(f"Added fault: {new_fault}")
            elif new_fault:
                st.warning("⚠️ Fault already exists.")

            st.session_state.new_fault_inputs[selected_machine] = ""

        if fault_list:
            fault_to_delete = col_delete.selectbox(
                "🗑️ Select Fault to Delete",
                fault_list
            )

            if col_delete.button("🗑️ Delete Fault"):
                if len(fault_list) == 1:
                    st.warning("⚠️ Cannot delete the last fault.")
                else:
                    st.session_state.fault_lists[selected_machine].remove(
                        fault_to_delete
                    )
                    pd.DataFrame(
                        {"Fault": st.session_state.fault_lists[selected_machine]}
                    ).to_csv(FAULT_FILES[selected_machine], index=False)
                    st.success(f"Deleted fault: {fault_to_delete}")

        st.markdown("**Current Fault Types:**")
        st.write(", ".join(st.session_state.fault_lists[selected_machine]))
