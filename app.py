import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Daily Check-Ins", page_icon="🗓️", layout="centered")

# --- Google Sheets setup from Streamlit secrets ---
sc = st.secrets["gsheets"]
creds = Credentials.from_service_account_info(
    {
        "type": sc["type"],
        "project_id": sc["project_id"],
        "private_key_id": sc["private_key_id"],
        "private_key": sc["private_key"],
        "client_email": sc["client_email"],
        "client_id": sc["client_id"],
        "token_uri": sc["token_uri"],
    },
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
)
gc = gspread.authorize(creds)
sh = gc.open_by_key(sc["1DofLjp8sBQHrDm1wn_Ep0YQvKG5fl1TG9Tt3VOZ0Ahg"])
ws = sh.worksheet(sc["Sheet1"])

# Initialize headers if sheet is empty
if len(ws.get_all_values()) == 0:
    ws.append_row([
        "timestamp", "date", "name", "tasks_done", "goals",
        "blockers", "hours_focused", "mood_1to5", "tags"
    ])

st.title("🗓️ Daily Work Check-Ins")
st.caption("Fast, simple check-ins with a live Google Sheet backend.")

with st.form("checkin_form", clear_on_submit=True):
    c = st.columns(2)
    with c[0]:
        name = st.text_input("Your name")
    with c[1]:
        date = st.date_input("Date", value=datetime.now().date())

    tasks_done = st.text_area("What did you do today?", placeholder="Key tasks, outcomes, links...", height=120)
    goals = st.text_area("Goals / Next steps", height=80)
    blockers = st.text_area("Blockers / Needs", height=60)

    c2 = st.columns(2)
    with c2[0]:
        hours = st.slider("Hours focused", 0.0, 12.0, 4.0, 0.5)
    with c2[1]:
        mood = st.slider("Mood (1–5)", 1, 5, 4)

    tags = st.text_input("Tags (comma separated)", placeholder="planning, review, client-X")

    submitted = st.form_submit_button("✅ Save Check-In")
    if submitted:
        ws.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            str(date),
            name.strip(),
            tasks_done.strip(),
            goals.strip(),
            blockers.strip(),
            float(hours),
            int(mood),
            tags.strip(),
        ])
        st.success("Check-in saved!")

st.subheader("📜 Recent History")
data = ws.get_all_records()
df = pd.DataFrame(data)
if not df.empty:
    df_view = df.tail(200)
    st.dataframe(df_view, use_container_width=True)
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"),
                       "checkins.csv", "text/csv")
else:
    st.info("No check-ins yet. Submit your first one above.")
