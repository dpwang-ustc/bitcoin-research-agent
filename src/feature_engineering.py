"""
Bitcoin Research Agent - 特征工程模块

功能：
1. 技术指标计算（MA, EMA, RSI, MACD, Bollinger Bands, ATR等）
2. 多数据源时间对齐
3. 缺失值填补策略
4. 异常值检测与处理
5. 特征标准化与归一化

作者：Bitcoin Research Agent Team
日期：2025-10-25
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """特征工程类 - 负责数据清洗与特征提取"""
    
    def __init__(self, verbose: bool = True):
        """
        初始化特征工程器
        
        Args:
            verbose: 是否打印详细信息
        """
        self.verbose = verbose
    
    def log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[FeatureEngineer] {message}")
    
    # ==================== 数据清洗 ====================
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗原始数据
        
        Args:
            df: 原始数据 DataFrame
        
        Returns:
            清洗后的 DataFrame
        """
        self.log(f"开始清洗数据，原始行数: {len(df)}")
        df = df.copy()
        
        # 确保数值列是数字类型
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 确保索引是 datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # 按时间排序
        df = df.sort_index()
        
        # 移除完全重复的行
        df = df[~df.index.duplicated(keep='first')]
        
        self.log(f"清洗后行数: {len(df)}")
        return df
    
    def detect_outliers(self, df: pd.DataFrame, columns: List[str], 
                       method: str = 'iqr', threshold: float = 3.0) -> pd.DataFrame:
        """
        检测异常值
        
        Args:
            df: 输入 DataFrame
            columns: 需要检测的列名列表
            method: 检测方法 ('iqr' 或 'zscore')
            threshold: 阈值（IQR 倍数或 Z-score 标准差倍数）
        
        Returns:
            添加了 outlier 标记的 DataFrame
        """
        df = df.copy()
        
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
            
            elif method == 'zscore':
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers = z_scores > threshold
            
            else:
                raise ValueError(f"Unknown method: {method}")
            
            df[f'{col}_outlier'] = outliers
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                self.log(f"  {col}: 检测到 {outlier_count} 个异常值")
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame, 
                             strategy: str = 'ffill',
                             limit: Optional[int] = None) -> pd.DataFrame:
        """
        处理缺失值
        
        Args:
            df: 输入 DataFrame
            strategy: 填补策略 ('ffill', 'bfill', 'interpolate', 'mean', 'median', 'drop')
            limit: 最大填补数量
        
        Returns:
            填补后的 DataFrame
        """
        df = df.copy()
        missing_before = df.isnull().sum().sum()
        
        if missing_before == 0:
            self.log("无缺失值")
            return df
        
        self.log(f"处理缺失值，总缺失数: {missing_before}, 策略: {strategy}")
        
        if strategy == 'ffill':
            df = df.ffill(limit=limit)
        elif strategy == 'bfill':
            df = df.bfill(limit=limit)
        elif strategy == 'interpolate':
            df = df.interpolate(method='linear', limit=limit)
        elif strategy == 'mean':
            df = df.fillna(df.mean())
        elif strategy == 'median':
            df = df.fillna(df.median())
        elif strategy == 'drop':
            df = df.dropna()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        missing_after = df.isnull().sum().sum()
        self.log(f"  填补后缺失数: {missing_after}")
        
        return df
    
    # ==================== 技术指标 ====================
    
    def add_moving_averages(self, df: pd.DataFrame, 
                          windows: List[int] = [7, 14, 30, 50, 200]) -> pd.DataFrame:
        """
        添加移动平均线
        
        Args:
            df: 输入 DataFrame
            windows: MA 窗口列表
        
        Returns:
            添加了 MA 的 DataFrame
        """
        df = df.copy()
        
        for window in windows:
            # 简单移动平均 (SMA)
            df[f'MA{window}'] = df['Close'].rolling(window=window).mean()
            
            # 指数移动平均 (EMA)
            df[f'EMA{window}'] = df['Close'].ewm(span=window, adjust=False).mean()
        
        self.log(f"添加了 {len(windows)} 个 MA/EMA 指标")
        return df
    
    def add_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        添加 RSI (相对强弱指标)
        
        Args:
            df: 输入 DataFrame
            period: RSI 周期
        
        Returns:
            添加了 RSI 的 DataFrame
        """
        df = df.copy()
        
        # 计算价格变化
        delta = df['Close'].diff()
        
        # 分离上涨和下跌
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # 计算 RS 和 RSI
        rs = gain / loss
        df[f'RSI{period}'] = 100 - (100 / (1 + rs))
        
        self.log(f"添加了 RSI{period} 指标")
        return df
    
    def add_macd(self, df: pd.DataFrame, 
                fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        添加 MACD (移动平均收敛/发散)
        
        Args:
            df: 输入 DataFrame
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
        
        Returns:
            添加了 MACD 的 DataFrame
        """
        df = df.copy()
        
        # 计算 EMA
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        
        # MACD 线
        df['MACD'] = ema_fast - ema_slow
        
        # 信号线
        df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        
        # MACD 柱状图
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        self.log(f"添加了 MACD ({fast},{slow},{signal}) 指标")
        return df
    
    def add_bollinger_bands(self, df: pd.DataFrame, 
                          window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
        """
        添加布林带 (Bollinger Bands)
        
        Args:
            df: 输入 DataFrame
            window: 移动平均窗口
            num_std: 标准差倍数
        
        Returns:
            添加了布林带的 DataFrame
        """
        df = df.copy()
        
        # 中轨 (SMA)
        df['BB_Middle'] = df['Close'].rolling(window=window).mean()
        
        # 标准差
        rolling_std = df['Close'].rolling(window=window).std()
        
        # 上轨和下轨
        df['BB_Upper'] = df['BB_Middle'] + (rolling_std * num_std)
        df['BB_Lower'] = df['BB_Middle'] - (rolling_std * num_std)
        
        # 布林带宽度
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        
        # 价格位置 (%B)
        df['BB_PercentB'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        self.log(f"添加了布林带 (window={window}, std={num_std}) 指标")
        return df
    
    def add_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        添加 ATR (平均真实波幅)
        
        Args:
            df: 输入 DataFrame
            period: ATR 周期
        
        Returns:
            添加了 ATR 的 DataFrame
        """
        df = df.copy()
        
        # 计算真实波幅
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # ATR 是真实波幅的移动平均
        df[f'ATR{period}'] = true_range.rolling(window=period).mean()
        
        self.log(f"添加了 ATR{period} 指标")
        return df
    
    def add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加成交量相关特征
        
        Args:
            df: 输入 DataFrame
        
        Returns:
            添加了成交量特征的 DataFrame
        """
        df = df.copy()
        
        # 成交量移动平均
        df['Volume_MA7'] = df['Volume'].rolling(window=7).mean()
        df['Volume_MA30'] = df['Volume'].rolling(window=30).mean()
        
        # 成交量变化率
        df['Volume_Change'] = df['Volume'].pct_change()
        
        # 价格成交量趋势 (Price Volume Trend)
        df['PVT'] = (df['Close'].pct_change() * df['Volume']).cumsum()
        
        # 能量潮 (On-Balance Volume)
        obv = []
        obv_val = 0
        for i in range(len(df)):
            if i == 0:
                obv.append(0)
            else:
                if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                    obv_val += df['Volume'].iloc[i]
                elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                    obv_val -= df['Volume'].iloc[i]
                obv.append(obv_val)
        df['OBV'] = obv
        
        self.log("添加了成交量特征")
        return df
    
    def add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加价格相关特征
        
        Args:
            df: 输入 DataFrame
        
        Returns:
            添加了价格特征的 DataFrame
        """
        df = df.copy()
        
        # 收益率
        df['Return'] = df['Close'].pct_change()
        df['Return_1d'] = df['Close'].pct_change(1)
        df['Return_7d'] = df['Close'].pct_change(7)
        df['Return_30d'] = df['Close'].pct_change(30)
        
        # 对数收益率
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # 波动率
        df['Volatility_7d'] = df['Return'].rolling(window=7).std()
        df['Volatility_30d'] = df['Return'].rolling(window=30).std()
        
        # 日内价格范围
        df['Price_Range'] = df['High'] - df['Low']
        df['Price_Range_Pct'] = (df['High'] - df['Low']) / df['Close']
        
        # 收盘价相对位置 (在当日高低价之间的位置)
        df['Close_Position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'])
        
        self.log("添加了价格特征")
        return df
    
    def add_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加所有技术指标
        
        Args:
            df: 输入 DataFrame
        
        Returns:
            添加了所有特征的 DataFrame
        """
        self.log("=" * 60)
        self.log("开始添加所有技术指标")
        self.log("=" * 60)
        
        df = self.add_price_features(df)
        df = self.add_moving_averages(df, windows=[7, 14, 30, 50, 200])
        df = self.add_rsi(df, period=14)
        df = self.add_macd(df)
        df = self.add_bollinger_bands(df, window=20)
        df = self.add_atr(df, period=14)
        df = self.add_volume_features(df)
        
        self.log("=" * 60)
        self.log(f"特征工程完成，共 {len(df.columns)} 个特征")
        self.log("=" * 60)
        
        return df
    
    # ==================== 多数据源整合 ====================
    
    def align_multiple_sources(self, 
                              dfs: Dict[str, pd.DataFrame],
                              method: str = 'outer',
                              fill_method: str = 'ffill') -> pd.DataFrame:
        """
        对齐多个数据源的时间序列
        
        Args:
            dfs: 数据源字典，格式 {'source_name': DataFrame}
            method: 合并方法 ('inner', 'outer', 'left')
            fill_method: 缺失值填充方法
        
        Returns:
            对齐后的 DataFrame
        """
        self.log(f"对齐 {len(dfs)} 个数据源，方法: {method}")
        
        if len(dfs) == 0:
            return pd.DataFrame()
        
        if len(dfs) == 1:
            return list(dfs.values())[0]
        
        # 逐步合并所有数据源
        result = None
        for name, df in dfs.items():
            # 为列名添加前缀
            df_prefixed = df.copy()
            if not df_prefixed.empty:
                df_prefixed.columns = [f"{name}_{col}" if col not in ['Date', 'date'] 
                                      else col for col in df_prefixed.columns]
            
            if result is None:
                result = df_prefixed
            else:
                result = pd.merge(result, df_prefixed, 
                                left_index=True, right_index=True, 
                                how=method)
        
        # 填补缺失值
        if fill_method:
            result = self.handle_missing_values(result, strategy=fill_method, limit=5)
        
        self.log(f"对齐完成，最终行数: {len(result)}, 列数: {len(result.columns)}")
        
        return result
    
    # ==================== 主流程 ====================
    
    def process_pipeline(self, 
                        df: pd.DataFrame,
                        clean: bool = True,
                        add_features: bool = True,
                        detect_outliers: bool = True,
                        handle_missing: bool = True,
                        output_path: Optional[str] = None) -> pd.DataFrame:
        """
        完整的特征工程流程
        
        Args:
            df: 输入 DataFrame
            clean: 是否清洗数据
            add_features: 是否添加特征
            detect_outliers: 是否检测异常值
            handle_missing: 是否处理缺失值
            output_path: 输出文件路径
        
        Returns:
            处理后的 DataFrame
        """
        self.log("\n" + "=" * 60)
        self.log("开始特征工程流程")
        self.log("=" * 60)
        
        # 1. 数据清洗
        if clean:
            df = self.clean_data(df)
        
        # 2. 添加特征
        if add_features:
            df = self.add_all_features(df)
        
        # 3. 检测异常值
        if detect_outliers:
            df = self.detect_outliers(df, columns=['Close', 'Volume'], 
                                     method='iqr', threshold=3.0)
        
        # 4. 处理缺失值
        if handle_missing:
            df = self.handle_missing_values(df, strategy='ffill', limit=3)
            # 删除剩余的缺失值
            df = df.dropna()
        
        # 5. 保存
        if output_path:
            df.to_csv(output_path)
            self.log(f"\n结果已保存到: {output_path}")
        
        self.log("\n" + "=" * 60)
        self.log(f"特征工程完成！最终数据: {len(df)} 行 × {len(df.columns)} 列")
        self.log("=" * 60 + "\n")
        
        return df


# ==================== 便捷函数 ====================

def add_features(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    便捷函数：添加所有特征
    
    Args:
        df: 输入 DataFrame
        verbose: 是否打印日志
    
    Returns:
        添加了特征的 DataFrame
    """
    engineer = FeatureEngineer(verbose=verbose)
    return engineer.process_pipeline(df)


if __name__ == '__main__':
    # 测试特征工程
    print("\n" + "=" * 60)
    print("  Bitcoin Research Agent - 特征工程测试")
    print("=" * 60 + "\n")
    
    # 加载数据
    df = pd.read_csv('data/raw/bitcoin_price.csv', index_col=0, parse_dates=True)
    print(f'✓ 加载数据: {len(df)} 行')
    print(f'✓ 时间范围: {df.index[0]} 到 {df.index[-1]}')
    print(f'✓ 原始特征: {list(df.columns)}\n')
    
    # 特征工程
    engineer = FeatureEngineer(verbose=True)
    df_processed = engineer.process_pipeline(
        df, 
        clean=True,
        add_features=True,
        detect_outliers=True,
        handle_missing=True,
        output_path='data/processed/bitcoin_features.csv'
    )
    
    # 显示结果
    print("\n" + "=" * 60)
    print("  处理结果摘要")
    print("=" * 60)
    print(f"\n最终特征列表 ({len(df_processed.columns)} 个):")
    for i, col in enumerate(df_processed.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\n前 5 行数据预览:")
    print(df_processed.head())
    
    print(f"\n数据统计:")
    print(df_processed.describe())
