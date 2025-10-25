"""
WAL-10 功能测试脚本

测试所有数据收集器的功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
from datetime import datetime


def test_data_loader():
    """测试 yfinance 数据加载器"""
    print("\n" + "=" * 60)
    print("测试 1: yfinance 数据加载器")
    print("=" * 60)
    
    try:
        from data_loader import load_bitcoin_data
        
        df = load_bitcoin_data(start='2024-01-01')
        
        if not df.empty:
            print(f"✓ yfinance 测试通过")
            print(f"  数据条数: {len(df)}")
            print(f"  数据范围: {df.index[0]} 到 {df.index[-1]}")
            print(f"  列: {list(df.columns)}")
            return True
        else:
            print(f"✗ yfinance 测试失败: 数据为空")
            return False
            
    except Exception as e:
        print(f"✗ yfinance 测试失败: {e}")
        return False


def test_binance_collector():
    """测试 Binance 收集器"""
    print("\n" + "=" * 60)
    print("测试 2: Binance 数据收集器")
    print("=" * 60)
    
    try:
        from data.binance_collector import BinanceCollector
        
        collector = BinanceCollector()
        
        # 测试 K线数据
        df = collector.get_klines(interval='1d', limit=10)
        
        if not df.empty:
            print(f"✓ Binance K线测试通过")
            print(f"  数据条数: {len(df)}")
            print(f"  最新价格: ${df['close'].iloc[-1]:,.2f}")
            return True
        else:
            print(f"⚠️  Binance 测试部分失败: K线数据为空")
            print(f"   (可能是网络限制或API限流)")
            return False
            
    except Exception as e:
        print(f"⚠️  Binance 测试跳过: {e}")
        print(f"   (Binance API 可能在你的地区不可用)")
        return False


def test_coingecko_collector():
    """测试 CoinGecko 收集器"""
    print("\n" + "=" * 60)
    print("测试 3: CoinGecko 数据收集器")
    print("=" * 60)
    
    try:
        from data.coingecko_collector import CoinGeckoCollector
        
        collector = CoinGeckoCollector()
        
        # 测试当前价格
        current = collector.get_current_price()
        
        if current:
            print(f"✓ CoinGecko 当前价格测试通过")
            price = current.get('usd', 0)
            print(f"  当前价格: ${price:,.2f}")
            
            # 测试市场数据
            df = collector.get_market_chart(days=7, interval='daily')
            if not df.empty:
                print(f"✓ CoinGecko 市场数据测试通过")
                print(f"  数据条数: {len(df)}")
                return True
            else:
                print(f"⚠️  CoinGecko 市场数据为空")
                return False
        else:
            print(f"✗ CoinGecko 测试失败")
            return False
            
    except Exception as e:
        print(f"✗ CoinGecko 测试失败: {e}")
        return False


def test_aggregator():
    """测试数据聚合器"""
    print("\n" + "=" * 60)
    print("测试 4: 数据聚合器")
    print("=" * 60)
    
    try:
        from data.market_data_aggregator import MarketDataAggregator
        
        aggregator = MarketDataAggregator()
        
        # 获取综合数据
        data_dict = aggregator.get_comprehensive_data(days_back=30, include_funding=False)
        
        if data_dict:
            print(f"✓ 数据聚合器测试通过")
            print(f"  数据源数量: {len(data_dict)}")
            
            # 合并数据
            merged_df = aggregator.merge_ohlcv_data(data_dict)
            
            if not merged_df.empty:
                print(f"✓ 数据合并测试通过")
                print(f"  合并后数据条数: {len(merged_df)}")
                
                # 验证数据
                validated_df = aggregator.validate_data(merged_df)
                print(f"✓ 数据验证测试通过")
                print(f"  验证后数据条数: {len(validated_df)}")
                
                return True
            else:
                print(f"✗ 数据合并失败")
                return False
        else:
            print(f"✗ 数据聚合失败")
            return False
            
    except Exception as e:
        print(f"✗ 数据聚合器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n")
    print("#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + " " * 15 + "WAL-10 功能测试" + " " * 15 + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    results = {}
    
    # 运行测试
    results['yfinance'] = test_data_loader()
    results['binance'] = test_binance_collector()
    results['coingecko'] = test_coingecko_collector()
    results['aggregator'] = test_aggregator()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:15s}: {status}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed >= 2:  # 至少2个数据源可用
        print("\n✓ WAL-10 功能测试通过！")
        print("  至少有2个数据源可用，可以继续开发。")
        return True
    else:
        print("\n⚠️  WAL-10 功能测试部分通过")
        print("  建议检查网络连接和API访问权限。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

