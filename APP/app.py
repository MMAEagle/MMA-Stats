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

if "multi_fights" not in st.session_state:
    st.session_state.multi_fights = []

if "parlay_probs" not in st.session_state:
    st.session_state.parlay_probs = []

if "current_pair" not in st.session_state:
    st.session_state.current_pair = {"f1": None, "f2": None}


# ------- ΚΥΡΙΑ ΣΕΛΙΔΑ --------
if st.session_state.page == "main":
    st.title("📊 MMA Fighter Comparison Tool")

        # Κουμπί Ιστορικού Προβλέψεων (πάνω δεξιά)
    top_col1, top_col2 = st.columns([8, 2])
    with top_col2:
        if st.button("📜 Δες ιστορικό προβλέψεων"):
            st.session_state.page = "history"
            st.rerun()
#----------------------------------------------
    
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

    if st.button("🏆 ΕΞΑΓΩΓΗ ΝΙΚΗΤΗ", use_container_width=True):
        st.session_state.winner_ready = True
        st.session_state.page = "winner"
        st.rerun()
        
    if st.button("➕ ΔΗΜΙΟΥΡΓΙΑ ΠΑΡΟΛΙ", use_container_width=True):
        f1 = df[df["Fighter"] == st.session_state.f1].iloc[0]
        f2 = df[df["Fighter"] == st.session_state.f2].iloc[0]
        score1 = calc_custom_score(f1)
        score2 = calc_custom_score(f2)
        prob1 = round(score1 / (score1 + score2) * 100, 1)
        prob2 = round(score2 / (score1 + score2) * 100, 1)
        winner = f1["Fighter"] if score1 > score2 else f2["Fighter"]
        prob = prob1 if winner == f1["Fighter"] else prob2

        st.session_state.multi_fights.append({
            "f1": f1["Fighter"],
            "f2": f2["Fighter"],
            "winner": winner,
            "prob": prob
        })
        st.session_state.page = "multi_fight"
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

    score1 = calc_custom_score(f1)
    score2 = calc_custom_score(f2)

    prob1 = round(score1 / (score1 + score2) * 100, 1)
    prob2 = round(score2 / (score1 + score2) * 100, 1)
    winner = f1["Fighter"] if score1 > score2 else f2["Fighter"]

    st.title("🏆 ΝΙΚΗΤΗΣ ΑΝΑΛΥΣΗΣ")
    st.markdown(f"<h1 style='text-align: center;'>🏆 {winner}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>({prob1}% vs {prob2}%)</h4>", unsafe_allow_html=True)

    if len(st.session_state.multi_fights) < 5:
        if st.button("➕ ΔΗΜΙΟΥΡΓΙΑ ΠΑΡΟΛΙ"):
            st.session_state.multi_fights.append({
                "f1": st.session_state["f1"],
                "f2": st.session_state["f2"],
                "winner": winner,
                "prob": prob1 if winner == f1["Fighter"] else prob2
            })
            st.session_state.page = "multi_fight"
            st.rerun()


    if st.button("🔙 ΕΠΙΣΤΡΟΦΗ ΣΤΗΝ ΑΡΧΙΚΗ"):
        st.session_state.page = "main"
        st.rerun()

    if st.button("📈 Υπολογισμός Value"):
        st.session_state.page = "value"
        st.rerun()

#-------Παρολι--------
elif st.session_state.page == "multi_fight":
    st.title("📋 Νέο Fight για Παρολί")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.current_pair["f1"] = st.selectbox("🧍 Μαχητής 1", df["Fighter"], key="mf_f1")
    with col2:
        st.session_state.current_pair["f2"] = st.selectbox("🧍 Μαχητής 2", df["Fighter"], key="mf_f2")

    if st.session_state.current_pair["f1"] == st.session_state.current_pair["f2"]:
        st.warning("⚠️ Οι δύο μαχητές πρέπει να είναι διαφορετικοί.")
    else:
        if st.button("🧾 ΠΡΟΣΘΗΚΗ ΣΤΟ ΠΑΡΟΛΙ"):
            f1 = df[df["Fighter"] == st.session_state.current_pair["f1"]].iloc[0]
            f2 = df[df["Fighter"] == st.session_state.current_pair["f2"]].iloc[0]
            score1 = calc_custom_score(f1)
            score2 = calc_custom_score(f2)
            prob1 = round(score1 / (score1 + score2) * 100, 1)
            prob2 = round(score2 / (score1 + score2) * 100, 1)
            winner = f1["Fighter"] if score1 > score2 else f2["Fighter"]
            prob = prob1 if winner == f1["Fighter"] else prob2
    
            st.session_state.multi_fights.append({
                "f1": f1["Fighter"],
                "f2": f2["Fighter"],
                "winner": winner,
                "prob": prob
            })
    
            st.success(f"✅ Προστέθηκε: {winner} ({prob}%)")


    if st.session_state.multi_fights:
        st.markdown("### 🧾 Προβλέψεις Παρολί")
        total_prob = 1
        for idx, fight in enumerate(st.session_state.multi_fights, 1):
            st.markdown(f"**{idx}. {fight['f1']} vs {fight['f2']} → 🏆 {fight['winner']} ({fight['prob']}%)**")
            total_prob *= (fight["prob"] / 100)

        st.markdown(f'## 🔢 Συνολικό Παρολί: **{total_prob_percent}%** ' +
            f'<span title="Αν η απόδοση του παρολί είναι μεγαλύτερη από αυτήν, θεωρείται ότι έχει value.">💡</span>' +
            f' → Value αν απόδοση > **{fair_odds}**',
            unsafe_allow_html=True)


    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 Επιστροφή στην αρχική"):
            st.session_state.page = "main"
            st.rerun()
    with col2:
        if st.button("🧹 Καθαρισμός Παρολί"):
            st.session_state.multi_fights = []
            st.rerun()


   # ------- VALUE BET --------
elif st.session_state.page == "value":

    #
    # Λήψη δεδομένων για τους μαχητές
    fighter1 = df[df["Fighter"] == st.session_state["f1"]].iloc[0]
    fighter2 = df[df["Fighter"] == st.session_state["f2"]].iloc[0]

    # Υπολογισμός σκορ
    score1 = calc_custom_score(fighter1)
    score2 = calc_custom_score(fighter2)

    # Υπολογισμός πιθανοτήτων
    total_score = score1 + score2
    prob1 = round(score1 / total_score * 100, 1)
    prob2 = round(score2 / total_score * 100, 1)

    # Καθορισμός νικητή/ηττημένου
    if score1 > score2:
        winner, loser = fighter1, fighter2
        winner_prob, loser_prob = prob1, prob2
    else:
        winner, loser = fighter2, fighter1
        winner_prob, loser_prob = prob2, prob1

    st.title("📈 Υπολογισμός Value Bet")
    st.markdown(f"### 🏆 Πιθανότερος Νικητής: **{winner['Fighter']}** με {winner_prob}%")
    st.markdown(f"Αντίπαλος: **{loser['Fighter']}** με {loser_prob}%")

    # Εισαγωγή αποδόσεων
    col1, col2 = st.columns(2)
    with col1:
        odds_winner = st.number_input(f"🔢 Απόδοση για **{winner['Fighter']}**", min_value=1.01, step=0.01, format="%.2f")
    with col2:
        odds_loser = st.number_input(f"🔢 Απόδοση για **{loser['Fighter']}**", min_value=1.01, step=0.01, format="%.2f")

    # Υπολογισμός value bet
    if st.button("📊 Υπολογισμός Value", use_container_width=True):

        def calculate_ev(p, odds):
            return round(p * (odds - 1) - (1 - p), 3)

        ev_win = calculate_ev(winner_prob / 100, odds_winner)
        ev_lose = calculate_ev(loser_prob / 100, odds_loser)

        st.markdown(f"#### 🧮 Δείκτης Value για {winner['Fighter']}: `{ev_win}`")
        st.markdown(f"#### 🧮 Δείκτης Value για {loser['Fighter']}: `{ev_lose}`")

        # Προτάσεις βάσει EV
        if ev_win > ev_lose and ev_win > 0:
            st.success(f"✅ Η καλύτερη επιλογή είναι ο **{winner['Fighter']}**, έχει μεγαλύτερο value.")
        elif ev_lose > ev_win and ev_lose > 0:
            st.success(f"✅ Η καλύτερη επιλογή είναι ο **{loser['Fighter']}**, έχει μεγαλύτερο value.")
        elif ev_win < 0 and ev_lose < 0:
            st.error("❌ Καμία απόδοση δεν παρουσιάζει θετικό value. Απόφυγε το στοίχημα.")
        else:
            st.info("ℹ️ Υπάρχει θετικό value αλλά όχι ξεκάθαρο πλεονέκτημα. Προσοχή στην επιλογή.")

    # Επιστροφή στην αρχική σελίδα
    if st.button("🔙 Επιστροφή στην αρχική"):
        st.session_state.page = "main"
        st.rerun()

# ------- ΙΣΤΟΡΙΚΟ ΠΡΟΒΛΕΨΕΩΝ --------
elif st.session_state.page == "history":
    st.title("📜 Ιστορικό Προβλέψεων")

    import os
    import pandas as pd

    history_folder = "APP"
    history_files = [f for f in os.listdir(history_folder) if f.endswith(".xlsx") and f != "002 Stats.xlsx"]

    if not history_files:
        st.info("Δεν υπάρχουν αποθηκευμένες προβλέψεις.")
    else:
        for file in history_files:
            with st.expander(f"📄 {file}"):
                file_path = os.path.join(history_folder, file)
                try:
                    hist_df = pd.read_excel(file_path)
                    required_cols = ["Fighter 1", "Fighter 2", "Prediction", "Winner"]
                    if set(required_cols).issubset(hist_df.columns):
                        
                        # Προσθήκη στήλης με ✔️ ή ❌
                        hist_df["✅"] = hist_df.apply(
                            lambda row: "✔️" if row["Prediction"] == row["Winner"] else "❌", axis=1
                        )

                        # Εμφάνιση πίνακα
                        st.dataframe(hist_df)

                        # Υπολογισμός ποσοστού επιτυχίας
                        correct = (hist_df["Prediction"] == hist_df["Winner"]).sum()
                        total = len(hist_df)
                        accuracy = correct / total * 100 if total > 0 else 0
                        st.markdown(f"**🎯 Ποσοστό επιτυχίας:** `{accuracy:.2f}%`")
                    else:
                        st.warning(f"Το αρχείο '{file}' δεν έχει τη σωστή μορφή.")
                except Exception as e:
                    st.error(f"Σφάλμα στο άνοιγμα του αρχείου '{file}': {e}")

    if st.button("🔙 Επιστροφή"):
        st.session_state.page = "main"
        st.rerun()
