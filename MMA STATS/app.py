import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth

# ----- LOGIN -----
names = ["MMAEagle81"]
usernames = ["MMAEagle81"]
passwords = ["MMAEagle"]

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names=names,
    usernames=usernames,
    passwords=hashed_passwords,
    cookie_name="mma_stats_app",
    key="auth",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Σύνδεση", "main")

if authentication_status is False:
    st.error("Λάθος όνομα χρήστη ή κωδικός.")
elif authentication_status is None:
    st.warning("Παρακαλώ εισάγετε τα στοιχεία σας.")
elif authentication_status:
    st.set_page_config(page_title="MMA Stats App", layout="wide")

    excel_file = "MMA STATS/002 Stats.xlsx"
    sheet = "App"

    custom_columns = [
        "Fighter", "Age", "Height", "Reach",
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

    for key in ["f1", "f2", "page", "winner_ready"]:
        if key not in st.session_state:
            st.session_state[key] = None if key != "page" else "main"

    if st.session_state.page == "main":
        st.title("📊 MMA Fighter Comparison Tool")

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.f1 = st.selectbox("🔎 Επιλογή Μαχητή 1", df["Fighter"], key="fighter1")
        with col2:
            st.session_state.f2 = st.selectbox("🔍 Επιλογή Μαχητή 2", df["Fighter"], key="fighter2")

        def show_stats(fighter_data):
            st.subheader(f"🡭 {fighter_data['Fighter']}")
            st.markdown("**__ΒΑΣΙΚΑ ΣΤΟΙΧΕΙΑ__**")
            st.markdown(f"- 👤 Ηλικία: {fighter_data['Age']}")
            st.markdown(f"- 📏 Ύψος: {fighter_data['Height']} cm")
            st.markdown(f"- 🖐️ Reach: {fighter_data['Reach']} cm")

            st.markdown("**__ΣΤΑΤΙΣΤΙΚΑ KO / SUB / DEC__**")
            st.markdown(f"- 🥊 KO: {fighter_data['KO Wins%']}% νίκες / {fighter_data['KO Losses%']}% ήττες")
            st.markdown(f"- 🦼 SUB: {fighter_data['SUB Wins%']}% νίκες / {fighter_data['SUB Losses%']}% ήττες")
            st.markdown(f"- 🧰 DEC: {fighter_data['DEC Wins%']}% νίκες / {fighter_data['DEC Losses%']}% ήττες")

            st.markdown("**__SIGNIFICANT STRIKES__**")
            st.markdown(f"- 🌟 Landed: {fighter_data['Sig Strikes Landed']} ανά λεπτό")
            st.markdown(f"- 🛡️ Absorbed: {fighter_data['Sig Strikes Absorbed']} ανά λεπτό")
            st.markdown(f"- 🔥 Στόχοι: Head: {fighter_data['Head %']}% | Body: {fighter_data['Body %']}% | Legs: {fighter_data['Legs %']}%")

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

    elif st.session_state.page == "conclusion":
        st.title("Κρίσιμος Νικητής")
        st.success(f"Εσύκρινη σύγκριση: {st.session_state.f1} και {st.session_state.f2}")
        if st.button("ΕΠΙΣΤΡΟΦΗ ΕΝΑ Σύγκριση", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()

        st.markdown("""
        Χρησιμοποιείτε τα στατιστικά και τα δεδομένα κάθε τη σύγκριση σας.
        Εξετάστε την επίλογη σας για ανάλυση!
        """)