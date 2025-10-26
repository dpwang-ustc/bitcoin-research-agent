"""
Bitcoin Research Agent - 自动周报生成器

功能：
1. 数据聚合 - 从各模块获取数据
2. 周度统计 - 计算本周vs上周变化
3. 报告生成 - 生成结构化Markdown周报
4. 图表嵌入 - 生成并嵌入可视化
5. 多格式导出 - Markdown/HTML

作者：Bitcoin Research Agent Team
日期：2025-10-26
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class WeeklyReportGenerator:
    """自动周报生成器"""
    
    def __init__(self, data_path: str = 'data/processed/capital_flow_analysis.csv', 
                 verbose: bool = True):
        """
        初始化周报生成器
        
        Args:
            data_path: 数据文件路径
            verbose: 是否打印详细信息
        """
        self.data_path = data_path
        self.verbose = verbose
        self.df = None
        self.week_data = None
        self.prev_week_data = None
        self.stats = {}
        
    def log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[WeeklyReport] {message}")
    
    # ==================== 数据加载 ====================
    
    def load_data(self):
        """加载数据"""
        self.log("加载数据...")
        try:
            self.df = pd.read_csv(self.data_path, index_col=0, parse_dates=True)
            self.log(f"  成功加载 {len(self.df)} 行数据")
            return True
        except FileNotFoundError:
            self.log(f"错误: 找不到数据文件 {self.data_path}")
            return False
    
    def get_week_data(self, end_date: Optional[datetime] = None, 
                     weeks_back: int = 0) -> pd.DataFrame:
        """
        获取指定周的数据
        
        Args:
            end_date: 结束日期（默认为最新日期）
            weeks_back: 往前推几周（0=本周，1=上周）
        
        Returns:
            该周的数据
        """
        if end_date is None:
            end_date = self.df.index[-1]
        
        # 计算周的开始和结束日期
        week_end = end_date - timedelta(days=7 * weeks_back)
        week_start = week_end - timedelta(days=6)
        
        # 筛选数据
        week_data = self.df[(self.df.index >= week_start) & (self.df.index <= week_end)]
        
        return week_data
    
    # ==================== 统计计算 ====================
    
    def calculate_weekly_stats(self):
        """计算周度统计数据"""
        self.log("计算周度统计...")
        
        # 获取本周和上周数据
        self.week_data = self.get_week_data(weeks_back=0)
        self.prev_week_data = self.get_week_data(weeks_back=1)
        
        if len(self.week_data) == 0 or len(self.prev_week_data) == 0:
            self.log("警告: 周数据不足")
            return {}
        
        stats = {}
        
        # 1. 价格统计
        stats['price'] = self._calculate_price_stats()
        
        # 2. 市场状态统计
        stats['regime'] = self._calculate_regime_stats()
        
        # 3. 波动率统计
        stats['volatility'] = self._calculate_volatility_stats()
        
        # 4. 情绪统计
        stats['sentiment'] = self._calculate_sentiment_stats()
        
        # 5. 资金流向统计
        stats['capital'] = self._calculate_capital_stats()
        
        self.stats = stats
        self.log(f"  计算完成，统计了 {len(stats)} 个维度")
        
        return stats
    
    def _calculate_price_stats(self) -> Dict:
        """计算价格统计"""
        current = self.week_data['market_Close'].iloc[-1]
        week_start = self.week_data['market_Close'].iloc[0]
        week_high = self.week_data['market_High'].max()
        week_low = self.week_data['market_Low'].min()
        week_return = (current / week_start - 1) * 100
        
        prev_current = self.prev_week_data['market_Close'].iloc[-1]
        
        return {
            'current': current,
            'week_start': week_start,
            'week_high': week_high,
            'week_low': week_low,
            'week_return': week_return,
            'prev_week_close': prev_current,
            'week_change': (current / prev_current - 1) * 100
        }
    
    def _calculate_regime_stats(self) -> Dict:
        """计算市场状态统计"""
        if 'market_regime_cn' not in self.week_data.columns:
            return {}
        
        # 本周状态分布
        current_regime = self.week_data['market_regime_cn'].mode()[0]
        regime_counts = self.week_data['market_regime_cn'].value_counts()
        regime_dist = (regime_counts / len(self.week_data) * 100).to_dict()
        
        # 上周主导状态
        prev_regime = self.prev_week_data['market_regime_cn'].mode()[0]
        
        return {
            'current_regime': current_regime,
            'prev_regime': prev_regime,
            'regime_changed': current_regime != prev_regime,
            'regime_distribution': regime_dist
        }
    
    def _calculate_volatility_stats(self) -> Dict:
        """计算波动率统计"""
        if 'RealizedVol_30d' not in self.week_data.columns:
            return {}
        
        current_vol = self.week_data['RealizedVol_30d'].iloc[-1] * 100
        avg_vol = self.week_data['RealizedVol_30d'].mean() * 100
        prev_vol = self.prev_week_data['RealizedVol_30d'].iloc[-1] * 100
        
        return {
            'current': current_vol,
            'average': avg_vol,
            'previous': prev_vol,
            'change': current_vol - prev_vol,
            'change_pct': (current_vol / prev_vol - 1) * 100 if prev_vol > 0 else 0
        }
    
    def _calculate_sentiment_stats(self) -> Dict:
        """计算情绪统计"""
        if 'Fear_Greed_Index' not in self.week_data.columns:
            return {}
        
        current_fg = self.week_data['Fear_Greed_Index'].iloc[-1]
        avg_fg = self.week_data['Fear_Greed_Index'].mean()
        prev_fg = self.prev_week_data['Fear_Greed_Index'].iloc[-1]
        
        # 判断情绪类别
        def get_fg_category(fg):
            if fg < 25: return "极度恐慌"
            elif fg < 45: return "恐慌"
            elif fg < 55: return "中性"
            elif fg < 75: return "贪婪"
            else: return "极度贪婪"
        
        return {
            'current': current_fg,
            'average': avg_fg,
            'previous': prev_fg,
            'current_category': get_fg_category(current_fg),
            'prev_category': get_fg_category(prev_fg),
            'change': current_fg - prev_fg
        }
    
    def _calculate_capital_stats(self) -> Dict:
        """计算资金流向统计"""
        stats = {}
        
        # 鲸鱼活动
        if 'Is_Whale_Activity' in self.week_data.columns:
            whale_count = self.week_data['Is_Whale_Activity'].sum()
            prev_whale_count = self.prev_week_data['Is_Whale_Activity'].sum()
            stats['whale_count'] = whale_count
            stats['whale_change'] = whale_count - prev_whale_count
        
        # 主力行为
        if 'Main_Behavior_CN' in self.week_data.columns:
            main_behavior = self.week_data['Main_Behavior_CN'].mode()[0]
            behavior_dist = self.week_data['Main_Behavior_CN'].value_counts()
            stats['main_behavior'] = main_behavior
            stats['behavior_distribution'] = (behavior_dist / len(self.week_data) * 100).to_dict()
        
        # 资金异动
        if 'Capital_Anomaly' in self.week_data.columns:
            anomalies = self.week_data[self.week_data['Capital_Anomaly'] != 'Normal']
            inflows = len(anomalies[anomalies['Capital_Anomaly'] == 'Large Inflow'])
            outflows = len(anomalies[anomalies['Capital_Anomaly'] == 'Large Outflow'])
            stats['inflow_count'] = inflows
            stats['outflow_count'] = outflows
        
        return stats
    
    # ==================== 报告生成 ====================
    
    def generate_report(self, output_path: str = 'reports/weekly_report.md') -> str:
        """
        生成周报
        
        Args:
            output_path: 输出文件路径
        
        Returns:
            报告内容
        """
        self.log("生成周报...")
        
        # 加载数据
        if self.df is None:
            if not self.load_data():
                return ""
        
        # 计算统计
        if not self.stats:
            self.calculate_weekly_stats()
        
        # 生成报告内容
        report = self._generate_report_content()
        
        # 保存报告
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.log(f"  报告已保存到: {output_path}")
        
        return report
    
    def _generate_report_content(self) -> str:
        """生成报告内容"""
        # 获取报告周期
        week_start = self.week_data.index[0].strftime('%Y-%m-%d')
        week_end = self.week_data.index[-1].strftime('%Y-%m-%d')
        
        # 生成各部分内容
        report_parts = [
            self._generate_header(week_start, week_end),
            self._generate_summary(),
            self._generate_market_overview(),
            self._generate_technical_analysis(),
            self._generate_sentiment_analysis(),
            self._generate_capital_flow(),
            self._generate_outlook(),
            self._generate_footer()
        ]
        
        return '\n\n'.join(report_parts)
    
    def _generate_header(self, week_start: str, week_end: str) -> str:
        """生成报告头部"""
        return f"""# 📊 Bitcoin 市场周报

**报告周期**: {week_start} ~ {week_end}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**作者**: Bitcoin Research Agent

---"""
    
    def _generate_summary(self) -> str:
        """生成执行摘要"""
        price = self.stats['price']
        regime = self.stats.get('regime', {})
        sentiment = self.stats.get('sentiment', {})
        
        return f"""## 📝 执行摘要

**本周核心观点**:

- 💵 **价格**: ${price['current']:,.0f} ({price['week_return']:+.2f}%)
- 📊 **市场状态**: {regime.get('current_regime', 'N/A')}
- 😊 **市场情绪**: {sentiment.get('current_category', 'N/A')} ({sentiment.get('current', 0):.0f})
- 🎯 **主力行为**: {self.stats.get('capital', {}).get('main_behavior', 'N/A')}

本周市场{'上涨' if price['week_return'] > 0 else '下跌'}**{abs(price['week_return']):.2f}%**，
处于**{regime.get('current_regime', 'N/A')}**状态，
市场情绪为**{sentiment.get('current_category', 'N/A')}**。

---"""
    
    def _generate_market_overview(self) -> str:
        """生成市场概览"""
        price = self.stats['price']
        regime = self.stats.get('regime', {})
        
        # 价格变化描述
        if price['week_return'] > 5:
            price_desc = "大幅上涨"
        elif price['week_return'] > 2:
            price_desc = "温和上涨"
        elif price['week_return'] > -2:
            price_desc = "窄幅震荡"
        elif price['week_return'] > -5:
            price_desc = "温和下跌"
        else:
            price_desc = "大幅下跌"
        
        content = f"""## 📊 市场概览

### 价格走势

本周比特币价格{price_desc}，周初开盘价为**${price['week_start']:,.0f}**，
周末收于**${price['current']:,.0f}**，周涨跌幅为**{price['week_return']:+.2f}%**。

| 指标 | 数值 |
|------|------|
| 周收盘价 | ${price['current']:,.0f} |
| 周涨跌幅 | {price['week_return']:+.2f}% |
| 周最高价 | ${price['week_high']:,.0f} |
| 周最低价 | ${price['week_low']:,.0f} |
| 周振幅 | {(price['week_high'] / price['week_low'] - 1) * 100:.2f}% |

### 市场状态"""
        
        if regime:
            regime_dist = regime.get('regime_distribution', {})
            content += f"""

本周市场主要处于**{regime['current_regime']}**状态"""
            
            if regime.get('regime_changed', False):
                content += f"，相比上周的**{regime['prev_regime']}**状态有所变化"
            
            content += "。\n\n**本周状态分布**:\n"
            for state, pct in regime_dist.items():
                content += f"- {state}: {pct:.1f}%\n"
        
        content += "\n---"
        
        return content
    
    def _generate_technical_analysis(self) -> str:
        """生成技术分析"""
        vol = self.stats.get('volatility', {})
        
        if not vol:
            return "## 📈 技术分析\n\n暂无技术指标数据。\n\n---"
        
        vol_trend = "上升" if vol.get('change', 0) > 0 else "下降"
        
        content = f"""## 📈 技术分析

### 波动率

本周市场波动率为**{vol['current']:.2f}%**，相比上周{vol_trend}**{abs(vol['change']):.2f}个百分点**。

| 指标 | 本周 | 上周 | 变化 |
|------|------|------|------|
| 当前波动率 | {vol['current']:.2f}% | {vol['previous']:.2f}% | {vol['change']:+.2f}% |
| 周平均波动率 | {vol['average']:.2f}% | - | - |

**波动率解读**: """
        
        if vol['current'] > 50:
            content += "市场处于高波动状态，风险较大。"
        elif vol['current'] > 30:
            content += "市场波动适中，正常交易环境。"
        else:
            content += "市场波动较低，相对平稳。"
        
        content += "\n\n---"
        
        return content
    
    def _generate_sentiment_analysis(self) -> str:
        """生成情绪分析"""
        sentiment = self.stats.get('sentiment', {})
        
        if not sentiment:
            return "## 😊 情绪分析\n\n暂无情绪数据。\n\n---"
        
        fg_change_desc = "上升" if sentiment.get('change', 0) > 0 else "下降"
        
        content = f"""## 😊 情绪分析

### Fear & Greed Index

本周市场情绪为**{sentiment['current_category']}**（{sentiment['current']:.0f}），
相比上周的**{sentiment['prev_category']}**有所{fg_change_desc}。

| 指标 | 本周 | 上周 | 变化 |
|------|------|------|------|
| F&G指数 | {sentiment['current']:.0f} | {sentiment['previous']:.0f} | {sentiment['change']:+.0f} |
| 情绪等级 | {sentiment['current_category']} | {sentiment['prev_category']} | - |

**情绪解读**: """
        
        if sentiment['current'] < 25:
            content += "市场极度恐慌，可能是抄底良机。"
        elif sentiment['current'] < 45:
            content += "市场较为恐慌，可以考虑分批建仓。"
        elif sentiment['current'] < 55:
            content += "市场情绪中性，观望为主。"
        elif sentiment['current'] < 75:
            content += "市场较为贪婪，注意控制仓位。"
        else:
            content += "市场极度贪婪，建议谨慎操作，警惕回调。"
        
        content += "\n\n---"
        
        return content
    
    def _generate_capital_flow(self) -> str:
        """生成资金流向分析"""
        capital = self.stats.get('capital', {})
        
        if not capital:
            return "## 💰 资金流向\n\n暂无资金数据。\n\n---"
        
        content = f"""## 💰 资金流向

### 主力行为

本周主力行为以**{capital.get('main_behavior', 'N/A')}**为主。"""
        
        if 'behavior_distribution' in capital:
            content += "\n\n**行为分布**:\n"
            for behavior, pct in capital['behavior_distribution'].items():
                content += f"- {behavior}: {pct:.1f}%\n"
        
        content += "\n### 鲸鱼活动\n"
        
        if 'whale_count' in capital:
            whale_change_desc = "增加" if capital.get('whale_change', 0) > 0 else "减少"
            content += f"""
本周检测到**{capital['whale_count']}次**鲸鱼活动，
相比上周{whale_change_desc}**{abs(capital.get('whale_change', 0))}次**。"""
        
        content += "\n\n### 资金异动\n"
        
        if 'inflow_count' in capital:
            content += f"""
- 大额流入事件: **{capital['inflow_count']}次**
- 大额流出事件: **{capital['outflow_count']}次**"""
            
            if capital['inflow_count'] > capital['outflow_count']:
                content += "\n- 解读: 资金净流入，看涨信号。"
            elif capital['inflow_count'] < capital['outflow_count']:
                content += "\n- 解读: 资金净流出，看跌信号。"
            else:
                content += "\n- 解读: 资金流入流出平衡。"
        
        content += "\n\n---"
        
        return content
    
    def _generate_outlook(self) -> str:
        """生成下周展望"""
        price = self.stats['price']
        regime = self.stats.get('regime', {})
        sentiment = self.stats.get('sentiment', {})
        capital = self.stats.get('capital', {})
        
        # 综合评分
        score = 0
        
        # 价格因素
        if price['week_return'] > 0:
            score += 1
        else:
            score -= 1
        
        # 情绪因素
        if sentiment and sentiment.get('current', 50) < 40:
            score += 2  # 恐慌是机会
        elif sentiment and sentiment.get('current', 50) > 70:
            score -= 2  # 贪婪是风险
        
        # 主力行为
        if capital:
            behavior = capital.get('main_behavior', '')
            if behavior == '吸筹':
                score += 2
            elif behavior == '派发':
                score -= 2
        
        # 生成展望
        if score >= 3:
            outlook = "看涨"
            suggestion = "建议适当增加仓位，但注意风险控制。"
        elif score >= 1:
            outlook = "谨慎乐观"
            suggestion = "可以小幅建仓，密切关注市场变化。"
        elif score >= -1:
            outlook = "中性观望"
            suggestion = "建议观望为主，等待更明确信号。"
        elif score >= -3:
            outlook = "谨慎看跌"
            suggestion = "建议减少仓位，保护利润。"
        else:
            outlook = "看跌"
            suggestion = "建议大幅减仓或清仓，规避风险。"
        
        content = f"""## 🎯 下周展望

### 综合判断

基于本周市场表现，我们对下周走势持**{outlook}**态度。

**操作建议**: {suggestion}

### 关键观察点

1. **价格支撑/阻力位**: 
   - 支撑: ${price['week_low'] * 0.98:,.0f}
   - 阻力: ${price['week_high'] * 1.02:,.0f}

2. **市场状态**: 关注是否延续{regime.get('current_regime', 'N/A')}状态

3. **情绪指标**: 关注F&G指数是否突破{sentiment.get('current', 50):.0f}±10

4. **资金流向**: 关注鲸鱼活动和主力行为变化

### 风险提示

- ⚠️ 市场有风险，投资需谨慎
- ⚠️ 本报告仅供参考，不构成投资建议
- ⚠️ 请根据自身风险承受能力决策

---"""
        
        return content
    
    def _generate_footer(self) -> str:
        """生成报告尾部"""
        return f"""## 📚 附录

### 数据来源

- 市场数据: Binance, CoinGecko
- 链上数据: CryptoQuant, Glassnode
- 宏观数据: Yahoo Finance
- 情绪数据: 多维度计算

### 方法论

本报告基于以下分析框架：
- 市场状态识别（K-Means + HMM）
- 波动率分析（GARCH模型）
- 情绪分析（Fear & Greed Index）
- 资金流向追踪（鲸鱼监控）

---

**免责声明**: 本报告由Bitcoin Research Agent自动生成，内容仅供参考学习，不构成任何投资建议。
投资有风险，入市需谨慎。请根据自身情况理性决策。

---

**© 2025 Bitcoin Research Agent Team**"""


def main():
    """主函数"""
    # Force UTF-8 output for Windows
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - Weekly Report Generator")
    print("=" * 70 + "\n")
    
    # 创建生成器
    generator = WeeklyReportGenerator(verbose=True)
    
    # 生成周报
    report = generator.generate_report()
    
    if report:
        print("\n" + "=" * 70)
        print("报告生成成功！")
        print("=" * 70)
        print(f"\n预览:\n")
        print(report[:500] + "...\n")
        print(f"完整报告已保存，共 {len(report)} 字符")
    else:
        print("\n报告生成失败！")


if __name__ == '__main__':
    main()

