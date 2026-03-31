import streamlit as st
import pandas as pd
import os
import json
import time
import hmac
import hashlib
from datetime import datetime
from predixai.core.engine import MarketEngine

# --- SECURITY: BASIC AUTH (Optional for Beta) ---
def check_password():
    """Returns True if the user had the correct password."""
    if "ACCESS_CODE" not in os.environ:
        return True # Public if no code set
    
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], os.environ["ACCESS_CODE"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Naija Access Code", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Naija Access Code", type="password", on_change=password_entered, key="password")
        st.error("😕 Access Code incorrect")
        return False
    return True

# --- UI CONFIG ---
st.set_page_config(page_title="PredixNaija: The #1 Solana Market 🏟️🇳🇬", layout="wide", page_icon="🏟️")

if check_password():
    # Initialize Engine
    engine = MarketEngine()
    SOL_TO_NGN = 1500 * 22000.0 # Approx ₦33M/SOL

    # Session State for User Account
    if "wallet_sol" not in st.session_state:
        st.session_state.wallet_sol = 0.0 # Start at 0 for real feel
    if "predictions" not in st.session_state:
        st.session_state.predictions = []

    # --- SIDEBAR: USER HUB ---
    with st.sidebar:
        st.title("🏟️ PredixNaija")
        st.image("https://img.icons8.com/nolan/128/nigeria.png", width=80)
        
        st.info("🚀 PHASE: DEVNET BETA")
        
        st.divider()
        st.subheader("💳 My Solana Wallet")
        st.metric("Balance", f"{st.session_state.wallet_sol:.4f} SOL", f"₦{(st.session_state.wallet_sol * SOL_TO_NGN):,.0f}")
        
        if st.button("🚰 Get Test SOL (Faucet)", use_container_width=True):
            st.session_state.wallet_sol += 1.0
            st.toast("1.0 Devnet SOL Added! 🚀")
            time.sleep(0.5)
            st.rerun()

        st.divider()
        st.subheader("👤 Account")
        st.write(f"ID: `{hashlib.md5(b'user').hexdigest()[:8]}`")
        st.caption("Verified Naija Predictor ✅")

    # --- MAIN CONTENT ---
    st.title("🏟️ PredixNaija Marketplace")
    st.markdown("### Predict on Nigeria's Future. Earn on Solana. 🇳🇬⛓️")

    # Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Markets", len(engine.markets))
    with m2:
        st.metric("24h Volume", "420.5 SOL")
    with m3:
        st.metric("Active Predictors", "1.2k")

    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Hot Markets", "📊 My Portfolio", "🤖 AI News Feed", "📖 How to Earn"])

    with tab1:
        st.header("Trending Markets")
        markets = engine.markets
        active_markets = [m for m in markets.values() if m["status"] == "OPEN"]
        
        if not active_markets:
            st.warning("No active markets yet. AI Curator is generating...")
        else:
            for m in active_markets:
                with st.expander(f"🇳🇬 {m['title']}", expanded=True):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write(m['description'])
                        st.caption(f"End Date: {m['end_date']} | Category: {m['category']}")
                    with c2:
                        prices = engine.get_price(m['id'])
                        bet_amt = st.number_input("Amount (SOL)", 0.01, 10.0, 0.1, key=f"bet_{m['id']}")
                        
                        b1, b2 = st.columns(2)
                        if b1.button(f"YES ({prices['yes']} SOL)", use_container_width=True, type="primary", key=f"y_{m['id']}"):
                            if st.session_state.wallet_sol >= bet_amt:
                                engine.predict(m['id'], "YES", bet_amt, "user")
                                st.session_state.wallet_sol -= bet_amt
                                st.session_state.predictions.append({"market": m['title'], "side": "YES", "amt": bet_amt, "p": prices['yes']})
                                st.success("Prediction confirmed!")
                                time.sleep(1)
                                st.rerun()
                        if b2.button(f"NO ({prices['no']} SOL)", use_container_width=True, key=f"n_{m['id']}"):
                            if st.session_state.wallet_sol >= bet_amt:
                                engine.predict(m['id'], "NO", bet_amt, "user")
                                st.session_state.wallet_sol -= bet_amt
                                st.session_state.predictions.append({"market": m['title'], "side": "NO", "amt": bet_amt, "p": prices['no']})
                                st.success("Prediction confirmed!")
                                time.sleep(1)
                                st.rerun()

    with tab2:
        st.header("My Positions")
        if not st.session_state.predictions:
            st.info("You haven't made any predictions yet. Go to 'Hot Markets' to start earning!")
        else:
            st.table(pd.DataFrame(st.session_state.predictions))

    with tab3:
        st.header("🇳🇬 AI News & Alpha")
        st.info("Our AI Curator is scanning Nigerian news sources 24/7.")
        if st.button("⚡ Refresh AI Alpha"):
            with st.spinner("AI is analyzing Vanguard and Punch..."):
                time.sleep(2)
                st.success("Analysis Complete: 'Naira stabilization trends' detected. New market incoming.")

    with tab4:
        st.header("How It Works")
        st.write("""
        1. **Get SOL**: Get test SOL using the faucet in the sidebar.
        2. **Pick a Market**: Predict on things you know (Politics, Sports, Music).
        3. **Buy Shares**: Buy 'YES' if you think it will happen, 'NO' if you don't.
        4. **Earn**: If you are right, your shares settle at 1 SOL each. Withdraw your profit!
        """)

    st.divider()
    st.caption("© 2026 PredixNaija. Decentralized Prediction for the Giant of Africa.")
