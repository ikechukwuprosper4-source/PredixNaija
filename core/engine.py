import json
import os
import math
from typing import Dict, List, Optional
from datetime import datetime

class MarketEngine:
    """
    A simple Constant Product Market Maker (CPMM) logic for Yes/No predictions.
    This manages the internal state of the PredixMarket platform.
    """
    def __init__(self, data_file: str = "data/markets.json"):
        self.data_file = data_file
        self.markets = self._load_markets()

    def _load_markets(self) -> Dict:
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                return json.load(f)
        return {}

    def _save_markets(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w") as f:
            json.dump(self.markets, f, indent=4)

    def create_market(self, title: str, category: str, description: str, end_date: str) -> str:
        """Adds a new prediction event to the marketplace."""
        market_id = f"m_{int(datetime.now().timestamp())}"
        self.markets[market_id] = {
            "id": market_id,
            "title": title,
            "category": category,
            "description": description,
            "end_date": end_date,
            "status": "OPEN", # OPEN, CLOSED, RESOLVED_YES, RESOLVED_NO
            "yes_liquidity": 100.0, # Initial seed
            "no_liquidity": 100.0,
            "total_volume": 0.0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save_markets()
        return market_id

    def get_price(self, market_id: str) -> Dict[str, float]:
        """Calculates current Yes/No prices based on liquidity."""
        market = self.markets.get(market_id)
        if not market: return {"yes": 0.5, "no": 0.5}
        
        total = market["yes_liquidity"] + market["no_liquidity"]
        return {
            "yes": round(market["yes_liquidity"] / total, 2),
            "no": round(market["no_liquidity"] / total, 2)
        }

    def predict(self, market_id: str, side: str, amount: float, user_id: str):
        """Processes a user prediction (Buy Yes or No)."""
        market = self.markets.get(market_id)
        if not market or market["status"] != "OPEN": return False
        
        if side == "YES":
            market["yes_liquidity"] += amount
        else:
            market["no_liquidity"] += amount
            
        market["total_volume"] += amount
        self._save_markets()
        
        # In a real app, this would also update a 'user_predictions' table
        return True

    def resolve_market(self, market_id: str, outcome: str):
        """Finalizes a market based on the AI Oracle's findings."""
        if market_id in self.markets:
            self.markets[market_id]["status"] = f"RESOLVED_{outcome}"
            self._save_markets()
            return True
        return False
