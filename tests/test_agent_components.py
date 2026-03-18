"""
Tests for Polymarket AI Trading Agent Components
"""
import unittest
import asyncio
from datetime import datetime
from core.market_data import MarketDataProcessor, MarketSnapshot
from core.decision_engine import DecisionEngine, TradeAction
from core.risk_manager import RiskManager


class TestAgentComponents(unittest.TestCase):
    """Test cases for agent components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.market_processor = MarketDataProcessor()
        self.decision_engine = DecisionEngine(self.market_processor)
        self.risk_manager = RiskManager()
    
    def test_market_processing(self):
        """Test market data processing"""
        # Sample market data
        market_data = {
            "id": "test-market-1",
            "question": "Will it rain tomorrow?",
            "yesPrice": "0.65",
            "noPrice": "0.35",
            "volume": "15000",
            "liquidity": "5000"
        }
        
        # Process the market
        snapshot = self.market_processor.process_market(market_data)
        
        # Verify the snapshot
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.market_id, "test-market-1")
        self.assertEqual(snapshot.question, "Will it rain tomorrow?")
        self.assertEqual(snapshot.yes_price, 0.65)
        self.assertEqual(snapshot.no_price, 0.35)
        self.assertEqual(snapshot.volume, 15000)
        self.assertEqual(snapshot.liquidity, 5000)
        self.assertAlmostEqual(snapshot.implied_probability, 0.65)
    
    def test_decision_engine_analysis(self):
        """Test decision engine analysis"""
        # Create a market snapshot
        snapshot = MarketSnapshot(
            market_id="test-market-2",
            question="Will the stock go up?",
            yes_price=0.75,
            no_price=0.25,
            volume=20000,
            liquidity=8000,
            timestamp=datetime.now()
        )
        
        # Analyze the market
        signal = self.decision_engine.analyze_market(snapshot)
        
        # Verify the signal
        self.assertIsNotNone(signal)
        self.assertEqual(signal.market_id, "test-market-2")
        self.assertIsInstance(signal.action, TradeAction)
        self.assertGreaterEqual(signal.confidence, 0.0)
        self.assertLessEqual(signal.confidence, 1.0)
        self.assertGreaterEqual(signal.size, 0.0)
    
    def test_risk_management(self):
        """Test risk management functionality"""
        # Check a trade
        risk_check = self.risk_manager.check_trade(
            market_id="test-market-3",
            size=50.0,
            side="buy_yes"
        )
        
        # Verify risk check
        self.assertIsInstance(risk_check.passed, bool)
        self.assertIsInstance(risk_check.reason, str)
        self.assertIsInstance(risk_check.risk_score, float)
        
        # Update exposure
        self.risk_manager.update_exposure(
            market_id="test-market-3",
            size=50.0,
            side="buy_yes"
        )
        
        # Check risk report
        report = self.risk_manager.get_risk_report()
        self.assertIsInstance(report, dict)
        self.assertIn("daily_pnl", report)
        self.assertIn("total_exposure", report)


if __name__ == "__main__":
    unittest.main()
