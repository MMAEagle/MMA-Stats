import streamlit as st
import pandas as pd
import re

# Ρύθμιση σελίδας
st.set_page_config(page_title="MMA Stats App", layout="wide")

# Ανάγνωση Excel
excel_file = "APP/002 Stats.xlsx"
sheet = "App"

custom_columns = [
    "Fighter", "Age", "Height", "Reach",
    "KO Wins%", "KO Losses%", "SUB Wins%", "SUB Losses%",
    "DEC Wins%", "DEC Losses%", "Sig Strikes Landed", "Sig Strikes Absorbed",
    "Head %", "Body %", "Legs %",
    "TD AVG", "TD ACC %", "TD DEF %",
    "Control Time (sec)", "Control %", "Controlled Time (sec)", "Controlled %",
    "Fight Time (sec)", "Streak"
]


df = pd.read_excel(excel_file, sheet_name=sheet, skiprows=2, header=None)
df = df.iloc[:, :len(custom_columns)]
df.columns = custom_columns
df = df.dropna(subset=["Fighter"])

# Ανάλυση streak
def parse_streak(val):
    if isinstance(val, str):
        match = re.match(r"([WL])(\d+)", val)
        if match:
            return int(match.group(2)) if match.group(1) == "W" else -int(match.group(2))
    return 0

df["Win Streak Numeric"] = df["Streak"].apply(parse_streak)
df["Fight Time (min)"] = (df["Fight Time (sec)"] / 60).round(1)

percent_cols = [
    "KO Wins%", "KO Losses%", "SUB Wins%", "SUB Losses%",
    "DEC Wins%", "DEC Losses%", "Head %", "Body %", "Legs %",
    "Control %", "Controlled %", "TD ACC %", "TD DEF %"
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

        st.markdown("**__TAKEDOWN ΣΤΑΤΙΣΤΙΚΑ__**")
        st.markdown(f"- 🎯 TD AVG: {fighter_data['TD AVG']} per 15 min")
        st.markdown(f"- 🎯 TD ACC: {fighter_data['TD ACC %']}%")
        st.markdown(f"- 🛡️ TD DEF: {fighter_data['TD DEF %']}%")


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

    def calc_custom_score(f):
        age = f["Age"]
        if 24 <= age <= 27 or 33 <= age <= 36: E = 3.5
        elif 28 <= age <= 32: E = 4
        elif age in [21, 22, 23, 37]: E = 2
        elif age in [18, 19, 20, 38]: E = 1
        elif 39 <= age <= 40: E = -1
        elif age >= 41: E = -2
        else: E = 0

        F = max(0, (f["Height"] - 155) * 0.12 + 1 if f["Height"] >= 155 else 0)
        G = max(0, (f["Reach"] - 155) * 0.14 + 1 if f["Reach"] >= 155 else 0)
        A = f["Sig Strikes Landed"]
        B = f["Sig Strikes Absorbed"]
        C = f["Control %"] / 100
        D = f["Controlled %"] / 100
        H = f["Win Streak Numeric"]
        I = f["KO Wins%"] / 100
        J = f["KO Losses%"] / 100
        K = f["SUB Wins%"] / 100
        L = f["SUB Losses%"] / 100
        M = f["DEC Wins%"] / 100
        N = f["DEC Losses%"] / 100
        O = f["TD ACC %"] / 100
        P = f["TD DEF %"] / 100
        Q = f["TD AVG"]


        return 10*(1.2*A - 0.9*B) + 30*(1.5*C - 1.3*D) + 0.65*(E + F + G) + 2*H + 15*(1.5*I + 0.85*K - 1.2*J - L) + 10*(1.5*M - 0.75*N)+ 10*Q*(1.25*O + 0.8*P)

    score1 = calc_custom_score(f1)
    score2 = calc_custom_score(f2)

    prob1 = round(score1 / (score1 + score2) * 100, 1)
    prob2 = round(score2 / (score1 + score2) * 100, 1)
    winner = f1["Fighter"] if score1 > score2 else f2["Fighter"]

    st.title("🏆 ΝΙΚΗΤΗΣ ΑΝΑΛΥΣΗΣ")
    st.markdown(f"<h1 style='text-align: center;'>🏆 {winner}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>({prob1}% vs {prob2}%)</h4>", unsafe_allow_html=True)

    if st.button("🔙 ΕΠΙΣΤΡΟΦΗ ΣΤΗΝ ΑΡΧΙΚΗ"):
        st.session_state.page = "main"
        st.rerun()

    if st.button("📈 Υπολογισμός Value"):
        st.session_state.page = "value"
        st.rerun()



   # ------- VALUE BET --------
elif st.session_state.page == "value":
    f1 = df[df["Fighter"] == st.session_state["f1"]].iloc[0]
    f2 = df[df["Fighter"] == st.session_state["f2"]].iloc[0]

    score1 = calc_custom_score(f1)
    score2 = calc_custom_score(f2)

    prob1 = round(score1 / (score1 + score2) * 100, 1)
    prob2 = round(score2 / (score1 + score2) * 100, 1)

    winner = f1 if score1 > score2 else f2
    loser = f2 if winner is f1 else f1
    winner_prob = prob1 if winner is f1 else prob2
    loser_prob = prob2 if winner is f1 else prob1

    st.title("📈 Υπολογισμός Value Bet")

    st.markdown(f"### 🏆 Πιθανότερος Νικητής: **{winner['Fighter']}** με {winner_prob}%")
    st.markdown(f"Αντίπαλος: **{loser['Fighter']}** με {loser_prob}%")

    col1, col2 = st.columns(2)

    with col1:
        odds_winner = st.number_input(f"🔢 Απόδοση για **{winner['Fighter']}**", min_value=1.01, step=0.01, format="%.2f")
    with col2:
        odds_loser = st.number_input(f"🔢 Απόδοση για **{loser['Fighter']}**", min_value=1.01, step=0.01, format="%.2f")

    if st.button("📊 Υπολογισμός Value", use_container_width=True):
        # Υπολογισμός EV και για τους δύο
        def calculate_ev(p, odds):
            q = 1 - p
            K = odds - 1
            L = 1
            return round(p * K - q * L, 3)

        p_win = winner_prob / 100
        p_lose = loser_prob / 100

        ev_winner = calculate_ev(p_win, odds_winner)
        ev_loser = calculate_ev(p_lose, odds_loser)

        st.markdown(f"#### 🧮 Υπολογισμένο EV για {winner['Fighter']}: `{ev_winner}`")
        st.markdown(f"#### 🧮 Υπολογισμένο EV για {loser['Fighter']}: `{ev_loser}`")

        if ev_winner > ev_loser and ev_winner > 0:
            st.success(f"✅ Η καλύτερη επιλογή είναι ο **{winner['Fighter']}**, έχει μεγαλύτερο value.")
        elif ev_loser > ev_winner and ev_loser > 0:
            st.success(f"✅ Η καλύτερη επιλογή είναι ο **{loser['Fighter']}**, έχει μεγαλύτερο value.")
        elif ev_winner < 0 and ev_loser < 0:
            st.error("❌ Καμία απόδοση δεν παρουσιάζει θετικό value. Απόφυγε το στοίχημα.")
        else:
            st.info("ℹ️ Υπάρχει θετικό value αλλά όχι ξεκάθαρο πλεονέκτημα. Προσοχή στην επιλογή.")

    if st.button("🔙 Επιστροφή στην αρχική"):
        st.session_state.page = "main"
        st.rerun()
