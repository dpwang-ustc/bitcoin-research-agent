# Bitcoin Research Agent - Public Demo

## 🎯 Overview

This is the **public-facing interactive demo** for Bitcoin Research Agent, showcasing the full capabilities of our AI-driven cryptocurrency market analysis system.

---

## 🚀 Quick Start

### Run the Demo

**Option 1: Direct Command**
```bash
streamlit run src/demo/demo_app.py
```

**Option 2: Using Launcher**

Windows:
```bash
run_demo.bat
```

Linux/Mac:
```bash
chmod +x run_demo.sh
./run_demo.sh
```

The demo will be available at: `http://localhost:8501`

---

## 🌟 Demo Features

### 5 Interactive Modes

1. **🏠 Overview**
   - Project introduction
   - Key metrics and stats
   - Core features showcase
   - Technical highlights

2. **🤖 AI Agent Demo**
   - Interactive query interface
   - Pre-set quick questions
   - Custom query support
   - Real-time analysis
   - Agent architecture visualization

3. **📊 Live Dashboard**
   - Real-time price charts
   - Key metrics display
   - 4 analysis modules
   - Interactive visualizations

4. **📈 Analysis Examples**
   - 4 case studies
   - Historical performance
   - Signal accuracy
   - Trading results

5. **📚 Documentation**
   - Getting started guide
   - Technical documentation
   - Research & white paper
   - Video tutorials & examples

---

## 📊 What to Showcase

### Key Highlights

**Performance Metrics**:
- ✅ 85% Market Regime Accuracy
- ✅ 64% Backtesting Win Rate
- ✅ 1.42 Sharpe Ratio
- ✅ 22.2s Processing Speed

**AI Capabilities**:
- ✅ LangGraph Workflow (10 nodes)
- ✅ GPT-4o-mini Integration
- ✅ Intelligent Task Routing
- ✅ Real-time Analysis

**Analysis Modules**:
- ✅ Market Regime Identification
- ✅ Volatility Analysis
- ✅ Sentiment Analysis
- ✅ Capital Flow Tracking
- ✅ Automated Reporting

---

## 🎯 Demo Scenarios

### For Potential Users

1. **Start with Overview**
   - Show project value
   - Highlight key metrics
   - Explain core features

2. **Demo AI Agent**
   - Try quick questions
   - Ask custom queries
   - Show real-time analysis

3. **Explore Dashboard**
   - Navigate through tabs
   - Interact with charts
   - Review metrics

4. **Review Case Studies**
   - Show successful signals
   - Explain methodology
   - Discuss outcomes

### For Investors

1. **Performance Data**
   - 64% win rate
   - 1.42 Sharpe ratio
   - Consistent results

2. **Technology Stack**
   - LangGraph + GPT-4o-mini
   - Production-ready
   - Scalable architecture

3. **Market Opportunity**
   - Growing crypto market
   - AI/ML adoption
   - Automation trend

### For Developers

1. **Architecture**
   - 5-layer design
   - Modular components
   - Clean code

2. **API Examples**
   - Easy integration
   - Well-documented
   - Extensible

3. **Open Source**
   - MIT License
   - Active development
   - Community welcome

---

## 🌐 Public Deployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub**:
   ```bash
   git push origin main
   ```

2. **Deploy**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect GitHub
   - Select `src/demo/demo_app.py`
   - Deploy!

3. **Access**:
   - URL: `https://bitcoin-research-agent.streamlit.app`
   - Share publicly!

**See**: `docs/DEMO_DEPLOYMENT_GUIDE.md` for detailed deployment instructions.

---

## 💬 Interactive Elements

### AI Agent Queries

**Pre-set Questions**:
- "What is the current Bitcoin market regime?"
- "Analyze current market sentiment"
- "Generate weekly market report"

**Custom Query Examples**:
- "What are the key support and resistance levels?"
- "Is this a good time to buy Bitcoin?"
- "Analyze the last week's price movement"
- "What do whale activities suggest?"

### Dashboard Interactions

**Price Chart**:
- Hover for details
- Zoom and pan
- Time series analysis

**Analysis Tabs**:
- Regime distribution
- Volatility comparison
- Sentiment gauge
- Capital flow status

---

## 📚 Documentation Links

From the demo, users can access:

- **GitHub Repository**: Full source code
- **White Paper**: Research document
- **Documentation**: Technical guides
- **API Reference**: Code examples

---

## 🔒 Configuration

### Optional: Enable AI Features

1. **Get API Key**:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

2. **Set Environment Variable**:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. **Restart Demo**:
   ```bash
   streamlit run src/demo/demo_app.py
   ```

**Note**: Demo works without API keys but with limited AI features.

---

## 🎨 Customization

### Branding

Edit `src/demo/demo_app.py`:

```python
st.set_page_config(
    page_title="Your Custom Title",
    page_icon="🎯",  # Your icon
    layout="wide"
)
```

### Styling

Modify CSS in the `st.markdown()` section:

```python
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #your-color-1, #your-color-2);
        ...
    }
</style>
""", unsafe_allow_html=True)
```

### Content

- Update text and descriptions
- Add/remove features
- Customize metrics
- Modify layout

---

## 📊 Analytics

### Track Usage

**Streamlit Cloud**:
- Built-in analytics dashboard
- View usage stats
- Monitor performance

**Custom Tracking**:
```python
import logging

logging.info(f"User query: {user_query}")
logging.info(f"Demo mode: {demo_mode}")
```

---

## 🐛 Troubleshooting

### Issue: Port in Use
```bash
# Kill process on port 8501
# Mac/Linux: lsof -i :8501
# Windows: netstat -ano | findstr :8501
```

### Issue: Module Not Found
```bash
pip install -r requirements.txt
```

### Issue: Slow Loading
```python
# Use caching
@st.cache_data(ttl=3600)
def load_data():
    return fetch_data()
```

---

## 📈 Performance Tips

1. **Use Caching**:
   ```python
   @st.cache_data(ttl=3600)
   @st.cache_resource
   ```

2. **Lazy Loading**:
   - Load data on demand
   - Use progressive rendering

3. **Optimize Images**:
   - Compress images
   - Use CDN for static assets

4. **Limit Data Size**:
   - Show recent data only
   - Paginate large datasets

---

## 📞 Support

### Get Help
- **GitHub Issues**: Report bugs
- **Discussions**: Ask questions
- **Email**: dpwang@ustc.edu

### Feedback
- What works well?
- What needs improvement?
- Feature requests?

---

## 🎊 Launch Checklist

Before going public:

- [x] Test all features
- [x] Verify API keys work
- [x] Check mobile responsive
- [x] Test on multiple browsers
- [ ] Set up monitoring
- [ ] Create demo video
- [ ] Update README
- [ ] Share on social media

---

## 🔗 Links

- **GitHub**: https://github.com/dpwang-ustc/bitcoin-research-agent
- **White Paper**: [docs/WHITEPAPER.md](../../docs/WHITEPAPER.md)
- **Deployment Guide**: [docs/DEMO_DEPLOYMENT_GUIDE.md](../../docs/DEMO_DEPLOYMENT_GUIDE.md)
- **User Guide**: [docs/DEMO_USER_GUIDE.md](../../docs/DEMO_USER_GUIDE.md)

---

**Ready to showcase the power of AI-driven cryptocurrency analysis!** 🚀

Start the demo and share it with the world!

```bash
streamlit run src/demo/demo_app.py
```

