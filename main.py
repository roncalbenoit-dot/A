#!/usr/bin/env python3
"""
Polymarket AI Trading Agent - Main Entry Point

An AI agent for automated trading on the Polymarket prediction market platform.
"""
import asyncio
import logging
import sys
from typing import Optional

from core.agent import PolymarketTradingAgent
from config.settings import agent_config


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('trading_agent.log')
        ]
    )


async def main():
    """Main entry point for the trading agent"""
    setup_logging(agent_config.log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Polymarket AI Trading Agent Starting")
    logger.info("=" * 50)
    
    # Create and run the agent
    agent = PolymarketTradingAgent()
    
    try:
        await agent.run()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


async def demo_mode():
    """Run agent in demo mode (analysis only, no trading)"""
    setup_logging("INFO")
    
    logger = logging.getLogger(__name__)
    logger.info("Running in DEMO mode (analysis only)")
    
    agent = PolymarketTradingAgent()
    await agent.initialize()
    
    try:
        # Run a few cycles for demonstration
        for i in range(3):
            logger.info(f"\n--- Demo Cycle {i+1} ---")
            await agent.trading_cycle()
            await asyncio.sleep(2)
        
        # Show final risk report
        report = agent.get_risk_report()
        logger.info("\n=== Final Risk Report ===")
        for key, value in report.items():
            logger.info(f"{key}: {value}")
            
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Polymarket AI Trading Agent")
    parser.add_argument(
        "--demo", 
        action="store_true", 
        help="Run in demo mode (analysis only, no trading)"
    )
    parser.add_argument(
        "--auto-trade", 
        action="store_true", 
        help="Enable automatic trading"
    )
    
    args = parser.parse_args()
    
    if args.auto_trade:
        agent_config.enable_auto_trading = True
    
    if args.demo:
        asyncio.run(demo_mode())
    else:
        asyncio.run(main())
