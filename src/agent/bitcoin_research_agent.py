"""
Bitcoin Research Agent - LangGraph 自驱动研究智能体

功能：
1. 自动化数据采集和处理
2. 多维度并行分析
3. AI 生成市场洞察
4. 自动生成和发布报告
5. 自然语言交互

基于 LangGraph 的状态机架构，实现完全可控的工作流。

作者：Bitcoin Research Agent Team
日期：2025-10-26
"""

import os
import sys
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# LangChain LLM imports
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: langchain-openai not installed")

# 现有模块
from src.data_loader import load_bitcoin_data
from src.feature_engineering import FeatureEngineer
from src.model.market_regime import MarketRegimeIdentifier
from src.analysis.volatility_analyzer import VolatilityAnalyzer
from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.analysis.capital_flow_analyzer import CapitalFlowAnalyzer
from src.model.agent_reasoner import MarketInsightAgent
from src.reports.weekly_report_generator import WeeklyReportGenerator

import pandas as pd


# ==================== 状态定义 ====================

class ResearchState(TypedDict):
    """研究 Agent 的状态"""
    # 输入
    user_input: str
    task_type: str  # "full_analysis", "quick_query", "generate_report"
    
    # 数据
    market_data: Optional[pd.DataFrame]
    processed_data: Optional[pd.DataFrame]
    
    # 分析结果
    regime_analysis: Optional[Dict[str, Any]]
    volatility_analysis: Optional[Dict[str, Any]]
    sentiment_analysis: Optional[Dict[str, Any]]
    capital_analysis: Optional[Dict[str, Any]]
    
    # AI 洞察
    ai_insights: Optional[str]
    
    # 输出
    report: Optional[str]
    response: Optional[str]
    
    # 元数据
    messages: Annotated[List, operator.add]  # 对话历史
    current_step: str  # 当前步骤
    error: Optional[str]  # 错误信息


# ==================== BitcoinResearchAgent 主类 ====================

class BitcoinResearchAgent:
    """
    比特币研究智能体（LangGraph 实现）
    
    特点：
    1. 自动化：自动执行完整的研究流程
    2. 可控：明确定义的工作流，可视化
    3. 并行：支持多个分析任务并行执行
    4. 智能：AI 驱动的洞察生成
    5. 交互：支持自然语言对话
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        verbose: bool = True
    ):
        """
        初始化研究 Agent
        
        Args:
            llm_provider: LLM 提供商（openai/anthropic）
            llm_model: 模型名称
            api_key: API 密钥
            verbose: 是否打印详细信息
        """
        self.verbose = verbose
        self.log("初始化 Bitcoin Research Agent...")
        
        # 初始化 LLM
        self.llm = self._init_llm(llm_provider, llm_model, api_key)
        
        # 初始化各个模块
        self.feature_engineer = FeatureEngineer(verbose=False)
        self.market_regime = MarketRegimeIdentifier(n_regimes=4, method='kmeans', verbose=False)
        self.volatility_analyzer = VolatilityAnalyzer(verbose=False)
        self.sentiment_analyzer = SentimentAnalyzer(verbose=False)
        self.capital_analyzer = CapitalFlowAnalyzer(verbose=False)
        self.market_insight_agent = MarketInsightAgent(
            provider=llm_provider,
            model=llm_model,
            api_key=api_key,
            verbose=False
        )
        
        # 构建 LangGraph 工作流
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        self.log("✅ Bitcoin Research Agent 初始化完成")
    
    def log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[Agent] {message}")
    
    def _init_llm(self, provider: str, model: str, api_key: Optional[str]):
        """初始化 LLM"""
        if provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("Please install: pip install langchain-openai")
            
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found")
            
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                temperature=0.7
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    # ==================== 节点函数 ====================
    
    def _node_route_task(self, state: ResearchState) -> ResearchState:
        """节点：任务路由"""
        self.log(f"路由任务: {state['user_input']}")
        
        # 使用 LLM 判断任务类型
        messages = [
            SystemMessage(content="""你是一个任务路由器。根据用户输入，判断任务类型。

任务类型：
- "full_analysis": 需要完整的数据采集和分析（如"生成周报"、"完整分析"）
- "quick_query": 简单查询（如"比特币价格"、"市场情绪如何"）
- "generate_report": 生成报告（如"生成报告"、"创建周报"）

只回答任务类型，不要其他内容。"""),
            HumanMessage(content=state['user_input'])
        ]
        
        try:
            response = self.llm.invoke(messages)
            task_type = response.content.strip().lower()
            
            if "full" in task_type:
                state['task_type'] = "full_analysis"
            elif "report" in task_type:
                state['task_type'] = "generate_report"
            else:
                state['task_type'] = "quick_query"
            
        except Exception as e:
            self.log(f"路由失败，默认为 full_analysis: {e}")
            state['task_type'] = "full_analysis"
        
        state['current_step'] = "task_routed"
        state['messages'] = [AIMessage(content=f"任务类型：{state['task_type']}")]
        
        return state
    
    def _node_collect_data(self, state: ResearchState) -> ResearchState:
        """节点：数据采集"""
        self.log("采集市场数据...")
        state['current_step'] = "collecting_data"
        
        try:
            # 加载比特币数据
            df = load_bitcoin_data(start='2023-01-01')
            state['market_data'] = df
            state['messages'].append(AIMessage(content=f"✅ 数据采集完成，共 {len(df)} 行"))
            
        except Exception as e:
            state['error'] = f"数据采集失败: {str(e)}"
            state['messages'].append(AIMessage(content=f"❌ 数据采集失败: {str(e)}"))
        
        return state
    
    def _node_process_data(self, state: ResearchState) -> ResearchState:
        """节点：数据处理和特征工程"""
        self.log("处理数据和提取特征...")
        state['current_step'] = "processing_data"
        
        try:
            df = state['market_data']
            
            # 特征工程
            df_processed = self.feature_engineer.process_pipeline(
                df,
                clean=True,
                add_features=True,
                detect_outliers=False,
                handle_missing=True
            )
            
            state['processed_data'] = df_processed
            state['messages'].append(AIMessage(content=f"✅ 特征工程完成，共 {len(df_processed.columns)} 个特征"))
            
        except Exception as e:
            state['error'] = f"数据处理失败: {str(e)}"
            state['messages'].append(AIMessage(content=f"❌ 数据处理失败: {str(e)}"))
        
        return state
    
    def _node_analyze_regime(self, state: ResearchState) -> ResearchState:
        """节点：市场状态分析"""
        self.log("分析市场状态...")
        state['current_step'] = "analyzing_regime"
        
        try:
            df = state['processed_data']
            
            # 市场状态识别
            df_regime = self.market_regime.fit(df, method='kmeans')
            regime_stats = self.market_regime.analyze_regime_characteristics(df_regime)
            
            state['regime_analysis'] = {
                'data': df_regime,
                'stats': regime_stats
            }
            state['messages'].append(AIMessage(content="✅ 市场状态分析完成"))
            
        except Exception as e:
            self.log(f"市场状态分析失败: {e}")
            state['regime_analysis'] = None
        
        return state
    
    def _node_analyze_volatility(self, state: ResearchState) -> ResearchState:
        """节点：波动率分析"""
        self.log("分析波动率...")
        state['current_step'] = "analyzing_volatility"
        
        try:
            df = state['regime_analysis']['data'] if state.get('regime_analysis') else state['processed_data']
            
            # 波动率分析
            df_vol = self.volatility_analyzer.process_pipeline(df)
            
            state['volatility_analysis'] = {'data': df_vol}
            state['messages'].append(AIMessage(content="✅ 波动率分析完成"))
            
        except Exception as e:
            self.log(f"波动率分析失败: {e}")
            state['volatility_analysis'] = None
        
        return state
    
    def _node_analyze_sentiment(self, state: ResearchState) -> ResearchState:
        """节点：情绪分析"""
        self.log("分析市场情绪...")
        state['current_step'] = "analyzing_sentiment"
        
        try:
            df = state['volatility_analysis']['data'] if state.get('volatility_analysis') else state['processed_data']
            
            # 情绪分析
            df_sentiment = self.sentiment_analyzer.process_pipeline(df)
            
            state['sentiment_analysis'] = {'data': df_sentiment}
            state['messages'].append(AIMessage(content="✅ 情绪分析完成"))
            
        except Exception as e:
            self.log(f"情绪分析失败: {e}")
            state['sentiment_analysis'] = None
        
        return state
    
    def _node_analyze_capital(self, state: ResearchState) -> ResearchState:
        """节点：资金流向分析"""
        self.log("分析资金流向...")
        state['current_step'] = "analyzing_capital"
        
        try:
            df = state['sentiment_analysis']['data'] if state.get('sentiment_analysis') else state['processed_data']
            
            # 资金流向分析
            df_capital = self.capital_analyzer.process_pipeline(df)
            
            state['capital_analysis'] = {'data': df_capital}
            state['messages'].append(AIMessage(content="✅ 资金流向分析完成"))
            
        except Exception as e:
            self.log(f"资金流向分析失败: {e}")
            state['capital_analysis'] = None
        
        return state
    
    def _node_generate_insights(self, state: ResearchState) -> ResearchState:
        """节点：生成 AI 洞察"""
        self.log("生成 AI 洞察...")
        state['current_step'] = "generating_insights"
        
        try:
            # 准备数据摘要
            df_final = state['capital_analysis']['data']
            
            # 提取关键统计
            stats = self._extract_key_stats(df_final)
            
            # 使用 AI 生成洞察
            insights = self.market_insight_agent.analyze_market_data(stats)
            
            state['ai_insights'] = insights
            state['messages'].append(AIMessage(content="✅ AI 洞察生成完成"))
            
        except Exception as e:
            self.log(f"AI 洞察生成失败: {e}")
            state['ai_insights'] = "无法生成 AI 洞察"
        
        return state
    
    def _node_generate_report(self, state: ResearchState) -> ResearchState:
        """节点：生成报告"""
        self.log("生成完整报告...")
        state['current_step'] = "generating_report"
        
        try:
            # 使用现有的周报生成器
            generator = WeeklyReportGenerator(
                data_path=None,  # 使用内存中的数据
                use_ai=True,
                verbose=False
            )
            
            # 使用已处理的数据
            generator.df = state['capital_analysis']['data']
            generator.calculate_weekly_stats()
            
            # 生成报告
            report = generator._generate_report_content()
            
            state['report'] = report
            state['response'] = f"✅ 报告生成完成\n\n{report[:500]}...\n\n[完整报告已生成]"
            state['messages'].append(AIMessage(content="✅ 报告生成完成"))
            
        except Exception as e:
            self.log(f"报告生成失败: {e}")
            state['report'] = None
            state['response'] = f"报告生成失败: {str(e)}"
        
        return state
    
    def _node_quick_response(self, state: ResearchState) -> ResearchState:
        """节点：快速响应（简单查询）"""
        self.log("生成快速响应...")
        state['current_step'] = "quick_response"
        
        try:
            # 使用 LLM 回答简单问题
            messages = [
                SystemMessage(content="你是比特币市场分析专家。简洁回答用户问题。"),
                HumanMessage(content=state['user_input'])
            ]
            
            response = self.llm.invoke(messages)
            state['response'] = response.content
            state['messages'].append(AIMessage(content=response.content))
            
        except Exception as e:
            state['response'] = f"无法回答: {str(e)}"
        
        return state
    
    # ==================== 辅助函数 ====================
    
    def _extract_key_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """从 DataFrame 提取关键统计数据"""
        try:
            latest = df.iloc[-1]
            prev_week = df.iloc[-7] if len(df) >= 7 else df.iloc[0]
            
            stats = {
                'price': {
                    'current': float(latest.get('market_Close', 0)),
                    'week_start': float(prev_week.get('market_Close', 0)),
                    'week_return': ((float(latest.get('market_Close', 0)) / 
                                    float(prev_week.get('market_Close', 1))) - 1) * 100
                },
                'regime': {
                    'current_regime': str(latest.get('market_regime_cn', 'N/A'))
                },
                'volatility': {
                    'current': float(latest.get('RealizedVol_30d', 0)) * 100
                },
                'sentiment': {
                    'current': float(latest.get('Fear_Greed_Index', 50)),
                    'current_category': self._get_fg_category(float(latest.get('Fear_Greed_Index', 50)))
                },
                'capital': {
                    'main_behavior': str(latest.get('Main_Behavior_CN', 'N/A'))
                }
            }
            
            return stats
            
        except Exception as e:
            self.log(f"提取统计数据失败: {e}")
            return {}
    
    def _get_fg_category(self, fg: float) -> str:
        """获取 Fear & Greed 类别"""
        if fg < 25: return "极度恐慌"
        elif fg < 45: return "恐慌"
        elif fg < 55: return "中性"
        elif fg < 75: return "贪婪"
        else: return "极度贪婪"
    
    # ==================== 工作流构建 ====================
    
    def _build_workflow(self) -> StateGraph:
        """构建 LangGraph 工作流"""
        self.log("构建 LangGraph 工作流...")
        
        # 创建工作流图
        workflow = StateGraph(ResearchState)
        
        # 添加节点
        workflow.add_node("route_task", self._node_route_task)
        workflow.add_node("collect_data", self._node_collect_data)
        workflow.add_node("process_data", self._node_process_data)
        workflow.add_node("analyze_regime", self._node_analyze_regime)
        workflow.add_node("analyze_volatility", self._node_analyze_volatility)
        workflow.add_node("analyze_sentiment", self._node_analyze_sentiment)
        workflow.add_node("analyze_capital", self._node_analyze_capital)
        workflow.add_node("generate_insights", self._node_generate_insights)
        workflow.add_node("generate_report", self._node_generate_report)
        workflow.add_node("quick_response", self._node_quick_response)
        
        # 定义工作流（基于任务类型的条件路由）
        workflow.set_entry_point("route_task")
        
        # 条件路由
        def should_do_full_analysis(state: ResearchState) -> str:
            """判断是否需要完整分析"""
            task_type = state.get('task_type', 'full_analysis')
            
            if task_type == "quick_query":
                return "quick"
            else:
                return "full"
        
        workflow.add_conditional_edges(
            "route_task",
            should_do_full_analysis,
            {
                "quick": "quick_response",
                "full": "collect_data"
            }
        )
        
        # 完整分析流程
        workflow.add_edge("collect_data", "process_data")
        workflow.add_edge("process_data", "analyze_regime")
        workflow.add_edge("analyze_regime", "analyze_volatility")
        workflow.add_edge("analyze_volatility", "analyze_sentiment")
        workflow.add_edge("analyze_sentiment", "analyze_capital")
        workflow.add_edge("analyze_capital", "generate_insights")
        workflow.add_edge("generate_insights", "generate_report")
        
        # 结束节点
        workflow.add_edge("generate_report", END)
        workflow.add_edge("quick_response", END)
        
        self.log("✅ 工作流构建完成")
        
        return workflow
    
    # ==================== 公共接口 ====================
    
    def run(self, user_input: str = "生成完整市场分析报告") -> Dict[str, Any]:
        """
        运行 Agent
        
        Args:
            user_input: 用户输入
        
        Returns:
            包含分析结果的字典
        """
        self.log(f"\n{'='*70}")
        self.log(f"开始执行任务: {user_input}")
        self.log(f"{'='*70}\n")
        
        # 初始化状态
        initial_state = ResearchState(
            user_input=user_input,
            task_type="",
            market_data=None,
            processed_data=None,
            regime_analysis=None,
            volatility_analysis=None,
            sentiment_analysis=None,
            capital_analysis=None,
            ai_insights=None,
            report=None,
            response=None,
            messages=[],
            current_step="initialized",
            error=None
        )
        
        # 执行工作流
        try:
            result = self.app.invoke(initial_state)
            
            self.log(f"\n{'='*70}")
            self.log("✅ 任务执行完成")
            self.log(f"{'='*70}\n")
            
            return result
            
        except Exception as e:
            self.log(f"❌ 任务执行失败: {e}")
            return {
                'error': str(e),
                'response': f"执行失败: {str(e)}"
            }
    
    def chat(self, message: str) -> str:
        """
        对话接口
        
        Args:
            message: 用户消息
        
        Returns:
            Agent 的回复
        """
        result = self.run(message)
        return result.get('response', '无响应')


def main():
    """测试函数"""
    # Force UTF-8 output for Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - LangGraph 实现")
    print("=" * 70 + "\n")
    
    try:
        # 创建 Agent
        agent = BitcoinResearchAgent(
            llm_provider="openai",
            llm_model="gpt-4o-mini",
            verbose=True
        )
        
        print("\n✅ Agent 创建成功！\n")
        
        # 测试：生成完整报告
        print("测试 1: 生成完整市场分析报告")
        print("-" * 70)
        
        result = agent.run("生成本周比特币市场分析报告")
        
        if result.get('report'):
            print("\n📊 报告预览:")
            print(result['report'][:1000])
            print("\n[... 完整报告已生成 ...]")
        else:
            print(f"\n响应: {result.get('response', '无响应')}")
        
        print("\n" + "=" * 70)
        print("测试完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n提示:")
        print("1. 确保已设置 OPENAI_API_KEY")
        print("2. 确保已安装所有依赖: pip install -r requirements.txt")


if __name__ == '__main__':
    main()

