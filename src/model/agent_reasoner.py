"""
Bitcoin Research Agent - AI 市场洞察智能体

功能：
1. LLM 集成 - 支持 OpenAI/Anthropic/Ollama
2. 数据分析 - 自动分析市场数据
3. 洞察生成 - 生成自然语言市场摘要
4. 多模型支持 - 灵活切换不同 LLM

作者：Bitcoin Research Agent Team
日期：2025-10-26
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. Run: pip install openai")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: Anthropic not installed. Run: pip install anthropic")


class MarketInsightAgent:
    """AI 市场洞察智能体"""
    
    def __init__(
        self,
        provider: str = "openai",  # "openai", "anthropic", "ollama"
        model: str = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        verbose: bool = True
    ):
        """
        初始化 AI Agent
        
        Args:
            provider: LLM 提供商 (openai/anthropic/ollama)
            model: 模型名称（如果为None，使用默认模型）
            api_key: API密钥（如果为None，从环境变量读取）
            temperature: 生成温度
            max_tokens: 最大token数
            verbose: 是否打印详细信息
        """
        self.provider = provider.lower()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.verbose = verbose
        
        # 设置默认模型
        if model is None:
            if self.provider == "openai":
                self.model = "gpt-4o-mini"  # 性价比最高
            elif self.provider == "anthropic":
                self.model = "claude-3-5-sonnet-20241022"
            elif self.provider == "ollama":
                self.model = "llama3.1:8b"
            else:
                raise ValueError(f"Unknown provider: {provider}")
        else:
            self.model = model
        
        # 初始化客户端
        self._init_client(api_key)
        
        self.log(f"✅ AI Agent initialized: {self.provider} / {self.model}")
    
    def _init_client(self, api_key: Optional[str]):
        """初始化 LLM 客户端"""
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI not installed. Run: pip install openai")
            
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            
            self.client = OpenAI(api_key=api_key)
        
        elif self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic not installed. Run: pip install anthropic")
            
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
            
            self.client = Anthropic(api_key=api_key)
        
        elif self.provider == "ollama":
            # Ollama doesn't need API key, runs locally
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    base_url="http://localhost:11434/v1",
                    api_key="ollama"  # dummy key
                )
            except Exception as e:
                raise RuntimeError(f"Failed to connect to Ollama: {e}")
    
    def log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[MarketAgent] {message}")
    
    def generate_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None
    ) -> str:
        """
        生成 LLM 回复
        
        Args:
            prompt: 用户提示词
            system_message: 系统消息
        
        Returns:
            生成的文本
        """
        try:
            if self.provider in ["openai", "ollama"]:
                messages = []
                
                if system_message:
                    messages.append({
                        "role": "system",
                        "content": system_message
                    })
                
                messages.append({
                    "role": "user",
                    "content": prompt
                })
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    system=system_message or "You are a helpful assistant.",
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                return response.content[0].text
            
        except Exception as e:
            self.log(f"❌ Error generating completion: {e}")
            return ""
    
    # ==================== 市场分析功能 ====================
    
    def analyze_market_data(self, stats: Dict[str, Any]) -> str:
        """
        分析市场数据，生成洞察
        
        Args:
            stats: 市场统计数据
        
        Returns:
            AI 生成的市场分析
        """
        self.log("🤖 Analyzing market data with AI...")
        
        # 构建系统消息
        system_message = """你是一位专业的加密货币市场分析师，擅长解读市场数据并给出深刻的洞察。

你的任务：
1. 分析提供的市场数据
2. 识别关键趋势和模式
3. 给出专业、客观的市场评估
4. 提供可操作的交易建议

注意事项：
- 使用专业但易懂的语言
- 基于数据而非主观臆测
- 给出具体的支撑/阻力位
- 识别风险和机会
- 保持中立和客观"""
        
        # 构建提示词
        prompt = self._build_analysis_prompt(stats)
        
        # 生成分析
        analysis = self.generate_completion(prompt, system_message)
        
        return analysis
    
    def _build_analysis_prompt(self, stats: Dict[str, Any]) -> str:
        """构建分析提示词"""
        price = stats.get('price', {})
        regime = stats.get('regime', {})
        volatility = stats.get('volatility', {})
        sentiment = stats.get('sentiment', {})
        capital = stats.get('capital', {})
        
        prompt = f"""请分析以下比特币市场数据并给出专业洞察：

# 价格数据
- 当前价格: ${price.get('current', 0):,.0f}
- 周涨跌幅: {price.get('week_return', 0):+.2f}%
- 周最高: ${price.get('week_high', 0):,.0f}
- 周最低: ${price.get('week_low', 0):,.0f}

# 市场状态
- 当前状态: {regime.get('current_regime', 'N/A')}
- 上周状态: {regime.get('prev_regime', 'N/A')}
- 状态分布: {json.dumps(regime.get('regime_distribution', {}), ensure_ascii=False)}

# 波动率
- 当前波动率: {volatility.get('current', 0):.2f}%
- 波动率变化: {volatility.get('change', 0):+.2f}%

# 市场情绪
- Fear & Greed: {sentiment.get('current', 50):.0f} ({sentiment.get('current_category', 'N/A')})
- 情绪变化: {sentiment.get('change', 0):+.0f}

# 资金流向
- 主力行为: {capital.get('main_behavior', 'N/A')}
- 鲸鱼活动: {capital.get('whale_count', 0)} 次
- 资金流入: {capital.get('inflow_count', 0)} 次
- 资金流出: {capital.get('outflow_count', 0)} 次

请提供：
1. 市场当前状况的综合评估（2-3句话）
2. 关键趋势和模式识别
3. 下周市场展望和操作建议
4. 主要风险点和机会

请用简洁、专业的中文回答，不要使用 Markdown 格式，直接输出文字内容。"""
        
        return prompt
    
    def generate_executive_summary(self, stats: Dict[str, Any]) -> str:
        """
        生成执行摘要
        
        Args:
            stats: 市场统计数据
        
        Returns:
            AI 生成的执行摘要
        """
        self.log("📝 Generating executive summary...")
        
        system_message = """你是一位专业的金融分析师，擅长撰写简洁有力的执行摘要。

要求：
1. 3-5句话概括核心要点
2. 突出最重要的市场变化
3. 给出明确的结论和建议
4. 语言简洁专业"""
        
        price = stats.get('price', {})
        regime = stats.get('regime', {})
        sentiment = stats.get('sentiment', {})
        capital = stats.get('capital', {})
        
        prompt = f"""请为本周比特币市场表现撰写执行摘要：

核心数据：
- 价格: ${price.get('current', 0):,.0f} ({price.get('week_return', 0):+.2f}%)
- 市场状态: {regime.get('current_regime', 'N/A')}
- 市场情绪: {sentiment.get('current_category', 'N/A')} ({sentiment.get('current', 50):.0f})
- 主力行为: {capital.get('main_behavior', 'N/A')}

请用3-5句话总结本周市场表现，包括：
1. 价格和状态变化
2. 最显著的市场特征
3. 整体判断和建议

用简洁的中文，不要使用 Markdown 格式。"""
        
        summary = self.generate_completion(prompt, system_message)
        
        return summary
    
    def generate_outlook(self, stats: Dict[str, Any]) -> str:
        """
        生成下周展望
        
        Args:
            stats: 市场统计数据
        
        Returns:
            AI 生成的市场展望
        """
        self.log("🔮 Generating outlook...")
        
        system_message = """你是一位经验丰富的交易策略分析师。

任务：
1. 基于当前数据预测下周走势
2. 给出具体的操作建议
3. 识别关键观察点
4. 提供风险提示"""
        
        prompt = self._build_outlook_prompt(stats)
        
        outlook = self.generate_completion(prompt, system_message)
        
        return outlook
    
    def _build_outlook_prompt(self, stats: Dict[str, Any]) -> str:
        """构建展望提示词"""
        price = stats.get('price', {})
        regime = stats.get('regime', {})
        sentiment = stats.get('sentiment', {})
        capital = stats.get('capital', {})
        volatility = stats.get('volatility', {})
        
        prompt = f"""基于以下市场数据，请预测下周走势并给出操作建议：

# 本周表现
- 价格走势: {price.get('week_return', 0):+.2f}%
- 市场状态: {regime.get('current_regime', 'N/A')}
- 波动率: {volatility.get('current', 0):.2f}%
- 市场情绪: {sentiment.get('current_category', 'N/A')} ({sentiment.get('current', 50):.0f})
- 主力行为: {capital.get('main_behavior', 'N/A')}

# 支撑/阻力位
- 周最高: ${price.get('week_high', 0):,.0f}
- 周最低: ${price.get('week_low', 0):,.0f}

请提供：
1. 下周市场展望（看涨/看跌/中性）及理由
2. 具体操作建议（建仓/持有/减仓）
3. 关键价格位（支撑/阻力）
4. 主要风险点

用中文回答，不要使用 Markdown 格式。"""
        
        return prompt
    
    def generate_narrative_report(self, stats: Dict[str, Any]) -> Dict[str, str]:
        """
        生成完整的叙事性报告
        
        Args:
            stats: 市场统计数据
        
        Returns:
            包含各部分AI生成内容的字典
        """
        self.log("📊 Generating full narrative report...")
        
        report = {
            'executive_summary': self.generate_executive_summary(stats),
            'market_analysis': self.analyze_market_data(stats),
            'outlook': self.generate_outlook(stats)
        }
        
        self.log("✅ Report generation complete!")
        
        return report


def main():
    """测试函数"""
    import sys
    import io
    
    # Force UTF-8 output for Windows
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - Market Insight Agent")
    print("=" * 70 + "\n")
    
    # 模拟市场数据
    mock_stats = {
        'price': {
            'current': 67500,
            'week_start': 65000,
            'week_high': 68000,
            'week_low': 64500,
            'week_return': 3.85,
            'prev_week_close': 65000
        },
        'regime': {
            'current_regime': '趋势',
            'prev_regime': '震荡',
            'regime_changed': True,
            'regime_distribution': {
                '趋势': 60.0,
                '震荡': 30.0,
                '恐慌': 10.0
            }
        },
        'volatility': {
            'current': 45.5,
            'average': 43.2,
            'previous': 42.0,
            'change': 3.5
        },
        'sentiment': {
            'current': 68,
            'average': 65,
            'previous': 62,
            'current_category': '贪婪',
            'prev_category': '中性',
            'change': 6
        },
        'capital': {
            'main_behavior': '吸筹',
            'whale_count': 15,
            'whale_change': 5,
            'inflow_count': 8,
            'outflow_count': 3
        }
    }
    
    # 测试不同的 provider
    # 如果没有 API key，会报错
    try:
        print("\n测试 AI Agent (需要 API key)...")
        print("如果没有 API key，请设置环境变量：")
        print("  export OPENAI_API_KEY=your_key")
        print("  或使用 Ollama (本地运行): provider='ollama'\n")
        
        # 使用 OpenAI（需要API key）
        agent = MarketInsightAgent(
            provider="openai",
            model="gpt-4o-mini",
            temperature=0.7,
            verbose=True
        )
        
        # 生成报告
        report = agent.generate_narrative_report(mock_stats)
        
        print("\n" + "=" * 70)
        print("生成的报告：")
        print("=" * 70 + "\n")
        
        print("📝 执行摘要：")
        print(report['executive_summary'])
        
        print("\n📊 市场分析：")
        print(report['market_analysis'])
        
        print("\n🔮 下周展望：")
        print(report['outlook'])
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n提示：")
        print("1. 确保已安装: pip install openai anthropic")
        print("2. 设置 API key: export OPENAI_API_KEY=your_key")
        print("3. 或使用本地 Ollama: ollama serve")


if __name__ == '__main__':
    main()
