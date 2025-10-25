"""
测试特征工程模块
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from src.feature_engineering import FeatureEngineer


def test_feature_engineering():
    print("=" * 60)
    print("  Bitcoin Research Agent - Feature Engineering Test")
    print("=" * 60)
    print()
    
    # 加载数据
    df = pd.read_csv('data/raw/bitcoin_price.csv', index_col=0, parse_dates=True)
    print(f'Loaded data: {len(df)} rows')
    print(f'Date range: {df.index[0]} to {df.index[-1]}')
    print(f'Original features: {list(df.columns)}')
    print()
    
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
    print("  Processing Results Summary")
    print("=" * 60)
    print(f"\nFinal features ({len(df_processed.columns)}):")
    for i, col in enumerate(df_processed.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\nFirst 5 rows:")
    print(df_processed.head())
    
    print(f"\nData statistics:")
    print(df_processed[['Close', 'Return', 'MA7', 'MA30', 'RSI14', 'MACD']].describe())
    
    print("\n" + "=" * 60)
    print("  Test completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    test_feature_engineering()

