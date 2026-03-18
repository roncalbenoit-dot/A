"""
Main AI Agent Orchestrator for Polymarket Trading
"""
import asyncio
import logging
from typing import List, Optional
from datetime import datetime

from config.settings import agent_config
from core.api_client import PolymarketAPIClient
from core.market_data import MarketDataProcessor
from core.decision_engine import DecisionEngine, TradeSignal
from core.risk_manager import RiskManager
from core.trading_executor import TradingExecutor

logger = logging.getLogger(__name__)


class PolymarketTradingAgent:
    """Main AI agent for automated Polymarket trading"""
    
    def __init__(self):
        self.config = agent_config
        self.market_processor = MarketDataProcessor()
        self.decision_engine = DecisionEngine(self.market_processor)
        self.risk_manager = RiskManager()
        self.api_client: Optional[PolymarketAPIClient] = None
        self.trading_executor: Optional[TradingExecutor] = None
        self.running = False
        
    async def initialize(self):
        """Initialize the agent and all components"""
        logger.info("Initializing Polymarket Trading Agent...")
        
        # Initialize API client
        self.api_client = PolymarketAPIClient()
        await self.api_client.initialize()
        
        # Initialize trading executor
        self.trading_executor = TradingExecutor(self.api_client, self.risk_manager)
        
        logger.info("Agent initialized successfully")
        
    async def shutdown(self):
        """Shutdown the agent gracefully"""
        logger.info("Shutting down Polymarket Trading Agent...")
        
        if self.api_client:
            await self.api_client.__aexit__(None, None, None)
        
        self.running = False
        logger.info("Agent shutdown complete")
        
    async def run(self):
        """Main agent loop"""
        await self.initialize()
        self.running = True
        
        logger.info(f"Agent started - Auto-trading: {self.config.enable_auto_trading}")
        
        try:
            while self.running:
                await self._trading_cycle()
                await asyncio.sleep(self.config.update_interval)
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
        finally:
            await self.shutdown()
    
    async def _trading_cycle(self):
        """Execute one trading cycle"""
        logger.debug("Starting trading cycle...")
        
        # 1. Fetch market data
        markets = await self._fetch_markets()
        
        # 2. Process market data
        liquid_markets = self._process_markets(markets)
        
        # 3. Generate trading signals
        signals = self._generate_signals(liquid_markets)
        
        # 4. Execute trades (if auto-trading enabled)
        if self.config.enable_auto_trading:
            await self._execute_signals(signals)
        
        # 5. Log status
        self._log_status(signals)
    
    async def _fetch_markets(self) -> List[dict]:
        """Fetch markets from Polymarket"""
        if not self.api_client:
            return []
        
        try:
            markets = await self.api_client.get_markets(limit=50)
            logger.debug(f"Fetched {len(markets)} markets")
            return markets
        except Exception as e:
            logger.error(f"Error fetching markets: {str(e)}")
            return []
    
    def _process_markets(self, markets: List[dict]) -> List:
        """Process market data and return liquid markets"""
        for market_data in markets:
            self.market_processor.process_market(market_data)
        
        # Get liquid markets
        liquid = self.market_processor.get_liquid_markets(min_volume=1000)
        logger.debug(f"Found {len(liquid)} liquid markets")
        return liquid
    
    def _generate_signals(self, markets: List) -> List[TradeSignal]:
        """Generate trading signals for markets"""
        signals = []
        
        for market in markets:
            signal = self.decision_engine.analyze_market(market)
            
            if self.decision_engine.should_execute_trade(signal):
                signals.append(signal)
                logger.info(f"Signal generated: {signal.action.value} on {market.question} "
                          f"(confidence: {signal.confidence:.2%})")
        
        return signals
    
    async def _execute_signals(self, signals: List[TradeSignal]):
        """Execute trading signals"""
        if not self.trading_executor:
            return
        
        for signal in signals:
            result = await self.trading_executor.execute_signal(signal)
            
            if result.success:
                logger.info(f"Trade executed: {result.order_id} - {result.message}")
            else:
                logger.warning(f"Trade failed: {result.message}")
    
    def _log_status(self, signals: List[TradeSignal]):
        """Log agent status"""
        risk_report = self.risk_manager.get_risk_report()
        
        logger.info(f"=== Agent Status ===")
        logger.info(f"Active signals: {len(signals)}")
        logger.info(f"Daily P&L: ${risk_report['daily_pnl']:.2f}")
        logger.info(f"Daily trades: {risk_report['daily_trades']}")
        logger.info(f"Total exposure: ${risk_report['total_exposure']:.2f}")
        logger.info(f"===================")
    
    async def analyze_market(self, market_id: str) -> Optional[TradeSignal]:
        """Analyze a specific market and return signal"""
        if not self.api_client:
            return None
        
        market_data = await self.api_client.get_market_details(market_id)
        if not market_data:
            return None
        
        snapshot = self.market_processor.process_market(market_data)
        if not snapshot:
            return None
        
        return self.decision_engine.analyze_market(snapshot)
    
    def get_risk_report(self) -> dict:
        """Get current risk report"""
        return self.risk_manager.get_risk_report()
