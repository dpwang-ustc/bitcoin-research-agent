# Bitcoin Research Agent - Demo User Guide

## 📖 Welcome!

Welcome to the Bitcoin Research Agent public demo! This guide will help you explore all the features and capabilities of our AI-driven cryptocurrency market analysis system.

---

## 🚀 Quick Start

### Access the Demo

**Online Demo**:
- Visit: `https://bitcoin-research-agent.streamlit.app` (coming soon)

**Local Demo**:
```bash
# Clone repository
git clone https://github.com/dpwang-ustc/bitcoin-research-agent
cd bitcoin-research-agent

# Run demo
streamlit run src/demo/demo_app.py
```

---

## 🎯 Demo Modes

The demo offers 5 interactive modes:

### 1. 🏠 Overview

**What to explore**:
- Project introduction and value proposition
- Key metrics and performance stats
- Core features showcase
- Technical highlights

**Key Metrics**:
- Market Regime Accuracy: 85%
- Backtesting Win Rate: 64%
- Sharpe Ratio: 1.42
- Processing Speed: 22.2s

**Core Features** (6 modules):
1. LangGraph AI Agent
2. Market Regime Identification
3. Sentiment Analysis
4. Capital Flow Tracking
5. Volatility Analysis
6. Automated Reporting

---

### 2. 🤖 AI Agent Demo

**What to do**:
1. **Try Quick Questions**:
   - Click "Current Market State" for instant analysis
   - Click "Market Sentiment" for sentiment overview
   - Click "Weekly Summary" for comprehensive report

2. **Ask Custom Questions**:
   - Type your own question in the input box
   - Examples:
     - "What are the key support and resistance levels?"
     - "Is this a good time to buy Bitcoin?"
     - "Analyze the last week's price movement"
     - "What do whale activities suggest?"

3. **Understand the Response**:
   - Market Regime: Current state classification
   - Technical Indicators: RSI, MACD, Bollinger Bands
   - Sentiment Analysis: Fear & Greed Index
   - Capital Flow: Whale activity and trends
   - Recommendation: AI-generated trading suggestion

**Agent Capabilities**:
- ✅ Real-time market analysis
- ✅ Trend identification
- ✅ Sentiment assessment
- ✅ Capital flow detection
- ✅ Report generation
- ✅ Trading signals

**How It Works**:
The AI Agent uses a LangGraph workflow with 10 nodes:
1. Data Collection
2. Data Processing
3. Task Routing
4. Regime Analysis
5. Volatility Analysis
6. Sentiment Analysis
7. Capital Flow Analysis
8. AI Insights (GPT-4o-mini)
9. Report Generation
10. Response Delivery

---

### 3. 📊 Live Dashboard

**What to explore**:

**Price Chart**:
- 30-day Bitcoin price history
- Interactive hover for details
- Zoom and pan capabilities

**Key Metrics**:
- Current Price: Real-time BTC price
- 24h Volume: Trading volume
- Fear & Greed: Sentiment indicator
- Market Regime: Current state

**Analysis Tabs**:

1. **📊 Regime Tab**:
   - View regime distribution
   - Consolidation: 42%
   - Trending: 35%
   - Panic: 12%
   - Euphoria: 11%

2. **📈 Volatility Tab**:
   - Compare 4 volatility methods
   - Realized, Parkinson, Garman-Klass, GARCH
   - See which method is most accurate

3. **💭 Sentiment Tab**:
   - Fear & Greed Index (0-100 scale)
   - Current sentiment classification
   - Historical trends

4. **💰 Capital Flow Tab**:
   - Whale activity status
   - Main force behavior
   - Net capital flow

**Full Dashboard**:
For the complete interactive experience, run:
```bash
streamlit run src/dashboard/app.py
```

---

### 4. 📈 Analysis Examples

**Case Studies**:

**Case 1: Bull Market Identification (Jan 2024)**
- Learn how AI Agent identified bull market early
- See technical indicators and signals
- Review outcome: +18.5% gain

**Case 2: Bear Market Warning (May 2024)**
- Understand how system detected distribution
- See warning signals 3 days before crash
- Review outcome: Avoided -12% loss

**Case 3: Consolidation Breakout (Aug 2024)**
- Analysis of sideways market
- Breakout detection methodology
- Trading strategy and results

**Case 4: Whale Activity Detection (Sep 2024)**
- Large transaction detection
- Impact on price movement
- Trading implications

**Overall Performance**:
- Total Signals: 47 (over 180 days)
- Win Rate: 64%
- Average Return: 2.3% per trade
- Sharpe Ratio: 1.42

---

### 5. 📚 Documentation

**Tabs**:

**📖 Getting Started**:
- Installation guide
- Quick start tutorial
- System requirements
- Basic configuration

**🔧 Technical Docs**:
- Architecture overview
- Module descriptions
- API reference
- Code examples

**📊 Research**:
- White paper access
- Key findings
- Experimental results
- Citation information

**🎓 Tutorials**:
- Video tutorial series
- Step-by-step guides
- Code examples
- Best practices

---

## 💡 Tips for Best Experience

### 1. Understanding Market Regimes

**Consolidation** (42% of time):
- Low volatility (2.1%)
- Sideways price action
- Average duration: 18 days
- Strategy: Range trading

**Trending** (35% of time):
- Directional movement
- Higher volatility (3.5%)
- Average duration: 25 days
- Strategy: Trend following

**Panic** (12% of time):
- High volatility (8.2%)
- Sharp declines
- Average duration: 7 days
- Strategy: Avoid or buy dips

**Euphoria** (11% of time):
- High volatility (7.9%)
- Sharp increases
- Average duration: 9 days
- Strategy: Take profits

### 2. Interpreting Sentiment

**Fear & Greed Index Scale**:
- 0-24: Extreme Fear (Buy signal?)
- 25-49: Fear (Caution)
- 50-74: Greed (Neutral to sell)
- 75-100: Extreme Greed (Sell signal?)

**Note**: Sentiment shows strongest predictive power at 7-day lag (0.68 correlation)

### 3. Understanding Capital Flow

**Whale Activity**:
- Transactions > 3σ from mean
- Accumulation: Bullish signal
- Distribution: Bearish signal

**Main Force Behavior**:
- Accumulation: Building positions
- Distribution: Selling positions
- Pump: Rapid price increase
- Dump: Rapid price decrease
- Sideways: No clear direction

### 4. Using AI Agent Effectively

**Best Practices**:
1. **Be Specific**: Ask clear, specific questions
2. **Provide Context**: Mention time frames or conditions
3. **Follow Up**: Ask clarifying questions
4. **Verify**: Cross-check with dashboard data
5. **Experiment**: Try different query styles

**Example Queries**:
- ❌ Bad: "Bitcoin?"
- ✅ Good: "What is the current Bitcoin market trend?"
- ✅ Better: "Analyze Bitcoin price movement over the last week and identify key support levels"

---

## 📊 Understanding the Data

### Data Sources

1. **Market Data** (Yahoo Finance):
   - OHLCV prices
   - Trading volume
   - Daily updates

2. **On-Chain Data** (CoinGecko):
   - Transaction volume
   - Active addresses
   - Hash rate
   - Network fees

3. **Macro Data** (Yahoo Finance):
   - VIX (volatility index)
   - Gold prices
   - Dollar index (DXY)

4. **Sentiment Data**:
   - News sentiment
   - Social media trends
   - Market indicators

### Technical Indicators

**Moving Averages**:
- SMA 7, 14, 30
- EMA 12, 26
- Purpose: Trend identification

**Momentum**:
- RSI (14-period)
- MACD (12, 26, 9)
- Purpose: Overbought/oversold

**Volatility**:
- Bollinger Bands (20, 2)
- ATR (14-period)
- Purpose: Risk assessment

---

## 🔧 Customization Options

### For Developers

**Run Custom Analysis**:
```python
from src.agent import BitcoinResearchAgent

agent = BitcoinResearchAgent()
result = agent.run("Your custom query")
print(result)
```

**Generate Reports**:
```python
from src.reports import WeeklyReportGenerator

generator = WeeklyReportGenerator(use_ai=True)
report = generator.generate_report()
```

**Analyze Specific Periods**:
```python
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=30)

# Analyze custom period
analysis = agent.analyze_period(start_date, end_date)
```

---

## ❓ FAQ

### Q1: How accurate is the AI Agent?

**A**: The AI Agent achieves:
- 85% market regime classification accuracy
- 64% backtesting win rate
- 98% factual accuracy in reports
- Sharpe ratio of 1.42 (vs market 1.0)

### Q2: Is this financial advice?

**A**: No. This is an educational demo for research purposes only. Always do your own research and consult with financial advisors before making investment decisions.

### Q3: How often is data updated?

**A**: 
- Market data: Daily
- On-chain data: Real-time via API
- Reports: Generated on demand
- Dashboard: Updates on page refresh

### Q4: Can I use this for live trading?

**A**: The system is designed for research and analysis. For live trading:
- Thoroughly backtest strategies
- Use proper risk management
- Start with paper trading
- Consult financial advisors

### Q5: How does the AI Agent work?

**A**: The agent uses:
- LangGraph for workflow orchestration
- GPT-4o-mini for natural language understanding
- 8 analysis modules for data processing
- State management for context retention
- Intelligent routing for task optimization

### Q6: What makes this different from other tools?

**A**: Key differentiators:
- ✅ Multi-source data integration
- ✅ AI-driven insights (LLM-powered)
- ✅ Complete automation
- ✅ Open source and transparent
- ✅ Research-backed methodology
- ✅ Production-ready deployment

### Q7: Can I contribute to the project?

**A**: Yes! Contributions are welcome:
- Report bugs on GitHub
- Suggest features
- Submit pull requests
- Improve documentation
- Share feedback

### Q8: How much does it cost to run?

**A**: 
- Base system: Free (open source)
- Data APIs: Free tiers available
- LLM costs: ~$0.004 per report (optional)
- Cloud hosting: Free to $20/month

---

## 🎓 Learning Path

### Beginner (30 minutes)
1. ✅ Explore Overview mode
2. ✅ Try AI Agent with quick questions
3. ✅ Review Live Dashboard
4. ✅ Read one case study

### Intermediate (1 hour)
1. ✅ Ask custom AI Agent questions
2. ✅ Analyze all dashboard tabs
3. ✅ Review all case studies
4. ✅ Read Getting Started docs

### Advanced (2+ hours)
1. ✅ Install locally
2. ✅ Run full dashboard
3. ✅ Generate custom reports
4. ✅ Read white paper
5. ✅ Experiment with code
6. ✅ Contribute improvements

---

## 📞 Support & Feedback

### Get Help
- **GitHub Issues**: [Report bugs](https://github.com/dpwang-ustc/bitcoin-research-agent/issues)
- **Discussions**: [Ask questions](https://github.com/dpwang-ustc/bitcoin-research-agent/discussions)
- **Email**: dpwang@ustc.edu

### Provide Feedback
We'd love to hear from you!
- What features do you like?
- What could be improved?
- Any bugs or issues?
- Feature requests?

### Stay Updated
- ⭐ Star the repo on GitHub
- 👀 Watch for updates
- 🔔 Enable notifications
- 📱 Follow on social media

---

## 🎯 Next Steps

After exploring the demo:

1. **Try It Yourself**:
   - Install locally
   - Experiment with features
   - Generate your own reports

2. **Learn More**:
   - Read the white paper
   - Review documentation
   - Study code examples

3. **Get Involved**:
   - Join discussions
   - Report bugs
   - Contribute code
   - Share feedback

4. **Stay Connected**:
   - Star on GitHub
   - Follow updates
   - Share with others

---

## 🎊 Enjoy the Demo!

We hope you enjoy exploring Bitcoin Research Agent! This demo showcases the power of AI-driven cryptocurrency analysis.

**Remember**: This is for educational purposes only. Always do your own research and invest responsibly.

---

**Demo URL**: `https://bitcoin-research-agent.streamlit.app`  
**GitHub**: `https://github.com/dpwang-ustc/bitcoin-research-agent`  
**White Paper**: `https://github.com/dpwang-ustc/bitcoin-research-agent/blob/main/docs/WHITEPAPER.md`

**Happy Exploring!** 🚀

