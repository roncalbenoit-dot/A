# Polymarket AI Trading Agent

An AI-powered trading agent for automated trading on the Polymarket prediction market platform.

## Features

- **AI Decision Engine**: Momentum-based and mean reversion trading strategies
- **Risk Management**: Position sizing, daily loss limits, and exposure tracking
- **Market Data Processing**: Real-time market analysis and price history tracking
- **Automated Trading**: Execute trades automatically based on AI signals
- **Demo Mode**: Test strategies without real trading

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PolymarketTradingAgent                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Decision   │  │    Market    │  │    Risk      │      │
│  │   Engine     │  │   Processor  │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐                         │
│  │     API      │  │   Trading    │                         │
│  │   Client     │  │   Executor   │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set environment variables for API access:

```bash
export POLYMARKET_API_KEY="your_api_key"
export POLYMARKET_API_SECRET="your_api_secret"
```

Or modify `config/settings.py` directly.

## Usage

### Demo Mode (Analysis Only)
```bash
python main.py --demo
```

### Live Trading
```bash
python main.py --auto-trade
```

## Components

### Core Modules

- **api_client.py**: Polymarket API integration
- **market_data.py**: Market data processing and analysis
- **decision_engine.py**: AI trading strategies and signal generation
- **risk_manager.py**: Risk management and position limits
- **trading_executor.py**: Trade execution and order management
- **agent.py**: Main agent orchestrator

### Trading Strategies

1. **Momentum Strategy**: Trade based on price momentum indicators
2. **Mean Reversion**: Identify overbought/oversold conditions
3. **Volume Confirmation**: Use volume to confirm trading signals

### Risk Management

- Maximum position size limits
- Daily loss limits
- Risk per trade (Kelly Criterion-inspired)
- Total exposure tracking

## Testing

```bash
python -m pytest tests/ -v
```

## License

MIT License
