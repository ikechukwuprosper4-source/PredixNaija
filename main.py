import os
import argparse
import time
from loguru import logger
from dotenv import load_dotenv

# Local Agent Imports
from predixmarket.agents.curator_agent import CuratorAgent
from predixmarket.core.engine import MarketEngine

# Load environment variables
load_dotenv()

def run_platform_worker(interval_minutes: int = 240):
    """
    Main 24/7 autonomous worker for the PredixMarket platform.
    This background process automates market discovery and resolution.
    """
    logger.info("Initializing PredixMarket AI Platform Worker...")
    
    # Initialize Engine & Curator Agent
    engine = MarketEngine()
    curator = CuratorAgent()
    
    while True:
        try:
            # 1. AI Market Discovery Phase
            logger.info("Phase 1: AI Market Discovery - Scanning news for new opportunities...")
            new_markets = curator.discover_markets(topic="global finance and crypto")
            
            for m in new_markets:
                # Check if market already exists (simplistic check)
                existing_titles = [market['title'] for market in engine.markets.values()]
                if m.title not in existing_titles:
                    market_id = engine.create_market(m.title, m.category, m.description, m.end_date)
                    logger.info(f"🆕 AI CURATOR: New market deployed! {m.title} (ID: {market_id})")
                else:
                    logger.debug(f"Market already exists: {m.title}")
            
            # 2. AI Market Resolution Phase
            logger.info("Phase 2: AI Market Resolution - Checking closing markets...")
            # markets = engine.markets
            # for m_id, m in markets.items():
            #    if m['status'] == 'OPEN' and m['end_date'] <= current_date:
            #        outcome = curator.resolve_market(m['title'])
            #        engine.resolve_market(m_id, outcome)
            #        logger.info(f"⚖️ AI ORACLE: Market resolved {outcome} for {m['title']}")
            
            logger.info(f"Worker loop complete. Resting for {interval_minutes} minutes.")
            time.sleep(interval_minutes * 60)
            
        except Exception as e:
            logger.error(f"Critical error in platform worker: {e}")
            time.sleep(60) # Wait 1 minute before retrying

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PredixMarket: Autonomous Platform Worker")
    parser.add_argument("--mode", type=str, choices=["worker", "manual"], default="worker")
    parser.add_argument("--interval", type=int, default=240, help="Interval in minutes between discovery scans.")
    
    args = parser.parse_args()
    
    if args.mode == "worker":
        run_platform_worker(args.interval)
    else:
        logger.info("Manual mode selected. Use the Streamlit dashboard to control the platform.")
