"""
Market Data Processor for Polymarket AI Trading Agent
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MarketSnapshot:
    """Snapshot of market data at a point in time"""
    market_id: str
    question: str
    yes_price: float
    no_price: float
    volume: float
    liquidity: float
    timestamp: datetime
    
    @property
    def implied_probability(self) -> float:
        """Calculate implied probability from yes price"""
        return self.yes_price
    
    @property
    def spread(self) -> float:
        """Calculate bid-ask spread"""
        return abs(self.yes_price - (1 - self.no_price))


class MarketDataProcessor:
    """Process and analyze market data"""
    
    def __init__(self):
        self.market_cache: Dict[str, MarketSnapshot] = {}
        self.price_history: Dict[str, List[Dict]] = {}
    
    def process_market(self, market_data: Dict) -> Optional[MarketSnapshot]:
        """Process raw market data into a MarketSnapshot"""
        try:
            market_id = market_data.get("id") or market_data.get("marketId")
            if not market_id:
                return None
            
            # Extract prices from market data
            yes_price = float(market_data.get("yesPrice", 0.5))
            no_price = float(market_data.get("noPrice", 0.5))
            
            snapshot = MarketSnapshot(
                market_id=market_id,
                question=market_data.get("question", "Unknown"),
                yes_price=yes_price,
                no_price=no_price,
                volume=float(market_data.get("volume", 0)),
                liquidity=float(market_data.get("liquidity", 0)),
                timestamp=datetime.now()
            )
            
            # Cache the snapshot
            self.market_cache[market_id] = snapshot
            
            # Update price history
            if market_id not in self.price_history:
                self.price_history[market_id] = []
            
            self.price_history[market_id].append({
                "timestamp": snapshot.timestamp,
                "yes_price": yes_price,
                "no_price": no_price
            })
            
            # Keep only last 1000 data points
            if len(self.price_history[market_id]) > 1000:
                self.price_history[market_id] = self.price_history[market_id][-1000:]
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error processing market data: {str(e)}")
            return None
    
    def get_price_momentum(self, market_id: str, periods: int = 10) -> float:
        """Calculate price momentum for a market"""
        if market_id not in self.price_history:
            return 0.0
        
        history = self.price_history[market_id]
        if len(history) < periods:
            return 0.0
        
        recent = history[-periods:]
        if len(recent) < 2:
            return 0.0
        
        # Calculate momentum as price change rate
        start_price = recent[0]["yes_price"]
        end_price = recent[-1]["yes_price"]
        
        if start_price == 0:
            return 0.0
        
        return (end_price - start_price) / start_price
    
    def get_volatility(self, market_id: str, periods: int = 20) -> float:
        """Calculate price volatility for a market"""
        if market_id not in self.price_history:
            return 0.0
        
        history = self.price_history[market_id]
        if len(history) < periods:
            return 0.0
        
        recent = history[-periods:]
        prices = [h["yes_price"] for h in recent]
        
        if len(prices) < 2:
            return 0.0
        
        # Calculate standard deviation
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        
        return variance ** 0.5
    
    def get_liquid_markets(self, min_volume: float = 1000) -> List[MarketSnapshot]:
        """Get markets with sufficient liquidity"""
        return [
            snapshot for snapshot in self.market_cache.values()
            if snapshot.volume >= min_volume and snapshot.liquidity > 0
        ]
