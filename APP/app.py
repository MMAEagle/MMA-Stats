import streamlit as st
import pandas as pd

# Ρύθμιση σελίδας
st.set_page_config(page_title="MMA Stats App", layout="wide")

# Ανάγνωση Excel
excel_file = "APP/002 Stats.xlsx"
sheet = "App"

custom_columns = [
    "Fighter", "Age", "Height", "Reach", "Streak",
    "KO Wins%", "KO Losses%", "SUB Wins%", "SUB Losses%",
    "DEC Wins%", "DEC Losses%",
    "Sig Strikes Landed", "Sig Strikes Absorbed",
    "Head %", "Body %", "Legs %",
    "Control Time (sec)", "Control %",
    "Controlled Time (sec)", "Controlled %",
    "Fight Time (sec)"
]

df = pd.read_excel(excel_file, sheet_name=sheet, skiprows=2, header=None)
df = df.iloc[:, :len(custom_columns)]
df.columns = custom_columns
df = df.dropna(subset=["Fighter"])
df["Fight Time (min)"] = (df["Fight Time (sec)"] / 60).round(1)

percent_cols = [
    "KO Wins%", "KO Losses%", "SUB Wins%", "SUB Losses%",
    "DEC Wins%", "DEC Losses%", "Head %", "Body %", "Legs %",
    "Control %", "Controlled %"
]

for col in percent_cols:
    df[col] = (df[col] * 100).round(1)

for col in ["Control Time (sec)", "Controlled Time (sec)", "Fight Time (sec)"]:
    df[col] = df[col].round(1)

# Αρχικοποίηση session_state
for key in ["f1", "f2", "page", "winner_ready"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "page" else "main"

# ------- ΚΥΡΙΑ ΣΕΛΙΔΑ --------
if st.session_state.page == "main":
    st.title("📊 MMA Fighter Comparison Tool")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.f1 = st.selectbox("🔎 Επιλογή Μαχητή 1", df["Fighter"], key="fighter1")
    with col2:
        st.session_state.f2 = st.selectbox("🔍 Επιλογή Μαχητή 2", df["Fighter"], key="fighter2")

    def show_stats(fighter_data):
        st.subheader(f"🧍 {fighter_data['Fighter']}")
        st.markdown("**__ΒΑΣΙΚΑ ΣΤΟΙΧΕΙΑ__**")
        st.markdown(f"- 👤 Ηλικία: {fighter_data['Age']}")
        st.markdown(f"- 📏 Ύψος: {fighter_data['Height']} cm")
        st.markdown(f"- 📐 Reach: {fighter_data['Reach']} cm")
        st.markdown(f"- 🔁 Streak: {fighter_data['Streak']}")

        st.markdown("**__ΣΤΑΤΙΣΤΙΚΑ KO / SUB / DEC__**")
        st.markdown(f"- 🥊 KO: {fighter_data['KO Wins%']}% νίκες / {fighter_data['KO Losses%']}% ήττες")
        st.markdown(f"- 🤼 SUB: {fighter_data['SUB Wins%']}% νίκες / {fighter_data['SUB Losses%']}% ήττες")
        st.markdown(f"- 🧾 DEC: {fighter_data['DEC Wins%']}% νίκες / {fighter_data['DEC Losses%']}% ήττες")

        st.markdown("**__SIGNIFICANT STRIKES__**")
        st.markdown(f"- 🎯 Landed: {fighter_data['Sig Strikes Landed']} ανά λεπτό")
        st.markdown(f"- 🛡️ Absorbed: {fighter_data['Sig Strikes Absorbed']} ανά λεπτό")
        st.markdown(f"- 🔥 Ποσοστά στόχων: Head: {fighter_data['Head %']}% | Body: {fighter_data['Body %']}% | Legs: {fighter_data['Legs %']}%")

        st.markdown("**__CONTROL STATS__**")
        st.markdown(f"- ⏱️ Control Time: {fighter_data['Control Time (sec)']} sec ({fighter_data['Control %']}%)")
        st.markdown(f"- ⛓️ Controlled Time: {fighter_data['Controlled Time (sec)']} sec ({fighter_data['Controlled %']}%)")

        st.markdown("**__FIGHT TIME__**")
        st.markdown(f"- ⌛ Μέση διάρκεια αγώνα: {fighter_data['Fight Time (sec)']} sec ({fighter_data['Fight Time (min)']} min)")

    col1, col2 = st.columns(2)
    f1_data = df[df["Fighter"] == st.session_state.f1].iloc[0]
    f2_data = df[df["Fighter"] == st.session_state.f2].iloc[0]

    with col1:
        show_stats(f1_data)
    with col2:
        show_stats(f2_data)

    if st.button("ΕΞΑΓΩΓΗ ΣΥΜΠΕΡΑΣΜΑΤΩΝ", use_container_width=True):
        st.session_state.page = "conclusion"
        st.rerun()

# ------- ΣΥΜΠΕΡΑΣΜΑΤΑ --------
elif st.session_state.page == "conclusion":
    # (Ο κώδικας για τα συμπεράσματα δεν αλλάζει εδώ)
    st.title("📋 Συμπεράσματα Μαχητών")
    # [...] (Το υπόλοιπο όπως ήδη το έχεις)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 ΕΠΙΣΤΡΟΦΗ"):
            st.session_state.page = "main"
            st.rerun()
    with col2:
        if st.button("🏆 ΕΞΑΓΩΓΗ ΝΙΚΗΤΗ"):
            st.session_state.page = "winner"
            st.session_state["winner_ready"] = True
            st.rerun()

# ------- ΝΙΚΗΤΗΣ --------
elif st.session_state.page == "winner" and st.session_state["winner_ready"]:
    f1 = df[df["Fighter"] == st.session_state["f1"]].iloc[0]
    f2 = df[df["Fighter"] == st.session_state["f2"]].iloc[0]

    def calc_score(f):
        if 28 <= f["Age"] <= 36:
            A = 5
        elif f["Age"] < 28:
            A = 3.5
        elif f["Age"] <= 38:
            A = 2.5
        else:
            A = 1.5

        B = min((f["Height"] - 165) / (200 - 165) * 5, 5)
        G = min(f["Sig Strikes Landed"] / 7 * 5, 5)
        D = max(5 - f["Sig Strikes Absorbed"], 1)
        E = min(f["Control %"] / 100 * 5, 5)
        Z = max(5 - f["Controlled %"] / 100 * 5, 1)
        H = min(f["KO Wins%"] / 100 * 5, 5)
        Th = min(f["SUB Wins%"] / 100 * 5, 5)
        I = min(f["DEC Wins%"] / 100 * 5, 5)
        streak_bonus = 0.18 * f.get("Streak", 0)

        return round((1.01*A + 1.2*B + 2.1*G + 2.1*D + 1.8*E + 1.8*Z + 0.33*H + 0.33*Th + 0.33*I + streak_bonus) / 5.5, 3)

    score1 = calc_score(f1)
    score2 = calc_score(f2)

    prob1 = round(score1 / (score1 + score2) * 100, 1)
    prob2 = round(score2 / (score1 + score2) * 100, 1)
    winner = f1["Fighter"] if score1 > score2 else f2["Fighter"]

    st.title("🏆 ΝΙΚΗΤΗΣ ΑΝΑΛΥΣΗΣ")
    st.markdown(f"<h1 style='text-align: center;'>🏆 {winner}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>({prob1}% vs {prob2}%)</h4>", unsafe_allow_html=True)

    if st.button("🔙 ΕΠΙΣΤΡΟΦΗ ΣΤΗΝ ΑΡΧΙΚΗ"):
        st.session_state.page = "main"
        st.rerun()
