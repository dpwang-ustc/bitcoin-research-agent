"""
Bitcoin Research Agent - 情绪与新闻影响分析

功能：
1. 新闻情绪分析（NLP情感分析）
2. Fear & Greed 指数计算
3. 社交媒体情绪追踪
4. 情绪与市场状态的关系分析
5. 情绪指标时间序列生成

作者：Bitcoin Research Agent Team
日期：2025-10-25
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class SentimentAnalyzer:
    """情绪与新闻影响分析器"""
    
    def __init__(self, verbose: bool = True):
        """
        初始化分析器
        
        Args:
            verbose: 是否打印详细信息
        """
        self.verbose = verbose
        
        # 情绪词典（简化版）
        self.positive_words = {
            'bullish', 'bull', 'rally', 'surge', 'pump', 'moon', 'gain', 'profit',
            'breakout', 'breakthrough', 'strength', 'strong', 'buy', 'accumulate',
            'optimistic', 'positive', 'growth', 'rise', 'soar', 'boom', 'up',
            'green', 'rocket', 'explosive', 'golden', 'winner', 'win', 'success'
        }
        
        self.negative_words = {
            'bearish', 'bear', 'crash', 'dump', 'plunge', 'fall', 'drop', 'loss',
            'breakdown', 'weak', 'weakness', 'sell', 'panic', 'fear', 'fud',
            'pessimistic', 'negative', 'decline', 'down', 'red', 'bloody',
            'disaster', 'collapse', 'failure', 'lose', 'losing', 'worst'
        }
        
        # Fear & Greed 组件权重
        self.fg_weights = {
            'volatility': 0.25,
            'momentum': 0.25,
            'volume': 0.15,
            'social_media': 0.15,
            'dominance': 0.10,
            'trends': 0.10
        }
    
    def log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[SentimentAnalyzer] {message}")
    
    # ==================== 简单情绪分析 ====================
    
    def simple_sentiment_score(self, text: str) -> float:
        """
        简单的情绪评分（基于词典）
        
        Args:
            text: 输入文本
        
        Returns:
            情绪分数 (-1到1之间)
        """
        if not text or not isinstance(text, str):
            return 0.0
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        # 归一化到 -1 到 1
        score = (positive_count - negative_count) / total
        return score
    
    # ==================== Fear & Greed 指数 ====================
    
    def calculate_fear_greed_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算 Fear & Greed 指数
        
        Args:
            df: 输入DataFrame
        
        Returns:
            添加了Fear & Greed指数的DataFrame
        """
        self.log("计算 Fear & Greed 指数...")
        df = df.copy()
        
        # 1. 波动率组件 (Volatility)
        vol_col = 'market_Volatility_30d' if 'market_Volatility_30d' in df.columns else 'RealizedVol_30d'
        if vol_col in df.columns:
            # 波动率越高，恐惧越大（0-100反转）
            vol_normalized = 100 - self._normalize_to_100(df[vol_col])
            df['FG_Volatility'] = vol_normalized
        else:
            df['FG_Volatility'] = 50  # 中性
        
        # 2. 动量组件 (Momentum/Market Strength)
        return_col = 'market_Return' if 'market_Return' in df.columns else 'Return'
        if return_col in df.columns:
            # 使用多个时间窗口的收益率
            momentum = df[return_col].rolling(window=30).mean()
            df['FG_Momentum'] = self._normalize_to_100(momentum)
        else:
            df['FG_Momentum'] = 50
        
        # 3. 成交量组件 (Volume)
        volume_col = 'market_Volume' if 'market_Volume' in df.columns else 'Volume'
        if volume_col in df.columns:
            # 成交量相对于平均值
            volume_ma = df[volume_col].rolling(window=30).mean()
            volume_ratio = df[volume_col] / volume_ma
            df['FG_Volume'] = self._normalize_to_100(volume_ratio - 1)
        else:
            df['FG_Volume'] = 50
        
        # 4. 市场主导地位 (Market Dominance)
        # 简化处理：使用RSI作为替代
        rsi_col = 'market_RSI14' if 'market_RSI14' in df.columns else 'RSI14'
        if rsi_col in df.columns:
            df['FG_Dominance'] = df[rsi_col]
        else:
            df['FG_Dominance'] = 50
        
        # 5. 社交媒体 (Social Media) - 简化版
        # 使用价格动量作为替代
        if return_col in df.columns:
            social_proxy = df[return_col].rolling(window=7).mean()
            df['FG_Social'] = self._normalize_to_100(social_proxy)
        else:
            df['FG_Social'] = 50
        
        # 6. 趋势 (Trends) - Google Trends替代
        # 使用成交量变化作为替代
        volume_change_col = 'market_Volume_Change' if 'market_Volume_Change' in df.columns else 'Volume_Change'
        if volume_change_col in df.columns:
            df['FG_Trends'] = self._normalize_to_100(df[volume_change_col])
        else:
            df['FG_Trends'] = 50
        
        # 计算综合 Fear & Greed 指数
        df['Fear_Greed_Index'] = (
            df['FG_Volatility'] * self.fg_weights['volatility'] +
            df['FG_Momentum'] * self.fg_weights['momentum'] +
            df['FG_Volume'] * self.fg_weights['volume'] +
            df['FG_Social'] * self.fg_weights['social_media'] +
            df['FG_Dominance'] * self.fg_weights['dominance'] +
            df['FG_Trends'] * self.fg_weights['trends']
        )
        
        # 分类
        df['FG_Category'] = pd.cut(
            df['Fear_Greed_Index'],
            bins=[0, 25, 45, 55, 75, 100],
            labels=['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
        )
        
        self.log(f"  Fear & Greed 指数计算完成")
        
        return df
    
    def _normalize_to_100(self, series: pd.Series) -> pd.Series:
        """
        归一化到0-100范围
        
        Args:
            series: 输入序列
        
        Returns:
            归一化后的序列
        """
        series_clean = series.replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(series_clean) == 0:
            return pd.Series(50, index=series.index)
        
        min_val = series_clean.quantile(0.01)  # 使用1%和99%分位数避免极端值
        max_val = series_clean.quantile(0.99)
        
        if max_val == min_val:
            return pd.Series(50, index=series.index)
        
        normalized = (series - min_val) / (max_val - min_val) * 100
        normalized = normalized.clip(0, 100)
        
        return normalized
    
    # ==================== 情绪与市场状态关系 ====================
    
    def analyze_sentiment_by_regime(self, 
                                    df: pd.DataFrame,
                                    regime_col: str = 'market_regime') -> pd.DataFrame:
        """
        按市场状态分析情绪
        
        Args:
            df: 输入DataFrame
            regime_col: 市场状态列名
        
        Returns:
            各状态的情绪统计DataFrame
        """
        if regime_col not in df.columns or 'Fear_Greed_Index' not in df.columns:
            self.log("错误: 缺少必要列")
            return pd.DataFrame()
        
        self.log("按市场状态分析情绪...")
        
        # 状态名称
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
                'avg_fg_index': regime_data['Fear_Greed_Index'].mean(),
                'std_fg_index': regime_data['Fear_Greed_Index'].std(),
                'min_fg_index': regime_data['Fear_Greed_Index'].min(),
                'max_fg_index': regime_data['Fear_Greed_Index'].max(),
            }
            
            # 分类分布
            if 'FG_Category' in regime_data.columns:
                category_counts = regime_data['FG_Category'].value_counts()
                for category in ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']:
                    stat[f'pct_{category.replace(" ", "_")}'] = \
                        (category_counts.get(category, 0) / len(regime_data) * 100)
            
            stats.append(stat)
        
        stats_df = pd.DataFrame(stats)
        
        self.log(f"  分析了 {len(stats)} 个市场状态")
        
        return stats_df
    
    # ==================== 情绪与价格滞后关系 ====================
    
    def analyze_sentiment_price_lag(self,
                                   df: pd.DataFrame,
                                   max_lag: int = 7) -> pd.DataFrame:
        """
        分析情绪与价格的滞后关系
        
        Args:
            df: 输入DataFrame
            max_lag: 最大滞后天数
        
        Returns:
            滞后相关性DataFrame
        """
        self.log(f"分析情绪与价格的滞后关系 (最大滞后={max_lag}天)...")
        
        if 'Fear_Greed_Index' not in df.columns:
            self.log("错误: 缺少 Fear_Greed_Index 列")
            return pd.DataFrame()
        
        return_col = 'market_Return' if 'market_Return' in df.columns else 'Return'
        if return_col not in df.columns:
            self.log("错误: 缺少收益率列")
            return pd.DataFrame()
        
        results = []
        
        for lag in range(0, max_lag + 1):
            # 情绪领先价格lag天
            if lag == 0:
                corr = df['Fear_Greed_Index'].corr(df[return_col])
            else:
                corr = df['Fear_Greed_Index'].shift(lag).corr(df[return_col])
            
            results.append({
                'lag_days': lag,
                'correlation': corr,
                'direction': 'Sentiment leads Price' if lag > 0 else 'Same day'
            })
        
        lag_df = pd.DataFrame(results)
        
        # 找到最强相关性
        max_corr_idx = lag_df['correlation'].abs().idxmax()
        best_lag = lag_df.loc[max_corr_idx]
        
        self.log(f"  最强相关性: Lag={best_lag['lag_days']}天, Corr={best_lag['correlation']:.4f}")
        
        return lag_df
    
    # ==================== 情绪极值检测 ====================
    
    def detect_sentiment_extremes(self,
                                  df: pd.DataFrame,
                                  threshold: float = 2.0) -> pd.DataFrame:
        """
        检测情绪极值
        
        Args:
            df: 输入DataFrame
            threshold: Z-score阈值
        
        Returns:
            添加了极值标记的DataFrame
        """
        self.log("检测情绪极值...")
        df = df.copy()
        
        if 'Fear_Greed_Index' not in df.columns:
            return df
        
        # 计算Z-score
        fg_mean = df['Fear_Greed_Index'].mean()
        fg_std = df['Fear_Greed_Index'].std()
        df['FG_Zscore'] = (df['Fear_Greed_Index'] - fg_mean) / fg_std
        
        # 标记极值
        df['FG_Extreme'] = 'Normal'
        df.loc[df['FG_Zscore'] < -threshold, 'FG_Extreme'] = 'Extreme Fear'
        df.loc[df['FG_Zscore'] > threshold, 'FG_Extreme'] = 'Extreme Greed'
        
        extreme_fear_count = (df['FG_Extreme'] == 'Extreme Fear').sum()
        extreme_greed_count = (df['FG_Extreme'] == 'Extreme Greed').sum()
        
        self.log(f"  检测到极度恐慌: {extreme_fear_count} 天")
        self.log(f"  检测到极度贪婪: {extreme_greed_count} 天")
        
        return df
    
    # ==================== 情绪变化率 ====================
    
    def calculate_sentiment_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算情绪变化率
        
        Args:
            df: 输入DataFrame
        
        Returns:
            添加了情绪变化率的DataFrame
        """
        self.log("计算情绪变化率...")
        df = df.copy()
        
        if 'Fear_Greed_Index' not in df.columns:
            return df
        
        # 1天变化
        df['FG_Change_1d'] = df['Fear_Greed_Index'].diff()
        
        # 7天变化
        df['FG_Change_7d'] = df['Fear_Greed_Index'].diff(7)
        
        # 30天变化
        df['FG_Change_30d'] = df['Fear_Greed_Index'].diff(30)
        
        # 变化率
        df['FG_ChangeRate_1d'] = df['Fear_Greed_Index'].pct_change() * 100
        
        self.log("  情绪变化率计算完成")
        
        return df
    
    # ==================== 主流程 ====================
    
    def full_analysis(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        完整的情绪分析
        
        Args:
            df: 输入DataFrame
        
        Returns:
            分析结果字典
        """
        self.log("\n" + "=" * 70)
        self.log("开始完整的情绪与新闻影响分析")
        self.log("=" * 70 + "\n")
        
        results = {}
        
        # 1. 计算 Fear & Greed 指数
        df = self.calculate_fear_greed_index(df)
        
        # 2. 检测极值
        df = self.detect_sentiment_extremes(df)
        
        # 3. 计算变化率
        df = self.calculate_sentiment_changes(df)
        
        # 4. 按市场状态分析
        regime_stats = pd.DataFrame()
        if 'market_regime' in df.columns:
            regime_stats = self.analyze_sentiment_by_regime(df)
        
        # 5. 滞后关系分析
        lag_analysis = self.analyze_sentiment_price_lag(df)
        
        # 保存结果
        results['data'] = df
        results['regime_analysis'] = regime_stats
        results['lag_analysis'] = lag_analysis
        
        self.log("\n" + "=" * 70)
        self.log("情绪与新闻影响分析完成")
        self.log("=" * 70 + "\n")
        
        return results


def main():
    """测试情绪分析"""
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - Sentiment Analysis Test")
    print("=" * 70 + "\n")
    
    # 加载数据
    try:
        df = pd.read_csv('data/processed/volatility_analysis.csv', index_col=0, parse_dates=True)
        print(f"Loaded data: {len(df)} rows")
    except FileNotFoundError:
        print("Error: Please run volatility_analyzer.py first (WAL-15)")
        return
    
    # 创建分析器
    analyzer = SentimentAnalyzer(verbose=True)
    
    # 完整分析
    results = analyzer.full_analysis(df)
    
    # 显示结果
    print("\n" + "=" * 70)
    print("Fear & Greed Index Summary:")
    print("=" * 70)
    fg_summary = results['data']['Fear_Greed_Index'].describe()
    print(fg_summary)
    
    print("\n" + "=" * 70)
    print("Fear & Greed Category Distribution:")
    print("=" * 70)
    if 'FG_Category' in results['data'].columns:
        category_dist = results['data']['FG_Category'].value_counts().sort_index()
        for category, count in category_dist.items():
            pct = count / len(results['data']) * 100
            print(f"  {category}: {count} days ({pct:.1f}%)")
    
    if not results['regime_analysis'].empty:
        print("\n" + "=" * 70)
        print("Sentiment by Market Regime:")
        print("=" * 70)
        print(results['regime_analysis'][['regime', 'count', 'avg_fg_index']].to_string(index=False))
    
    print("\n" + "=" * 70)
    print("Sentiment-Price Lag Analysis:")
    print("=" * 70)
    print(results['lag_analysis'].to_string(index=False))
    
    # 保存结果
    output_file = 'data/processed/sentiment_analysis.csv'
    results['data'].to_csv(output_file)
    print(f"\n[SUCCESS] Results saved to: {output_file}")
    
    print("\n" + "=" * 70)
    print("Test completed successfully!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
