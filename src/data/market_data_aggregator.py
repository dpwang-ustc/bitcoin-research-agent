"""
市场数据聚合器

整合多个数据源：
1. yfinance - 历史数据
2. Binance - 实时数据 + 资金费率
3. CoinGecko - 市场数据 + 币种信息
4. Blockchain.com & Mempool.space - 链上数据
5. Glassnode - 高级链上指标（可选）

提供统一的接口和数据验证
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import warnings
warnings.filterwarnings('ignore')

# 导入各个数据收集器
from data_loader import load_bitcoin_data
try:
    from binance_collector import BinanceCollector
except ImportError:
    from data.binance_collector import BinanceCollector

try:
    from coingecko_collector import CoinGeckoCollector
except ImportError:
    from data.coingecko_collector import CoinGeckoCollector

try:
    from onchain_collector import OnchainCollector
except ImportError:
    from data.onchain_collector import OnchainCollector


class MarketDataAggregator:
    """市场数据聚合器"""
    
    def __init__(self, glassnode_key: Optional[str] = None):
        """
        初始化所有数据源
        
        Args:
            glassnode_key: Glassnode API Key (可选)
        """
        self.binance = BinanceCollector()
        self.coingecko = CoinGeckoCollector()
        self.onchain = OnchainCollector(glassnode_key=glassnode_key)
        
    def get_comprehensive_data(self, 
                               days_back: int = 365,
                               include_funding: bool = True,
                               include_market_info: bool = True,
                               include_onchain: bool = True) -> Dict[str, pd.DataFrame]:
        """
        获取综合市场数据
        
        Args:
            days_back: 回溯天数
            include_funding: 是否包含资金费率
            include_market_info: 是否包含市场信息
            include_onchain: 是否包含链上数据
        
        Returns:
            Dict with multiple DataFrames
        """
        print("=" * 60)
        print("  开始收集综合市场数据")
        print("=" * 60)
        print()
        
        result = {}
        
        # 1. yfinance 历史数据（主要数据源）
        print("1. 从 yfinance 获取历史数据...")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        df_yfinance = load_bitcoin_data(start=start_date)
        
        if not df_yfinance.empty:
            result['yfinance'] = df_yfinance
            print(f"   ✓ yfinance: {len(df_yfinance)} 条数据")
        else:
            print(f"   ✗ yfinance: 数据获取失败")
        print()
        
        # 2. Binance 数据
        print("2. 从 Binance 获取数据...")
        df_binance = self.binance.get_klines(interval='1d', limit=min(days_back, 1000))
        
        if not df_binance.empty:
            result['binance'] = df_binance
            print(f"   ✓ Binance K线: {len(df_binance)} 条数据")
        else:
            print(f"   ✗ Binance K线: 数据获取失败")
        
        # 资金费率
        if include_funding:
            df_funding = self.binance.get_funding_rate(limit=100)
            if not df_funding.empty:
                result['funding_rate'] = df_funding
                print(f"   ✓ Binance 资金费率: {len(df_funding)} 条数据")
        print()
        
        # 3. CoinGecko 数据
        print("3. 从 CoinGecko 获取数据...")
        df_coingecko = self.coingecko.get_market_chart(days=min(days_back, 365))
        
        if not df_coingecko.empty:
            result['coingecko'] = df_coingecko
            print(f"   ✓ CoinGecko 市场数据: {len(df_coingecko)} 条数据")
        else:
            print(f"   ✗ CoinGecko 市场数据: 数据获取失败")
        
        # 币种信息
        if include_market_info:
            coin_info = self.coingecko.get_coin_info()
            if coin_info:
                result['coin_info'] = coin_info
                print(f"   ✓ CoinGecko 币种信息获取成功")
        print()
        
        # 4. 链上数据
        if include_onchain:
            print("4. 从区块链获取链上数据...")
            
            # 区块链统计
            blockchain_stats = self.onchain.get_blockchain_stats()
            if blockchain_stats:
                result['blockchain_stats'] = pd.DataFrame([blockchain_stats])
                print(f"   ✓ 区块链统计数据获取成功")
            
            # 内存池信息
            mempool_info = self.onchain.get_mempool_info()
            if mempool_info:
                result['mempool_info'] = pd.DataFrame([mempool_info])
                print(f"   ✓ 内存池信息获取成功")
            
            # Glassnode 数据（如果有 API Key）
            if self.onchain.glassnode_key:
                # 活跃地址
                active_addrs = self.onchain.get_active_addresses(days=min(days_back, 180))
                if not active_addrs.empty:
                    result['active_addresses'] = active_addrs
                    print(f"   ✓ 活跃地址数据: {len(active_addrs)} 条")
                
                # UTXO 数量
                utxo_count = self.onchain.get_utxo_count(days=min(days_back, 180))
                if not utxo_count.empty:
                    result['utxo_count'] = utxo_count
                    print(f"   ✓ UTXO 数据: {len(utxo_count)} 条")
                
                # 交易所流动
                exchange_flows = self.onchain.get_exchange_flows(flow_type='net', days=min(days_back, 180))
                if not exchange_flows.empty:
                    result['exchange_flows'] = exchange_flows
                    print(f"   ✓ 交易所流动数据: {len(exchange_flows)} 条")
            else:
                print(f"   ⚠️  Glassnode 数据跳过（需要 API Key）")
            
            print()
        
        print("=" * 60)
        print(f"  数据收集完成！共 {len(result)} 个数据集")
        print("=" * 60)
        print()
        
        return result
    
    def merge_ohlcv_data(self, data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        合并多个数据源的 OHLCV 数据
        
        优先级: yfinance > Binance > CoinGecko
        
        Args:
            data_dict: 包含多个数据源的字典
        
        Returns:
            Merged DataFrame
        """
        print("正在合并 OHLCV 数据...")
        
        dfs_to_merge = []
        
        # 按优先级添加数据源
        if 'yfinance' in data_dict and not data_dict['yfinance'].empty:
            df = data_dict['yfinance'].copy()
            df['source'] = 'yfinance'
            dfs_to_merge.append(df)
            print(f"  ✓ 添加 yfinance 数据: {len(df)} 条")
        
        if 'binance' in data_dict and not data_dict['binance'].empty:
            df = data_dict['binance'].copy()
            # 标准化列名
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)
            df['source'] = 'binance'
            dfs_to_merge.append(df)
            print(f"  ✓ 添加 Binance 数据: {len(df)} 条")
        
        if 'coingecko' in data_dict and not data_dict['coingecko'].empty:
            df = data_dict['coingecko'].copy()
            # CoinGecko 只有 price，需要填充其他列
            df.rename(columns={'price': 'Close'}, inplace=True)
            df['source'] = 'coingecko'
            # 对于缺失的 OHLV 数据，用 Close 填充
            for col in ['Open', 'High', 'Low']:
                if col not in df.columns:
                    df[col] = df['Close']
            dfs_to_merge.append(df)
            print(f"  ✓ 添加 CoinGecko 数据: {len(df)} 条")
        
        if not dfs_to_merge:
            print("  ✗ 没有可合并的数据")
            return pd.DataFrame()
        
        # 合并数据（按时间戳）
        merged_df = pd.concat(dfs_to_merge)
        
        # 去重（保留最高优先级的数据）
        merged_df = merged_df[~merged_df.index.duplicated(keep='first')]
        merged_df.sort_index(inplace=True)
        
        print(f"  ✓ 合并完成: {len(merged_df)} 条数据")
        return merged_df
    
    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据验证和清洗
        
        Args:
            df: 输入 DataFrame
        
        Returns:
            Validated DataFrame
        """
        print("\n正在验证数据质量...")
        
        original_len = len(df)
        
        # 1. 检查必需列
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"  ✗ 缺少必需列: {missing_cols}")
            return df
        
        # 2. 检查空值
        null_counts = df[required_cols].isnull().sum()
        if null_counts.sum() > 0:
            print(f"  ⚠️  发现空值:")
            for col, count in null_counts[null_counts > 0].items():
                print(f"     {col}: {count} 个空值")
            
            # 前向填充
            df.fillna(method='ffill', inplace=True)
            print(f"  ✓ 已使用前向填充处理空值")
        
        # 3. 检查异常值
        # OHLC 关系检查
        invalid_ohlc = (df['High'] < df['Low']) | \
                       (df['High'] < df['Open']) | \
                       (df['High'] < df['Close']) | \
                       (df['Low'] > df['Open']) | \
                       (df['Low'] > df['Close'])
        
        if invalid_ohlc.sum() > 0:
            print(f"  ⚠️  发现 {invalid_ohlc.sum()} 条 OHLC 关系异常的数据")
            df = df[~invalid_ohlc]
        
        # 4. 检查价格异常（极端波动）
        df['returns'] = df['Close'].pct_change()
        extreme_returns = (df['returns'].abs() > 0.5)  # 单日涨跌幅超过 50%
        
        if extreme_returns.sum() > 0:
            print(f"  ⚠️  发现 {extreme_returns.sum()} 条极端波动数据（>50%）")
            # 不删除，仅警告
        
        # 5. 检查零值或负值
        zero_or_negative = (df[required_cols] <= 0).any(axis=1)
        if zero_or_negative.sum() > 0:
            print(f"  ⚠️  发现 {zero_or_negative.sum()} 条零值或负值数据")
            df = df[~zero_or_negative]
        
        # 6. 删除重复的时间戳
        duplicates = df.index.duplicated(keep='first')
        if duplicates.sum() > 0:
            print(f"  ⚠️  发现 {duplicates.sum()} 条重复时间戳")
            df = df[~duplicates]
        
        final_len = len(df)
        removed = original_len - final_len
        
        if removed > 0:
            print(f"  ✓ 数据清洗完成: 移除 {removed} 条异常数据")
        else:
            print(f"  ✓ 数据验证通过: 无异常数据")
        
        return df
    
    def save_all_data(self, data_dict: Dict, output_dir: str = 'data/raw'):
        """
        保存所有数据到文件
        
        Args:
            data_dict: 数据字典
            output_dir: 输出目录
        """
        print(f"\n正在保存数据到 {output_dir}...")
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        saved_count = 0
        
        for key, value in data_dict.items():
            if isinstance(value, pd.DataFrame) and not value.empty:
                filename = f"{output_dir}/{key}_data.csv"
                value.to_csv(filename)
                print(f"  ✓ {filename}")
                saved_count += 1
            elif isinstance(value, dict):
                filename = f"{output_dir}/{key}_info.csv"
                pd.DataFrame([value]).to_csv(filename, index=False)
                print(f"  ✓ {filename}")
                saved_count += 1
        
        print(f"\n✓ 共保存 {saved_count} 个文件")


def main():
    """测试市场数据聚合器"""
    print("=" * 60)
    print("  市场数据聚合器测试")
    print("=" * 60)
    print()
    
    aggregator = MarketDataAggregator()
    
    # 1. 获取综合数据
    print("【步骤 1】获取综合数据\n")
    data_dict = aggregator.get_comprehensive_data(
        days_back=90,
        include_funding=True,
        include_market_info=True
    )
    
    # 2. 合并 OHLCV 数据
    print("\n【步骤 2】合并 OHLCV 数据\n")
    merged_df = aggregator.merge_ohlcv_data(data_dict)
    
    if not merged_df.empty:
        print(f"\n合并后的数据预览:")
        print(merged_df.tail(10))
    
    # 3. 数据验证
    if not merged_df.empty:
        print("\n【步骤 3】数据验证")
        validated_df = aggregator.validate_data(merged_df)
        
        # 添加到数据字典
        data_dict['merged_validated'] = validated_df
    
    # 4. 保存所有数据
    print("\n【步骤 4】保存数据")
    aggregator.save_all_data(data_dict)
    
    # 5. 数据统计
    print("\n" + "=" * 60)
    print("  数据统计")
    print("=" * 60)
    
    if not merged_df.empty:
        print(f"\n数据范围: {merged_df.index[0]} 到 {merged_df.index[-1]}")
        print(f"数据条数: {len(merged_df)}")
        print(f"\n基本统计:")
        print(merged_df[['Open', 'High', 'Low', 'Close', 'Volume']].describe())
        
        if 'funding_rate' in data_dict:
            print(f"\n资金费率统计:")
            print(data_dict['funding_rate']['fundingRate'].describe())
    
    print("\n" + "=" * 60)
    print("  测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

