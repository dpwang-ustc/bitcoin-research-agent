"""
CoinGecko API 数据收集器

功能：
1. 获取比特币市场数据（价格、市值、交易量）
2. 获取历史数据
3. 获取币种基本信息
4. 支持多种法币

依赖：requests, pandas
免费 API，有限流（10-50次/分钟）
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time


class CoinGeckoCollector:
    """CoinGecko 数据收集器"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # 币种 ID 映射
    COIN_IDS = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'USDT': 'tether'
    }
    
    def __init__(self, coin_id: str = "bitcoin", vs_currency: str = "usd"):
        """
        初始化
        
        Args:
            coin_id: 币种 ID（如 'bitcoin', 'ethereum'）
            vs_currency: 对标货币（如 'usd', 'cny'）
        """
        self.coin_id = coin_id
        self.vs_currency = vs_currency
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Bitcoin Research Agent)',
            'Accept': 'application/json'
        })
        self.request_count = 0
        self.last_request_time = time.time()
    
    def _rate_limit(self):
        """限流控制（免费版约 10-50 次/分钟）"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # 每次请求至少间隔 2 秒（安全起见）
        if time_since_last < 2:
            time.sleep(2 - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get_current_price(self) -> Dict:
        """
        获取当前价格及市场数据
        
        Returns:
            Dict with current price and market data
        """
        endpoint = f"{self.BASE_URL}/simple/price"
        
        params = {
            "ids": self.coin_id,
            "vs_currencies": self.vs_currency,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
            "include_last_updated_at": "true"
        }
        
        self._rate_limit()
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if self.coin_id in data:
                result = data[self.coin_id]
                print(f"✓ 成功获取 {self.coin_id} 当前数据")
                return result
            else:
                print(f"✗ 未找到 {self.coin_id} 数据")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"✗ CoinGecko API 请求失败: {e}")
            return {}
    
    def get_market_chart(self, days: int = 365, interval: str = 'daily') -> pd.DataFrame:
        """
        获取市场图表数据（价格、市值、交易量）
        
        Args:
            days: 回溯天数 (1, 7, 14, 30, 90, 180, 365, max)
            interval: 数据间隔 ('daily' 或自动)
        
        Returns:
            DataFrame with price, market_cap, volume
        """
        endpoint = f"{self.BASE_URL}/coins/{self.coin_id}/market_chart"
        
        params = {
            "vs_currency": self.vs_currency,
            "days": days if days != 'max' else 'max',
            "interval": interval
        }
        
        self._rate_limit()
        
        try:
            response = self.session.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # 解析数据
            prices = data.get('prices', [])
            market_caps = data.get('market_caps', [])
            volumes = data.get('total_volumes', [])
            
            # 转换为 DataFrame
            df_price = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df_market_cap = pd.DataFrame(market_caps, columns=['timestamp', 'market_cap'])
            df_volume = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
            
            # 合并数据
            df = df_price.merge(df_market_cap, on='timestamp', how='outer')
            df = df.merge(df_volume, on='timestamp', how='outer')
            
            # 转换时间戳
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            print(f"✓ 成功获取 {len(df)} 条市场数据 ({days} 天)")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ CoinGecko 市场数据请求失败: {e}")
            return pd.DataFrame()
    
    def get_coin_info(self) -> Dict:
        """
        获取币种详细信息
        
        Returns:
            Dict with coin information
        """
        endpoint = f"{self.BASE_URL}/coins/{self.coin_id}"
        
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false"
        }
        
        self._rate_limit()
        
        try:
            response = self.session.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # 提取关键信息
            market_data = data.get('market_data', {})
            
            result = {
                'id': data.get('id'),
                'symbol': data.get('symbol', '').upper(),
                'name': data.get('name'),
                'market_cap_rank': data.get('market_cap_rank'),
                'current_price': market_data.get('current_price', {}).get(self.vs_currency),
                'market_cap': market_data.get('market_cap', {}).get(self.vs_currency),
                'total_volume': market_data.get('total_volume', {}).get(self.vs_currency),
                'high_24h': market_data.get('high_24h', {}).get(self.vs_currency),
                'low_24h': market_data.get('low_24h', {}).get(self.vs_currency),
                'price_change_24h': market_data.get('price_change_24h'),
                'price_change_percentage_24h': market_data.get('price_change_percentage_24h'),
                'circulating_supply': market_data.get('circulating_supply'),
                'total_supply': market_data.get('total_supply'),
                'max_supply': market_data.get('max_supply'),
                'ath': market_data.get('ath', {}).get(self.vs_currency),
                'ath_date': market_data.get('ath_date', {}).get(self.vs_currency),
                'atl': market_data.get('atl', {}).get(self.vs_currency),
                'atl_date': market_data.get('atl_date', {}).get(self.vs_currency),
            }
            
            print(f"✓ 成功获取 {self.coin_id} 详细信息")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"✗ CoinGecko 币种信息请求失败: {e}")
            return {}
    
    def get_ohlc(self, days: int = 90) -> pd.DataFrame:
        """
        获取 OHLC 数据（仅支持特定天数）
        
        Args:
            days: 天数 (1, 7, 14, 30, 90, 180, 365)
        
        Returns:
            DataFrame with OHLC data
        """
        endpoint = f"{self.BASE_URL}/coins/{self.coin_id}/ohlc"
        
        # CoinGecko OHLC 仅支持特定天数
        valid_days = [1, 7, 14, 30, 90, 180, 365]
        if days not in valid_days:
            days = min(valid_days, key=lambda x: abs(x - days))
            print(f"ℹ️  调整为支持的天数: {days}")
        
        params = {
            "vs_currency": self.vs_currency,
            "days": days
        }
        
        self._rate_limit()
        
        try:
            response = self.session.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # 转换为 DataFrame
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            print(f"✓ 成功获取 {len(df)} 条 OHLC 数据 ({days} 天)")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ CoinGecko OHLC 请求失败: {e}")
            return pd.DataFrame()
    
    def get_historical_data_by_date(self, date: str) -> Dict:
        """
        获取特定日期的历史数据
        
        Args:
            date: 日期字符串 (格式: DD-MM-YYYY)
        
        Returns:
            Dict with historical data for that date
        """
        endpoint = f"{self.BASE_URL}/coins/{self.coin_id}/history"
        
        params = {
            "date": date,
            "localization": "false"
        }
        
        self._rate_limit()
        
        try:
            response = self.session.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            market_data = data.get('market_data', {})
            
            result = {
                'date': date,
                'price': market_data.get('current_price', {}).get(self.vs_currency),
                'market_cap': market_data.get('market_cap', {}).get(self.vs_currency),
                'total_volume': market_data.get('total_volume', {}).get(self.vs_currency)
            }
            
            print(f"✓ 成功获取 {date} 的历史数据")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"✗ CoinGecko 历史数据请求失败: {e}")
            return {}


def main():
    """测试 CoinGecko 数据收集器"""
    print("=" * 60)
    print("  CoinGecko 数据收集器测试")
    print("=" * 60)
    print()
    
    collector = CoinGeckoCollector()
    
    # 1. 测试当前价格
    print("1. 获取当前价格:")
    current = collector.get_current_price()
    if current:
        price = current.get('usd', 0)
        market_cap = current.get('usd_market_cap', 0)
        volume_24h = current.get('usd_24h_vol', 0)
        change_24h = current.get('usd_24h_change', 0)
        
        print(f"  当前价格: ${price:,.2f}")
        print(f"  市值: ${market_cap:,.0f}")
        print(f"  24h 交易量: ${volume_24h:,.0f}")
        print(f"  24h 变化: {change_24h:.2f}%")
    print()
    
    # 2. 测试币种信息
    print("2. 获取币种详细信息:")
    info = collector.get_coin_info()
    if info:
        print(f"  名称: {info.get('name')} ({info.get('symbol')})")
        print(f"  市值排名: #{info.get('market_cap_rank')}")
        print(f"  历史最高: ${info.get('ath'):,.2f}")
        print(f"  流通供应: {info.get('circulating_supply'):,.0f} BTC")
    print()
    
    # 3. 测试市场图表数据
    print("3. 获取最近 30 天的市场数据:")
    df_market = collector.get_market_chart(days=30, interval='daily')
    if not df_market.empty:
        print(f"  数据范围: {df_market.index[0]} 到 {df_market.index[-1]}")
        print(f"\n最近 5 天数据:")
        print(df_market.tail())
    print()
    
    # 4. 测试 OHLC 数据
    print("4. 获取 OHLC 数据 (90天):")
    df_ohlc = collector.get_ohlc(days=90)
    if not df_ohlc.empty:
        print(f"  数据范围: {df_ohlc.index[0]} 到 {df_ohlc.index[-1]}")
        print(f"\n最近 5 天数据:")
        print(df_ohlc.tail())
    print()
    
    # 5. 保存数据
    print("5. 保存数据到文件:")
    if not df_market.empty:
        df_market.to_csv('data/raw/coingecko_bitcoin_market.csv')
        print("  ✓ 已保存: data/raw/coingecko_bitcoin_market.csv")
    
    if not df_ohlc.empty:
        df_ohlc.to_csv('data/raw/coingecko_bitcoin_ohlc.csv')
        print("  ✓ 已保存: data/raw/coingecko_bitcoin_ohlc.csv")
    
    print()
    print("=" * 60)
    print("  测试完成！")
    print("=" * 60)
    print()
    print("⚠️  注意: CoinGecko 免费 API 有限流")
    print("   建议每次请求间隔 2 秒以上")


if __name__ == "__main__":
    main()

