"""
Binance API 数据收集器

功能：
1. 获取 BTC/USDT K线数据（历史和实时）
2. 获取资金费率数据（期货）
3. 获取 24h 交易统计
4. 支持多种时间间隔

依赖：requests, pandas
无需 API Key（使用公开接口）
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
import time


class BinanceCollector:
    """Binance 数据收集器"""
    
    # API 端点
    SPOT_BASE_URL = "https://api.binance.com/api/v3"
    FUTURES_BASE_URL = "https://fapi.binance.com/fapi/v1"
    
    # 时间间隔映射
    INTERVALS = {
        '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m', '30m': '30m',
        '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h', '8h': '8h', '12h': '12h',
        '1d': '1d', '3d': '3d', '1w': '1w', '1M': '1M'
    }
    
    def __init__(self, symbol: str = "BTCUSDT"):
        """
        初始化
        
        Args:
            symbol: 交易对符号，默认 BTCUSDT
        """
        self.symbol = symbol
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Bitcoin Research Agent)'
        })
    
    def get_klines(self, 
                   interval: str = '1d', 
                   limit: int = 500,
                   start_time: Optional[str] = None,
                   end_time: Optional[str] = None) -> pd.DataFrame:
        """
        获取 K线数据
        
        Args:
            interval: 时间间隔 (1m, 5m, 1h, 1d 等)
            limit: 返回数据条数 (最大1000)
            start_time: 开始时间 (YYYY-MM-DD 格式)
            end_time: 结束时间 (YYYY-MM-DD 格式)
        
        Returns:
            DataFrame with OHLCV data
        """
        endpoint = f"{self.SPOT_BASE_URL}/klines"
        
        params = {
            "symbol": self.symbol,
            "interval": interval,
            "limit": min(limit, 1000)  # Binance 最大限制
        }
        
        # 转换时间格式
        if start_time:
            params["startTime"] = int(pd.to_datetime(start_time).timestamp() * 1000)
        if end_time:
            params["endTime"] = int(pd.to_datetime(end_time).timestamp() * 1000)
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 转换为 DataFrame
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # 数据类型转换
            df['timestamp'] = pd.to_datetime(df['open_time'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 选择需要的列
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df.set_index('timestamp', inplace=True)
            
            print(f"✓ 成功获取 {len(df)} 条 Binance K线数据 ({interval})")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Binance API 请求失败: {e}")
            return pd.DataFrame()
    
    def get_historical_klines(self,
                             interval: str = '1d',
                             days_back: int = 365) -> pd.DataFrame:
        """
        获取历史 K线数据（自动分批处理大量数据）
        
        Args:
            interval: 时间间隔
            days_back: 回溯天数
        
        Returns:
            DataFrame with historical data
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        print(f"正在获取 {days_back} 天的历史数据...")
        
        all_data = []
        current_start = start_time
        
        # 分批获取（每次最多1000条）
        while current_start < end_time:
            df_batch = self.get_klines(
                interval=interval,
                limit=1000,
                start_time=current_start.strftime('%Y-%m-%d'),
                end_time=end_time.strftime('%Y-%m-%d')
            )
            
            if df_batch.empty:
                break
            
            all_data.append(df_batch)
            current_start = df_batch.index[-1] + timedelta(days=1)
            time.sleep(0.5)  # 避免请求过快
        
        if all_data:
            df = pd.concat(all_data)
            df = df[~df.index.duplicated(keep='first')]  # 去重
            df.sort_index(inplace=True)
            print(f"✓ 总共获取 {len(df)} 条历史数据")
            return df
        else:
            return pd.DataFrame()
    
    def get_funding_rate(self, limit: int = 100) -> pd.DataFrame:
        """
        获取资金费率数据（期货）
        
        Args:
            limit: 返回数据条数 (最大1000)
        
        Returns:
            DataFrame with funding rate data
        """
        endpoint = f"{self.FUTURES_BASE_URL}/fundingRate"
        
        params = {
            "symbol": self.symbol,
            "limit": min(limit, 1000)
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            df['fundingTime'] = pd.to_datetime(df['fundingTime'], unit='ms')
            df['fundingRate'] = pd.to_numeric(df['fundingRate'])
            
            df.set_index('fundingTime', inplace=True)
            print(f"✓ 成功获取 {len(df)} 条资金费率数据")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Binance 资金费率请求失败: {e}")
            return pd.DataFrame()
    
    def get_24h_ticker(self) -> dict:
        """
        获取 24h 价格变动统计
        
        Returns:
            Dict with 24h statistics
        """
        endpoint = f"{self.SPOT_BASE_URL}/ticker/24hr"
        
        params = {"symbol": self.symbol}
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 提取关键信息
            result = {
                'symbol': data['symbol'],
                'price_change': float(data['priceChange']),
                'price_change_percent': float(data['priceChangePercent']),
                'last_price': float(data['lastPrice']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume']),
                'high_price': float(data['highPrice']),
                'low_price': float(data['lowPrice']),
                'open_price': float(data['openPrice']),
                'trades': int(data['count'])
            }
            
            print(f"✓ 成功获取 24h 统计数据")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Binance 24h 统计请求失败: {e}")
            return {}
    
    def get_current_price(self) -> float:
        """
        获取当前价格
        
        Returns:
            Current price as float
        """
        endpoint = f"{self.SPOT_BASE_URL}/ticker/price"
        
        params = {"symbol": self.symbol}
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            price = float(data['price'])
            print(f"✓ {self.symbol} 当前价格: ${price:,.2f}")
            return price
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Binance 价格请求失败: {e}")
            return 0.0


def main():
    """测试 Binance 数据收集器"""
    print("=" * 60)
    print("  Binance 数据收集器测试")
    print("=" * 60)
    print()
    
    collector = BinanceCollector()
    
    # 1. 测试当前价格
    print("1. 获取当前价格:")
    price = collector.get_current_price()
    print()
    
    # 2. 测试 24h 统计
    print("2. 获取 24h 统计:")
    stats = collector.get_24h_ticker()
    if stats:
        print(f"  价格变动: {stats['price_change_percent']:.2f}%")
        print(f"  24h 最高: ${stats['high_price']:,.2f}")
        print(f"  24h 最低: ${stats['low_price']:,.2f}")
        print(f"  24h 交易量: {stats['volume']:,.2f} BTC")
    print()
    
    # 3. 测试 K线数据
    print("3. 获取最近 30 天的日线数据:")
    df_daily = collector.get_klines(interval='1d', limit=30)
    if not df_daily.empty:
        print(f"  数据范围: {df_daily.index[0]} 到 {df_daily.index[-1]}")
        print(f"\n最近 5 天数据:")
        print(df_daily.tail())
    print()
    
    # 4. 测试资金费率
    print("4. 获取最近的资金费率:")
    df_funding = collector.get_funding_rate(limit=10)
    if not df_funding.empty:
        print(f"  最近资金费率: {df_funding['fundingRate'].iloc[-1]:.6f}")
        print(f"\n最近 5 条记录:")
        print(df_funding.tail())
    print()
    
    # 5. 保存数据
    print("5. 保存数据到文件:")
    if not df_daily.empty:
        df_daily.to_csv('data/raw/binance_btcusdt_daily.csv')
        print("  ✓ 已保存: data/raw/binance_btcusdt_daily.csv")
    
    if not df_funding.empty:
        df_funding.to_csv('data/raw/binance_funding_rate.csv')
        print("  ✓ 已保存: data/raw/binance_funding_rate.csv")
    
    print()
    print("=" * 60)
    print("  测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

