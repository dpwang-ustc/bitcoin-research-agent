"""
Bitcoin Research Agent - 波动率与流动性分析

功能：
1. 历史波动率分析（实际波动率）
2. GARCH模型预测波动率
3. 流动性指标分析
4. 波动率锥形图（Volatility Cone）
5. 结合市场状态的波动率分析

作者：Bitcoin Research Agent Team
日期：2025-10-25
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')


class VolatilityAnalyzer:
    """波动率与流动性分析器"""
    
    def __init__(self, verbose: bool = True):
        """
        初始化分析器
        
        Args:
            verbose: 是否打印详细信息
        """
        self.verbose = verbose
        self.garch_model = None
        self.garch_forecast = None
    
    def log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[VolatilityAnalyzer] {message}")
    
    # ==================== 历史波动率分析 ====================
    
    def calculate_realized_volatility(self, 
                                     df: pd.DataFrame,
                                     return_col: str = 'Return',
                                     windows: List[int] = [7, 14, 30, 60, 90]) -> pd.DataFrame:
        """
        计算实际波动率（Realized Volatility）
        
        Args:
            df: 输入DataFrame
            return_col: 收益率列名
            windows: 计算窗口列表
        
        Returns:
            添加了波动率列的DataFrame
        """
        self.log("计算历史波动率...")
        df = df.copy()
        
        # 确保列名
        if f'market_{return_col}' in df.columns:
            return_col = f'market_{return_col}'
        
        if return_col not in df.columns:
            self.log(f"警告: 列 {return_col} 不存在")
            return df
        
        # 计算不同窗口的波动率
        for window in windows:
            vol_col = f'RealizedVol_{window}d'
            df[vol_col] = df[return_col].rolling(window=window).std() * np.sqrt(252)  # 年化
        
        self.log(f"  计算了 {len(windows)} 个时间窗口的波动率")
        
        return df
    
    def calculate_parkinson_volatility(self, df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
        """
        计算Parkinson波动率（基于高低价）
        
        Args:
            df: 输入DataFrame
            window: 计算窗口
        
        Returns:
            添加了Parkinson波动率的DataFrame
        """
        self.log("计算Parkinson波动率...")
        df = df.copy()
        
        # 确保列名
        high_col = 'market_High' if 'market_High' in df.columns else 'High'
        low_col = 'market_Low' if 'market_Low' in df.columns else 'Low'
        
        if high_col not in df.columns or low_col not in df.columns:
            self.log("警告: 缺少High或Low列")
            return df
        
        # Parkinson公式: sqrt(1/(4*ln(2)) * (ln(High/Low))^2)
        hl_ratio = np.log(df[high_col] / df[low_col])
        parkinson_vol = hl_ratio.rolling(window=window).apply(
            lambda x: np.sqrt(np.mean(x**2) / (4 * np.log(2))) * np.sqrt(252)
        )
        
        df[f'ParkinsonVol_{window}d'] = parkinson_vol
        
        self.log(f"  计算了 {window} 天窗口的Parkinson波动率")
        
        return df
    
    def calculate_garman_klass_volatility(self, df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
        """
        计算Garman-Klass波动率（更高效的OHLC波动率估计）
        
        Args:
            df: 输入DataFrame
            window: 计算窗口
        
        Returns:
            添加了GK波动率的DataFrame
        """
        self.log("计算Garman-Klass波动率...")
        df = df.copy()
        
        # 确保列名
        high_col = 'market_High' if 'market_High' in df.columns else 'High'
        low_col = 'market_Low' if 'market_Low' in df.columns else 'Low'
        open_col = 'market_Open' if 'market_Open' in df.columns else 'Open'
        close_col = 'market_Close' if 'market_Close' in df.columns else 'Close'
        
        # GK公式
        log_hl = np.log(df[high_col] / df[low_col])
        log_co = np.log(df[close_col] / df[open_col])
        
        gk_vol = np.sqrt(
            0.5 * log_hl.rolling(window=window).apply(lambda x: np.mean(x**2)) -
            (2 * np.log(2) - 1) * log_co.rolling(window=window).apply(lambda x: np.mean(x**2))
        ) * np.sqrt(252)
        
        df[f'GKVol_{window}d'] = gk_vol
        
        self.log(f"  计算了 {window} 天窗口的GK波动率")
        
        return df
    
    # ==================== GARCH模型 ====================
    
    def fit_garch(self, 
                  df: pd.DataFrame,
                  return_col: str = 'Return',
                  p: int = 1,
                  q: int = 1) -> Dict:
        """
        拟合GARCH模型
        
        Args:
            df: 输入DataFrame
            return_col: 收益率列名
            p: GARCH(p,q)的p参数
            q: GARCH(p,q)的q参数
        
        Returns:
            模型拟合结果字典
        """
        self.log(f"拟合GARCH({p},{q})模型...")
        
        # 确保列名
        if f'market_{return_col}' in df.columns:
            return_col = f'market_{return_col}'
        
        if return_col not in df.columns:
            self.log(f"错误: 列 {return_col} 不存在")
            return {}
        
        # 准备数据（百分比）
        returns = df[return_col].dropna() * 100
        
        # 拟合GARCH模型
        model = arch_model(returns, vol='Garch', p=p, q=q, rescale=False)
        self.garch_model = model.fit(disp='off')
        
        self.log("  GARCH模型拟合完成")
        self.log(f"  AIC: {self.garch_model.aic:.2f}")
        self.log(f"  BIC: {self.garch_model.bic:.2f}")
        
        # 提取条件波动率
        conditional_vol = self.garch_model.conditional_volatility / 100  # 转回比例
        
        return {
            'model': self.garch_model,
            'conditional_volatility': conditional_vol,
            'aic': self.garch_model.aic,
            'bic': self.garch_model.bic
        }
    
    def forecast_garch(self, horizon: int = 30) -> pd.DataFrame:
        """
        使用GARCH模型预测未来波动率
        
        Args:
            horizon: 预测天数
        
        Returns:
            预测结果DataFrame
        """
        if self.garch_model is None:
            self.log("错误: 请先拟合GARCH模型")
            return pd.DataFrame()
        
        self.log(f"预测未来 {horizon} 天波动率...")
        
        # 预测
        forecast = self.garch_model.forecast(horizon=horizon, reindex=False)
        
        # 提取波动率预测
        vol_forecast = np.sqrt(forecast.variance.values[-1, :]) / 100  # 转回比例
        
        # 年化
        vol_forecast_annual = vol_forecast * np.sqrt(252)
        
        self.garch_forecast = pd.DataFrame({
            'horizon': range(1, horizon + 1),
            'forecast_volatility': vol_forecast_annual
        })
        
        self.log(f"  预测完成，平均预测波动率: {vol_forecast_annual.mean():.4f}")
        
        return self.garch_forecast
    
    # ==================== 流动性分析 ====================
    
    def calculate_liquidity_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算流动性指标
        
        Args:
            df: 输入DataFrame
        
        Returns:
            添加了流动性指标的DataFrame
        """
        self.log("计算流动性指标...")
        df = df.copy()
        
        # 确保列名
        volume_col = 'market_Volume' if 'market_Volume' in df.columns else 'Volume'
        close_col = 'market_Close' if 'market_Close' in df.columns else 'Close'
        high_col = 'market_High' if 'market_High' in df.columns else 'High'
        low_col = 'market_Low' if 'market_Low' in df.columns else 'Low'
        
        # 1. 成交额（Turnover）
        df['Turnover'] = df[volume_col] * df[close_col]
        
        # 2. Amihud非流动性指标
        # |Return| / Turnover
        return_col = 'market_Return' if 'market_Return' in df.columns else 'Return'
        if return_col in df.columns:
            df['Amihud_Illiquidity'] = np.abs(df[return_col]) / (df['Turnover'] + 1e-10)
            df['Amihud_Illiquidity'] = df['Amihud_Illiquidity'].replace([np.inf, -np.inf], np.nan)
        
        # 3. 相对价差（Relative Spread）
        df['Relative_Spread'] = (df[high_col] - df[low_col]) / df[close_col]
        
        # 4. 成交量波动率
        df['Volume_Volatility'] = df[volume_col].pct_change().rolling(window=30).std()
        
        # 5. 价格影响（Price Impact，简化版）
        # 成交量变化 vs 价格变化的比率
        volume_change = df[volume_col].pct_change()
        price_change = df[close_col].pct_change()
        df['Price_Impact'] = np.abs(price_change) / (np.abs(volume_change) + 1e-10)
        df['Price_Impact'] = df['Price_Impact'].replace([np.inf, -np.inf], np.nan)
        
        self.log("  计算了 5 个流动性指标")
        
        return df
    
    # ==================== 波动率锥形图 ====================
    
    def create_volatility_cone(self, 
                               df: pd.DataFrame,
                               return_col: str = 'Return',
                               windows: List[int] = [7, 14, 30, 60, 90, 180]) -> pd.DataFrame:
        """
        创建波动率锥形图数据
        
        Args:
            df: 输入DataFrame
            return_col: 收益率列名
            windows: 计算窗口列表
        
        Returns:
            波动率锥形数据DataFrame
        """
        self.log("创建波动率锥形图数据...")
        
        # 确保列名
        if f'market_{return_col}' in df.columns:
            return_col = f'market_{return_col}'
        
        cone_data = []
        
        for window in windows:
            # 计算滚动波动率
            rolling_vol = df[return_col].rolling(window=window).std() * np.sqrt(252)
            
            # 计算分位数
            cone_data.append({
                'window': window,
                'min': rolling_vol.min(),
                'p05': rolling_vol.quantile(0.05),
                'p25': rolling_vol.quantile(0.25),
                'median': rolling_vol.quantile(0.50),
                'p75': rolling_vol.quantile(0.75),
                'p95': rolling_vol.quantile(0.95),
                'max': rolling_vol.max(),
                'current': rolling_vol.iloc[-1] if len(rolling_vol) > 0 else np.nan
            })
        
        cone_df = pd.DataFrame(cone_data)
        
        self.log(f"  生成了 {len(windows)} 个窗口的波动率锥形数据")
        
        return cone_df
    
    # ==================== 市场状态波动率分析 ====================
    
    def analyze_volatility_by_regime(self, 
                                    df: pd.DataFrame,
                                    regime_col: str = 'market_regime') -> pd.DataFrame:
        """
        按市场状态分析波动率
        
        Args:
            df: 包含市场状态的DataFrame
            regime_col: 状态列名
        
        Returns:
            各状态的波动率统计DataFrame
        """
        if regime_col not in df.columns:
            self.log(f"错误: 缺少列 {regime_col}")
            return pd.DataFrame()
        
        self.log("按市场状态分析波动率...")
        
        # 定义状态名称
        regime_names = {
            0: 'Consolidation',
            1: 'Trending',
            2: 'Panic',
            3: 'Euphoria'
        }
        
        stats = []
        
        # 找到波动率列
        vol_cols = [col for col in df.columns if 'Vol' in col or 'Volatility' in col]
        main_vol_col = next((col for col in vol_cols if '7d' in col or '30d' in col), None)
        
        if not main_vol_col:
            self.log("警告: 未找到主要波动率列")
            return pd.DataFrame()
        
        for regime_id in sorted(df[regime_col].unique()):
            regime_data = df[df[regime_col] == regime_id]
            
            stat = {
                'regime': regime_names.get(regime_id, f'Regime_{regime_id}'),
                'regime_id': regime_id,
                'count': len(regime_data),
                'avg_volatility': regime_data[main_vol_col].mean(),
                'std_volatility': regime_data[main_vol_col].std(),
                'min_volatility': regime_data[main_vol_col].min(),
                'max_volatility': regime_data[main_vol_col].max(),
            }
            
            # 添加流动性指标（如果存在）
            if 'Amihud_Illiquidity' in df.columns:
                stat['avg_illiquidity'] = regime_data['Amihud_Illiquidity'].mean()
            
            if 'Relative_Spread' in df.columns:
                stat['avg_spread'] = regime_data['Relative_Spread'].mean()
            
            stats.append(stat)
        
        stats_df = pd.DataFrame(stats)
        
        self.log(f"  分析了 {len(stats)} 个市场状态")
        
        return stats_df
    
    # ==================== 主流程 ====================
    
    def full_analysis(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        完整的波动率与流动性分析
        
        Args:
            df: 输入DataFrame
        
        Returns:
            分析结果字典
        """
        self.log("\n" + "=" * 70)
        self.log("开始完整的波动率与流动性分析")
        self.log("=" * 70 + "\n")
        
        results = {}
        
        # 1. 计算各种波动率
        df = self.calculate_realized_volatility(df)
        df = self.calculate_parkinson_volatility(df)
        df = self.calculate_garman_klass_volatility(df)
        
        # 2. 流动性指标
        df = self.calculate_liquidity_metrics(df)
        
        # 3. GARCH模型
        garch_results = self.fit_garch(df)
        if garch_results:
            df['GARCH_ConditionalVol'] = np.nan
            df.loc[garch_results['conditional_volatility'].index, 'GARCH_ConditionalVol'] = \
                garch_results['conditional_volatility'].values
        
        # 4. 预测
        forecast_df = self.forecast_garch(horizon=30)
        
        # 5. 波动率锥形图
        cone_df = self.create_volatility_cone(df)
        
        # 6. 按市场状态分析
        regime_stats = pd.DataFrame()
        if 'market_regime' in df.columns:
            regime_stats = self.analyze_volatility_by_regime(df)
        
        # 保存结果
        results['data'] = df
        results['forecast'] = forecast_df
        results['volatility_cone'] = cone_df
        results['regime_analysis'] = regime_stats
        results['garch_model'] = garch_results
        
        self.log("\n" + "=" * 70)
        self.log("波动率与流动性分析完成")
        self.log("=" * 70 + "\n")
        
        return results


def main():
    """测试波动率分析"""
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - Volatility & Liquidity Analysis Test")
    print("=" * 70 + "\n")
    
    # 加载数据
    try:
        df = pd.read_csv('data/processed/market_regime.csv', index_col=0, parse_dates=True)
        print(f"Loaded data: {len(df)} rows")
    except FileNotFoundError:
        print("Error: Please run market_regime.py first (WAL-14)")
        return
    
    # 创建分析器
    analyzer = VolatilityAnalyzer(verbose=True)
    
    # 完整分析
    results = analyzer.full_analysis(df)
    
    # 显示结果
    print("\n" + "=" * 70)
    print("Volatility Cone:")
    print("=" * 70)
    print(results['volatility_cone'].to_string(index=False))
    
    if not results['regime_analysis'].empty:
        print("\n" + "=" * 70)
        print("Volatility by Market Regime:")
        print("=" * 70)
        print(results['regime_analysis'].to_string(index=False))
    
    print("\n" + "=" * 70)
    print("GARCH Forecast (next 30 days):")
    print("=" * 70)
    print(results['forecast'].head(10).to_string(index=False))
    
    # 保存结果
    output_file = 'data/processed/volatility_analysis.csv'
    results['data'].to_csv(output_file)
    print(f"\n[SUCCESS] Results saved to: {output_file}")
    
    print("\n" + "=" * 70)
    print("Test completed successfully!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()

