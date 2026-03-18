"""
Polymarket API Client for AI Trading Agent
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import aiohttp
from config.settings import polymarket_config

logger = logging.getLogger(__name__)


class PolymarketAPIClient:
    """API client for interacting with Polymarket"""
    
    def __init__(self):
        self.config = polymarket_config
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_markets(self, limit: int = 100) -> List[Dict]:
        """Fetch active markets from Polymarket"""
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        url = f"{self.config.base_url}/markets"
        params = {"limit": limit, "active": True}
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("markets", [])
                else:
                    logger.error(f"Failed to fetch markets: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching markets: {str(e)}")
            return []
    
    async def get_market_details(self, market_id: str) -> Optional[Dict]:
        """Get detailed information for a specific market"""
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        url = f"{self.config.base_url}/markets/{market_id}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to fetch market {market_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching market {market_id}: {str(e)}")
            return None
    
    async def get_order_book(self, market_id: str) -> Optional[Dict]:
        """Get order book for a market"""
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        url = f"{self.config.base_url}/markets/{market_id}/order-book"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to fetch order book for {market_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching order book for {market_id}: {str(e)}")
            return None
    
    async def place_order(self, order_data: Dict) -> Optional[Dict]:
        """Place an order on Polymarket"""
        if not self.session:
            raise RuntimeError("Client session not initialized")
            
        url = f"{self.config.base_url}/orders"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.post(url, headers=headers, json=order_data) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    logger.error(f"Failed to place order: {response.status}")
                    text = await response.text()
                    logger.error(f"Response: {text}")
                    return None
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
