"""
Configuration settings for Polymarket AI Trading Agent
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class PolymarketConfig:
    """Polymarket API configuration"""
    api_key: str = os.getenv("POLYMARKET_API_KEY", "")
    api_secret: str = os.getenv("POLYMARKET_API_SECRET", "")
    base_url: str = "https://api.polymarket.com"
    ws_url: str = "wss://ws.polymarket.com"


@dataclass
class TradingConfig:
    """Trading configuration"""
    max_position_size: float = 100.0  # Maximum position size in USD
    max_daily_loss: float = 50.0  # Maximum daily loss limit
    risk_per_trade: float = 0.02  # Risk per trade (2%)
    min_confidence: float = 0.6  # Minimum confidence threshold for trades
    default_slippage: float = 0.01  # Default slippage tolerance (1%)


@dataclass
class AgentConfig:
    """AI Agent configuration"""
    agent_name: str = "PolymarketAI"
    update_interval: int = 60  # Seconds between market updates
    strategy_type: str = "momentum"  # Default strategy
    enable_auto_trading: bool = False  # Auto-trading enabled by default
    log_level: str = "INFO"


# Global configuration instances
polymarket_config = PolymarketConfig()
trading_config = TradingConfig()
agent_config = AgentConfig()
