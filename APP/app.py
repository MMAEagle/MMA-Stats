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
    "MMA WINS", "MMA LOSSES",
    "UFC WINS", "UFC LOSSES",
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

def calculate_finish_scores(f):
    mma_wins = f["MMA WINS"]
    mma_losses = f["MMA LOSSES"]
    ufc_wins = f["UFC WINS"]
    ufc_losses = f["UFC LOSSES"]
    
    ko_wins_pct = f["KO Wins%"] / 100
    ko_losses_pct = f["KO Losses%"] / 100
    sub_wins_pct = f["SUB Wins%"] / 100
    sub_losses_pct = f["SUB Losses%"] / 100

    # Avoid division by zero
    win_denom = 0.37 * (mma_wins - ufc_wins) + 0.63 * ufc_wins
    loss_denom = 0.45 * (mma_losses - ufc_losses) + 0.55 * ufc_losses

    ko_win_score = ko_wins_pct * ((0.37 * (mma_wins - ufc_wins) + 0.63 * (ufc_wins - 0.5)) / win_denom) if win_denom else 0
    ko_loss_score = ko_losses_pct * ((0.45 * (mma_losses - ufc_losses) + 0.55 * (ufc_losses - 0.15)) / loss_denom) if loss_denom else 0

    sub_win_score = sub_wins_pct * ((0.37 * (mma_wins - ufc_wins) + 0.63 * (ufc_wins - 0.5)) / win_denom) if win_denom else 0
    sub_loss_score = sub_losses_pct * ((0.45 * (mma_losses - ufc_losses) + 0.55 * (ufc_losses - 0.15)) / loss_denom) if loss_denom else 0

    dec_win_score = 1 - ko_win_score - sub_win_score
    dec_loss_score = 1 - ko_loss_score - sub_loss_score

    return {
        "KO Win Score": ko_win_score,
        "KO Loss Score": ko_loss_score,
        "SUB Win Score": sub_win_score,
        "SUB Loss Score": sub_loss_score,
        "DEC Win Score": dec_win_score,
        "DEC Loss Score": dec_loss_score
    }


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
    if "show_help" not in st.session_state:
        st.session_state.show_help = False

    
    st.title("📊 MMA Fighter Comparison Tool")

    help_col1, help_col2 = st.columns([10, 1])
    with help_col2:
        if st.button("❓", help="Οδηγίες Χρήσης", key="help_btn"):
            st.session_state.show_help = not st.session_state.get("show_help", False)


    if st.session_state.get("show_help", False):
        st.markdown("""
        <div style='
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin-top: 10px;
            border: 1px solid #555;
        '>
            <h4>📘 Οδηγίες Χρήσης</h4>
            <ul>
                <li>Επίλεξε δύο μαχητές από τα dropdown μενού.</li>
                <li>Δες συγκριτικά στατιστικά και λεπτομέρειες για τον κάθε μαχητή.</li>
                <li>Πάτησε <b>🏆 ΕΞΑΓΩΓΗ ΝΙΚΗΤΗ</b> για αυτόματη πρόβλεψη νικητή.</li>
                <li>Μπορείς να αποθηκεύσεις την πρόβλεψη ή να δημιουργήσεις παρολί.</li>
                <li>Χρησιμοποίησε το μενού πάνω δεξιά για να δεις ιστορικό ή συμπεράσματα.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)



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

        st.markdown("**__ΡΕΚΟΡ__**")
        st.markdown(f"- 🧾 **MMA Record:** ✅ {int(fighter_data['MMA WINS'])}  ❌ {int(fighter_data['MMA LOSSES'])}")
        st.markdown(f"- 🧾 **UFC Record:** ✅ {int(fighter_data['UFC WINS'])}  ❌ {int(fighter_data['UFC LOSSES'])}")


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
    
    if st.button("🏆 ΕΞΑΓΩΓΗ ΝΙΚΗΤΗ", use_container_width=True):
        st.session_state.winner_ready = True
        st.session_state.page = "winner"
        st.rerun()

    if st.button("📊 ΤΡΟΠΟΣ ΕΚΒΑΣΗΣ", use_container_width=True):
        st.session_state.page = "outcome"
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
        
    if st.button("ΕΞΑΓΩΓΗ ΣΥΜΠΕΡΑΣΜΑΤΩΝ", use_container_width=True):
        st.session_state.page = "conclusion"
        st.rerun()

# ------- ΣΥΜΠΕΡΑΣΜΑΤΑ --------
elif st.session_state.page == "conclusion":
    f1 = df[df["Fighter"] == st.session_state["f1"]].iloc[0]
    f2 = df[df["Fighter"] == st.session_state["f2"]].iloc[0]

    def conclusion_text(f1, f2):
        def age_comment(f1, f2):
            def age_statement(f):
                if f["Age"] < 28:
                    return f"Ο {f['Fighter']} είναι αρκετά νέος ⚠️"
                if f["Age"] >= 38:
                    return f"Ο {f['Fighter']} σίγουρα έχει περάσει την αγωνιστική του ακμή ❗"
                if f["Age"] >= 36:
                    return f"Ο {f['Fighter']} πλησιάζει την αγωνιστική κάμψη"
                return f"Ο {f['Fighter']} είναι σε καλή ηλικιακή φάση ✅"
            return "\n".join(["- " + age_statement(f1), "- " + age_statement(f2)])

        def height_comment(f1, f2):
            diff = abs(f1["Height"] - f2["Height"])
            if diff >= 5:
                taller = f1 if f1["Height"] > f2["Height"] else f2
                return f"- 📏 Ο {taller['Fighter']} έχει σαφές πλεονέκτημα ύψους ✅"
            return "- 📏 Δεν υπάρχει σημαντική διαφορά ύψους"

        def time_comment(f1, f2):
            if f1["Fight Time (min)"] < 10 and f2["Fight Time (min)"] < 10:
                return "- ⏱️ Και οι δύο τείνουν να τελειώνουν τους αγώνες τους νωρίς ❗"
            elif f1["Fight Time (min)"] < 10:
                return f"- ⏱️ Ο {f1['Fighter']} τελειώνει τους αγώνες του γρήγορα ⚠️"
            elif f2["Fight Time (min)"] < 10:
                return f"- ⏱️ Ο {f2['Fighter']} τελειώνει τους αγώνες του γρήγορα ⚠️"
            return "- 🧭 Δεν αναμένονται γρήγορες εξελίξεις στον αγώνα"

        def striking_comment(f1, f2):
            diff = abs(f1["Sig Strikes Landed"] - f2["Sig Strikes Landed"])
            if diff > 1.5:
                stronger = f1 if f1["Sig Strikes Landed"] > f2["Sig Strikes Landed"] else f2
                return f"- 🥊 Ο {stronger['Fighter']} έχει σημαντικό πλεονέκτημα στα σημαντικά χτυπήματα ✅"
            return "- 🥊 Παρόμοιος ρυθμός στα σημαντικά χτυπήματα"

        def zone_comment(f1, f2):
            comments = []
            for f in [f1, f2]:
                if f["Legs %"] > 20:
                    comments.append(f"- 👣 Ο {f['Fighter']} προτιμά leg kicks")
                if all(p > 15 for p in [f["Head %"], f["Body %"], f["Legs %"]]):
                    comments.append(f"- 🎯 Ο {f['Fighter']} έχει ολοκληρωμένο striking ✅")
            if not comments:
                comments.append("- ❔ Δεν διαφαίνεται προτίμηση σε συγκεκριμένες ζώνες")
            return "\n".join(comments)

        def control_comment(f1, f2):
            control_diff = abs(f1["Control %"] - f2["Control %"])
            controlled_diff = abs(f1["Controlled %"] - f2["Controlled %"])
            comments = []
            if control_diff > 10:
                fav = f1 if f1["Control %"] > f2["Control %"] else f2
                comments.append(f"- 🤼 Ο {fav['Fighter']} κυριαρχεί στο έδαφος ✅")
            if controlled_diff > 10:
                res = f1 if f1["Controlled %"] < f2["Controlled %"] else f2
                comments.append(f"- 🛡️ Ο {res['Fighter']} δύσκολα ελέγχεται από τους αντιπάλους του")
            if not comments:
                comments.append("- ⚖️ Δεν υπάρχει σαφής υπεροχή στον έλεγχο εδάφους")
            return "\n".join(comments)

        def method_comment(f1, f2):
            comments = []
            for f in [f1, f2]:
                if f["KO Wins%"] > 50:
                    comments.append(f"- 💥 Ο {f['Fighter']} είναι επικίνδυνος για νοκ άουτ ❗")
                if f["SUB Wins%"] > 50:
                    comments.append(f"- 🧷 Ο {f['Fighter']} μπορεί να τελειώσει τον αγώνα με υποταγή ⚠️")
                if f["DEC Wins%"] > 50:
                    comments.append(f"- 📝 Ο {f['Fighter']} έχει τάση να πηγαίνει σε απόφαση")
                if f["KO Losses%"] > 50:
                    comments.append(f"- 😵 Το σαγόνι του {f['Fighter']} είναι ευάλωτο σε KO")
                if f["SUB Losses%"] > 40:
                    comments.append(f"- 🔓 Ο {f['Fighter']} έχει αδυναμία στο έδαφος")
            if not comments:
                comments.append("- ⚖️ Δεν προκύπτει πλεονέκτημα σε μέθοδο νίκης")
            return "\n".join(comments)

        return (
            age_comment(f1, f2),
            height_comment(f1, f2),
            time_comment(f1, f2),
            striking_comment(f1, f2),
            zone_comment(f1, f2),
            control_comment(f1, f2),
            method_comment(f1, f2),
        )

    st.title("📋 Συμπεράσματα Μαχητών")
    age, height, time, striking, zones, control, method = conclusion_text(f1, f2)

    st.markdown("### 🧠 ΒΑΣΙΚΕΣ ΠΛΗΡΟΦΟΡΙΕΣ")
    st.markdown(age)
    st.markdown(height)
    st.markdown(time)

    st.markdown("### 🥊 STRIKING")
    st.markdown(striking)
    st.markdown(zones)

    st.markdown("### 🤼 WRESTLING")
    st.markdown(control)

    st.markdown("### 🧾 Μέθοδος Νίκης")
    st.markdown(method)

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

    # ➕ Δημιουργία Παρολί
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

    if st.button("📈 Υπολογισμός Value"):
        st.session_state.page = "value"
        st.rerun()

    if st.button("🔙 Επιστροφή στην αρχική"):
        st.session_state.page = "main"
        st.rerun()

    # ➕ Συνδυασμός Νικητή και Μεθόδου
    with st.expander("🎯 Συνδυασμός Νικητή και Μεθόδου"):
        selected_fighter = st.selectbox("👤 Επίλεξε Νικητή", [f1["Fighter"], f2["Fighter"]])
        method = st.radio("⚔️ Επιλογή Μεθόδου Νίκης", ["🥊 KO ή 🧠 Υποταγή", "⚖️ Απόφαση"])

        scores_f1 = calculate_finish_scores(f1)
        scores_f2 = calculate_finish_scores(f2)

        p_win_f1 = prob1 / 100
        p_win_f2 = prob2 / 100

        if selected_fighter == f1["Fighter"]:
            p_win = p_win_f1
            ko_sub_score = (
                scores_f1["KO Win Score"] + scores_f2["KO Loss Score"] +
                scores_f1["SUB Win Score"] + scores_f2["SUB Loss Score"]
            ) * 0.5
            dec_score = (
                scores_f1["DEC Win Score"] + scores_f2["DEC Loss Score"]
            ) * 0.5
        else:
            p_win = p_win_f2
            ko_sub_score = (
                scores_f2["KO Win Score"] + scores_f1["KO Loss Score"] +
                scores_f2["SUB Win Score"] + scores_f1["SUB Loss Score"]
            ) * 0.5
            dec_score = (
                scores_f2["DEC Win Score"] + scores_f1["DEC Loss Score"]
            ) * 0.5

        result_prob = p_win * ko_sub_score if method == "🥊 KO ή 🧠 Υποταγή" else p_win * dec_score

        st.markdown("---")
        st.markdown(f"### 📊 Πιθανότητα για **{selected_fighter}** να νικήσει με **{method}**:")
        st.markdown(f"<h2 style='text-align: center; color: green;'>{round(result_prob * 100, 2)}%</h2>", unsafe_allow_html=True)




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
  
    
    # Επιστροφή στην αρχική σελίδα
    if st.button("🔙 Επιστροφή στην αρχική"):
        st.session_state.page = "main"
        st.rerun()
# ----------------ΤΡΟΠΟΣ ΕΚΒΑΣΗΣ--------------

elif st.session_state["page"] == "outcome":
    st.title("🔎 Τρόπος Εκβασης Fight")

    f1 = st.session_state["f1"]
    f2 = st.session_state["f2"]

    if f1 is None or f2 is None:
        st.warning("Επίλεξε δύο μαχητές πρώτα.")
    else:
        fighter1 = df[df["Fighter"] == f1].iloc[0]
        fighter2 = df[df["Fighter"] == f2].iloc[0]

        cs1 = calc_custom_score(fighter1)
        cs2 = calc_custom_score(fighter2)

        finish_scores1 = calculate_finish_scores(fighter1)
        finish_scores2 = calculate_finish_scores(fighter2)

        P_KO = (cs1 * (0.5 * finish_scores1["KO Win Score"] + 0.5 * finish_scores2["KO Loss Score"]) + 
                cs2 * (0.5 * finish_scores2["KO Win Score"] + 0.5 * finish_scores1["KO Loss Score"])) / (cs1 + cs2)

        P_SUB = (cs1 * (0.5 * finish_scores1["SUB Win Score"] + 0.5 * finish_scores2["SUB Loss Score"]) + 
                 cs2 * (0.5 * finish_scores2["SUB Win Score"] + 0.5 * finish_scores1["SUB Loss Score"])) / (cs1 + cs2)

        P_DEC = 1 - P_KO - P_SUB

        # Αναλυτικές πιθανότητες
        st.markdown("### 🎯 <b>Αναλυτικές Πιθανότητες Τρόπου Εκβασης</b><br><br>", unsafe_allow_html=True)

        st.markdown(f"<p style='font-size:20px;'>🥊 <b>KO/TKO:</b> {round(P_KO*100, 1)}%</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:20px;'>🤼‍♂️ <b>Υποταγή:</b> {round(P_SUB*100, 1)}%</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:20px;'>📜 <b>Απόφαση:</b> {round(P_DEC*100, 1)}%</p>", unsafe_allow_html=True)

        # Νέο tab για value αποδόσεις
        with st.expander("📊 Value αποδόσεις"):
            if P_KO + P_SUB > 0:
                val_finish_odds = round(1 / (P_KO + P_SUB), 2)
            else:
                val_finish_odds = "—"

            if P_DEC > 0:
                val_decision_odds = round(1 / P_DEC, 2)
            else:
                val_decision_odds = "—"

            st.markdown(f"""
            <p style='font-size:17px;'>
            ✅ Ο αγώνας να <b>μην πάει σε απόφαση</b> αξίζει για απόδοση μεγαλύτερη του: <b>{val_finish_odds}</b><br>
            ✅ Ο αγώνας να <b>πάει σε απόφαση</b> αξίζει για απόδοση μεγαλύτερη του: <b>{val_decision_odds}</b>
            </p>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.button("🔙 Επιστροφή", on_click=lambda: st.session_state.update({"page": "main"}))
