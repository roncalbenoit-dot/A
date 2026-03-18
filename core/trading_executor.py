"""
Trading Executor for Polymarket AI Trading Agent
"""
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from core.api_client import PolymarketAPIClient
from core.decision_engine import TradeSignal, TradeAction
from core.risk_manager import RiskManager, RiskCheck

logger = logging.getLogger(__name__)


@dataclass
class TradeResult:
    """Result of a trade execution"""
    success: bool
    order_id: Optional[str]
    filled_size: float
    filled_price: float
    message: str
    timestamp: datetime


class TradingExecutor:
    """Executes trades on Polymarket"""
    
    def __init__(self, api_client: PolymarketAPIClient, risk_manager: RiskManager):
        self.api_client = api_client
        self.risk_manager = risk_manager
    
    async def execute_signal(self, signal: TradeSignal) -> TradeResult:
        """Execute a trading signal"""
        # Check risk limits first
        side = self._get_order_side(signal.action)
        risk_check = self.risk_manager.check_trade(
            signal.market_id, 
            signal.size, 
            side
        )
        
        if not risk_check.passed:
            logger.warning(f"Trade rejected by risk manager: {risk_check.reason}")
            return TradeResult(
                success=False,
                order_id=None,
                filled_size=0,
                filled_price=0,
                message=f"Risk check failed: {risk_check.reason}",
                timestamp=datetime.now()
            )
        
        # Prepare order data
        order_data = self._prepare_order(signal)
        
        # Execute order
        try:
            response = await self.api_client.place_order(order_data)
            
            if response:
                # Update risk tracking
                self.risk_manager.update_exposure(
                    signal.market_id, 
                    signal.size, 
                    side
                )
                
                logger.info(f"Trade executed: {signal.action.value} {signal.size} on {signal.market_id}")
                
                return TradeResult(
                    success=True,
                    order_id=response.get("orderId"),
                    filled_size=signal.size,
                    filled_price=0.0,  # Price should be derived from market data
                    message=f"Order placed successfully: {response.get('status', 'unknown')}",
                    timestamp=datetime.now()
                )
            else:
                return TradeResult(
                    success=False,
                    order_id=None,
                    filled_size=0,
                    filled_price=0,
                    message="Order placement failed - no response from API",
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            return TradeResult(
                success=False,
                order_id=None,
                filled_size=0,
                filled_price=0,
                message=f"Execution error: {str(e)}",
                timestamp=datetime.now()
            )
    
    def _get_order_side(self, action: TradeAction) -> str:
        """Convert trade action to order side"""
        mapping = {
            TradeAction.BUY_YES: "buy_yes",
            TradeAction.BUY_NO: "buy_no",
            TradeAction.SELL_YES: "sell_yes",
            TradeAction.SELL_NO: "sell_no",
            TradeAction.HOLD: "hold"
        }
        return mapping.get(action, "hold")
    
    def _prepare_order(self, signal: TradeSignal) -> Dict:
        """Prepare order data for API"""
        side = self._get_order_side(signal.action)
        
        return {
            "marketId": signal.market_id,
            "side": side,
            "size": signal.size,
            "type": "limit",  # Use limit orders for better control
            "timeInForce": "GTC",  # Good till cancelled
            "metadata": {
                "confidence": signal.confidence,
                "reason": signal.reason,
                "agent_version": "1.0.0"
            }
        }
