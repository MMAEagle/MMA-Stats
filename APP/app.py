import streamlit as st

if "page" not in st.session_state:
    st.session_state.page = "value"

if st.session_state.page == "value":
    st.title("📈 Υπολογισμός Value Bet")

    odds = st.number_input("Απόδοση", min_value=1.01, step=0.01)
    if st.button("📊 Υπολογισμός Value"):
        st.write("Υπολογισμός γίνεται...")

    if st.button("🔙 Επιστροφή"):
        st.session_state.page = "main"
        st.rerun()
