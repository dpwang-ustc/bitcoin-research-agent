"""
Bitcoin Research Agent - 主力资金追踪分析

功能：
1. 资金流向分析（流入/流出）
2. 大户持仓追踪（鲸鱼监控）
3. 资金聚集度指标
4. 主力行为识别
5. 资金与价格关系分析

作者：Bitcoin Research Agent Team
日期：2025-10-25
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class CapitalFlowAnalyzer:
    """主力资金流向分析器"""
    
    def __init__(self, verbose: bool = True):
        """
        初始化分析器
        
        Args:
            verbose: 是否打印详细信息
        """
        self.verbose = verbose
        
        # 鲸鱼阈值（成交量分位数）
        self.whale_threshold = 0.95  # 前5%的大额交易
        
        # 主力行为模式
        self.patterns = {
            'accumulation': '吸筹',  # 价跌量增
            'distribution': '派发',   # 价涨量增
            'pump': '拉升',          # 价涨量涨
            'dump': '砸盘',          # 价跌量涨
            'sideways': '横盘'       # 价平量平
        }
    
    def log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[CapitalFlow] {message}")
    
    # ==================== 资金流向分析 ====================
    
    def calculate_money_flow(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算资金流向指标
        
        Args:
            df: 输入DataFrame
        
        Returns:
            添加了资金流向指标的DataFrame
        """
        self.log("计算资金流向指标...")
        df = df.copy()
        
        # 确保列名
        close_col = 'market_Close' if 'market_Close' in df.columns else 'Close'
        high_col = 'market_High' if 'market_High' in df.columns else 'High'
        low_col = 'market_Low' if 'market_Low' in df.columns else 'Low'
        volume_col = 'market_Volume' if 'market_Volume' in df.columns else 'Volume'
        
        # 1. 典型价格 (Typical Price)
        df['Typical_Price'] = (df[high_col] + df[low_col] + df[close_col]) / 3
        
        # 2. 资金流量 (Money Flow)
        df['Money_Flow'] = df['Typical_Price'] * df[volume_col]
        
        # 3. 资金流向 (正负)
        # 如果典型价格上涨，为正资金流；下跌为负资金流
        price_change = df['Typical_Price'].diff()
        df['Money_Flow_Direction'] = np.where(price_change > 0, 
                                              df['Money_Flow'], 
                                              -df['Money_Flow'])
        
        # 4. 累积资金流 (Cumulative Money Flow)
        df['Cumulative_Money_Flow'] = df['Money_Flow_Direction'].cumsum()
        
        # 5. 资金流强度 (Money Flow Index - MFI类似)
        window = 14
        positive_flow = df['Money_Flow'].where(price_change > 0, 0).rolling(window).sum()
        negative_flow = df['Money_Flow'].where(price_change < 0, 0).rolling(window).sum()
        
        money_ratio = positive_flow / (negative_flow + 1e-10)
        df['MFI'] = 100 - (100 / (1 + money_ratio))
        
        # 6. 净资金流 (Net Money Flow)
        df['Net_Money_Flow'] = positive_flow - negative_flow
        
        self.log(f"  计算了 6 个资金流向指标")
        
        return df
    
    # ==================== 大户追踪 ====================
    
    def identify_whale_activity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        识别鲸鱼（大户）活动
        
        Args:
            df: 输入DataFrame
        
        Returns:
            添加了鲸鱼活动指标的DataFrame
        """
        self.log("识别鲸鱼活动...")
        df = df.copy()
        
        volume_col = 'market_Volume' if 'market_Volume' in df.columns else 'Volume'
        
        # 1. 鲸鱼交易阈值（动态）
        # 使用滚动窗口的分位数
        whale_threshold_value = df[volume_col].rolling(window=90).quantile(self.whale_threshold)
        
        # 2. 鲸鱼活动标记
        df['Is_Whale_Activity'] = (df[volume_col] > whale_threshold_value).astype(int)
        
        # 3. 鲸鱼活动强度
        # 超过阈值的倍数
        df['Whale_Intensity'] = df[volume_col] / (whale_threshold_value + 1e-10)
        df['Whale_Intensity'] = df['Whale_Intensity'].clip(upper=10)  # 限制最大值
        
        # 4. 鲸鱼活动频率（7天窗口）
        df['Whale_Frequency_7d'] = df['Is_Whale_Activity'].rolling(window=7).sum()
        
        # 5. 鲸鱼活动趋势
        # 最近7天 vs 之前7天
        recent_whale = df['Is_Whale_Activity'].rolling(window=7).sum()
        previous_whale = df['Is_Whale_Activity'].shift(7).rolling(window=7).sum()
        df['Whale_Trend'] = (recent_whale - previous_whale) / (previous_whale + 1)
        
        whale_count = df['Is_Whale_Activity'].sum()
        self.log(f"  检测到 {whale_count} 次鲸鱼活动")
        
        return df
    
    # ==================== 资金聚集度 ====================
    
    def calculate_capital_concentration(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算资金聚集度指标
        
        Args:
            df: 输入DataFrame
        
        Returns:
            添加了聚集度指标的DataFrame
        """
        self.log("计算资金聚集度...")
        df = df.copy()
        
        if 'Money_Flow' not in df.columns:
            self.log("警告: 请先计算资金流向")
            return df
        
        # 1. 资金聚集度（基尼系数思想）
        # 计算30天窗口内资金流的集中程度
        window = 30
        
        def gini_coefficient(x):
            """计算基尼系数"""
            if len(x) < 2:
                return 0
            x = np.abs(x)  # 使用绝对值
            x = np.sort(x)
            n = len(x)
            index = np.arange(1, n + 1)
            return (2 * np.sum(index * x)) / (n * np.sum(x)) - (n + 1) / n
        
        df['Capital_Concentration'] = df['Money_Flow'].rolling(window=window).apply(
            gini_coefficient, raw=True
        )
        
        # 2. 主力控盘度
        # 大额交易占比
        total_flow = df['Money_Flow'].rolling(window=window).sum()
        
        # 计算前20%交易的资金占比
        def top20_ratio(x):
            if len(x) < 5:
                return 0.5
            threshold = np.percentile(x, 80)
            top20_sum = x[x >= threshold].sum()
            total = x.sum()
            return top20_sum / (total + 1e-10) if total > 0 else 0.5
        
        df['Main_Control_Ratio'] = df['Money_Flow'].rolling(window=window).apply(
            top20_ratio, raw=True
        )
        
        # 3. 资金分散度（标准差/均值）
        df['Capital_Dispersion'] = (
            df['Money_Flow'].rolling(window=window).std() /
            (df['Money_Flow'].rolling(window=window).mean() + 1e-10)
        )
        
        self.log(f"  计算了 3 个聚集度指标")
        
        return df
    
    # ==================== 主力行为识别 ====================
    
    def identify_main_behavior(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        识别主力行为模式
        
        Args:
            df: 输入DataFrame
        
        Returns:
            添加了主力行为标记的DataFrame
        """
        self.log("识别主力行为模式...")
        df = df.copy()
        
        # 确保列名
        return_col = 'market_Return' if 'market_Return' in df.columns else 'Return'
        volume_col = 'market_Volume' if 'market_Volume' in df.columns else 'Volume'
        
        if return_col not in df.columns or volume_col not in df.columns:
            self.log("警告: 缺少必要列")
            return df
        
        # 计算价格和成交量的变化
        price_change = df[return_col]
        volume_ma = df[volume_col].rolling(window=20).mean()
        volume_ratio = df[volume_col] / (volume_ma + 1e-10)
        
        # 定义阈值
        price_up_threshold = 0.01    # 1%上涨
        price_down_threshold = -0.01  # 1%下跌
        volume_high_threshold = 1.2   # 成交量高于均值20%
        volume_low_threshold = 0.8    # 成交量低于均值20%
        
        # 识别模式
        conditions = [
            # 1. 吸筹 (Accumulation): 价跌量增
            (price_change < price_down_threshold) & (volume_ratio > volume_high_threshold),
            
            # 2. 派发 (Distribution): 价涨量增
            (price_change > price_up_threshold) & (volume_ratio > volume_high_threshold),
            
            # 3. 拉升 (Pump): 价涨量正常或减
            (price_change > price_up_threshold) & (volume_ratio <= volume_high_threshold),
            
            # 4. 砸盘 (Dump): 价跌量正常或减  
            (price_change < price_down_threshold) & (volume_ratio <= volume_high_threshold),
        ]
        
        choices = ['Accumulation', 'Distribution', 'Pump', 'Dump']
        
        df['Main_Behavior'] = np.select(conditions, choices, default='Sideways')
        df['Main_Behavior_CN'] = df['Main_Behavior'].map({
            'Accumulation': '吸筹',
            'Distribution': '派发',
            'Pump': '拉升',
            'Dump': '砸盘',
            'Sideways': '横盘'
        })
        
        # 统计各行为
        behavior_counts = df['Main_Behavior'].value_counts()
        self.log("  主力行为分布:")
        for behavior, count in behavior_counts.items():
            pct = count / len(df) * 100
            self.log(f"    {behavior}: {count} ({pct:.1f}%)")
        
        return df
    
    # ==================== 资金与价格关系 ====================
    
    def analyze_capital_price_relationship(self, 
                                          df: pd.DataFrame,
                                          window: int = 30) -> pd.DataFrame:
        """
        分析资金流与价格的关系
        
        Args:
            df: 输入DataFrame
            window: 分析窗口
        
        Returns:
            关系分析结果DataFrame
        """
        self.log(f"分析资金与价格关系 (窗口={window}天)...")
        
        if 'Net_Money_Flow' not in df.columns:
            self.log("警告: 缺少资金流数据")
            return pd.DataFrame()
        
        return_col = 'market_Return' if 'market_Return' in df.columns else 'Return'
        if return_col not in df.columns:
            self.log("警告: 缺少收益率数据")
            return pd.DataFrame()
        
        # 计算滚动相关性
        df['Capital_Price_Corr'] = df['Net_Money_Flow'].rolling(window=window).corr(
            df[return_col]
        )
        
        # 整体相关性
        overall_corr = df['Net_Money_Flow'].corr(df[return_col])
        self.log(f"  资金流与价格相关性: {overall_corr:.4f}")
        
        return df
    
    # ==================== 资金异动检测 ====================
    
    def detect_capital_anomaly(self, 
                               df: pd.DataFrame,
                               threshold: float = 2.5) -> pd.DataFrame:
        """
        检测资金异动
        
        Args:
            df: 输入DataFrame
            threshold: Z-score阈值
        
        Returns:
            添加了异动标记的DataFrame
        """
        self.log("检测资金异动...")
        df = df.copy()
        
        if 'Net_Money_Flow' not in df.columns:
            return df
        
        # 计算Z-score
        nf_mean = df['Net_Money_Flow'].rolling(window=90).mean()
        nf_std = df['Net_Money_Flow'].rolling(window=90).std()
        df['Capital_Zscore'] = (df['Net_Money_Flow'] - nf_mean) / (nf_std + 1e-10)
        
        # 标记异动
        df['Capital_Anomaly'] = 'Normal'
        df.loc[df['Capital_Zscore'] < -threshold, 'Capital_Anomaly'] = 'Large Outflow'
        df.loc[df['Capital_Zscore'] > threshold, 'Capital_Anomaly'] = 'Large Inflow'
        
        inflow_count = (df['Capital_Anomaly'] == 'Large Inflow').sum()
        outflow_count = (df['Capital_Anomaly'] == 'Large Outflow').sum()
        
        self.log(f"  检测到大额流入: {inflow_count} 次")
        self.log(f"  检测到大额流出: {outflow_count} 次")
        
        return df
    
    # ==================== 按市场状态分析资金 ====================
    
    def analyze_capital_by_regime(self,
                                  df: pd.DataFrame,
                                  regime_col: str = 'market_regime') -> pd.DataFrame:
        """
        按市场状态分析资金流向
        
        Args:
            df: 输入DataFrame
            regime_col: 市场状态列名
        
        Returns:
            各状态的资金统计DataFrame
        """
        if regime_col not in df.columns or 'Net_Money_Flow' not in df.columns:
            self.log("错误: 缺少必要列")
            return pd.DataFrame()
        
        self.log("按市场状态分析资金...")
        
        regime_names = {
            0: 'Consolidation',
            1: 'Trending',
            2: 'Panic',
            3: 'Euphoria'
        }
        
        stats = []
        
        for regime_id in sorted(df[regime_col].unique()):
            regime_data = df[df[regime_col] == regime_id]
            
            stat = {
                'regime': regime_names.get(regime_id, f'Regime_{regime_id}'),
                'regime_id': regime_id,
                'count': len(regime_data),
                'avg_net_flow': regime_data['Net_Money_Flow'].mean(),
                'total_inflow': regime_data['Net_Money_Flow'].clip(lower=0).sum(),
                'total_outflow': regime_data['Net_Money_Flow'].clip(upper=0).sum(),
                'whale_frequency': regime_data.get('Is_Whale_Activity', pd.Series([0])).mean(),
            }
            
            # 主力行为分布
            if 'Main_Behavior' in regime_data.columns:
                behavior_dist = regime_data['Main_Behavior'].value_counts()
                for behavior in ['Accumulation', 'Distribution', 'Pump', 'Dump']:
                    stat[f'pct_{behavior}'] = (behavior_dist.get(behavior, 0) / 
                                               len(regime_data) * 100)
            
            stats.append(stat)
        
        stats_df = pd.DataFrame(stats)
        
        self.log(f"  分析了 {len(stats)} 个市场状态")
        
        return stats_df
    
    # ==================== 主流程 ====================
    
    def full_analysis(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        完整的资金流向分析
        
        Args:
            df: 输入DataFrame
        
        Returns:
            分析结果字典
        """
        self.log("\n" + "=" * 70)
        self.log("开始完整的主力资金追踪分析")
        self.log("=" * 70 + "\n")
        
        results = {}
        
        # 1. 资金流向
        df = self.calculate_money_flow(df)
        
        # 2. 鲸鱼活动
        df = self.identify_whale_activity(df)
        
        # 3. 资金聚集度
        df = self.calculate_capital_concentration(df)
        
        # 4. 主力行为
        df = self.identify_main_behavior(df)
        
        # 5. 资金-价格关系
        df = self.analyze_capital_price_relationship(df)
        
        # 6. 异动检测
        df = self.detect_capital_anomaly(df)
        
        # 7. 按市场状态分析
        regime_stats = pd.DataFrame()
        if 'market_regime' in df.columns:
            regime_stats = self.analyze_capital_by_regime(df)
        
        results['data'] = df
        results['regime_analysis'] = regime_stats
        
        self.log("\n" + "=" * 70)
        self.log("主力资金追踪分析完成")
        self.log("=" * 70 + "\n")
        
        return results


def main():
    """测试资金流向分析"""
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - Capital Flow Analysis Test")
    print("=" * 70 + "\n")
    
    # 加载数据
    try:
        df = pd.read_csv('data/processed/sentiment_analysis.csv', index_col=0, parse_dates=True)
        print(f"Loaded data: {len(df)} rows")
    except FileNotFoundError:
        print("Error: Please run sentiment_analyzer.py first (WAL-17)")
        return
    
    # 创建分析器
    analyzer = CapitalFlowAnalyzer(verbose=True)
    
    # 完整分析
    results = analyzer.full_analysis(df)
    
    # 显示结果
    print("\n" + "=" * 70)
    print("Capital Flow Summary:")
    print("=" * 70)
    
    if 'Net_Money_Flow' in results['data'].columns:
        nf_summary = results['data']['Net_Money_Flow'].describe()
        print(nf_summary)
    
    print("\n" + "=" * 70)
    print("Whale Activity Summary:")
    print("=" * 70)
    if 'Is_Whale_Activity' in results['data'].columns:
        whale_count = results['data']['Is_Whale_Activity'].sum()
        whale_pct = whale_count / len(results['data']) * 100
        print(f"Total whale activities: {whale_count} ({whale_pct:.1f}%)")
    
    print("\n" + "=" * 70)
    print("Main Behavior Distribution:")
    print("=" * 70)
    if 'Main_Behavior' in results['data'].columns:
        behavior_dist = results['data']['Main_Behavior'].value_counts()
        for behavior, count in behavior_dist.items():
            pct = count / len(results['data']) * 100
            print(f"  {behavior}: {count} ({pct:.1f}%)")
    
    if not results['regime_analysis'].empty:
        print("\n" + "=" * 70)
        print("Capital Flow by Market Regime:")
        print("=" * 70)
        print(results['regime_analysis'][['regime', 'count', 'avg_net_flow', 
                                         'whale_frequency']].to_string(index=False))
    
    # 保存结果
    output_file = 'data/processed/capital_flow_analysis.csv'
    results['data'].to_csv(output_file)
    print(f"\n[SUCCESS] Results saved to: {output_file}")
    
    print("\n" + "=" * 70)
    print("Test completed successfully!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()

