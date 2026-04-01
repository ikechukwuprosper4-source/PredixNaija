import os
import json
from typing import Dict, List, Optional
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from loguru import logger
from datetime import datetime

class ProposedMarket(BaseModel):
    """Structured output for the AI Curator to suggest a new market."""
    title: str = Field(description="A catchy, concise title for the prediction event.")
    category: str = Field(description="Politics, Economy, Entertainment, or Sports.")
    description: str = Field(description="A brief, clear description of the event.")
    end_date: str = Field(description="Resolution date in YYYY-MM-DD format.")
    reasoning: str = Field(description="Why this market is relevant now.")

class CuratorAgent:
    """
    Naija Market Curator Agent responsible for scanning Nigerian news 
    and proposing high-interest prediction markets for users.
    """
    def __init__(self, model_name: str = "llama3-70b-8192"):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY missing. Curator will operate in SIMULATION mode.")
            self.llm = None
        else:
            self.llm = ChatGroq(model=model_name, api_key=self.api_key)
            
        self.search_tool = DuckDuckGoSearchRun()

    def discover_markets(self, topic: str = "Nigerian Politics, Economy and Sports") -> List[ProposedMarket]:
        """
        Scans Nigerian news (Punch, Vanguard, Vanguard, X-Naija) for markets.
        """
        logger.info(f"Naija Curator scanning news for topic: {topic}")
        
        # Step 1: Perform Web Search (Free) - Focus on Naija sources
        query = f"breaking news and trending events in {topic} from Nigerian news sources like Punch, Vanguard, and X"
        try:
            news_data = self.search_tool.run(query)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            news_data = "No news data found."

        # Step 2: Use LLM to propose a market
        if not self.llm:
            # Fallback for simulation
            return [ProposedMarket(
                title="Will the Naira hit 1400/$ by June?",
                category="Economy",
                description="Analysis of current CBN policy and exchange rates.",
                end_date="2026-06-30",
                reasoning="High-interest topic for every Nigerian today."
            )]

        prompt = ChatPromptTemplate.from_template("""
        You are the PredixNaija Visionary Curator. 
        Analyze the following news data from Nigeria and propose THREE high-interest prediction markets.
        
        News Data: {data}
        
        Criteria for a good market:
        1. Focused on Nigeria (Politics, Economy, NPFL/EPL, Nollywood/Afrobeats).
        2. Binary outcome (YES or NO).
        3. Clear, verifiable resolution.
        
        Output format: Valid JSON as a list of ProposedMarket schemas.
        """)
        
        try:
            chain = prompt | self.llm.with_structured_output(List[ProposedMarket])
            results = chain.invoke({"data": news_data})
            return results
        except Exception as e:
            logger.error(f"AI Market Proposal failed: {e}")
            return []

    def resolve_market(self, market_title: str) -> str:
        """
        AI Oracle logic: Verify Nigerian events (YES or NO).
        """
        logger.info(f"AI Oracle resolving market: {market_title}")
        query = f"Has this event occurred yet? {market_title} site:punchng.com OR site:vanguardngr.com"
        news_verification = self.search_tool.run(query)
        
        # Simplistic LLM check (stub)
        return "YES" if "confirmed" in news_verification.lower() else "NO"
