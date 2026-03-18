"""
Risk Manager for Polymarket AI Trading Agent
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from config.settings import trading_config

logger = logging.getLogger(__name__)


@dataclass
class RiskCheck:
    """Result of a risk check"""
    passed: bool
    reason: str
    risk_score: float


class RiskManager:
    """Manages trading risk and position limits"""
    
    def __init__(self):
        self.daily_pnl: float = 0.0
        self.daily_trades: int = 0
        self.last_reset: datetime = datetime.now()
        self.trade_history: List[Dict] = []
        self.exposure: Dict[str, float] = {}
    
    def check_trade(self, market_id: str, size: float, side: str) -> RiskCheck:
        """Check if a trade passes risk criteria"""
        # Reset daily stats if needed
        self._reset_daily_stats()
        
        # Check daily loss limit
        if self.daily_pnl <= -trading_config.max_daily_loss:
            return RiskCheck(
                passed=False,
                reason=f"Daily loss limit reached: ${self.daily_pnl:.2f}",
                risk_score=1.0
            )
        
        # Check position size
        if size > trading_config.max_position_size:
            return RiskCheck(
                passed=False,
                reason=f"Position size {size} exceeds max {trading_config.max_position_size}",
                risk_score=0.9
            )
        
        # Check total exposure
        current_exposure = sum(self.exposure.values())
        if current_exposure + size > trading_config.max_position_size * 3:
            return RiskCheck(
                passed=False,
                reason=f"Total exposure would exceed limit",
                risk_score=0.8
            )
        
        # Check market-specific exposure
        current_market_exposure = self.exposure.get(market_id, 0)
        if current_market_exposure + size > trading_config.max_position_size:
            return RiskCheck(
                passed=False,
                reason=f"Market exposure limit reached for {market_id}",
                risk_score=0.7
            )
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(size, current_exposure)
        
        return RiskCheck(
            passed=True,
            reason="Risk check passed",
            risk_score=risk_score
        )
    
    def _calculate_risk_score(self, trade_size: float, current_exposure: float) -> float:
        """Calculate a risk score for the trade (0-1, higher = more risky)"""
        exposure_ratio = (current_exposure + trade_size) / (trading_config.max_position_size * 3)
        size_ratio = trade_size / trading_config.max_position_size
        
        # Combine factors
        risk_score = (exposure_ratio * 0.5) + (size_ratio * 0.5)
        return min(risk_score, 1.0)
    
    def update_exposure(self, market_id: str, size: float, side: str):
        """Update exposure tracking after a trade"""
        if side in ["buy_yes", "buy_no"]:
            self.exposure[market_id] = self.exposure.get(market_id, 0) + size
        else:
            self.exposure[market_id] = max(0, self.exposure.get(market_id, 0) - size)
        
        self.daily_trades += 1
    
    def record_trade_result(self, market_id: str, pnl: float):
        """Record trade P&L"""
        self.daily_pnl += pnl
        self.trade_history.append({
            "market_id": market_id,
            "pnl": pnl,
            "timestamp": datetime.now()
        })
    
    def _reset_daily_stats(self):
        """Reset daily statistics if it's a new day"""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.last_reset = now
            logger.info("Daily risk stats reset")
    
    def get_risk_report(self) -> Dict:
        """Get current risk status report"""
        self._reset_daily_stats()
        
        return {
            "daily_pnl": self.daily_pnl,
            "daily_trades": self.daily_trades,
            "total_exposure": sum(self.exposure.values()),
            "market_exposures": self.exposure.copy(),
            "daily_loss_limit": trading_config.max_daily_loss,
            "remaining_daily_loss": trading_config.max_daily_loss + self.daily_pnl
        }
