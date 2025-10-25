"""
链上数据收集器

功能：
1. 区块链基础数据（区块高度、哈希率等）
2. UTXO 分布和持仓分析
3. 活跃地址数和网络活跃度
4. 大额转账监控（鲸鱼行为）
5. 交易所资金流动

支持的数据源：
- Blockchain.com API (免费)
- Glassnode API (免费层 + 付费)
- Mempool.space API (免费)

依赖：requests, pandas
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
import os


class OnchainCollector:
    """链上数据收集器"""
    
    # API 端点
    BLOCKCHAIN_COM_BASE = "https://blockchain.info"
    MEMPOOL_SPACE_BASE = "https://mempool.space/api"
    GLASSNODE_BASE = "https://api.glassnode.com/v1/metrics"
    
    def __init__(self, glassnode_key: Optional[str] = None):
        """
        初始化
        
        Args:
            glassnode_key: Glassnode API Key (可选，免费层也需要)
        """
        self.glassnode_key = glassnode_key or os.getenv("GLASSNODE_API_KEY")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Bitcoin Research Agent)'
        })
        self.request_count = 0
        self.last_request_time = time.time()
    
    def _rate_limit(self, min_interval: float = 1.0):
        """限流控制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    # ==================== Blockchain.com API ====================
    
    def get_blockchain_stats(self) -> Dict:
        """
        获取区块链统计数据 (Blockchain.com)
        
        Returns:
            Dict with blockchain statistics
        """
        endpoint = f"{self.BLOCKCHAIN_COM_BASE}/stats"
        
        self._rate_limit()
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = {
                'timestamp': datetime.now(),
                'market_price_usd': data.get('market_price_usd'),
                'hash_rate': data.get('hash_rate'),
                'total_btc': data.get('totalbc') / 1e8,  # Satoshi to BTC
                'n_btc_mined': data.get('n_btc_mined') / 1e8,
                'n_tx': data.get('n_tx'),
                'n_blocks_mined': data.get('n_blocks_mined'),
                'minutes_between_blocks': data.get('minutes_between_blocks'),
                'total_fees_btc': data.get('total_fees') / 1e8,
                'difficulty': data.get('difficulty'),
                'estimated_btc_sent': data.get('estimated_btc_sent') / 1e8,
                'blocks_size': data.get('blocks_size'),
                'miners_revenue_usd': data.get('miners_revenue_usd'),
                'market_cap_usd': data.get('market_price_usd') * data.get('totalbc') / 1e8
            }
            
            print(f"✓ 成功获取区块链统计数据")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Blockchain.com API 请求失败: {e}")
            return {}
    
    def get_mempool_info(self) -> Dict:
        """
        获取内存池信息 (Mempool.space)
        
        Returns:
            Dict with mempool info
        """
        endpoint = f"{self.MEMPOOL_SPACE_BASE}/mempool"
        
        self._rate_limit()
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = {
                'timestamp': datetime.now(),
                'mempool_size': data.get('size'),
                'mempool_bytes': data.get('bytes'),
                'mempool_usage': data.get('usage'),
                'total_fee': data.get('total_fee')
            }
            
            print(f"✓ 成功获取内存池信息")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Mempool.space API 请求失败: {e}")
            return {}
    
    def get_address_balance(self, address: str) -> Dict:
        """
        获取地址余额 (Blockchain.com)
        
        Args:
            address: Bitcoin 地址
        
        Returns:
            Dict with address balance info
        """
        endpoint = f"{self.BLOCKCHAIN_COM_BASE}/balance"
        params = {"active": address}
        
        self._rate_limit()
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if address in data:
                addr_data = data[address]
                result = {
                    'address': address,
                    'balance_btc': addr_data.get('final_balance', 0) / 1e8,
                    'total_received_btc': addr_data.get('total_received', 0) / 1e8,
                    'total_sent_btc': addr_data.get('total_sent', 0) / 1e8,
                    'n_tx': addr_data.get('n_tx', 0)
                }
                return result
            else:
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 地址余额查询失败: {e}")
            return {}
    
    def get_large_transactions(self, threshold_btc: float = 100.0) -> pd.DataFrame:
        """
        获取大额交易 (Blockchain.com)
        
        Args:
            threshold_btc: 大额交易阈值（BTC）
        
        Returns:
            DataFrame with large transactions
        """
        # 注意: Blockchain.com 的未确认交易 API
        endpoint = f"{self.BLOCKCHAIN_COM_BASE}/unconfirmed-transactions"
        params = {"format": "json"}
        
        self._rate_limit()
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            transactions = []
            for tx in data.get('txs', []):
                # 计算交易总额
                total_output = sum(out.get('value', 0) for out in tx.get('out', []))
                total_btc = total_output / 1e8
                
                if total_btc >= threshold_btc:
                    transactions.append({
                        'hash': tx.get('hash'),
                        'time': datetime.fromtimestamp(tx.get('time', 0)),
                        'size': tx.get('size'),
                        'total_btc': total_btc,
                        'fee_btc': tx.get('fee', 0) / 1e8,
                        'n_inputs': len(tx.get('inputs', [])),
                        'n_outputs': len(tx.get('out', []))
                    })
            
            df = pd.DataFrame(transactions)
            if not df.empty:
                print(f"✓ 发现 {len(df)} 笔大额交易 (>{threshold_btc} BTC)")
            else:
                print(f"ℹ️  当前无大额交易")
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ 大额交易查询失败: {e}")
            return pd.DataFrame()
    
    # ==================== Glassnode API ====================
    
    def get_active_addresses(self, days: int = 30) -> pd.DataFrame:
        """
        获取活跃地址数 (Glassnode)
        
        Args:
            days: 回溯天数
        
        Returns:
            DataFrame with active addresses over time
        """
        if not self.glassnode_key:
            print("⚠️  需要 Glassnode API Key")
            print("   注册: https://studio.glassnode.com/settings/api")
            print("   设置环境变量: GLASSNODE_API_KEY")
            return pd.DataFrame()
        
        endpoint = f"{self.GLASSNODE_BASE}/addresses/active_count"
        
        since = int((datetime.now() - timedelta(days=days)).timestamp())
        params = {
            "a": "BTC",
            "api_key": self.glassnode_key,
            "s": since,
            "i": "24h"  # 日数据
        }
        
        self._rate_limit(min_interval=2.0)
        
        try:
            response = self.session.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['t'], unit='s')
            df['active_addresses'] = df['v']
            df = df[['timestamp', 'active_addresses']]
            df.set_index('timestamp', inplace=True)
            
            print(f"✓ 成功获取 {len(df)} 天的活跃地址数据")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Glassnode API 请求失败: {e}")
            if "401" in str(e) or "403" in str(e):
                print("   请检查 API Key 是否正确")
            return pd.DataFrame()
    
    def get_utxo_count(self, days: int = 30) -> pd.DataFrame:
        """
        获取 UTXO 数量 (Glassnode)
        
        Args:
            days: 回溯天数
        
        Returns:
            DataFrame with UTXO count over time
        """
        if not self.glassnode_key:
            print("⚠️  需要 Glassnode API Key")
            return pd.DataFrame()
        
        endpoint = f"{self.GLASSNODE_BASE}/blockchain/utxo_count"
        
        since = int((datetime.now() - timedelta(days=days)).timestamp())
        params = {
            "a": "BTC",
            "api_key": self.glassnode_key,
            "s": since,
            "i": "24h"
        }
        
        self._rate_limit(min_interval=2.0)
        
        try:
            response = self.session.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['t'], unit='s')
            df['utxo_count'] = df['v']
            df = df[['timestamp', 'utxo_count']]
            df.set_index('timestamp', inplace=True)
            
            print(f"✓ 成功获取 {len(df)} 天的 UTXO 数据")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Glassnode UTXO 数据请求失败: {e}")
            return pd.DataFrame()
    
    def get_exchange_flows(self, flow_type: str = "net", days: int = 30) -> pd.DataFrame:
        """
        获取交易所资金流动 (Glassnode)
        
        Args:
            flow_type: "inflow", "outflow", "net"
            days: 回溯天数
        
        Returns:
            DataFrame with exchange flows
        """
        if not self.glassnode_key:
            print("⚠️  需要 Glassnode API Key")
            return pd.DataFrame()
        
        flow_endpoints = {
            "inflow": "transactions/transfers_volume_exchanges_in",
            "outflow": "transactions/transfers_volume_exchanges_out",
            "net": "transactions/transfers_volume_exchanges_net"
        }
        
        if flow_type not in flow_endpoints:
            flow_type = "net"
        
        endpoint = f"{self.GLASSNODE_BASE}/{flow_endpoints[flow_type]}"
        
        since = int((datetime.now() - timedelta(days=days)).timestamp())
        params = {
            "a": "BTC",
            "api_key": self.glassnode_key,
            "s": since,
            "i": "24h"
        }
        
        self._rate_limit(min_interval=2.0)
        
        try:
            response = self.session.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['t'], unit='s')
            df['flow_btc'] = df['v']
            df = df[['timestamp', 'flow_btc']]
            df.set_index('timestamp', inplace=True)
            
            print(f"✓ 成功获取 {len(df)} 天的交易所{flow_type}数据")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Glassnode 交易所流动数据请求失败: {e}")
            return pd.DataFrame()
    
    # ==================== 综合分析 ====================
    
    def get_network_health_summary(self) -> Dict:
        """
        获取网络健康度综合指标
        
        Returns:
            Dict with network health metrics
        """
        print("\n正在获取网络健康度综合指标...")
        
        result = {}
        
        # 1. 区块链统计
        blockchain_stats = self.get_blockchain_stats()
        if blockchain_stats:
            result['blockchain_stats'] = blockchain_stats
        
        # 2. 内存池信息
        mempool_info = self.get_mempool_info()
        if mempool_info:
            result['mempool_info'] = mempool_info
        
        # 3. 活跃地址（如果有 API Key）
        if self.glassnode_key:
            active_addrs = self.get_active_addresses(days=7)
            if not active_addrs.empty:
                result['avg_active_addresses_7d'] = active_addrs['active_addresses'].mean()
        
        return result


def main():
    """测试链上数据收集器"""
    print("=" * 60)
    print("  链上数据收集器测试")
    print("=" * 60)
    print()
    
    collector = OnchainCollector()
    
    # 1. 测试区块链统计
    print("1. 获取区块链统计数据:")
    stats = collector.get_blockchain_stats()
    if stats:
        print(f"  当前价格: ${stats.get('market_price_usd', 0):,.2f}")
        print(f"  哈希率: {stats.get('hash_rate', 0):,.0f} TH/s")
        print(f"  总供应量: {stats.get('total_btc', 0):,.2f} BTC")
        print(f"  24h 交易数: {stats.get('n_tx', 0):,}")
    print()
    
    # 2. 测试内存池信息
    print("2. 获取内存池信息:")
    mempool = collector.get_mempool_info()
    if mempool:
        print(f"  内存池大小: {mempool.get('mempool_size', 0):,} 笔交易")
        print(f"  内存池字节: {mempool.get('mempool_bytes', 0):,} bytes")
    print()
    
    # 3. 测试大额交易
    print("3. 查询大额交易 (>100 BTC):")
    large_txs = collector.get_large_transactions(threshold_btc=100.0)
    if not large_txs.empty:
        print(f"\n最近的大额交易:")
        print(large_txs.head())
    print()
    
    # 4. 测试 Glassnode (如果有 API Key)
    if collector.glassnode_key:
        print("4. 测试 Glassnode API:")
        
        # 活跃地址
        active = collector.get_active_addresses(days=7)
        if not active.empty:
            print(f"  最近7天活跃地址:")
            print(active.tail())
    else:
        print("4. Glassnode API 测试跳过")
        print("   提示: 设置 GLASSNODE_API_KEY 环境变量以启用")
    print()
    
    # 5. 综合健康度
    print("5. 网络健康度综合指标:")
    health = collector.get_network_health_summary()
    print(f"  数据项数: {len(health)}")
    
    # 6. 保存数据
    print("\n6. 保存数据:")
    if stats:
        df_stats = pd.DataFrame([stats])
        df_stats.to_csv('data/raw/onchain_stats.csv', index=False)
        print("  ✓ data/raw/onchain_stats.csv")
    
    if not large_txs.empty:
        large_txs.to_csv('data/raw/large_transactions.csv')
        print("  ✓ data/raw/large_transactions.csv")
    
    print("\n" + "=" * 60)
    print("  测试完成！")
    print("=" * 60)
    print("\n提示:")
    print("- Blockchain.com 和 Mempool.space API 完全免费")
    print("- Glassnode 需要注册免费账号获取 API Key")
    print("- 更多指标可通过付费 API 获取")


if __name__ == "__main__":
    main()

