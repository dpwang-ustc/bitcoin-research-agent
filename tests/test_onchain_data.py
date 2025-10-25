"""
WAL-11 链上数据收集测试

测试内容：
1. Blockchain.com API 连接测试
2. Mempool.space API 连接测试
3. Glassnode API 连接测试（如有 API Key）
4. 数据聚合器链上数据集成测试
5. 数据保存和加载测试
"""

import sys
import io
import os
import pandas as pd
from datetime import datetime

# Windows UTF-8 输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.onchain_collector import OnchainCollector
from data.market_data_aggregator import MarketDataAggregator


def print_section_header(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"{' ' * ((60 - len(title)) // 2)}{title}")
    print("=" * 60)


def test_blockchain_com_api():
    """测试 Blockchain.com API"""
    print_section_header("测试 1: Blockchain.com API")
    
    collector = OnchainCollector()
    
    try:
        # 测试区块链统计
        stats = collector.get_blockchain_stats()
        
        if stats and 'market_price_usd' in stats:
            print(f"✓ Blockchain.com API 连接成功")
            print(f"\n当前数据快照:")
            print(f"  比特币价格: ${stats.get('market_price_usd', 0):,.2f}")
            print(f"  哈希率: {stats.get('hash_rate', 0):,.0f} TH/s")
            print(f"  总供应量: {stats.get('total_btc', 0):,.2f} BTC")
            print(f"  24h 交易数: {stats.get('n_tx', 0):,}")
            print(f"  难度: {stats.get('difficulty', 0):,.0f}")
            print(f"  市值: ${stats.get('market_cap_usd', 0):,.0f}")
            return True
        else:
            print("✗ Blockchain.com API 返回数据为空")
            return False
            
    except Exception as e:
        print(f"✗ Blockchain.com API 测试失败: {e}")
        return False


def test_mempool_space_api():
    """测试 Mempool.space API"""
    print_section_header("测试 2: Mempool.space API")
    
    collector = OnchainCollector()
    
    try:
        # 测试内存池信息
        mempool = collector.get_mempool_info()
        
        if mempool and 'mempool_size' in mempool:
            print(f"✓ Mempool.space API 连接成功")
            print(f"\n当前内存池状态:")
            print(f"  待确认交易数: {mempool.get('mempool_size', 0):,}")
            print(f"  内存池大小: {mempool.get('mempool_bytes', 0):,} bytes")
            print(f"  总手续费: {mempool.get('total_fee', 0):,.0f} satoshi")
            return True
        else:
            print("✗ Mempool.space API 返回数据为空")
            return False
            
    except Exception as e:
        print(f"✗ Mempool.space API 测试失败: {e}")
        return False


def test_large_transactions():
    """测试大额交易查询"""
    print_section_header("测试 3: 大额交易查询")
    
    collector = OnchainCollector()
    
    try:
        # 查询大额交易（阈值 50 BTC）
        large_txs = collector.get_large_transactions(threshold_btc=50.0)
        
        if not large_txs.empty:
            print(f"✓ 发现 {len(large_txs)} 笔大额交易 (>50 BTC)")
            print(f"\n最新的大额交易:")
            print(large_txs[['time', 'total_btc', 'fee_btc']].head())
            return True
        else:
            print("ℹ️  当前未发现大额交易（这是正常的）")
            return True  # 没有大额交易也算正常
            
    except Exception as e:
        print(f"✗ 大额交易查询失败: {e}")
        return False


def test_glassnode_api():
    """测试 Glassnode API"""
    print_section_header("测试 4: Glassnode API")
    
    # 检查是否有 API Key
    glassnode_key = os.getenv('GLASSNODE_API_KEY')
    
    if not glassnode_key:
        print("⚠️  跳过 Glassnode 测试（未设置 GLASSNODE_API_KEY）")
        print("\n如需测试 Glassnode API:")
        print("1. 访问: https://studio.glassnode.com/settings/api")
        print("2. 注册免费账号并获取 API Key")
        print("3. 设置环境变量: set GLASSNODE_API_KEY=your_key")
        return True  # 跳过不算失败
    
    collector = OnchainCollector(glassnode_key=glassnode_key)
    
    try:
        # 测试活跃地址
        print("测试活跃地址数据...")
        active_addrs = collector.get_active_addresses(days=7)
        
        if not active_addrs.empty:
            print(f"✓ Glassnode API 连接成功")
            print(f"\n最近7天活跃地址:")
            print(active_addrs.tail())
            return True
        else:
            print("✗ Glassnode API 返回数据为空")
            return False
            
    except Exception as e:
        print(f"✗ Glassnode API 测试失败: {e}")
        if "401" in str(e) or "403" in str(e):
            print("   提示: 请检查 API Key 是否正确")
        return False


def test_network_health():
    """测试网络健康度综合指标"""
    print_section_header("测试 5: 网络健康度综合指标")
    
    collector = OnchainCollector()
    
    try:
        health = collector.get_network_health_summary()
        
        if health:
            print(f"✓ 网络健康度数据收集成功")
            print(f"\n收集到的指标数:")
            for key in health.keys():
                print(f"  - {key}")
            return True
        else:
            print("✗ 网络健康度数据收集失败")
            return False
            
    except Exception as e:
        print(f"✗ 网络健康度测试失败: {e}")
        return False


def test_aggregator_integration():
    """测试数据聚合器链上数据集成"""
    print_section_header("测试 6: 数据聚合器链上数据集成")
    
    try:
        aggregator = MarketDataAggregator()
        
        print("正在收集综合数据（包含链上数据）...")
        data_dict = aggregator.get_comprehensive_data(
            days_back=7,
            include_funding=True,
            include_market_info=True,
            include_onchain=True
        )
        
        if data_dict:
            print(f"\n✓ 数据聚合成功，共 {len(data_dict)} 个数据集")
            
            # 检查是否包含链上数据
            onchain_keys = ['blockchain_stats', 'mempool_info', 'active_addresses', 'utxo_count', 'exchange_flows']
            found_onchain = [key for key in onchain_keys if key in data_dict]
            
            if found_onchain:
                print(f"\n包含的链上数据集:")
                for key in found_onchain:
                    print(f"  ✓ {key}")
                return True
            else:
                print("⚠️  未找到链上数据集")
                return False
        else:
            print("✗ 数据聚合失败")
            return False
            
    except Exception as e:
        print(f"✗ 数据聚合器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_save_load():
    """测试数据保存和加载"""
    print_section_header("测试 7: 数据保存和加载")
    
    try:
        collector = OnchainCollector()
        
        # 获取一些数据
        stats = collector.get_blockchain_stats()
        
        if not stats:
            print("⚠️  无法获取数据进行保存测试")
            return False
        
        # 保存到 DataFrame
        df_stats = pd.DataFrame([stats])
        
        # 确保目录存在
        os.makedirs('data/raw', exist_ok=True)
        
        # 保存
        output_file = 'data/raw/onchain_stats_test.csv'
        df_stats.to_csv(output_file, index=False)
        print(f"✓ 数据已保存到: {output_file}")
        
        # 加载
        df_loaded = pd.read_csv(output_file)
        print(f"✓ 数据已加载: {len(df_loaded)} 行, {len(df_loaded.columns)} 列")
        
        # 验证
        if len(df_loaded) > 0:
            print(f"\n加载的数据预览:")
            print(df_loaded.head())
            return True
        else:
            print("✗ 加载的数据为空")
            return False
            
    except Exception as e:
        print(f"✗ 数据保存/加载测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("  WAL-11 链上数据收集 - 完整测试套件")
    print("=" * 60)
    print()
    
    results = {}
    
    # 运行所有测试
    results['Blockchain.com API'] = test_blockchain_com_api()
    results['Mempool.space API'] = test_mempool_space_api()
    results['大额交易查询'] = test_large_transactions()
    results['Glassnode API'] = test_glassnode_api()
    results['网络健康度'] = test_network_health()
    results['数据聚合器集成'] = test_aggregator_integration()
    results['数据保存加载'] = test_data_save_load()
    
    # 汇总结果
    print_section_header("WAL-11 测试结果汇总")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print()
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}  {test_name}")
    
    print()
    print("=" * 60)
    if passed == total:
        print(f"🎉 所有测试通过！({passed}/{total})")
    else:
        print(f"⚠️  部分测试失败 ({passed}/{total})")
    print("=" * 60)
    print()
    
    # 额外说明
    print("📝 注意事项:")
    print("- Blockchain.com 和 Mempool.space 完全免费无需注册")
    print("- Glassnode 需要免费注册获取 API Key")
    print("- 部分 API 可能因地区限制无法访问")
    print("- 如需完整测试，请配置 GLASSNODE_API_KEY 环境变量")
    print()
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

