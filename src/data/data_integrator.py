"""
Bitcoin Research Agent - 数据整合模块

功能：
1. 整合多个数据源（市场数据、链上数据、宏观数据、新闻数据）
2. 时间序列对齐
3. 生成统一的特征数据集

作者：Bitcoin Research Agent Team
日期：2025-10-25
"""

import pandas as pd
import numpy as np
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.feature_engineering import FeatureEngineer


class DataIntegrator:
    """数据整合器 - 合并多个数据源"""
    
    def __init__(self, data_dir: str = 'data', verbose: bool = True):
        """
        初始化数据整合器
        
        Args:
            data_dir: 数据根目录
            verbose: 是否打印详细信息
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / 'raw'
        self.processed_dir = self.data_dir / 'processed'
        self.verbose = verbose
        
        # 确保目录存在
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # 特征工程器
        self.feature_engineer = FeatureEngineer(verbose=verbose)
    
    def log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[DataIntegrator] {message}")
    
    def load_market_data(self) -> Optional[pd.DataFrame]:
        """
        加载市场数据
        
        Returns:
            市场数据 DataFrame
        """
        market_file = self.raw_dir / 'bitcoin_price.csv'
        
        if not market_file.exists():
            self.log(f"Warning: Market data not found at {market_file}")
            return None
        
        try:
            df = pd.read_csv(market_file, index_col=0, parse_dates=True)
            self.log(f"Loaded market data: {len(df)} rows")
            return df
        except Exception as e:
            self.log(f"Error loading market data: {e}")
            return None
    
    def load_onchain_data(self) -> Optional[pd.DataFrame]:
        """
        加载链上数据
        
        Returns:
            链上数据 DataFrame
        """
        onchain_file = self.raw_dir / 'onchain_data.csv'
        
        if not onchain_file.exists():
            self.log(f"Info: Onchain data not found at {onchain_file} (skipping)")
            return None
        
        try:
            df = pd.read_csv(onchain_file, index_col=0, parse_dates=True)
            self.log(f"Loaded onchain data: {len(df)} rows")
            return df
        except Exception as e:
            self.log(f"Error loading onchain data: {e}")
            return None
    
    def load_macro_data(self) -> Optional[pd.DataFrame]:
        """
        加载宏观数据
        
        Returns:
            宏观数据 DataFrame
        """
        macro_dir = self.raw_dir
        macro_files = {
            'gold': macro_dir / 'macro_gold_test.csv',
            'vix': macro_dir / 'macro_vix_test.csv',
        }
        
        dfs = {}
        for name, file_path in macro_files.items():
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                    dfs[name] = df
                    self.log(f"Loaded {name} data: {len(df)} rows")
                except Exception as e:
                    self.log(f"Error loading {name} data: {e}")
        
        if not dfs:
            self.log("Info: No macro data found (skipping)")
            return None
        
        # 合并所有宏观数据
        result = None
        for name, df in dfs.items():
            if result is None:
                result = df.copy()
                result.columns = [f'macro_{name}_{col}' for col in result.columns]
            else:
                df_renamed = df.copy()
                df_renamed.columns = [f'macro_{name}_{col}' for col in df_renamed.columns]
                result = pd.merge(result, df_renamed, 
                                left_index=True, right_index=True, how='outer')
        
        self.log(f"Combined macro data: {len(result)} rows, {len(result.columns)} columns")
        return result
    
    def load_news_sentiment(self) -> Optional[pd.DataFrame]:
        """
        加载新闻情感数据
        
        Returns:
            新闻情感数据 DataFrame
        """
        news_file = self.raw_dir / 'news_sentiment.csv'
        
        if not news_file.exists():
            self.log(f"Info: News sentiment data not found at {news_file} (skipping)")
            return None
        
        try:
            df = pd.read_csv(news_file, index_col=0, parse_dates=True)
            self.log(f"Loaded news sentiment data: {len(df)} rows")
            return df
        except Exception as e:
            self.log(f"Error loading news sentiment data: {e}")
            return None
    
    def integrate_all_data(self, 
                          add_market_features: bool = True,
                          align_method: str = 'outer',
                          fill_method: str = 'ffill') -> pd.DataFrame:
        """
        整合所有数据源
        
        Args:
            add_market_features: 是否添加市场技术指标
            align_method: 时间对齐方法 ('inner', 'outer', 'left')
            fill_method: 缺失值填补方法
        
        Returns:
            整合后的 DataFrame
        """
        self.log("\n" + "=" * 60)
        self.log("Starting data integration pipeline")
        self.log("=" * 60 + "\n")
        
        # 1. 加载所有数据源
        self.log("Step 1: Loading all data sources...")
        market_df = self.load_market_data()
        onchain_df = self.load_onchain_data()
        macro_df = self.load_macro_data()
        news_df = self.load_news_sentiment()
        
        if market_df is None:
            raise ValueError("Market data is required but not found!")
        
        # 2. 处理市场数据并添加技术指标
        self.log("\nStep 2: Processing market data and adding technical indicators...")
        if add_market_features:
            market_df = self.feature_engineer.process_pipeline(
                market_df,
                clean=True,
                add_features=True,
                detect_outliers=True,
                handle_missing=True,
                output_path=None
            )
        else:
            market_df = self.feature_engineer.clean_data(market_df)
        
        # 重命名列（为市场数据添加前缀）
        market_columns = {col: f'market_{col}' if col not in ['Date', 'date'] 
                         else col for col in market_df.columns}
        market_df = market_df.rename(columns=market_columns)
        
        # 3. 构建数据源字典
        data_sources = {'market': market_df}
        
        if onchain_df is not None:
            # 清洗链上数据
            onchain_df = self.feature_engineer.clean_data(onchain_df)
            onchain_columns = {col: f'onchain_{col}' if col not in ['Date', 'date'] 
                              else col for col in onchain_df.columns}
            onchain_df = onchain_df.rename(columns=onchain_columns)
            data_sources['onchain'] = onchain_df
        
        if macro_df is not None:
            # 宏观数据已经有前缀了
            data_sources['macro'] = macro_df
        
        if news_df is not None:
            # 清洗新闻情感数据
            news_df = self.feature_engineer.clean_data(news_df)
            news_columns = {col: f'news_{col}' if col not in ['Date', 'date'] 
                           else col for col in news_df.columns}
            news_df = news_df.rename(columns=news_columns)
            data_sources['news'] = news_df
        
        # 4. 时间对齐
        self.log(f"\nStep 3: Aligning {len(data_sources)} data sources (method={align_method})...")
        
        result = None
        for name, df in data_sources.items():
            if result is None:
                result = df
                self.log(f"  Base: {name} ({len(df)} rows, {len(df.columns)} columns)")
            else:
                before_rows = len(result)
                result = pd.merge(result, df, 
                                left_index=True, right_index=True, 
                                how=align_method)
                self.log(f"  Merged: {name} ({len(df)} rows, {len(df.columns)} columns) -> {len(result)} rows")
        
        # 5. 处理缺失值
        self.log(f"\nStep 4: Handling missing values (method={fill_method})...")
        missing_before = result.isnull().sum().sum()
        self.log(f"  Missing values before: {missing_before}")
        
        if fill_method and missing_before > 0:
            result = self.feature_engineer.handle_missing_values(
                result, strategy=fill_method, limit=5
            )
            # 删除剩余缺失值过多的行
            result = result.dropna(thresh=len(result.columns) * 0.7)  # 至少70%的列有值
        
        missing_after = result.isnull().sum().sum()
        self.log(f"  Missing values after: {missing_after}")
        
        # 6. 保存结果
        output_file = self.processed_dir / 'integrated_features.csv'
        result.to_csv(output_file)
        self.log(f"\nStep 5: Saved integrated data to {output_file}")
        
        # 7. 生成数据报告
        self.log("\n" + "=" * 60)
        self.log("Data Integration Summary")
        self.log("=" * 60)
        self.log(f"Final dataset: {len(result)} rows x {len(result.columns)} columns")
        self.log(f"Date range: {result.index[0]} to {result.index[-1]}")
        self.log(f"Data sources integrated: {len(data_sources)}")
        self.log(f"  - Market data: {len([c for c in result.columns if c.startswith('market_')])} features")
        self.log(f"  - Onchain data: {len([c for c in result.columns if c.startswith('onchain_')])} features")
        self.log(f"  - Macro data: {len([c for c in result.columns if c.startswith('macro_')])} features")
        self.log(f"  - News data: {len([c for c in result.columns if c.startswith('news_')])} features")
        self.log("=" * 60 + "\n")
        
        return result
    
    def create_feature_groups(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        将特征分组
        
        Args:
            df: 输入 DataFrame
        
        Returns:
            特征分组字典
        """
        groups = {
            'market': [c for c in df.columns if c.startswith('market_')],
            'onchain': [c for c in df.columns if c.startswith('onchain_')],
            'macro': [c for c in df.columns if c.startswith('macro_')],
            'news': [c for c in df.columns if c.startswith('news_')],
        }
        
        # 进一步细分市场特征
        market_cols = groups['market']
        groups['market_price'] = [c for c in market_cols if any(x in c.lower() for x in ['close', 'open', 'high', 'low', 'return', 'price'])]
        groups['market_volume'] = [c for c in market_cols if 'volume' in c.lower() or 'obv' in c.lower() or 'pvt' in c.lower()]
        groups['market_technical'] = [c for c in market_cols if any(x in c.lower() for x in ['ma', 'ema', 'rsi', 'macd', 'bb_', 'atr'])]
        
        return groups


def main():
    """主函数 - 运行数据整合"""
    print("\n" + "=" * 60)
    print("  Bitcoin Research Agent - Data Integration")
    print("=" * 60 + "\n")
    
    # 创建数据整合器
    integrator = DataIntegrator(data_dir='data', verbose=True)
    
    # 整合所有数据
    try:
        df_integrated = integrator.integrate_all_data(
            add_market_features=True,
            align_method='outer',
            fill_method='ffill'
        )
        
        # 显示特征分组
        feature_groups = integrator.create_feature_groups(df_integrated)
        
        print("\nFeature Groups:")
        for group_name, features in feature_groups.items():
            if features:
                print(f"\n{group_name} ({len(features)} features):")
                for feat in features[:5]:  # 只显示前5个
                    print(f"  - {feat}")
                if len(features) > 5:
                    print(f"  ... and {len(features) - 5} more")
        
        # 显示数据样本
        print("\n" + "=" * 60)
        print("Sample Data (first 5 rows, first 10 columns):")
        print("=" * 60)
        print(df_integrated.iloc[:5, :10])
        
        print("\n" + "=" * 60)
        print("Integration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during integration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

