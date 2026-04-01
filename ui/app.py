import streamlit as st
import pandas as pd
import os
import json
import time
import hashlib
from datetime import datetime
from core.engine import MarketEngine
from utils.wallet import solana_connect_button

# --- APP CONFIG & STYLING ---
st.set_page_config(
    page_title="PredixNaija | Predict & Earn on Solana",
    layout="wide",
    page_icon="🏗️",
    initial_sidebar_state="collapsed"
)

# Check for URL parameters (Wallet Bridge)
if "wallet" in st.query_params:
    st.session_state.wallet_address = st.query_params["wallet"]
    # Clear parameter to prevent loop, but stay on page
    # st.query_params.clear() # Optional

# Kalshi-inspired Minimalist Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Header Styling */
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #F0F0F0;
        margin-bottom: 2rem;
    }
    
    .logo {
        font-size: 1.5rem;
        font-weight: 800;
        color: #000000;
        text-decoration: none;
    }
    
    /* Market Card Styling */
    .market-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 1.5rem;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    .market-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    
    .market-category {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #888888;
        letter-spacing: 0.05rem;
    }
    
    .market-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: #000000;
    }
    
    .price-container {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .price-btn {
        flex: 1;
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .btn-yes { background-color: #E6F4EA; color: #1E8E3E; }
    .btn-no { background-color: #FCE8E6; color: #D93025; }
    
    /* Wallet Badge */
    .wallet-badge {
        background: #F8F9FA;
        border: 1px solid #E0E0E0;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZATION ---
engine = MarketEngine()

if "wallet_address" not in st.session_state:
    st.session_state.wallet_address = None

# --- AUTH LAYER (Wallet Connection) ---
def connect_wallet():
    with st.container():
        st.markdown("<div style='text-align: center; padding: 100px 0;'>", unsafe_allow_html=True)
        st.markdown("<h1>🏗️ PredixNaija</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666;'>Predict on Nigeria's Future. Earn on Solana.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Real Wallet Signing Component
        solana_connect_button()
        
        st.markdown("<p style='font-size: 0.8rem; color: #BBB;'>Trusted by 5k+ Naija Predictors</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- MAIN APP INTERFACE ---
if not st.session_state.wallet_address:
    connect_wallet()
else:
    # Ensure user is registered in engine
    engine.register_user(st.session_state.wallet_address)
    
    # Header
    st.markdown(f"""
        <div class='main-header'>
            <div class='logo'>🏗️ PredixNaija</div>
            <div class='wallet-badge'>
                🏦 {st.session_state.wallet_address[:4]}...{st.session_state.wallet_address[-4:]} | 0.00 SOL
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Search & Filter
    c1, c2 = st.columns([3, 1])
    search = c1.text_input("Search events", placeholder="Elections, Sports, Economy...", label_visibility="collapsed")
    filter_cat = c2.selectbox("Category", ["All", "Politics", "Economy", "Sports", "Music"], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    # Market Grid
    markets = engine.markets
    active_markets = [m for m in markets.values() if m["status"] == "OPEN"]
    
    if not active_markets:
        st.info("The AI Curator is currently drafting new markets. Check back in 5 mins.")
    else:
        # Categorized Display
        for m in active_markets:
            if filter_cat != "All" and m['category'] != filter_cat:
                continue
                
            prices = engine.get_price(m['id'])
            
            with st.container():
                st.markdown(f"""
                    <div class='market-card'>
                        <div class='market-category'>{m['category']}</div>
                        <div class='market-title'>{m['title']}</div>
                        <div style='color: #666; font-size: 0.9rem;'>{m['description']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Transaction Controls
                cols = st.columns([1, 1, 1, 3])
                with cols[0]:
                    if st.button(f"Yes {int(prices['yes']*100)}¢", key=f"y_{m['id']}", use_container_width=True):
                        st.toast(f"Opening order for 'YES' at {prices['yes']} SOL...")
                with cols[1]:
                    if st.button(f"No {int(prices['no']*100)}¢", key=f"n_{m['id']}", use_container_width=True):
                        st.toast(f"Opening order for 'NO' at {prices['no']} SOL...")
                with cols[2]:
                    st.button("Details", key=f"d_{m['id']}", use_container_width=True)

    # Footer
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #BBB; font-size: 0.8rem;'>Built for the Giant of Africa on Solana Mainnet Beta.</p>", unsafe_allow_html=True)
