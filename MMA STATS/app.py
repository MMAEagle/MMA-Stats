import streamlit as st
import pandas as pd

# Ρύθμιση σελίδας
st.set_page_config(page_title="MMA Stats App", layout="wide")

# Ανάγνωση Excel
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
    f1 = df[df["Fighter"] == st.session_state["f1"]].iloc[0]
    f2 = df[df["Fighter"] == st.session_state["f2"]].iloc[0]

    def conclusion_text(f1, f2):
        def age_comment(age):
            if age < 28: return "αρκετά νέος και σίγουρα του λείπει η εμπειρία"
            if age >= 38: return "σίγουρα τα καλύτερά του χρόνια έχουν περάσει"
            if age >= 36: return "πλησιάζει την κάμψη από πλευράς ηλικίας"
            return "σε πολύ καλό ηλικιακό σημείο"
        
        p1 = f"{f1['Fighter']} είναι {age_comment(f1['Age'])}, ενώ ο {f2['Fighter']} είναι {age_comment(f2['Age'])}."
        height_comment = f"{f1['Fighter']} πλεονεκτεί σε ύψος." if f1['Height'] > f2['Height'] else f"{f2['Fighter']} πλεονεκτεί σε ύψος."
        time_comment = ""
        if f1["Fight Time (min)"] < 10 and f2["Fight Time (min)"] < 10:
            time_comment = "Δύσκολα θα δούμε τον αγώνα να πηγαίνει στους κριτές."
        elif f1["Fight Time (min)"] < 10:
            time_comment = f"{f1['Fighter']} είναι πολύ επικίνδυνος και τελειώνει γρήγορα τους αγώνες."
        elif f2["Fight Time (min)"] < 10:
            time_comment = f"{f2['Fighter']} είναι πολύ επικίνδυνος και τελειώνει γρήγορα τους αγώνες."

        striker = f1 if f1["Sig Strikes Landed"] > f2["Sig Strikes Landed"] else f2
        striking_comment = f"Ο {striker['Fighter']} φαίνεται να υπερτερεί στο striking."
        if striker["Sig Strikes Landed"] > 5:
            striking_comment += " Έχει υπερβολικά καλό ρυθμό."
        if striker["Sig Strikes Landed"] < 3:
            striking_comment += " Είναι ξεκάθαρο ότι μειονεκτεί στο striking."
        dist1 = [f1["Head %"], f1["Body %"], f1["Legs %"]]
        dist2 = [f2["Head %"], f2["Body %"], f2["Legs %"]]
        zone_comment = ""
        for f in [f1, f2]:
            if f["Legs %"] > 20:
                zone_comment += f"Ο {f['Fighter']} προτιμάει leg kicks. "
            if all(p > 15 for p in [f["Head %"], f["Body %"], f["Legs %"]]):
                zone_comment += f"Ο {f['Fighter']} έχει ολοκληρωμένο striking. "

        c_comment = ""
        control_fav = f1 if f1["Control %"] > f2["Control %"] else f2
        c_comment += f"{control_fav['Fighter']} κυριαρχεί στο έδαφος. "
        controlled_less = f1 if f1["Controlled %"] < f2["Controlled %"] else f2
        c_comment += f"{controlled_less['Fighter']} δεν αφήνει τους αντιπάλους να τον ελέγξουν. "

        method_comment = ""
        for f in [f1, f2]:
            if f["KO Wins%"] > 50:
                method_comment += f"Ο {f['Fighter']} είναι πολύ επικίνδυνος για νοκ άουτ. "
            if f["SUB Wins%"] > 40:
                method_comment += f"Ο {f['Fighter']} μπορεί να τελειώσει τον αγώνα με υποταγή ανά πάσα στιγμή. "
            if f["DEC Wins%"] > 50:
                method_comment += f"Ο {f['Fighter']} συνήθως πάει σε απόφαση. "
            if f["KO Losses%"] > 50:
                method_comment += f"Το σαγόνι του {f['Fighter']} δεν είναι το πιο δυνατό. "
            if f["SUB Losses%"] > 40:
                method_comment += f"Ο {f['Fighter']} έχει σοβαρή αδυναμία στο έδαφος. "

        return p1 + " " + height_comment + " " + time_comment, striking_comment + " " + zone_comment, c_comment, method_comment

    st.title("📋 Συμπεράσματα Μαχητών")
    bp, stg, wrest, meth = conclusion_text(f1, f2)

    st.markdown("### 🧠 ΒΑΣΙΚΕΣ ΠΛΗΡΟΦΟΡΙΕΣ")
    st.write(bp)
    st.markdown("### 🥊 STRIKING")
    st.write(stg)
    st.markdown("### 🤼 WRESTLING")
    st.write(wrest)
    st.markdown("### 🧾 Μέθοδος Νίκης")
    st.write(meth)

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
        A = 5 if 28 <= f["Age"] <= 36 else (3 if f["Age"] < 27 else (1.5 if f["Age"] > 38 else 2.5))
        B = 5 if f["Height"] > f2["Height"] else 4
        G = 5 if f["Sig Strikes Landed"] > f2["Sig Strikes Landed"] else 3
        D = 5 if f["Sig Strikes Absorbed"] < f2["Sig Strikes Absorbed"] else 3
        E = 5 if f["Control %"] > f2["Control %"] else 3
        Z = 5 if f["Controlled %"] < f2["Controlled %"] else 3
        H = 5 if f["KO Wins%"] > f2["KO Wins%"] else 4.5
        Th = 5 if f["SUB Wins%"] > f2["SUB Wins%"] else 4.5
        I = 5 if f["DEC Wins%"] > f2["DEC Wins%"] else 4.5
        return (1.01*A + 1.2*B + 2.1*G + 2.1*D + 1.8*E + 1.8*Z + 0.33*H + 0.33*Th + 0.33*I) / 5.5

    score1 = calc_score(f1)
    score2 = calc_score(f2)

    winner = f1["Fighter"] if score1 > score2 else f2["Fighter"]
    prob1 = round(score1 / (score1 + score2) * 100, 1)
    prob2 = round(score2 / (score1 + score2) * 100, 1)

    st.title("🏆 ΝΙΚΗΤΗΣ ΑΝΑΛΥΣΗΣ")
    st.markdown(f"<h1 style='text-align: center;'>🏆 {winner}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>({prob1}% vs {prob2}%)</h4>", unsafe_allow_html=True)

    # ✅ Προσθήκη κουμπιού επιστροφής στην αρχική
    if st.button("🔙 ΕΠΙΣΤΡΟΦΗ ΣΤΗΝ ΑΡΧΙΚΗ"):
        st.session_state.page = "main"
        st.rerun()
