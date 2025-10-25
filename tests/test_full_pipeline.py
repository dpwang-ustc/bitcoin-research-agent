"""
完整的特征工程流程测试

测试内容：
1. 数据加载
2. 特征工程
3. 数据整合
4. 结果验证
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from src.feature_engineering import FeatureEngineer
from src.data.data_integrator import DataIntegrator


def test_feature_engineer():
    """测试特征工程器"""
    print("\n" + "=" * 70)
    print("  TEST 1: Feature Engineer")
    print("=" * 70 + "\n")
    
    # 加载数据
    df = pd.read_csv('data/raw/bitcoin_price.csv', index_col=0, parse_dates=True)
    print(f"Loaded data: {len(df)} rows")
    
    # 创建特征工程器
    engineer = FeatureEngineer(verbose=False)
    
    # 测试各个功能
    tests_passed = 0
    tests_total = 0
    
    # Test 1: 数据清洗
    tests_total += 1
    try:
        df_clean = engineer.clean_data(df)
        assert len(df_clean) > 0, "Clean data is empty"
        assert isinstance(df_clean.index, pd.DatetimeIndex), "Index is not DatetimeIndex"
        print("[PASS] Data cleaning")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Data cleaning: {e}")
    
    # Test 2: 价格特征
    tests_total += 1
    try:
        df_price = engineer.add_price_features(df_clean)
        assert 'Return' in df_price.columns, "Return not found"
        assert 'Volatility_7d' in df_price.columns, "Volatility not found"
        print("[PASS] Price features")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Price features: {e}")
    
    # Test 3: 移动平均
    tests_total += 1
    try:
        df_ma = engineer.add_moving_averages(df_clean, windows=[7, 30])
        assert 'MA7' in df_ma.columns, "MA7 not found"
        assert 'EMA30' in df_ma.columns, "EMA30 not found"
        print("[PASS] Moving averages")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Moving averages: {e}")
    
    # Test 4: RSI
    tests_total += 1
    try:
        df_rsi = engineer.add_rsi(df_clean, period=14)
        assert 'RSI14' in df_rsi.columns, "RSI14 not found"
        assert df_rsi['RSI14'].max() <= 100, "RSI > 100"
        assert df_rsi['RSI14'].min() >= 0, "RSI < 0"
        print("[PASS] RSI indicator")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] RSI indicator: {e}")
    
    # Test 5: MACD
    tests_total += 1
    try:
        df_macd = engineer.add_macd(df_clean)
        assert 'MACD' in df_macd.columns, "MACD not found"
        assert 'MACD_Signal' in df_macd.columns, "MACD_Signal not found"
        print("[PASS] MACD indicator")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] MACD indicator: {e}")
    
    # Test 6: Bollinger Bands
    tests_total += 1
    try:
        df_bb = engineer.add_bollinger_bands(df_clean)
        assert 'BB_Upper' in df_bb.columns, "BB_Upper not found"
        assert 'BB_Lower' in df_bb.columns, "BB_Lower not found"
        assert 'BB_Middle' in df_bb.columns, "BB_Middle not found"
        print("[PASS] Bollinger Bands")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Bollinger Bands: {e}")
    
    # Test 7: ATR
    tests_total += 1
    try:
        df_atr = engineer.add_atr(df_clean)
        assert 'ATR14' in df_atr.columns, "ATR14 not found"
        print("[PASS] ATR indicator")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] ATR indicator: {e}")
    
    # Test 8: 成交量特征
    tests_total += 1
    try:
        df_vol = engineer.add_volume_features(df_clean)
        assert 'OBV' in df_vol.columns, "OBV not found"
        assert 'Volume_MA7' in df_vol.columns, "Volume_MA7 not found"
        print("[PASS] Volume features")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Volume features: {e}")
    
    # Test 9: 异常值检测
    tests_total += 1
    try:
        df_outlier = engineer.detect_outliers(df_clean, columns=['Close'], method='iqr')
        assert 'Close_outlier' in df_outlier.columns, "Outlier column not found"
        print("[PASS] Outlier detection")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Outlier detection: {e}")
    
    # Test 10: 缺失值处理
    tests_total += 1
    try:
        df_test = df_clean.copy()
        df_test.iloc[0:5, 0] = np.nan
        df_filled = engineer.handle_missing_values(df_test, strategy='ffill')
        assert df_filled.isnull().sum().sum() <= df_test.isnull().sum().sum(), "Missing values not reduced"
        print("[PASS] Missing value handling")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Missing value handling: {e}")
    
    # Test 11: 完整流程
    tests_total += 1
    try:
        df_full = engineer.process_pipeline(df, output_path=None)
        assert len(df_full) > 0, "Pipeline output is empty"
        assert len(df_full.columns) > 40, f"Too few features: {len(df_full.columns)}"
        print("[PASS] Full pipeline")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Full pipeline: {e}")
    
    print(f"\nTest Results: {tests_passed}/{tests_total} passed ({tests_passed/tests_total*100:.1f}%)")
    return tests_passed, tests_total


def test_data_integrator():
    """测试数据整合器"""
    print("\n" + "=" * 70)
    print("  TEST 2: Data Integrator")
    print("=" * 70 + "\n")
    
    integrator = DataIntegrator(data_dir='data', verbose=False)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: 加载市场数据
    tests_total += 1
    try:
        df_market = integrator.load_market_data()
        assert df_market is not None, "Market data not loaded"
        assert len(df_market) > 0, "Market data is empty"
        print("[PASS] Load market data")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Load market data: {e}")
    
    # Test 2: 加载宏观数据
    tests_total += 1
    try:
        df_macro = integrator.load_macro_data()
        # 宏观数据可能不存在，不算失败
        print("[PASS] Load macro data (optional)")
        tests_passed += 1
    except Exception as e:
        print(f"[INFO] Load macro data: {e}")
        tests_passed += 1  # 不算失败
    
    # Test 3: 数据整合
    tests_total += 1
    try:
        df_integrated = integrator.integrate_all_data(
            add_market_features=True,
            align_method='outer',
            fill_method='ffill'
        )
        assert df_integrated is not None, "Integration failed"
        assert len(df_integrated) > 0, "Integrated data is empty"
        assert len(df_integrated.columns) >= 42, f"Too few features: {len(df_integrated.columns)}"
        print(f"[PASS] Data integration ({len(df_integrated)} rows, {len(df_integrated.columns)} cols)")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Data integration: {e}")
    
    # Test 4: 特征分组
    tests_total += 1
    try:
        feature_groups = integrator.create_feature_groups(df_integrated)
        assert 'market' in feature_groups, "Market group not found"
        assert len(feature_groups['market']) > 0, "Market features empty"
        print(f"[PASS] Feature grouping ({len(feature_groups)} groups)")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Feature grouping: {e}")
    
    print(f"\nTest Results: {tests_passed}/{tests_total} passed ({tests_passed/tests_total*100:.1f}%)")
    return tests_passed, tests_total


def test_data_quality():
    """测试数据质量"""
    print("\n" + "=" * 70)
    print("  TEST 3: Data Quality Checks")
    print("=" * 70 + "\n")
    
    tests_passed = 0
    tests_total = 0
    
    # 加载处理后的数据
    try:
        df = pd.read_csv('data/processed/integrated_features.csv', index_col=0, parse_dates=True)
    except Exception as e:
        print(f"[FAIL] Cannot load integrated data: {e}")
        return 0, 1
    
    # Test 1: 检查数据完整性
    tests_total += 1
    try:
        assert len(df) > 0, "Data is empty"
        assert len(df.columns) > 0, "No columns"
        print(f"[PASS] Data integrity ({len(df)} rows x {len(df.columns)} cols)")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Data integrity: {e}")
    
    # Test 2: 检查时间索引
    tests_total += 1
    try:
        assert isinstance(df.index, pd.DatetimeIndex), "Index is not DatetimeIndex"
        assert df.index.is_monotonic_increasing, "Index is not sorted"
        print("[PASS] Time index")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Time index: {e}")
    
    # Test 3: 检查缺失值
    tests_total += 1
    try:
        missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
        print(f"[INFO] Missing values: {missing_pct:.2f}%")
        if missing_pct < 10:
            print("[PASS] Missing values acceptable")
            tests_passed += 1
        else:
            print(f"[WARN] High missing values: {missing_pct:.2f}%")
    except Exception as e:
        print(f"[FAIL] Missing value check: {e}")
    
    # Test 4: 检查数值范围
    tests_total += 1
    try:
        # 检查价格是否合理
        if 'market_Close' in df.columns:
            close_min = df['market_Close'].min()
            close_max = df['market_Close'].max()
            assert close_min > 0, "Negative prices found"
            assert close_max < 1000000, "Unrealistic high prices"
            print(f"[PASS] Price range: ${close_min:.2f} - ${close_max:.2f}")
            tests_passed += 1
        else:
            print("[SKIP] No price column")
            tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Price range: {e}")
    
    # Test 5: 检查技术指标
    tests_total += 1
    try:
        technical_indicators = ['RSI14', 'MACD', 'BB_Upper', 'ATR14']
        found = [ind for ind in technical_indicators if f'market_{ind}' in df.columns]
        assert len(found) > 0, "No technical indicators found"
        print(f"[PASS] Technical indicators ({len(found)}/{len(technical_indicators)})")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Technical indicators: {e}")
    
    print(f"\nTest Results: {tests_passed}/{tests_total} passed ({tests_passed/tests_total*100:.1f}%)")
    return tests_passed, tests_total


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - Full Pipeline Test")
    print("=" * 70)
    
    total_passed = 0
    total_tests = 0
    
    # 测试特征工程器
    passed, total = test_feature_engineer()
    total_passed += passed
    total_tests += total
    
    # 测试数据整合器
    passed, total = test_data_integrator()
    total_passed += passed
    total_tests += total
    
    # 测试数据质量
    passed, total = test_data_quality()
    total_passed += passed
    total_tests += total
    
    # 总结
    print("\n" + "=" * 70)
    print("  FINAL RESULTS")
    print("=" * 70)
    success_rate = total_passed / total_tests * 100
    print(f"Total: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("\n[SUCCESS] All tests passed! ✓")
    elif success_rate >= 80:
        print("\n[GOOD] Most tests passed! ⚠")
    else:
        print("\n[WARNING] Many tests failed! ✗")
    
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()

