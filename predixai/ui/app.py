import streamlit as st
import pandas as pd
import os
import json
import time
from datetime import datetime
from predixai.core.engine import MarketEngine

# Configuration
st.set_page_config(page_title="PredixNaija: Devnet Beta 🏟️🇳🇬", layout="wide", page_icon="🏟️")

# Initialize Engine
engine = MarketEngine()

# DEVNET STATUS
st.sidebar.warning("⚠️ PHASE: DEVNET BETA (Testing Only)")
st.sidebar.info("Predict with TEST SOL - No Real Money.")

# NGN/SOL Rate (Stub - Updated to reflect real-time approx for ₦)
SOL_TO_NGN = 22000.0 * 1500.0 # ~₦33,000,000 per SOL (based on market)

# Simulated Wallet (In production, this would be a real Solana wallet)
if "wallet_sol" not in st.session_state:
    st.session_state.wallet_sol = 5.0 # 5.0 SOL
if "predictions" not in st.session_state:
    st.session_state.predictions = []

# Sidebar Navigation
with st.sidebar:
    st.title("🏟️ PredixNaija")
    st.image("https://img.icons8.com/nolan/128/nigeria.png", width=100)
    st.divider()
    
    # Wallet Info
    st.metric("SOL Balance", f"{st.session_state.wallet_sol:.2f} SOL", 
              f"₦{(st.session_state.wallet_sol * SOL_TO_NGN):,.0f} NGN")
    
    st.divider()
    st.subheader("Your Naija Profile")
    st.write("Mavitan CEO 🇳🇬")
    st.caption("Solana Whale 🐋")
    st.divider()
    if st.button("🔌 Connect Phantom / Solflare", use_container_width=True):
        st.success("Wallet connected via Solana Mainnet.")

# Main Dashboard
st.title("⛓️ PredixNaija: Predict on Local Events")
st.caption("AI-powered prediction platform for Nigerians. Predict on Politics, Sports, and Culture.")

# 1. Platform Tabs
tab_browse, tab_my, tab_create = st.tabs(["🔍 Browse Naija Markets", "📉 My Positions", "🤖 Naija Curator"])

# Tab 1: Browse Markets
with tab_browse:
    st.header("What's Trending in Nigeria?")
    
    # Filter by Category
    category = st.radio("Category", ["All", "Naija Politics", "NPFL/Sports", "Entertainment", "Economy"], horizontal=True)
    
    # Load markets from Engine
    markets = engine.markets
    active_markets = [m for m in markets.values() if m["status"] == "OPEN"]
    
    if not active_markets:
        st.info("No active markets. The Curator is scanning Punch and Vanguard...")
    else:
        # Display as grid
        cols = st.columns(2)
        for i, m in enumerate(active_markets):
            with cols[i % 2]:
                with st.container(border=True):
                    st.subheader(f"{m['title']} 🇳🇬")
                    st.write(m['description'])
                    st.caption(f"Resolution Date: {m['end_date']}")
                    
                    prices = engine.get_price(m['id'])
                    
                    # Columns for Yes/No prices in SOL
                    p1, p2 = st.columns(2)
                    with p1:
                        st.metric("YES Price", f"{prices['yes']:.2f} SOL", 
                                  f"₦{(prices['yes'] * SOL_TO_NGN):,.0f}")
                    with p2:
                        st.metric("NO Price", f"{prices['no']:.2f} SOL", 
                                  f"₦{(prices['no'] * SOL_TO_NGN):,.0f}", delta_color="inverse")
                    
                    # Prediction Actions
                    bet_amount = st.number_input(f"Bet Amount (SOL) for {m['id']}", 0.1, step=0.1, key=f"amt_{m['id']}")
                    col_b1, col_b2 = st.columns(2)
                    
                    with col_b1:
                        if st.button(f"Naija YES on {m['id']}", type="primary", use_container_width=True):
                            if st.session_state.wallet_sol >= bet_amount:
                                engine.predict(m['id'], "YES", bet_amount, "user_1")
                                st.session_state.wallet_sol -= bet_amount
                                st.session_state.predictions.append({
                                    "market": m['title'],
                                    "side": "YES",
                                    "amount_sol": bet_amount,
                                    "entry_sol": prices['yes'],
                                    "time": datetime.now().strftime("%H:%M:%S")
                                })
                                st.success("Prediction Placed on Solana! 🚀")
                                st.rerun()
                                
                    with col_b2:
                        if st.button(f"Naija NO on {m['id']}", use_container_width=True):
                            if st.session_state.wallet_sol >= bet_amount:
                                engine.predict(m['id'], "NO", bet_amount, "user_1")
                                st.session_state.wallet_sol -= bet_amount
                                st.session_state.predictions.append({
                                    "market": m['title'],
                                    "side": "NO",
                                    "amount_sol": bet_amount,
                                    "entry_sol": prices['no'],
                                    "time": datetime.now().strftime("%H:%M:%S")
                                })
                                st.success("Prediction Placed on Solana! 🚀")
                                st.rerun()

# Tab 2: My Predictions
with tab_my:
    st.header("My Portfolio & Solana Earnings")
    if not st.session_state.predictions:
        st.write("No active predictions in your portfolio.")
    else:
        df_p = pd.DataFrame(st.session_state.predictions)
        st.table(df_p)

# Tab 3: Naija Market Curator
with tab_create:
    st.header("🇳🇬 Naija AI Curator")
    st.write("Automated discovery of Nigerian trending topics to build new markets.")
    
    if st.button("🇳🇬 Run Naija News Discovery", type="primary"):
        with st.status("AI Agent is scanning Punch, Vanguard, and Linda Ikeji..."):
            st.write("Analyzing Groq context for 'Nigeria Trends'...")
            time.sleep(2)
            
            # Simulated Naija-centric Markets
            naija_market = {
                "title": "Will the Naira reach ₦1,400 per 1$ by June 2026?",
                "category": "Economy",
                "description": "Analyzing current inflation and CBN policies to predict the exchange rate.",
                "end_date": "2026-06-30"
            }
            
            st.success("New Naija Market Found!")
            st.json(naija_market)
            
            if st.button("🇳🇬 Deploy Market to Solana Marketplace"):
                mid = engine.create_market(naija_market['title'], naija_market['category'], naija_market['description'], naija_market['end_date'])
                st.success(f"Naija Market Live! (ID: {mid})")
                st.rerun()

# 4. Global Footer
st.divider()
st.caption("PredixNaija © 2026. Built on Solana for Nigerians. Powered by Mavitan AI.")
