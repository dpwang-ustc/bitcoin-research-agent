# Bitcoin Research Agent - Public Demo Deployment Guide

## 📋 Overview

This guide explains how to deploy and showcase the Bitcoin Research Agent public demo. The demo provides an interactive interface to explore all system capabilities, including AI agent analysis, market insights, and automated reporting.

---

## 🚀 Quick Start

### Option 1: Local Deployment (Fastest)

```bash
# Navigate to project directory
cd bitcoin-research-agent

# Run the demo
streamlit run src/demo/demo_app.py
```

The demo will be available at: `http://localhost:8501`

### Option 2: Using Launcher Script

**Windows**:
```bash
run_demo.bat
```

**Linux/Mac**:
```bash
chmod +x run_demo.sh
./run_demo.sh
```

---

## 🌐 Public Deployment Options

### 1. Streamlit Cloud (Recommended ⭐)

**Advantages**:
- ✅ Free for public repos
- ✅ Automatic HTTPS
- ✅ Easy deployment
- ✅ Auto-restart on updates

**Steps**:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add public demo"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select repository: `dpwang-ustc/bitcoin-research-agent`
   - Main file path: `src/demo/demo_app.py`
   - Click "Deploy"

3. **Configure Secrets** (Optional - for AI features):
   - In app settings, add:
     ```toml
     OPENAI_API_KEY = "your-api-key-here"
     ```

4. **Access Your Demo**:
   - URL: `https://bitcoin-research-agent.streamlit.app`
   - Share this URL publicly!

**Estimated Time**: 5-10 minutes  
**Cost**: Free

---

### 2. Heroku Deployment

**Advantages**:
- ✅ Full control
- ✅ Custom domain support
- ✅ Scalable

**Steps**:

1. **Create Heroku App**:
   ```bash
   heroku create bitcoin-research-agent-demo
   ```

2. **Create Procfile**:
   ```
   web: sh setup.sh && streamlit run src/demo/demo_app.py
   ```

3. **Create setup.sh**:
   ```bash
   mkdir -p ~/.streamlit/
   echo "[server]
   headless = true
   port = $PORT
   enableCORS = false
   " > ~/.streamlit/config.toml
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

5. **Set Environment Variables**:
   ```bash
   heroku config:set OPENAI_API_KEY="your-api-key"
   ```

**Estimated Time**: 15-20 minutes  
**Cost**: Free tier available

---

### 3. Vercel Deployment

**Advantages**:
- ✅ Fast deployment
- ✅ Global CDN
- ✅ Free tier

**Steps**:

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Configure**:
   - Add `vercel.json`:
     ```json
     {
       "builds": [
         {
           "src": "src/demo/demo_app.py",
           "use": "@vercel/python"
         }
       ]
     }
     ```

**Estimated Time**: 10 minutes  
**Cost**: Free

---

### 4. Docker Deployment

**Advantages**:
- ✅ Consistent environment
- ✅ Easy scaling
- ✅ Platform independent

**Steps**:

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.12-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "src/demo/demo_app.py", "--server.port=8501", "--server.headless=true"]
   ```

2. **Build Image**:
   ```bash
   docker build -t bitcoin-research-agent-demo .
   ```

3. **Run Container**:
   ```bash
   docker run -p 8501:8501 -e OPENAI_API_KEY="your-key" bitcoin-research-agent-demo
   ```

4. **Deploy to Cloud**:
   - **Docker Hub**: `docker push username/bitcoin-research-agent-demo`
   - **AWS ECS**: Deploy container
   - **Google Cloud Run**: `gcloud run deploy`

**Estimated Time**: 20-30 minutes  
**Cost**: Varies by platform

---

### 5. Alibaba Cloud Deployment

**Advantages**:
- ✅ China-friendly
- ✅ Fast in Asia
- ✅ Flexible pricing

**Option A: ECS (Elastic Compute Service)**

1. **Create ECS Instance**:
   - OS: Ubuntu 20.04
   - Specs: 2 vCPU, 4GB RAM
   - Security Group: Open port 8501

2. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3.12 python3-pip git
   ```

3. **Deploy Application**:
   ```bash
   git clone https://github.com/dpwang-ustc/bitcoin-research-agent
   cd bitcoin-research-agent
   pip3 install -r requirements.txt
   
   # Run with systemd
   sudo systemctl enable bitcoin-demo
   sudo systemctl start bitcoin-demo
   ```

4. **Configure Nginx** (Optional):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

**Option B: Function Compute**
- Serverless deployment
- Pay-per-use
- Auto-scaling

**Option C: Container Service**
- Kubernetes-based
- High availability
- Load balancing

**Estimated Time**: 30-45 minutes  
**Cost**: Starting from ¥100/month

---

## 🔧 Configuration

### Environment Variables

Create `.env` file (optional):

```bash
# OpenAI API (for AI features)
OPENAI_API_KEY=your-openai-api-key

# Anthropic API (alternative)
ANTHROPIC_API_KEY=your-anthropic-api-key

# Server configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
```

### Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#262730"
```

---

## 📊 Demo Features

### 1. Overview Page
- Project introduction
- Key metrics and stats
- Core features showcase
- Technical highlights

### 2. AI Agent Demo
- Interactive query interface
- Pre-set quick questions
- Custom query support
- Real-time analysis
- Agent architecture visualization

### 3. Live Dashboard
- Real-time price chart
- Key metrics display
- Analysis modules (Regime, Volatility, Sentiment, Capital Flow)
- Interactive visualizations

### 4. Analysis Examples
- Case studies
- Historical performance
- Signal accuracy
- Trading results

### 5. Documentation
- Getting started guide
- Technical documentation
- Research & white paper
- Video tutorials
- Code examples

---

## 🎯 Usage Scenarios

### For Developers
```python
# Access via API
import requests

response = requests.post(
    "http://your-demo-url/api/analyze",
    json={"query": "What is the current market state?"}
)
print(response.json())
```

### For Traders
1. Open demo in browser
2. Navigate to "Live Dashboard"
3. Review market metrics
4. Check AI Agent recommendations
5. Generate custom reports

### For Researchers
1. Access "Documentation" section
2. Review white paper
3. Explore code examples
4. Run custom analyses

---

## 🔒 Security Considerations

### API Keys
- **Never** commit API keys to Git
- Use environment variables
- Rotate keys regularly
- Monitor usage

### Rate Limiting
```python
# Add to demo_app.py
from streamlit_extras.rate_limiter import rate_limiter

@rate_limiter(max_calls=100, period=3600)
def analyze_market():
    # Your analysis code
    pass
```

### CORS Configuration
```python
# Only allow specific origins
st.set_page_config(
    ...,
    cors_origins=["https://your-domain.com"]
)
```

---

## 📈 Performance Optimization

### Caching
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    return fetch_market_data()

@st.cache_resource
def load_model():
    return MarketRegimeIdentifier()
```

### Lazy Loading
```python
# Load components on demand
if st.button("Generate Report"):
    report = generate_report()  # Only load when clicked
```

### CDN for Static Assets
- Use CDN for images
- Compress CSS/JS
- Optimize chart rendering

---

## 🐛 Troubleshooting

### Issue: Port Already in Use
```bash
# Find process using port
lsof -i :8501  # Mac/Linux
netstat -ano | findstr :8501  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

### Issue: Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: API Key Error
```bash
# Verify API key is set
echo $OPENAI_API_KEY  # Mac/Linux
echo %OPENAI_API_KEY%  # Windows
```

### Issue: Memory Error
```python
# Reduce data size
df = df.tail(100)  # Use last 100 rows only

# Clear cache
st.cache_data.clear()
```

---

## 📊 Monitoring & Analytics

### Streamlit Cloud Analytics
- Built-in analytics dashboard
- View usage statistics
- Monitor errors
- Track performance

### Custom Analytics
```python
import logging

logging.basicConfig(
    filename='demo_usage.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Log user interactions
logging.info(f"User query: {user_query}")
```

### Google Analytics Integration
```html
<!-- Add to demo_app.py -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## 🎊 Launch Checklist

Before going public:

- [ ] Test all demo features
- [ ] Verify API keys are set
- [ ] Check mobile responsiveness
- [ ] Test on multiple browsers
- [ ] Set up error monitoring
- [ ] Create backup
- [ ] Prepare demo video/screenshots
- [ ] Update README with demo link
- [ ] Share on social media
- [ ] Monitor initial feedback

---

## 📞 Support & Feedback

### Getting Help
- **GitHub Issues**: [Report bugs](https://github.com/dpwang-ustc/bitcoin-research-agent/issues)
- **Discussions**: [Ask questions](https://github.com/dpwang-ustc/bitcoin-research-agent/discussions)
- **Email**: dpwang@ustc.edu

### Feedback
We welcome feedback! Please let us know:
- What features you like
- What could be improved
- Any bugs or issues
- Feature requests

---

## 🚀 Next Steps

After deploying the demo:

1. **Share widely**:
   - Social media
   - Crypto communities
   - Tech forums
   - LinkedIn

2. **Gather feedback**:
   - User surveys
   - Analytics review
   - Community discussions

3. **Iterate**:
   - Fix bugs
   - Add features
   - Improve UX

4. **Scale**:
   - Optimize performance
   - Add more data sources
   - Enhance AI capabilities

---

**Congratulations on deploying Bitcoin Research Agent Demo!** 🎉

Your public demo is now ready to showcase the power of AI-driven cryptocurrency analysis to the world!

---

**Demo URL**: `https://bitcoin-research-agent.streamlit.app` (after Streamlit Cloud deployment)  
**GitHub**: `https://github.com/dpwang-ustc/bitcoin-research-agent`  
**Version**: 1.0.0  
**Last Updated**: 2025-10-26

